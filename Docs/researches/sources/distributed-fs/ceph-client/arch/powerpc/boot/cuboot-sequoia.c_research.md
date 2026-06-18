# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sequoia.c

## Purpose
Old U-Boot compatibility wrapper for Sequoia 440EP/Denali-memory boards.

## Important APIs, Types, And Control Flow
`sequoia_fixups()` applies fixed 33.333 MHz sysclk and 50 MHz timer clock, fixes EBC ranges, calculates Denali memory size, and writes Ethernet alias MAC addresses. `platform_init()` copies board info, sets fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State includes board info, callbacks, FDT, and hardware-derived Denali/EBC data. Dependencies include `4xx.c`, EBC path `/plb/opb/ebc`, aliases, and Sequoia-specific Denali chip-select assumptions. Risks are fixed clocks, memory sizing if U-Boot misprogrammed chip selects, and alias absence. Test with `cuImage.sequoia`, memory size compared to installed RAM, clock-frequency properties, and DBCR reset.
