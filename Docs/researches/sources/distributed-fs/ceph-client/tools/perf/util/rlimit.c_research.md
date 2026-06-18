# sources/distributed-fs/ceph-client/tools/perf/util/rlimit.c

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rlimit.c` contains small helpers for increasing process resource limits needed by perf workloads, especially BPF map creation and many open perf fds.

## Important APIs, Types, and Functions

The public functions are `rlimit__bump_memlock` and `rlimit__increase_nofile`.

## Control Flow

`rlimit__bump_memlock` reads `RLIMIT_MEMLOCK`, multiplies current and max values by four, tries `setrlimit`, then halves that attempted increase and retries once if the first set fails. If both fail, it logs a debug warning. `rlimit__increase_nofile` uses an `enum rlimit_action` state pointer: first call raises current to max, second raises both current and max by 1000, later calls do nothing. It preserves the caller's `errno` across attempts and returns whether a limit was successfully changed.

## State and Persistence Behavior

The helpers mutate process resource limits. Changes are process-local and inherited by child processes according to normal rlimit semantics. The nofile helper advances caller-owned action state.

## Dependencies and Integration Points

It depends on libc `getrlimit/setrlimit`, perf debug logging, and declarations in `rlimit.h`. It supports perf trace/BPF tests and high-fd recording sessions.

## Risks and Edge Cases

Multiplying infinite or very large rlimit values can overflow `rlim_t`. Raising hard limits usually requires privilege and can fail silently except for debug output. `rlimit__increase_nofile` assumes adding 1000 to `rlim_max` is meaningful and permitted. Preserving `errno` is useful for callers but can hide failure details unless debug logging is enabled.

## Test Signals

Tests should mock or isolate rlimit calls for success, first-fail-second-success, complete failure, nofile state progression, errno preservation, and overflow/`RLIM_INFINITY` handling.
