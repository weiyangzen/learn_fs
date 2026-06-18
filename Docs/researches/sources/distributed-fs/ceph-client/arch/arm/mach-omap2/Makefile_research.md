<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Makefile

## Purpose
Maps OMAP2+ Kconfig symbols to the architecture objects that implement common setup, clocks, PRCM, power/voltage/clock domains, PM, restart, board support, hwmod data, and platform quirks.

## Important APIs, Types, and Functions
Exports no C API but defines build composition variables such as `hwmod-common`, `clock-common`, `secure-common`, `omap-4-5-common`, PM common groups, PRCM groups, and per-SoC `obj-*` object lists.

## Control Flow
Kbuild evaluates symbols and adds common objects first, then SoC-specific restart, SRAM, PM, PRCM, voltage/power/clockdomain, clock, OPP, hwmod, board, PHY, USB, and IOMMU objects. It also generates `pm-asm-offsets.h` for AM33xx/AM43xx sleep assembly.

## State and Persistence Behavior
No runtime state. Build output state is the object set linked into `vmlinux` and generated offset headers.

## Dependencies and Integration Points
Depends directly on Kconfig symbols from this directory and subsystem configs such as MCBSP, TWL4030, CPCAP, PM_OPP, CPU_IDLE, OMAP_IOMMU, and TUSB6010.

## Risks
Object inclusion order and conditional grouping are critical; missing common objects can break unresolved symbols only in specific SoC configs. Generated PM offsets must be available before sleep objects build.

## Test Signals
Build matrix across OMAP2/3/4/5, AM33xx, AM43xx, DRA7, with PM and CPU_IDLE toggled. Use `make W=1` to catch stale object dependencies and generated-header ordering issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/Makefile -->
