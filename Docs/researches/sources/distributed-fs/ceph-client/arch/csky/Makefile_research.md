# sources/distributed-fs/ceph-client/arch/csky/Makefile

## Purpose

sets C-SKY architecture compiler flags, ABI-specific include paths, image targets, and boot/install
helpers

## Important APIs, Types, and Functions

Source read size: 78 lines, 1530 bytes. Build selections: `core-y -> arch/csky/$(CSKYABI)/`, `libs-y
-> arch/csky/lib/ \`.

## Control Flow and Behavior

the file selects ABI v1/v2 options, CPU tuning flags, Kbuild image names, head objects, and archhelp
text

## State and Persistence

state is build configuration only

## Dependencies and Integration Points

integrates Kconfig selections with compiler, linker, boot image, and dtb build rules

## Risks and Test Signals

wrong flags or head object ordering can make kernels unbootable; defconfig image builds and linker
checks are the primary tests
