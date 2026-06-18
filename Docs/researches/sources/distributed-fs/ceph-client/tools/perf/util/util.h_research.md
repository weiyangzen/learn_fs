# sources/distributed-fs/ceph-client/tools/perf/util/util.h

## Purpose

`util.h` declares shared utility APIs and global settings used throughout perf.

## Important APIs, Types, and Functions

It declares usage strings, `input_name`, host/guest exclusion globals, filesystem helpers, sysctl helpers, tips, CPU mask conversion, threading mode flags, executable path, debuginfod configuration, basename/chroot helpers, dynamic array growth, endian detection, and compatibility declarations for `sched_getcpu()` and `scandirat()`. It defines `struct perf_debuginfod`, `realloc_array_as_needed()`, and inline `host_is_bigendian()`.

## Control Flow and State

Most declarations reference process-global state. The `realloc_array_as_needed()` macro evaluates the requested index once and calls the implementation only when growth is needed.

## Dependencies and Integration Points

It pulls in common POSIX and Linux headers and is one of perf's broad utility include points.

## Risks and Test Signals

Risks include macro side effects, buffer-size assumptions for `perf_exe()`, and byte-order detection portability. Compile and unit tests should exercise the macro with side-effecting expressions and both compiler/endian paths where possible.
