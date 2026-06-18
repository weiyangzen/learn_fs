<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smc.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smc.S

## Purpose
`omap-smc.S` provides low-level ARM secure monitor call wrappers for OMAP ROM/HAL/PPA services and AuxCoreBoot register access.

## Important APIs, Types, and Functions
Assembly entry points are `_omap_smc1`, `omap_smc2`, `omap_smc3`, `omap_modify_auxcoreboot0`, `omap_auxcoreboot_addr`, and `omap_read_auxcoreboot0`.

## Control Flow
Each wrapper saves caller registers on the stack, arranges service IDs and arguments in the ROM-expected registers, issues memory barriers, executes `smc #0` or `smc #1`, then restores registers and returns. `omap_smc2()` is for low-power HAL/PPA parameter-list calls; `omap_smc3()` supports RX-51 PPA calls with explicit service/process IDs. AuxCoreBoot helpers use fixed ROM API IDs.

## State and Persistence Behavior
No local persistent state exists. Calls can mutate secure-world state, AuxCoreBoot registers, L2/ACTLR settings, or firmware context depending on service ID.

## Dependencies and Integration Points
It depends on ARMv7 secure extension support, Linux linkage macros, and the calling conventions expected by `omap-secure.c` and `omap-smp.c`. It is used by secure dispatch, SMP secondary release, and secure register programming.

## Risks
Register preservation is critical; clobbering ABI registers can corrupt callers. Wrong SMC immediate or service register placement can hang in secure firmware. These routines require secure extension support and correct CPU mode.

## Test Signals
Boot paths that invoke each wrapper: secure L2 writes, SMP CPU1 release on secure devices, RX-51 secure APIs, and low-power secure context save. Watch for SMC failure warnings, CPU1 startup hangs, and register corruption after calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-smc.S -->
