<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.h

## Purpose
`omap-wakeupgen.h` declares WakeupGen register offsets and small public helpers for OMAP4/5 wakeup interrupt integration.

## Important APIs, Types, and Functions
It defines `OMAP_WKUPGEN_BASE`, enable bank offsets `OMAP_WKG_ENB_*`, `OMAP_AUX_CORE_BOOT_0`, `OMAP_AUX_CORE_BOOT_1`, `OMAP_AMBA_IF_MODE`, PTM sync/timestamp offsets, and declares `omap_get_wakeupgen_base()` and `omap_secure_apis_support()`.

## Control Flow
No runtime control flow exists. C and assembly-side users consume constants for MMIO offsets and public helper prototypes.

## State and Persistence Behavior
No local state exists. The constants point to WakeupGen hardware state and AuxCoreBoot release/startup registers.

## Dependencies and Integration Points
It integrates `omap-wakeupgen.c`, `omap-smp.c`, and MPUSS low-power code. It is part of the DT irqchip and SMP release path contract.

## Risks
Offset mistakes can break CPU1 boot or interrupt wake. Constants are shared across OMAP4 and OMAP5 but not all registers are equally valid on every SoC.

## Test Signals
Compile WakeupGen, SMP, and low-power users. Runtime validation includes secondary CPU boot, interrupt wake from idle, and SMC programming of `OMAP_AMBA_IF_MODE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.h -->
