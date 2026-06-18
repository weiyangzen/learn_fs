# Research: subset-b-001056

Grouped research for DRBD state, worker, string, and VLI helpers under `sources/distributed-fs/ceph-client/drivers/block/drbd/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.h

## Purpose

`drbd_state.h` declares the public state-machine interface and macro language used by DRBD callers to express state changes. It is the small but important contract between administrative paths, receiver/worker code, request code, and the implementation in `drbd_state.c`.

## Important APIs, Types, and Macros

The `NS`, `NS2`, and `NS3` macros build `(mask, value)` pairs for one, two, or three state fields. The `_NS`, `_NS2`, and `_NS3` variants read the current state from a device and produce a full new state suitable for callers already holding state protection. Field-specific masks such as `role_MASK`, `conn_MASK`, `disk_MASK`, `susp_nod_MASK`, and `susp_fen_MASK` connect named state fields to the bit layout of `union drbd_state`.

`enum chg_state_flags` controls transition behavior. `CS_HARD` bypasses soft policy checks for environmental facts; `CS_VERBOSE` logs failures; `CS_WAIT_COMPLETE` waits for queued after-change work; `CS_SERIALIZE` uses `state_mutex`; `CS_ORDERED` combines wait and serialization; `CS_LOCAL_ONLY` suppresses cluster-wide connection handling; the `CS_DC_*` flags control which fields are displayed as connection-level changes; `CS_IGN_OUTD_FAIL` relaxes outdate failure handling; and `CS_INHIBIT_MD_IO` serializes graceful detach with metadata I/O.

`union drbd_dev_state` is a compact device-state bitfield distinct from the wider `union drbd_state`: it tracks role, peer role, connection, local disk, peer disk, and resync pause bits, but excludes some resource-level suspension flags. Public prototypes expose device state requests, connection state requests, detach, aggregate state queries, and `drbd_resume_al()`.

## Control Flow

Typical callers use `drbd_request_state(device, NS(field, value))`, which expands to `_drbd_request_state(..., CS_VERBOSE + CS_ORDERED)`. Lower-level callers can choose flags explicitly through `_drbd_request_state()` or can call `_drbd_set_state()` only when they already satisfy the locking contract. Connection-wide callers use `_conn_request_state()` under `req_lock` or `conn_request_state()` when they need the wrapper to take the lock.

## State and Persistence Behavior

This header does not persist state itself. It defines how state writes are represented and which flags request serialization with metadata I/O. The macros are expression-style GNU C blocks, so they evaluate to typed `union drbd_state` objects rather than raw integers, helping call sites avoid ad hoc bit manipulation.

## Dependencies and Integration Points

The header forward-declares `struct drbd_device` and `struct drbd_connection`, but relies on DRBD enums and `union drbd_state` from included DRBD core headers at users. Its macros are used throughout DRBD code paths that initiate transitions: administration, receiver, worker, request error handling, attach/detach, verify, and resync.

## Risks and Edge Cases

The macros depend on field names matching mask macros exactly. Because they are GNU statement expressions, they are kernel/GCC-specific and must not be reused in plain C tooling without that support. `_NS*` reads live state and should only be used in contexts where callers understand locking and race semantics. Flag combinations matter: omitting `CS_WAIT_COMPLETE` can leave important after-state side effects queued, while incorrectly using `CS_HARD` can skip policy checks.

## Test Signals

Compilation is the first guard for mask/field drift. Runtime tests should verify common macro call sites perform the intended transitions and that `CS_ORDERED`, `CS_WAIT_COMPLETE`, and `CS_INHIBIT_MD_IO` produce observable wait/serialization behavior during detach, promotion, disconnect, and resync start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state_change.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state_change.h

## Purpose

`drbd_state_change.h` defines the old/new state-change record structures used to broadcast DRBD state changes to userspace and internal notification consumers. It separates resource, connection, device, and peer-device state dimensions so a single transition can describe all affected objects in a multi-volume resource.

## Important APIs and Types

`struct drbd_resource_state_change` stores the resource pointer, role, and resource suspension flags (`susp`, `susp_nod`, `susp_fen`) for `OLD` and `NEW` slots. `struct drbd_device_state_change` stores local disk state for a device. `struct drbd_connection_state_change` stores connection state and peer role. `struct drbd_peer_device_state_change` stores per-peer-device disk state, replication state, and the three resync suspension booleans.

`struct drbd_state_change` is the aggregate container: it has a list node, counts for devices/connections, an inline single resource entry, and pointers into a packed allocation for device, connection, and peer-device arrays. The declared helpers are `remember_old_state()`, `copy_old_to_new_state_change()`, and `forget_state_change()`, plus four `notify_*_state_change()` functions that serialize individual dimensions into notification messages.

## Control Flow

`drbd_state.c` allocates and fills this structure before applying a state transition, fills the `NEW` slots afterward, queues it with after-change work, and eventually passes it to `broadcast_state_change()`. Notification code compares `OLD` and `NEW` slots and emits only changed resource, connection, device, or peer-device messages, preserving continuation markers until the final notification in a batch.

## State and Persistence Behavior

The structures are snapshots, not persistent state. They hold kref-protected pointers to live DRBD objects while queued work may run later. The `OLD` and `NEW` array indices make transitions explicit and avoid reconstructing previous state after the live object has already changed.

## Dependencies and Integration Points

The file depends on DRBD object types, state enums, `struct list_head`, `struct sk_buff`, and the notification type enum from surrounding kernel/DRBD headers. It integrates with `drbd_state.c`, generated netlink notification helpers such as `notify_resource_state()`, `notify_connection_state()`, `notify_device_state()`, and `notify_peer_device_state()`, and any code that wants to report state changes after a deferred transition.

## Risks and Edge Cases

The packed allocation layout in `drbd_state.c` must match the pointer fields declared here. Peer-device entries are ordered as the Cartesian product of devices and connections, so enumeration order must remain stable between old and new capture. Forgetting to drop captured krefs would leak resources; failing to take them would risk use-after-free in queued notifications.

## Test Signals

Tests should confirm that multi-volume transitions produce one coherent notification sequence, unchanged dimensions are skipped, continuation flags are set until the last message, and teardown transitions still notify destroyed peer devices/connections while references are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_state_change.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.c

## Purpose

`drbd_strings.c` maps DRBD state enums and state-change error codes to stable human-readable strings. It is used by logging, state transition diagnostics, and any output path that needs textual names for connection, role, disk, or state validation results.

## Important APIs and Data

The file defines static indexed string tables for connection states (`drbd_conn_s_names`), roles (`drbd_role_s_names`), disk states (`drbd_disk_s_names`), and negative state-machine return codes (`drbd_state_sw_errors`). Exported functions are `drbd_conn_str(enum drbd_conns)`, `drbd_role_str(enum drbd_role)`, `drbd_disk_str(enum drbd_disk_state)`, and `drbd_set_st_err_str(enum drbd_state_rv)`.

## Control Flow

Each conversion function is a bounds-checked table lookup. Invalid high enum values return `"TOO_LARGE"`. `drbd_set_st_err_str()` additionally checks whether an error is below the known negative range and returns `"TOO_SMALL"` before indexing with `-err` into the negative-code table.

## State and Persistence Behavior

The file is read-only at runtime. It has no persistence behavior and no mutable state. Its table indexes must stay aligned with the enum numeric values in DRBD public/core headers.

## Dependencies and Integration Points

The file includes `<linux/drbd.h>` for enum definitions and `drbd_strings.h` for prototypes. It is directly used by `drbd_state.c` to print failed transitions and state changes, and likely by other DRBD modules for logs or diagnostics.

## Risks and Edge Cases

Sparse designated initializers make enum drift visible at compile time only if constants remain defined, but not if ranges change without table updates. The error table indexes negative enum values; a bad range check would turn an invalid code into an out-of-bounds access. Callers should not parse these strings as protocol because they are diagnostic names.

## Test Signals

Compile coverage catches missing enum constants. Runtime checks should cover all valid connection, role, disk, and state-error values plus out-of-range high/low values. State-transition failure tests should assert useful messages appear for two-primary rejection, no up-to-date disk, active resync, missing verify algorithm, unsupported protocol, transient state, and peer-refused cluster-wide change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.h

## Purpose

`drbd_strings.h` declares the enum-to-string helpers implemented in `drbd_strings.c`. It is a narrow diagnostic interface for translating DRBD connection, role, disk, and state return-code values.

## Important APIs

The header exports `drbd_conn_str()`, `drbd_role_str()`, `drbd_disk_str()`, and `drbd_set_st_err_str()`. Each returns a `const char *` for use in logs, state dumps, and error messages.

## Control Flow

The header has no control flow beyond include guards. Callers include it when they need textual state names and delegate all bounds checking to the implementation.

## State and Persistence Behavior

There is no state or persistence. The functions expose static string data owned by `drbd_strings.c`; callers must treat returned pointers as immutable.

## Dependencies and Integration Points

The prototypes rely on DRBD enum declarations being visible before use, typically through `<linux/drbd.h>` or DRBD internal headers. Integration points are diagnostic paths in `drbd_state.c`, request/worker logging, and any administrative or notification formatting code that wants canonical state names.

## Risks and Edge Cases

Because the header does not include the enum-defining header itself, include order matters for standalone users. The interface is unsuitable for wire-format compatibility because string spelling is diagnostic, not a negotiated protocol.

## Test Signals

Build tests should catch missing enum declarations at include sites. Runtime tests belong with `drbd_strings.c` and should verify valid and invalid enum conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_strings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_vli.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_vli.h

## Purpose

`drbd_vli.h` implements DRBD's variable-length integer and bitstream helpers used to compress bitmap run lengths during replication. It is optimized for DRBD dirty-bit maps where long runs of equal polarity are common, but short noisy runs should not be much worse than plaintext.

## Important APIs and Types

`VLI_L_1_1()` is a macro table of encoding levels. Each `LEVEL(total_bits, prefix_bits, prefix_value)` defines one prefix/data-size class. `vli_decode_bits()` decodes a VLI value from the least significant bits of a `u64` input and returns consumed bits. `__vli_encode_bits()` encodes a positive `u64` into a code word and returns code length, with `-EINVAL` for zero and `-EOVERFLOW` for too-large values. `vli_encode_bits()` writes an encoded value into a bitstream.

`struct bitstream_cursor` tracks a byte pointer and bit offset. `struct bitstream` tracks the cursor, buffer, byte length, and input padding bits. Helper functions are `bitstream_cursor_reset()`, `bitstream_cursor_advance()`, `bitstream_init()`, `bitstream_rewind()`, `bitstream_put_bits()`, and `bitstream_get_bits()`.

## Control Flow

Encoding selects the first level whose cumulative maximum includes the input. It subtracts the level's adjustment base, shifts the payload above the prefix, ORs in the prefix value, and writes the low-order code bits to the bitstream. Decoding tests each level's prefix mask against the low bits of the input, reconstructs the adjusted value from the payload, and returns the level's total bit count. The level table is deliberately compile-time macro-expanded so encode/decode stay in sync.

Bitstream writes first check capacity, strip high bits above the requested width, OR the low byte into the current partial byte, then continue byte-wise and advance the cursor. Reads cap the requested width to available valid bits after padding, copy up to the needed bytes into a `u64`, convert from little endian, align by the current bit offset, mask unwanted high bits, advance the cursor, and return the actual bit count.

## State and Persistence Behavior

The helpers mutate only caller-provided bitstream buffers and cursor fields. `bitstream_rewind()` also zeroes the buffer to prepare for fresh output. There is no persistent state, but encoded streams become part of DRBD bitmap transfer payloads, so compatibility depends on the level table and little-endian least-significant-bit-first semantics remaining stable.

## Dependencies and Integration Points

The header depends on kernel integer types, `BUG()`, errno constants, `memset()`, `memcpy()`, and `le64_to_cpu()`. It integrates with bitmap send/receive code that compresses run-length encoded dirty-bit polarity. The comments explicitly frame it as a DRBD receiver/bitmap transfer support utility.

## Risks and Edge Cases

Zero cannot be encoded because run lengths are positive. Values above the maximum table coverage return `-EOVERFLOW`. `vli_decode_bits()` calls `BUG()` if no level matches, assuming the static table is correct; corrupted input must therefore be guarded by callers that provide enough bits and valid framing. `bitstream_get_bits()` has a special hazard when `bits == 64`: the final mask expression shifts by `64 - bits`, so callers and compiler behavior need scrutiny for undefined shift-by-width behavior. Capacity and padding calculations are bit-level and easy to regress with off-by-one errors.

## Test Signals

Round-trip tests should cover every VLI level boundary, zero input, maximum encodable value, overflow, short buffers, non-byte-aligned cursor positions, padding-limited reads, and repeated rewind/reuse. Interoperability tests should verify compressed bitmap streams generated on one endian architecture decode identically on another, preserving the documented little-endian bitstream order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_vli.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_worker.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_worker.c

## Purpose

`drbd_worker.c` implements the DRBD sender/worker thread's asynchronous execution path. It handles lower-level bio completions, peer request completions, checksum and verify work, resync request generation, resync completion, outgoing replicated request transmission, bitmap/metadata maintenance work, diskless teardown, and the main worker loop for a connection.

## Important APIs, Types, and Functions

End-I/O handlers include `drbd_md_endio()`, `drbd_peer_request_endio()`, and `drbd_request_endio()`. Peer finalizers split read and write behavior through `drbd_endio_read_sec_final()` and `drbd_endio_write_sec_final()`. Checksum helpers are `drbd_csum_ee()` for peer-request page chains and `drbd_csum_bio()` for local bios.

Resync and verify are driven by `w_resync_timer()`, `resync_timer_fn()`, `make_resync_request()`, `make_ov_request()`, `drbd_resync_finished()`, and `drbd_start_resync()`. Rate control uses `struct fifo_buffer`, `fifo_alloc()`, `drbd_rs_controller()`, `drbd_rs_number_requests()`, and `drbd_rs_controller_reset()`.

Worker callbacks for network responses include `w_e_send_csum()`, `w_e_end_data_req()`, `w_e_end_rsdata_req()`, `w_e_end_csum_rs_req()`, `w_e_end_ov_req()`, and `w_e_end_ov_reply()`. Outgoing local request callbacks include `w_send_out_of_sync()`, `w_send_dblock()`, `w_send_read_req()`, `w_send_write_hint()`, and `w_restart_disk_io()`. Device work is multiplexed by `do_device_work()`, `get_work_bits()`, and `do_unqueued_work()`. `drbd_worker()` is the thread entry point.

## Control Flow

The worker thread waits in `wait_for_work()` for queued sender work or device flag work. It drains batches from `connection->sender_work`, optionally uncorks/corks TCP according to `net_conf`, closes write epochs with barriers when needed, handles signals, and invokes each work callback with a `cancel` argument derived from connection state. A callback returning nonzero while connected triggers `conn_request_state(... C_NETWORK_FAILURE, CS_HARD)`.

Local bio completion in `drbd_request_endio()` maps block status to DRBD request events and calls `__req_mod()` under `req_lock`; it also panics on delayed successful completion of a request previously aborted for disk-timeout safety. Peer request completion in `drbd_peer_request_endio()` records errors, decrements pending bios, and then queues final read replies or moves completed writes to `done_ee` and schedules ack sending.

Resync target flow starts from `drbd_start_resync()`, which runs before-resync helpers, serializes state with `state_mutex`, sets `C_SYNC_SOURCE` or `C_SYNC_TARGET`, initializes counters/marks, resets the resync LRU, chooses checksum-based resync when supported/configured, sends sync UUIDs as required by protocol version, and arms `resync_timer`. Timer work calls `make_resync_request()` for `C_SYNC_TARGET`, scanning dirty bitmap bits, merging adjacent blocks within bio and extent boundaries, honoring thin resync discard granularity, throttling against socket send-buffer pressure, and either sending data requests or reading local data for checksum requests. Online verify uses `make_ov_request()` to send checksum verify requests until capacity or stop sector is reached.

Completion callbacks compare checksums, send data replies or in-sync acknowledgements, update bitmap/resync accounting, and call `drbd_resync_finished()` when all work is done. `drbd_resync_finished()` removes resync LRU entries, computes throughput, checks bitmap out-of-sync weight, updates UUIDs and disk states, emits helper events such as `after-resync-target`, `out-of-sync`, or `unfence-peer`, resets counters, syncs metadata, and moves connection state back to `C_CONNECTED`.

## State and Persistence Behavior

The worker mutates request queues (`read_ee`, `active_ee`, `sync_ee`, `done_ee`), resync counters (`rs_total`, `rs_failed`, `rs_pending_cnt`, `rs_in_flight`, `rs_same_csum`, `ov_left`, `ov_position`), bitmap state, UUID history, and connection send epoch fields. It persists metadata via `drbd_md_sync()`, writes bitmap pages through `drbd_bm_write_lazy()`, `drbd_bm_write()`, and state-triggered bitmap I/O, and destroys local backing state in `drbd_ldev_destroy()` after diskless transition cleanup. `go_diskless()` attempts final bitmap writeout and may set `MDF_FULL_SYNC` if read errors prevented reliable detach persistence.

## Dependencies and Integration Points

This file depends on Linux bio/block APIs, crypto shash, timers, wait queues, socket/TCP corking, partition stats, slab allocation, memcontrol/mm helpers, and DRBD internals from `drbd_int.h`, `drbd_protocol.h`, and `drbd_req.h`. It integrates tightly with `drbd_state.c` through `_drbd_set_state()`, `conn_request_state()`, `drbd_force_state()`, `resume_next_sg()`, and `suspend_other_sg()`. It also uses bitmap, activity-log, transfer-log, UUID, metadata, khelper, and protocol send helpers.

## Risks and Edge Cases

This file is heavily concurrency-sensitive. Endio callbacks may run in IRQ/softirq context and must use irq-safe locking. Worker callbacks may block on network congestion, so several paths free peer request pages before sending to avoid distributed deadlock on buffer exhaustion. Resync throttling must avoid overrunning peer buffers while still making progress. Disk-timeout abort handling intentionally panics on later successful local completion to prevent silent memory corruption. Resync-finish handling retries if LRU entries remain because replies are still queued. Protocol-version branches around sync UUIDs and empty resyncs are compatibility-sensitive.

Memory pressure paths can defer checksum reads, fail verify digest allocation, or fail queued retry allocation. State may change between queued work and execution, so many paths re-check current `device->state` or `connection->cstate`. Incorrect accounting of `rs_pending_cnt`, `unacked_cnt`, `rs_in_flight`, or bitmap bits can hang resync completion or prematurely mark data in sync.

## Test Signals

Test coverage should include local read/write/discard completion success and failure, delayed completion after forced detach, peer read/write request completion, protocol A/B/C ack behavior, checksum-based resync equality and mismatch, thin resync zero-block handling, online verify mismatch reporting and stop sectors, resync pause/resume dependencies, socket congestion requeue, empty resync on older protocol versions, disk failure during resync, bitmap persistence after progress and completion, and worker shutdown draining with `cancel=1`. Logs from resync start/finish, verify mismatch, send failures, diskless transition, metadata sync timer expiry, and network-failure transition are strong integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_worker.c -->
