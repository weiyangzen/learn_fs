# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-85xx-cpm2.c

## Purpose
Old U-Boot compatibility wrapper for 85xx boards with CPM2.

## Important APIs, Types, And Control Flow
`platform_fixups()` updates memory, Ethernet aliases 0-2, CPU/timebase/bus clocks using `bi_busfreq / 8`, SoC `bus-frequency`, direct child serial clocks, and `fsl,cpm2-brg` `clock-frequency` from `bi_brgfreq`. `platform_init()` uses `CUBOOT_INIT()`, initializes FDT/serial, and registers the fixup.

## State, Dependencies, Risks, And Tests
State includes copied CPM2-capable board info and FDT properties. Dependencies include `TARGET_85xx`, `TARGET_CPM2`, DT compatible strings, and serial/CPM nodes. Risks include absent CPM BRG node, missing third Ethernet alias, bus-frequency divisor mistakes, and stale U-Boot board-info values. Test with CPM2 85xx cuImages, serial console, CPM BRG consumers, and FDT property inspection.
