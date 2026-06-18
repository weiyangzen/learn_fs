# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-yosemite.c

## Purpose
Old U-Boot compatibility wrapper for Yosemite 440EP boards.

## Important APIs, Types, And Control Flow
`yosemite_fixups()` uses fixed clock inputs, applies 440EP clock fixups, reads SDRAM memory size, quiesces EMAC/MAL at hard-coded MMIO addresses, and writes two Ethernet alias MACs. `platform_init()` copies board info, sets fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State includes copied board info, FDT changes, platform callbacks, and hardware quiesce side effects. Dependencies include 4xx helpers, Ethernet aliases, and EMAC address constants. Risks are fixed clocks, EMAC reset on variants, MAC pointer validity, and SDRAM errata handling. Test with `cuImage.yosemite`, serial boot, Ethernet initialization after kernel starts, and FDT memory/clock/MAC validation.
