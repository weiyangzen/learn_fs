<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap34xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap34xx.h

## Purpose
`omap34xx.h` defines base physical addresses for OMAP34xx/AM35xx-era interconnects and core peripherals.

## Important APIs, Types, and Functions
Key constants include `L4_34XX_BASE`, `L4_WK_34XX_BASE`, `L4_PER_34XX_BASE`, `L4_EMU_34XX_BASE`, `L3_34XX_BASE`, `L4_WK_AM33XX_BASE`, 32K sync, CM/PRM, SMS/SDRC/GPMC, SCM/control, interrupt controller, ISP, USB, SmartReflex, mailbox, and security accelerator bases.

## Control Flow
No runtime control flow exists. The constants are consumed by IO mapping and register-address code.

## State and Persistence Behavior
No state is stored; the header describes fixed hardware address state.

## Dependencies and Integration Points
It integrates with `iomap.h`, `control.h`, `io.c`, and many OMAP3 platform subsystems.

## Risks
Address changes are high risk and can break early boot, PRCM/control access, USB, ISP, SDRC/GPMC, or interrupt controller setup. AM33xx wakeup base sharing also makes this header relevant outside pure OMAP34xx paths.

## Test Signals
Compile and boot OMAP3430/3630/AM35xx/AM33xx-related configs. Confirm early MMIO, PRM/CM, control, interrupt, USB, ISP, and mailbox users access valid addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap34xx.h -->
