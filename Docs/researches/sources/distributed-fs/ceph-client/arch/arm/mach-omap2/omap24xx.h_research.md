<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap24xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap24xx.h

## Purpose
`omap24xx.h` defines base physical addresses for OMAP2420/2430 interconnects and major peripherals. It supplies the address constants consumed by static IO mapping, control, PRCM, SDRC, GPMC, DSP, mailbox, camera, and security code.

## Important APIs, Types, and Functions
Macros include `L4_24XX_BASE`, `L4_WK_243X_BASE`, `L3_24XX_BASE`, interrupt-controller bases, `OMAP242X_CTRL_BASE`, PRCM/CM/PRM bases, SDRC/SMS/GPMC bases, DSP subsystem bases, mailbox/camera bases, and security accelerator bases. No functions or types are defined.

## Control Flow
No runtime control flow exists. The constants are used by mapping and register-address macros during early boot and driver setup.

## State and Persistence Behavior
No mutable state exists. The constants define the hardware address map.

## Dependencies and Integration Points
It integrates with `iomap.h`, `control.h`, `io.c`, and peripheral platform code for OMAP24xx.

## Risks
Wrong base addresses cause early MMIO failures or devices probing at invalid locations. Some constants are needed for OMAP1 compile compatibility per the file comment, so cleanup must consider cross-family includes.

## Test Signals
Compile and boot OMAP2420/2430 configurations. Verify early PRCM/control access, interrupt controller, SDRC/GPMC, and any enabled DSP/mailbox/camera/security device probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap24xx.h -->
