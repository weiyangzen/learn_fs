# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-taishan.c

## Purpose
Old U-Boot compatibility wrapper for Taishan 440GX boards.

## Important APIs, Types, And Control Flow
`taishan_fixups()` uses a fixed 33 MHz sysclk, computes 440GX clocks, reads SDRAM memory size, writes Ethernet aliases 0/1, and fixes EBC ranges. `platform_init()` copies board info, installs the fixup, initializes FDT, and starts serial console. A 4 KiB BSS stack is declared.

## State, Dependencies, Risks, And Tests
State is board info, BSS stack, FDT updates, and DCR-derived clocks/memory. Dependencies include `TARGET_440GX`, 4xx helpers, and EBC path. Risks include the source FIXME that sysclk should come from FPGA registers, MAC alias mismatch, and SDRAM sizing errata. Test with `cuImage.taishan`, measured clock comparison, EBC range validation, and Ethernet MAC propagation.
