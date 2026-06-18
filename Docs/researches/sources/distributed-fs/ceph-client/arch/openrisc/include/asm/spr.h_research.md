<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr.h

## Purpose
Defines inline assembly accessors for OpenRISC special-purpose registers.

## Important APIs, Types, And Functions
`mtspr(_spr, _val)` writes an immediate SPR address, `mtspr_off(_spr, _off, _val)` writes indexed SPRs, `mfspr(add)` reads an SPR, and `mfspr_off(add, offset)` reads an indexed SPR.

## Control Flow
There is no higher-level flow; callers issue `l.mtspr` or `l.mfspr` directly. These helpers underpin timer, MMU, cache, interrupt, CPU-info, and SMP code.

## State And Persistence
Writes change hardware CPU state such as SR, TTMR, TLB, cache-control, PIC, and PM registers. Effects persist until overwritten or reset.

## Dependencies And Integration Points
SPR numeric constants come from `spr_defs.h`. Inline constraints use OpenRISC assembler support for the `K` immediate operand.

## Risks
Invalid SPR numbers or ordering mistakes can corrupt privileged CPU state. These helpers do not provide memory barriers beyond volatile asm.

## Test Signals
Boot-time reads of `SPR_UPR`, `SPR_VR`, `SPR_TTCR`, and TLB/cache SPR writes should behave consistently on simulator and hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/spr.h -->
