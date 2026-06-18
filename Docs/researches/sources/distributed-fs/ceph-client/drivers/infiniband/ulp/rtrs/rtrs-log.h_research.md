# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/rtrs/rtrs-log.h

## Purpose
Provides small logging wrappers that prefix RTRS log messages with the session/path name.

## Important APIs, Types, And Functions
Defines `rtrs_log(fn, obj, fmt, ...)` and severity/rate-limited wrappers: `rtrs_err`, `rtrs_err_rl`, `rtrs_wrn`, `rtrs_wrn_rl`, `rtrs_info`, and `rtrs_info_rl`.

## Control Flow
Callers pass an object with a `sessname` member, typically `struct rtrs_path` or a compatible session-like object. The macro calls the supplied kernel printk function with `"<%s>: "` prefixing the caller message.

## State And Persistence
No state is stored. The only persistent effect is kernel log output.

## Dependencies And Integration Points
Relies on kernel `pr_*` functions and on object layout conventions used across RTRS client/server/core code. The source files set `pr_fmt` before including it, so line/module prefixes combine with this session prefix.

## Risks
Because this is macro-based and assumes `obj->sessname`, passing an incompatible pointer causes compile failures or worse if hidden behind casts. Format-string correctness remains the caller's responsibility. Rate-limited variants are essential in hot error paths to avoid log floods during transport failures.

## Test Signals
Compile-time use across all RTRS files is the main guard. Runtime signals are readable, rate-limited logs during connection failure, heartbeat loss, malformed messages, and sysfs-triggered disconnects.
