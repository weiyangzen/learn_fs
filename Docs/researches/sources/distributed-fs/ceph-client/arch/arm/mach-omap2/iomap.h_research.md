<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/iomap.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/iomap.h

## Purpose
`iomap.h` defines OMAP2+ static physical-to-virtual IO mapping offsets, base/size constants, and address translation macros for L3/L4/EMU/wakeup/peripheral interconnect windows across OMAP2, OMAP3, AM33xx, OMAP4, OMAP5, and DRA7.

## Important APIs, Types, and Functions
Key macros include `OMAP2_L3_IO_ADDRESS()`, `OMAP2_L4_IO_ADDRESS()`, `OMAP4_L3_IO_ADDRESS()`, `AM33XX_L4_WK_IO_ADDRESS()`, `OMAP4_L3_PER_IO_ADDRESS()`, and many `*_PHYS`, `*_VIRT`, `*_SIZE` definitions for static `map_desc` arrays.

## Control Flow
There is no runtime control flow. `io.c` consumes the constants to build the early static MMIO map, while register headers use address macros for direct MMIO address formation.

## State and Persistence Behavior
No mutable state exists. The constants define kernel virtual address layout for early and static mappings, which persists for the life of the kernel.

## Dependencies and Integration Points
It depends on SoC base-address headers such as `omap24xx.h`, `omap34xx.h`, `omap44xx.h`, and `omap54xx.h` included by consumers. It integrates with low-level MMIO access, `control.h`, and `io.c`.

## Risks
Wrong offsets or sizes cause overlapping virtual mappings, inaccessible registers, or early boot data aborts. Comments document deliberate overmapping and address holes; cleanup must preserve section-aligned requirements and early users.

## Test Signals
Compile all SoC variants and boot with early MMIO users enabled. Check early access to PRCM/control/GIC/SDRC/GPMC, absence of data aborts, and sane `/proc/vmallocinfo` or debug mapping output where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/iomap.h -->
