# sources/distributed-fs/ceph-client/arch/powerpc/boot/cuboot.c

## Purpose
Shared compatibility setup for old U-Boot wrappers that do not receive a ready device tree.

## Important APIs, Types, And Control Flow
`cuboot_init(r4, r5, r6, r7, end_of_ram)` interprets U-Boot registers as initrd start/end and command-line start/end, writes `loader_info`, computes available RAM from `_end` to `end_of_ram`, and initializes the simple allocator with a 1 MiB reserve below the RAM end.

## State, Dependencies, Risks, And Tests
State is global `loader_info` and simple allocator state. Dependencies include boot-wrapper symbols `_end`, `loader_info`, and old U-Boot calling conventions. Risks include bad `end_of_ram` from board info, invalid command-line bounds, reserve underflow on tiny RAM, and assuming `r4 == 0` means no initrd. Test each cuboot wrapper with and without initrd/cmdline and verify allocator placement does not overlap wrapper, kernel, or initrd.
