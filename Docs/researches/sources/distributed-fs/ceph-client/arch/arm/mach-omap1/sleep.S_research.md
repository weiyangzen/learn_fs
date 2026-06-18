<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sleep.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sleep.S

## Purpose
Implements the low-level OMAP1510 and OMAP1610 CPU suspend routines that are copied to internal SRAM and executed while external memory or clocks may be unavailable.

## Important APIs, Types, and Functions
Exports assembly entries `omap1510_cpu_suspend`, `omap1510_cpu_suspend_sz`, `omap1610_cpu_suspend`, and `omap1610_cpu_suspend_sz` when the corresponding SoC configs are enabled.

## Control Flow
Each routine saves registers, programs traffic-controller and SDRAM self-refresh state, writes ARM IDLECT registers to request deep sleep, executes CP15 wait-for-interrupt, then resumes at the next instruction, restores IDLECT and memory-controller state, restores registers, and returns. The 1610 path drains write cache and includes 74 NOPs for a documented wake erratum.

## State and Persistence Behavior
Uses the caller's stack and hardware register state only. It relies on `pm.c` passing saved `ARM_IDLECT1/2` values in `r0/r1` and on being copied to SRAM by `omap_sram_push()`.

## Dependencies and Integration Points
Depends on constants from `pm.h`, `iomap.h`, and `hardware.h`; called indirectly through `omap_sram_suspend` in `pm.c`.

## Risks
This code runs in the most fragile suspend context. Any stack, address, or timing error can hang resume. Constants must remain assembly-safe and match actual mapped IO addresses.

## Test Signals
Suspend/resume on OMAP1510 and OMAP1610-class devices, including repeated cycles and wake IRQ sources. Disassembly checks should confirm size symbols cover the intended function bodies for SRAM copy.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/sleep.S -->
