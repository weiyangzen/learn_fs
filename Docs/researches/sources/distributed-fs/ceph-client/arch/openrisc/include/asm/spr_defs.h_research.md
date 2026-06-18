<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr_defs.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr_defs.h

## Purpose
Defines the OpenRISC SPR address map and bit masks for system, MMU, cache, debug, performance, power, PIC, tick timer, FPU, and simulator NOP facilities.

## Important APIs, Types, And Functions
Major address groups include `SPRGROUP_SYS`, `DMMU`, `IMMU`, `DC`, `IC`, `D`, `PC`, `PM`, `PIC`, `TT`, and `FP`. Important registers include `SPR_SR`, `SPR_EVBAR`, exception PC/address/status bases, TLB match/translate ranges, cache block invalidate/flush registers, `SPR_COREID`, `SPR_NUMCORES`, `SPR_TTMR`, `SPR_TTCR`, and `SPR_FPCSR`.

## Control Flow
The file has no executable flow. It supplies constants that are consumed by boot assembly, exception return, TLB miss handlers, timer setup, cache maintenance, FPU exception handling, and SMP CPU identification.

## State And Persistence
Definitions describe privileged hardware state. SR bits control MMU, cache, interrupt, supervisor, delay-slot, and endian modes; TLB and cache SPRs affect translations and coherency; tick timer bits control clocksource and clockevent behavior.

## Dependencies And Integration Points
Paired with `spr.h` accessors. The numeric values must match the OpenRISC 1000 architecture and the assembly code in `head.S` and `entry.S`.

## Risks
Mask or offset drift is high impact: a wrong SR, TLB, cache, or TTMR bit can break boot, memory protection, interrupt delivery, or timing. Some comments reflect old simulator heritage, so changes require architecture-manual validation.

## Test Signals
Cross-build all OpenRISC configs; boot through MMU enable; verify CPU feature printout, cacheinfo, timer interrupts, FPU signal codes, TLB miss refill, and SMP core ID reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr_defs.h -->
