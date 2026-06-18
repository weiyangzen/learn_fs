# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx.c

## Purpose
Old U-Boot compatibility wrapper for non-CPM2 Freescale 85xx systems with up to four Ethernet addresses.

## Important APIs, Types, And Control Flow
The wrapper defines `TARGET_85xx` and `TARGET_HAS_ETH3`. `platform_fixups()` updates memory, Ethernet aliases 0-3, CPU/timebase/bus clocks, SoC `bus-frequency`, and direct child serial clock properties. `platform_init()` copies board info via `CUBOOT_INIT()`, initializes FDT and serial console, and assigns the fixup callback.

## State, Dependencies, Risks, And Tests
State is board info, loader info, allocator, and FDT. Dependencies include alias naming, 85xx board-info layout, and serial nodes under the SoC. Risks include invalid fourth MAC on boards without ETH3, wrong timebase divisor, and old DT node naming. Test with 85xx board cuImages, four-port and fewer-port DTBs, and serial clock/MAC validation after fixups.
