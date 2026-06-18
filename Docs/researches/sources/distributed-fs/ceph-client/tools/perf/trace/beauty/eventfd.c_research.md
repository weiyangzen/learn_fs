# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/eventfd.c

## Purpose
This inline beautifier formats `eventfd2` flag values for `perf trace`.

## Important APIs, Types, And Functions
It defines fallback constants for `EFD_SEMAPHORE`, `EFD_NONBLOCK`, and `EFD_CLOEXEC` when system headers lack them. The local formatter is `syscall_arg__scnprintf_eventfd_flags()`, exposed as `SCA_EFD_FLAGS`.

## Control Flow
The formatter returns `NONE` for zero flags. Otherwise it tests known bits in a fixed order, appends `SEMAPHORE`, `CLOEXEC`, and `NONBLOCK` with optional `EFD_` prefix, clears handled bits, and appends any unknown remainder as hex.

## State, Dependencies, And Integration
It has no persistent state and mutates no argument masks. It relies on `scnprintf()` and the `struct syscall_arg` prefix policy. `builtin-trace.c` maps eventfd flags to `SCA_EFD_FLAGS`.

## Risks And Test Signals
Fallback constants must match UAPI values. Tests should cover zero, each known flag, combined flags, prefix suppression, and unknown extra bits.
