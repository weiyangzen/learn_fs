# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot-bamboo.c

## Purpose
Old U-Boot compatibility wrapper for Bamboo that reuses the native Bamboo initialization path.

## Important APIs, Types, And Control Flow
`platform_init()` copies U-Boot board info with `CUBOOT_INIT()` and calls `bamboo_init(&bd.bi_enetaddr, &bd.bi_enet1addr)`. The actual FDT/serial/fixup setup is delegated to `bamboo.c`.

## State, Dependencies, Risks, And Tests
State is `bd_t bd` plus the state created by `bamboo_init()`. Dependencies include `TARGET_4xx`, `TARGET_44x`, `44x.h`, and linked `bamboo.o`. Risks are board-info MAC pointer lifetime, mismatch between cuboot board fields and native fixup expectations, and missing Bamboo object in the build. Test by building `cuImage.bamboo` and verifying it performs the same clock/memory/MAC fixups as the native Bamboo path.
