# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/prctl.h

## Purpose

`prctl.h` defines operation numbers and sub-flags for `prctl(2)`, Linux's multiplexed task/process control syscall. Perf trace beauty uses it to decode process naming, parent-death signals, dumpability, capabilities, seccomp, no-new-privs, memory-map changes, architecture vector controls, speculation mitigation, syscall user dispatch, core scheduling, MDWE, RISC-V controls, shadow stacks, CFI, and other task attributes.

## Important APIs, Types, and Constants

The header defines many `PR_*` get/set operation pairs and sub-flags. Major groups include basic task controls, floating-point and endian controls, seccomp/capability/TSC/securebits controls, timerslack and perf event toggles, MCE kill mode, `PR_SET_MM` with `struct prctl_mm_map`, ptracer/subreaper/no-new-privs, THP disable, ambient capabilities, arm64 SVE/SME/PAC/MTE controls, speculation controls, syscall user dispatch, core scheduling, MDWE, VMA naming, auxv query, memory merge, RISC-V vector and icache controls, PowerPC DEXCR, shadow stacks, timer-create restore IDs, futex hash slots, rseq slice extension, and CFI branch landing pads.

## Control Flow and Integration

Runtime flow is `prctl(option, arg2, arg3, arg4, arg5)`, with the meaning of every later argument selected by `option`. Some options have subcommands or nested masks, such as `PR_SET_MM`, `PR_CAP_AMBIENT`, speculation controls, syscall user dispatch, core scheduling, architecture vector controls, and CFI. Perf trace must decode the first argument before assigning names to later arguments.

## State and Persistence Behavior

Most set operations mutate current task, thread, process, or mm state. Some persist until exec or have explicit inheritance/on-exec flags. Get operations query state. `PR_SET_MM` mutates mm metadata visible through `/proc`, mainly for checkpoint/restore.

## Dependencies and Integration Points

The header includes `linux/types.h` and integrates with signal handling, mm, credentials/capabilities, seccomp, perf, scheduler, architecture-specific task state, CRIU, LSM behavior, and hardware mitigation controls.

## Risks

`prctl` is highly multiplexed; flat arg decoding is wrong. Many values are architecture- or config-specific. Magic non-sequential constants such as `PR_SET_PTRACER`, `PR_SET_VMA`, and `PR_GET_AUXV` must be preserved. Removed MPX values remain reserved. `struct prctl_mm_map` contains user pointers and sensitive mm metadata.

## Test Signals

Decode `PR_SET_NAME`, `PR_SET_NO_NEW_PRIVS`, `PR_SET_SECCOMP`, `PR_CAP_AMBIENT`, `PR_SET_MDWE`, `PR_SET_CFI`, speculation masks, tagged-address/MTE controls, SVE/SME, RISC-V, PowerPC DEXCR, shadow stack controls, and `PR_SET_MM` subcommands.
