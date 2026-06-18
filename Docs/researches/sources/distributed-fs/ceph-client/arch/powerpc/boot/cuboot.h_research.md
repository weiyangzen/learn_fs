# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.h

## Purpose
Header contract and convenience macro for old U-Boot compatibility wrappers.

## Important APIs, Types, And Control Flow
It declares `cuboot_init()` and defines `CUBOOT_INIT()`, which copies the firmware `bd_t` at `r3` into the wrapper's local `bd` variable, then calls `cuboot_init(r4, r5, r6, r7, bd.bi_memstart + bd.bi_memsize)`.

## State, Dependencies, Risks, And Tests
State is the wrapper-local `bd` variable and global loader/allocator state set by `cuboot_init()`. Dependencies include each cuboot file declaring `static bd_t bd`, register names in `platform_init()`, and the `ppcboot.h` layout selected by `TARGET_*` macros. Risks are macro capture, wrong `bd_t` layout for a board, and end-of-RAM overflow. Test by compiling every cuboot wrapper and booting with old U-Boot register conventions.
