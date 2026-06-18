# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-ebony.c

## Purpose
Old U-Boot compatibility wrapper for Ebony that delegates board-specific setup to `ebony_init()`.

## Important APIs, Types, And Control Flow
`platform_init()` copies `bd_t` through `CUBOOT_INIT()` and passes the first two U-Boot Ethernet addresses to `ebony_init()`. FDT initialization, serial console setup, and fixup registration happen in the Ebony implementation outside this file.

## State, Dependencies, Risks, And Tests
State is copied board info and Ebony initialization state. Dependencies include `TARGET_4xx`, `TARGET_44x`, `44x.h`, and linked Ebony support. Risks include invalid MAC address pointers, missing implementation linkage, and assumptions about old U-Boot `bd_t` layout. Test with `cuImage.ebony`, verifying memory, clock, EBC, and Ethernet properties after delegated fixups.
