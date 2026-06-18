# sources/distributed-fs/ceph-client/tools/arch/csky/include/uapi/asm/perf_regs.h

## Purpose
Defines C-SKY perf register indexes matching `struct pt_regs` layout.

## Important APIs, Types, and Functions
Exports `enum perf_event_csky_regs` covering TLS, LR, PC, SR, SP, original A0, argument registers, `regs0`-`regs9`, and ABI v2 extra registers plus HI/LO/DCSR when `__CSKYABIV2__` is defined.

## Control Flow, State, and Persistence
No runtime state. Conditional preprocessing changes the maximum enum value for ABI v1 versus ABI v2 builds.

## Dependencies and Integration Points
Integrated with perf register sampling and C-SKY tools that decode register masks.

## Risks and Test Signals
Risk is ABI-conditional enum mismatch between producer and consumer. Test signals are perf build coverage for both ABI modes and register dump/sample mask decode tests.
