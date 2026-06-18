# sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/boot/dts`

## Important APIs, Types, and Functions

Source read size: 20 lines, 355 bytes. Build selections: `dtb-y -> system.dtb`, `obj-y ->
linked_dtb.o`.

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
