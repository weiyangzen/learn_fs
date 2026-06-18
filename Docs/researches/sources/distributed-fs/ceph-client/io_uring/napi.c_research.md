<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.c -->
# sources/distributed-fs/ceph-client/io_uring/napi.c

## Purpose
`napi.c` implements optional io_uring integration with network RX busy polling when `CONFIG_NET_RX_BUSY_POLL` is enabled. It tracks NAPI IDs statically or dynamically per ring, registers/unregisters busy-poll configuration, removes stale dynamic IDs, and drives busy-poll loops during blocking CQ waits or SQPOLL polling.

## Important APIs, Types, and Functions
- `struct io_napi_entry` stores one NAPI id, list/hash nodes, timeout, and RCU head.
- `io_napi_init()` initializes per-ring NAPI state from `sysctl_net_busy_poll`.
- `io_napi_free()` removes and RCU-frees tracked entries.
- `io_register_napi()` handles register/static-add/static-del UAPI operations and returns the previous config to userspace.
- `io_unregister_napi()` disables tracking and optionally returns previous timeout/prefer settings.
- `__io_napi_add_id()` and `__io_napi_del_id()` manage tracked ids.
- `__io_napi_busy_loop()` runs busy polling during blocking wait.
- `io_napi_sqpoll_busy_poll()` runs busy polling from SQPOLL context.

## Control Flow
Dynamic tracking is fed by `io_napi_add(req)` in `napi.h`, which reads the socket's `sk_napi_id` for requests when the ring is in dynamic mode. `__io_napi_add_id()` rejects invalid ids, checks the hash under RCU, refreshes timeout for existing entries, allocates a new entry, then under `napi_lock` verifies tracking mode has not changed and inserts into both hash and list.

Registration copies an `io_uring_napi` struct from userspace, validates padding, first copies the current config back to userspace, then either changes tracking mode/config, adds a static id, or deletes a static id. Registering a new mode disables tracking, frees existing entries, caps busy-poll timeout at 10 msec, updates prefer-busy-poll, and enables the selected mode.

Busy polling checks wait conditions through `io_napi_busy_loop_should_end()`: pending signals, enough CQEs, ring work, or timeout. Static mode loops all ids and never reports stale. Dynamic mode also detects expired entries and removes them after the RCU loop. Blocking waits skip SQPOLL rings, clamp busy-poll duration to the CQ wait timeout, and then call the blocking busy loop. SQPOLL busy poll runs only when a nonzero timeout and nonempty list are present.

## State and Persistence Behavior
Per-ring state includes `napi_list`, `napi_ht`, `napi_lock`, `napi_track_mode`, `napi_busy_poll_dt`, and `napi_prefer_busy_poll`. Dynamic entries expire after `NAPI_TIMEOUT` jiffies unless refreshed. Entry removal uses RCU list/hash deletion and `kfree_rcu()`, so readers can busy-loop under RCU without holding `napi_lock`.

## Dependencies and Integration Points
The module depends on net busy-poll APIs (`napi_busy_loop_rcu`, `busy_loop_current_time`, `BUSY_POLL_BUDGET`), socket NAPI IDs, RCU, spinlocks, and io_uring wait/task state. It is initialized/freed from ring context allocation/free and used by wait paths and SQPOLL loops. `napi.h` provides no-op stubs when busy poll is disabled.

## Risks and Edge Cases
- Tracking mode can change while adding ids; `__io_napi_add_id()` rechecks under lock and returns `-EINVAL` if mode changed.
- Dynamic stale removal iterates with assumptions about RCU list deletion not resetting next pointers before grace period.
- Busy loops must terminate on signals and CQ/work readiness to avoid starving user tasks.
- IOPOLL rings reject NAPI registration.
- Static add/del operations require current mode to be static and use `op_param` as the NAPI id.

## Test Signals
Tests should cover register/unregister, current-config copyback, dynamic id learning from sockets, duplicate id refresh, stale dynamic removal, static add/delete validation, invalid padding/mode/id, busy-poll timeout clamping, blocking wait wake conditions, SQPOLL busy-poll path, and builds with `CONFIG_NET_RX_BUSY_POLL` disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.c -->
