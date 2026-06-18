<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap44xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap44xx.h

## Purpose
`omap44xx.h` defines OMAP4 interconnect and peripheral base addresses for static mapping, SMP, GIC, L2, WakeupGen, SAR, USB, mailbox, and MMU integration.

## Important APIs, Types, and Functions
Key constants include `L4_44XX_BASE`, `L4_WK_44XX_BASE`, `L4_PER_44XX_BASE`, `L3_44XX_BASE`, EMIF/DMM bases, PRCM/CM/PRM bases, GPMC, SCM/control bases, GIC distributor/CPU bases, local timer base, L2 cache base, WakeupGen base, MCPDM, SAR RAM, mailbox, USB, and MMU bases.

## Control Flow
No runtime control flow exists. Constants feed IO mapping, SMP, interrupt, cache, and peripheral setup code.

## State and Persistence Behavior
No mutable state exists. Constants describe the fixed OMAP4 hardware address map.

## Dependencies and Integration Points
It integrates with `iomap.h`, `omap-headsmp.S`, `omap4-common.c`, `omap-smp.c`, `omap-mpuss-lowpower.c`, and OMAP4 peripheral drivers.

## Risks
Wrong base addresses can break early boot, interrupts, SMP, cache setup, or peripheral probes. Address definitions are shared between C and assembly, so type-safe checks are limited.

## Test Signals
Compile and boot OMAP443x/446x/4470 configurations. Validate GIC/TWD, L2 cache, WakeupGen, SAR, PRCM, USB, mailbox, and SMP secondary boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap44xx.h -->
