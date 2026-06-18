# sources/distributed-fs/ceph-client/arch/microblaze/include/asm/Kbuild

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/include/asm`

## Important APIs, Types, and Functions

Source read size: 11 lines, 279 bytes. Build selections: `generated-y -> syscall_table.h`,
`generic-y -> cmpxchg.h`, `generic-y -> extable.h`, `generic-y -> kvm_para.h`, `generic-y ->
mcs_spinlock.h`, `generic-y -> parport.h`, `generic-y -> syscalls.h`, `generic-y -> tlb.h`,
`generic-y -> user.h`, `generic-y -> text-patching.h`.

## Control Flow and Behavior

Kbuild variables choose core kernel, mm, lib, boot image, DTB, or CPU-support objects according to
CONFIG_MMU, CONFIG_PCI, CONFIG_FUNCTION_TRACER, and related symbols

## State and Persistence

state is build output and generated headers/images, not runtime kernel memory

## Dependencies and Integration Points

integrates with top-level Kbuild recursion, generated asm offsets, boot image creation, and
architecture-specific library linkage

## Risks and Test Signals

wrong object selection causes missing low-level entry, cache, IRQ, or syscall code; microblaze
defconfig/allmodconfig builds and clean rebuilds are signals
