# sources/distributed-fs/ceph-client/arch/csky/Kbuild

## Purpose

selects the top-level C-SKY architecture subdirectories that participate in the kernel build

## Important APIs, Types, and Functions

Source read size: 6 lines, 94 bytes. Build selections: `obj-y -> kernel/ mm/`.

## Control Flow and Behavior

Kbuild descends into kernel, mm, boot, and ABI-specific object directories according to the object
list

## State and Persistence

there is no runtime state

## Dependencies and Integration Points

integrates the C-SKY architecture tree into the generic recursive Kbuild system

## Risks and Test Signals

missing directories omit boot-critical code; allmodconfig/defconfig build coverage is the main
signal
