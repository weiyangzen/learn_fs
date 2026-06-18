# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-log.h

## Purpose
Provides small logging macros for RNBD client and server code that prepend device path and session name to messages.

## Important APIs, types, and functions
- `rnbd_clt_log()` formats `<pathname@sessname>`.
- `rnbd_srv_log()` formats `<pathname@sessname>:` for server session-device objects.
- Convenience macros wrap `pr_err`, `pr_err_ratelimited`, `pr_info`, and `pr_info_ratelimited` for client and server paths.

## Control flow
This header is included by both client and server headers, allowing implementation files to call `rnbd_clt_err()`, `rnbd_srv_info()`, and ratelimited variants without repeating session/path formatting.

## State and persistence behavior
No state is owned here. Macros evaluate fields of live client/server objects; callers must ensure the referenced object and its `sess` pointer remain valid.

## Dependencies and integration points
Includes `rnbd-clt.h` and `rnbd-srv.h`, which creates a circular-looking but include-guarded dependency. It integrates with kernel printk APIs.

## Risks and test signals
Because macros dereference object fields directly, use-after-free bugs in caller lifetime management may surface as logging crashes. Build checks should catch include-order regressions; runtime fault paths should verify ratelimited logs do not dereference already released session objects.
