# sources/distributed-fs/ceph-client/arch/microblaze/kernel/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/kernel`

## Important APIs, Types, and Functions

Source read size: 29 lines, 687 bytes. Build selections: `obj-y -> head.o dma.o exceptions.o \`,
`obj-y -> cpu/`, `obj-y -> misc.o`, `obj-y -> entry.o`.

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
