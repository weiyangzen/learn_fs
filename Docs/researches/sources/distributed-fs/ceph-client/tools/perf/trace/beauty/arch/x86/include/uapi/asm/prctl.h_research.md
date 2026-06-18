# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/arch/x86/include/uapi/asm/prctl.h

## Purpose
This x86 UAPI header defines `arch_prctl` operation codes and feature bits consumed by perf trace's `arch_prctl` argument beautifier.

## Important APIs, Types, And Functions
It declares macros for FS/GS base operations (`ARCH_SET_GS`, `ARCH_SET_FS`, `ARCH_GET_FS`, `ARCH_GET_GS`), CPUID toggles, extended state permission queries/requests, AMX xcomp component IDs, VDSO mapping options, tagged-address operations, shadow-stack operations, and shadow-stack feature bits (`ARCH_SHSTK_SHSTK`, `ARCH_SHSTK_WRSS`).

## Control Flow
There is no runtime control flow. The header is protected by `_ASM_X86_PRCTL_H` and consists of numeric macro definitions grouped by command family.

## State, Dependencies, And Integration
No state is held. The integration point is `trace/beauty/arch_prctl.c`, which includes generated arrays built from these constants and formats syscall argument values into names.

## Risks And Test Signals
The main risk is ABI drift when new x86 `arch_prctl` commands are added upstream but this copy or generated tables are not refreshed. Tests should check that known codes print as symbolic `ARCH_*` names and unknown values fall back to hex.
