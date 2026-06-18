# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-warp.c

## Purpose
Old U-Boot compatibility wrapper for PIKA Warp 44x systems.

## Important APIs, Types, And Control Flow
`warp_fixups()` applies 440EP clocks with fixed 66 MHz sysclk, reads SDRAM memory size, fixes EBC ranges, and writes `ethernet0` MAC address. `platform_init()` copies board info, sets fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State is board info, platform callbacks, FDT properties, and DCR-derived memory/clock data. Dependencies include 4xx helpers and EBC/alias paths. Risks include single-Ethernet assumption, hard-coded clock constants, and firmware/DT mismatch for EBC. Test with `cuImage.warp`, FDT memory/EBC/clock/MAC properties, and reboot through DBCR.
