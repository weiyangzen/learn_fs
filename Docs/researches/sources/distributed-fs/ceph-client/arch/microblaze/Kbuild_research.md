# sources/distributed-fs/ceph-client/arch/microblaze/Kbuild

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze`

## Important APIs, Types, and Functions

Source read size: 8 lines, 153 bytes. Build selections: `obj-y -> kernel/`, `obj-y -> mm/`, `obj-y
-> boot/dts/`.

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
