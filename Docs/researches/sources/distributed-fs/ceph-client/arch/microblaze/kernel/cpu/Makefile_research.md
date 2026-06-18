# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/Makefile

## Purpose

selects MicroBlaze build objects, generated artifacts, or boot targets for `sources/distributed-
fs/ceph-client/arch/microblaze/kernel/cpu`

## Important APIs, Types, and Functions

Source read size: 13 lines, 311 bytes. Build selections: `ccflags-y -> -DCPU_MAJOR=$(CPU_MAJOR)
-DCPU_MINOR=$(CPU_MINOR) \`, `obj-y -> cache.o cpuinfo.o cpuinfo-pvr-full.o cpuinfo-static.o mb.o
pvr.o`.

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
