# sources/distributed-fs/ceph-client/tools/perf/tests/workloads/landlock.c

## Purpose
This workload issues `landlock_add_rule` syscalls with two rule types so `perf trace` can test enum and struct argument augmentation, especially with BTF.

## Important APIs, Types, And Functions
The workload locally defines missing Landlock syscall numbers, access bits, rule constants, and `landlock_path_beneath_attr` / `landlock_net_port_attr` when older system headers lack them. The only entry point is `landlock()`, registered with `DEFINE_WORKLOAD(landlock)`.

## Control Flow
`landlock()` initializes dummy file descriptor and flags values, builds a path-beneath rule with a fake parent fd, builds a network-port rule with a fake port, and calls `syscall(__NR_landlock_add_rule, ...)` twice. It ignores syscall return values because only argument capture matters.

## State, Dependencies, And Integration
There is no persistent state. The workload depends on raw syscall availability but does not require successful Landlock setup. It is integrated into perf tests that intercept syscall arguments and decode enum values.

## Risks And Test Signals
Hard-coded syscall number 445 is architecture-sensitive if used outside the intended supported environment. Since invalid fds/flags are intentional, syscall failure is not a workload failure. The signal is `perf trace` displaying decoded rule types and augmented struct fields.
