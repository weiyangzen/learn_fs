# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-rainier.c

## Purpose
Old U-Boot compatibility wrapper for Rainier 440EP/Denali-memory boards.

## Important APIs, Types, And Control Flow
`platform_init()` copies board info, installs `rainier_fixups()`, sets DBCR reset exit, initializes FDT, and starts serial console. `rainier_fixups()` applies fixed clocks, fixes EBC ranges, computes Denali DDR memory size, and writes Ethernet alias MAC addresses.

## State, Dependencies, Risks, And Tests
State is `bd_t`, platform callbacks, FDT properties, and DCR-derived memory/clock data. Dependencies include Denali memory logic, EBC path, Ethernet aliases, and `ibm44x_dbcr_reset()`. Risks include hard-coded clocks, Denali chip-select workaround behavior shared with Sequoia/Rainier, and missing aliases. Test with `cuImage.rainier`, FDT memory/clock/EBC/MAC validation, and reset callback behavior.
