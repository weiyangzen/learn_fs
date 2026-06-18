# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/sched.h

## Purpose

`sched.h` defines Linux task creation and scheduler UAPI constants: clone flags, `clone3` argument layout, scheduler policy values, and `sched_setattr`/`sched_getattr` flags. Perf trace beauty uses it to decode `clone`, `clone3`, `unshare`, namespace flags, and scheduler attribute masks.

## Important APIs, Types, and Constants

Important definitions are `CSIGNAL`; classic `CLONE_*` flags for VM/fs/files/sighand/thread/namespace/TLS/TID/pidfd/vfork/io behavior; 64-bit `clone3` flags `CLONE_CLEAR_SIGHAND` and `CLONE_INTO_CGROUP`; overlapping `CLONE_NEWTIME`; `struct clone_args`; `CLONE_ARGS_SIZE_VER*`; scheduling policies `SCHED_NORMAL`, `FIFO`, `RR`, `BATCH`, `IDLE`, `DEADLINE`, and `SCHED_EXT`; `SCHED_RESET_ON_FORK`; and `SCHED_FLAG_*` masks including keep-policy/params and utilization clamp flags.

## Control Flow and Integration

Classic `clone` uses low bits as an exit signal and high bits as flags. `clone3` uses `struct clone_args`, with separate `flags` and `exit_signal`. `unshare` uses a subset of clone namespace/sharing flags, including `CLONE_NEWTIME`. Scheduler syscalls use `SCHED_*` policies and `SCHED_FLAG_*` masks. Perf must choose decoding based on syscall.

## State and Persistence Behavior

Clone flags create new task sharing relationships, namespaces, cgroup placement, pidfds, TLS, and TID set/clear behavior. Scheduler policies and attributes persist until changed or reset-on-fork semantics apply. The header stores no state.

## Dependencies and Integration Points

The header includes `linux/types.h` for `__aligned_u64`. It integrates with process creation, pidfd, namespaces, cgroups, futex/TID clearing, scheduler classes, deadline scheduling, utilization clamping, and extensible scheduler policy support.

## Risks

`CLONE_NEWTIME` overlaps `CSIGNAL`; classic clone decoders can mislabel signal bits. `CLONE_DETACHED` is unused but ABI-visible. `struct clone_args` is versioned by size. `SCHED_EXT` may not be enabled on all kernels. Aggregate masks must track new flags.

## Test Signals

Decode classic `clone` with signal bits separated, `clone3` flags and `exit_signal`, `unshare(CLONE_NEWUSER|CLONE_NEWTIME)`, scheduler policies including `SCHED_DEADLINE` and `SCHED_EXT`, and aggregate scheduler flag masks.
