<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.h -->
# sources/distributed-fs/ceph-client/io_uring/napi.h

## Purpose
`napi.h` declares and conditionally stubs io_uring NAPI busy-poll integration. It lets networking-enabled builds track NAPI IDs and lets non-busy-poll builds compile with no-op behavior and `-EOPNOTSUPP` registration.

## Important APIs, Types, and Functions
- Enabled declarations: `io_napi_init()`, `io_napi_free()`, `io_register_napi()`, `io_unregister_napi()`, `__io_napi_add_id()`, `__io_napi_busy_loop()`, and `io_napi_sqpoll_busy_poll()`.
- `io_napi(ctx)` checks whether the ring has any tracked NAPI entries.
- `io_napi_busy_loop(ctx, iowq)` runs busy polling only when entries exist.
- `io_napi_add(req)` dynamically tracks a request socket's NAPI id when the ring mode is dynamic.
- Disabled stubs no-op init/free/add/busy-loop, return false or 0 where appropriate, and return `-EOPNOTSUPP` for register/unregister.

## Control Flow
Networking request paths can call `io_napi_add(req)` after socket activity; it quickly exits unless `ctx->napi_track_mode` is dynamic, then calls `sock_from_file()` and `__io_napi_add_id()`. Wait paths call `io_napi_busy_loop()`, which avoids the heavier implementation when no ids are present.

## State and Persistence Behavior
The header only manipulates per-ring fields owned by `napi.c`: tracking mode and NAPI list state. Dynamic add is opportunistic and ignores sockets without a valid `sk`.

## Dependencies and Integration Points
It includes kernel io_uring and net busy-poll headers. It is used by ring allocation/free, wait paths, SQPOLL, and network opcode handlers. Conditional compilation isolates callers from `CONFIG_NET_RX_BUSY_POLL`.

## Risks and Edge Cases
- `io_napi_add()` uses `READ_ONCE` on tracking mode and socket `sk_napi_id`; races are tolerated by the implementation rechecking under lock.
- Disabled builds must return `-EOPNOTSUPP` rather than silently accepting registration.

## Test Signals
Build both enabled and disabled configs. Runtime tests should verify dynamic tracking only occurs in dynamic mode and registration fails with `-EOPNOTSUPP` when busy poll support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/napi.h -->
