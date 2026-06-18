# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-sam440ep.c

## Purpose
Old U-Boot compatibility wrapper for Sam440ep, derived from Bamboo support with Sam-specific clock values.

## Important APIs, Types, And Control Flow
`sam440ep_fixups()` uses a 66.666 MHz sysclk, applies 440EP clocks, reads SDRAM memory size, quiesces EMAC/MAL, and writes two MAC addresses. `platform_init()` copies board info, installs fixup and DBCR reset callbacks, initializes FDT, and starts serial console.

## State, Dependencies, Risks, And Tests
State is copied board info, platform callbacks, and FDT/hardware updates. Dependencies include `4xx.c`, `44x.h`, EMAC MMIO addresses, and U-Boot MAC fields. Risks include hard-coded EMAC addresses, indentation hiding no logic but inviting churn, fixed clocks, and MAC helper argument shape. Test with `cuImage.sam440ep`, serial console, Ethernet reset behavior, and FDT memory/clock/MAC properties.
