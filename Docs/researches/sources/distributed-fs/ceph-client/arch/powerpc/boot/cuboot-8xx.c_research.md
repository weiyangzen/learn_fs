# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-8xx.c

## Purpose
Old U-Boot compatibility wrapper for 8xx systems with CPM.

## Important APIs, Types, And Control Flow
`platform_fixups()` updates memory, two MAC addresses, CPU/timebase/bus clocks using `bi_busfreq / 16`, and CPM/BRG clock properties under `/soc/cpm` and `/soc/cpm/brg`. `platform_init()` copies board info, initializes the embedded DTB and serial console, and registers the fixup.

## State, Dependencies, Risks, And Tests
State is copied 8xx board info, loader info, and FDT mutations. Dependencies include `TARGET_8xx`, `TARGET_HAS_ETH1`, CPM DT paths, and generic DT helpers. Risks include fixed CPM paths not matching a board DTB, divisor assumptions, and MAC ordering. Test with 8xx cuImages, CPM serial boot console, and FDT clock/MAC properties.
