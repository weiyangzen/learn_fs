# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.c

## Purpose

`drbd_state.c` is the central DRBD state-machine implementation for a replicated block device, its connection, peer device, and resource-level suspension flags. It validates requested state transitions, sanitizes implied state fields, applies state changes under `resource->req_lock`, records old/new state snapshots for notifications, and queues post-transition work that may sleep. The file bridges kernel-visible DRBD state, cluster-wide peer negotiation, userspace notification, metadata persistence, bitmap actions, UUID handling, receiver thread control, and resync/verify start-stop transitions.

## Important APIs, Types, and Functions

The key private work objects are `struct after_state_chg_work` and `struct after_conn_state_chg_work`, which defer sleeping after-change side effects onto `connection->sender_work`. `enum sanitize_state_warnings` captures implicit changes such as aborted verify/resync and connection-loss during negotiation.

State-change snapshot helpers implement the notification record model declared in `drbd_state_change.h`: `remember_old_state()` counts devices/connections, allocates one packed `struct drbd_state_change`, records resource, connection, device, and peer-device old fields, and takes krefs; `remember_new_state()` fills the new fields after the state mutation; `copy_old_to_new_state_change()` is used when a caller needs a no-op-looking notification record; `forget_state_change()` drops captured krefs and frees the packed allocation.

Public state APIs are `drbd_change_state()`, `drbd_force_state()`, `_drbd_request_state()`, `_drbd_request_state_holding_state_mutex()`, `drbd_request_detach_interruptible()`, `_drbd_set_state()`, `_conn_request_state()`, and `conn_request_state()`. The connection aggregate helpers `conn_highest_role()`, `conn_highest_peer()`, `conn_highest_disk()`, `conn_lowest_disk()`, `conn_highest_pdsk()`, `conn_lowest_conn()`, and `conn_all_vols_unconf()` summarize all peer devices on a connection under RCU.

Validation is split into `is_valid_conn_transition()`, `is_valid_transition()`, `is_valid_state()`, and `is_valid_soft_transition()`. Sanitization is centralized in `sanitize_state()`. Notification callbacks include `notify_resource_state_change()`, `notify_connection_state_change()`, `notify_device_state_change()`, `notify_peer_device_state_change()`, and `broadcast_state_change()`.

## Control Flow

Simple callers enter through `drbd_change_state()` or the inline wrapper `drbd_request_state()` in `drbd_state.h`. The request path computes `ns = apply_mask_val(os, mask, val)`, passes it through `sanitize_state()`, and checks hard transition legality. For soft transitions, `_drbd_set_state()` additionally validates data safety, fencing constraints, two-primary policy, open-count demotion constraints, resync/verify preconditions, and transient handshake states.

Cluster-wide transitions are detected by `cl_wide_st_chg()`, including promotion, resync start, disk failure, disconnect, verify start, and report-params transitions while connected. `drbd_req_state()` sends `drbd_send_state_req()` to the peer, waits on `device->state_wait` until `_req_st_cond()` observes success/failure flags or a local validation result, then applies the state. Connection-wide transitions use `_conn_request_state()`, which can send `conn_send_state_req()` and wait on `connection->ping_wait` before calling `conn_set_state()` for every volume.

`_drbd_set_state()` is the mutation point. The caller must hold `req_lock`. It sanitizes, validates, logs, optionally increments `local_cnt` for transitions into `D_FAILED` or `D_DISKLESS`, remembers old state, writes `device->state` plus resource suspension flags with write barriers, remembers new state, updates transfer-log epoch boundaries, wakes wait queues, updates verify/resync counters, updates metadata flags, and queues `w_after_state_ch()`.

`after_state_ch()` performs the operations that cannot run inside the spinlock: broadcasts netlink notifications, sends state/UUID/bitmap messages, calls userspace helpers, resumes or suspends dependent sync groups, writes bitmap pages, handles local disk failure/detach cleanup, coordinates UUID bumps after peer data loss, and marks metadata dirty/synced. Connection-wide queued work `w_after_conn_state_ch()` starts/stops receiver side effects, emits destroy notifications, clears network configuration after disconnect completion, handles successful fencing/outdate recovery, syncs metadata, and releases the connection kref.

## State and Persistence Behavior

`sanitize_state()` encodes most implicit state coupling: below `C_CONNECTED`, peer role and peer-ISP are cleared and peer disk becomes `D_UNKNOWN`; disk/peer-disk bounds are derived from connection state; verify/resync states collapse to `C_CONNECTED` if a disk fails; `D_CONSISTENT`/`D_OUTDATED` are promoted to `D_UP_TO_DATE` when reconnecting; sync pause flags switch `C_SYNC_*` to `C_PAUSED_SYNC_*`; fencing and no-data policies set `susp_fen` or `susp_nod`.

Metadata persistence is managed in `_drbd_set_state()` and `after_state_ch()`. The code updates `ldev->md.flags` for consistency, primary, connected, peer-outdated, crashed-primary, and was-up-to-date indicators, marks metadata dirty, records exposed-data UUIDs, writes changed bitmap pages on demote/detach/resync finish, and calls `drbd_md_sync()` after many state-side effects. Transitions through `D_FAILED` and `D_DISKLESS` are reference-counted using `local_cnt` to serialize `drbd_ldev_destroy()` with after-change cleanup.

## Dependencies and Integration Points

This file depends on DRBD core types and helpers from `drbd_int.h`, wire protocol helpers from `drbd_protocol.h`, request state machinery from `drbd_req.h`, and notification layouts from `drbd_state_change.h`. It integrates with the sender work queue, receiver thread lifecycle, transfer log epochs, bitmap I/O, UUID management, metadata I/O, userspace helper hooks, RCU-protected config, netlink notifications, and wait queues (`state_wait`, `misc_wait`, `ping_wait`).

## Risks and Edge Cases

The file is concurrency-sensitive: state fields are protected by `req_lock`, connection/device lists by RCU, lifecycle by krefs and `local_cnt`, and some transitions deliberately drop locks to perform cluster-wide handshakes. Bugs here can create split-brain exposure, stale peer-disk assumptions, lost bitmap persistence, deadlocks around metadata buffers, or use-after-free in delayed after-change work. The allocation failure path for after-change work logs but does not run the deferred side effects inline, so notification or cleanup gaps are possible under memory pressure. Many invariants depend on exact state ordering and comments note historical enum-order issues.

## Test Signals

Useful test signals include transition return codes and log lines from `print_st_err()`, `drbd_pr_state_change()`, `conn_pr_state_change()`, and sanitize warnings. Functional coverage should exercise promotion/demotion, disconnect from each connection phase, attach failure, local I/O error to `D_FAILED` then `D_DISKLESS`, fencing/no-data suspension, online verify start/stop, resync start/finish/abort, peer disk attach/detach, and multi-volume connection-wide transitions. Persistence tests should inspect metadata flags and bitmap writeouts after demote, detach, and resync completion. Race tests should target cluster-wide request waits, `STATE_SENT` transient handling, receiver restart/stop, and queued after-state work under connection teardown.
