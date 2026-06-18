# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/utils.h

## Purpose

`utils.h` exposes shared constants, inline helpers, scheduler structures, enums, and utility prototypes for rtla source files.

## Important APIs, Types, and Functions

Constants include `BUFF_U64_STR_SIZE`, `MAX_PATH`, `MAX_NICE`, `MIN_NICE`, `ARRAY_SIZE`, `STRING_LENGTH`, and `strncmp_static`. Inline helpers include `str_has_prefix()`, `container_of()`, `update_min()`, `update_max()`, and `update_sum()`. The header defines `struct sched_attr` when the libc headers do not, `enum stack_format`, and `enum result`.

## Control Flow and Data Flow

There is no runtime control flow beyond inline functions. The update helpers mutate aggregate statistics in caller-owned storage, and the parsing/scheduling/cgroup prototypes connect command modules to `utils.c`.

## State and Persistence Behavior

The header declares external `config_debug` and functions that affect persistent process/kernel state, but it stores no state itself. The fallback cpupower inline functions return unsupported defaults when libcpupower support is not compiled in.

## Dependencies and Integration Points

It depends on standard integer, string, time, scheduler, boolean, and allocation headers. It is included broadly by rtla modules, including tracing, timerlat tools, and unit tests.

## Risks and Edge Cases

`container_of()` requires correct member pointers and type pairing. The update helpers do no overflow checking. The compile-time `struct sched_attr` fallback must stay ABI-compatible with kernel expectations. Feature-conditional cpupower stubs make unsupported builds fail at runtime rather than compile time.

## Test Signals

Compile coverage across supported libc/kernel header combinations is important. Unit tests indirectly exercise `update_*`, parsing prototypes, scheduler attr layout, and unsupported cpupower stubs through `utils.c` tests.
