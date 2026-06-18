# sources/distributed-fs/ceph-client/arch/microblaze/boot/dts/linked_dtb.S

## Purpose

embeds a linked device tree blob into a dedicated assembly section for MicroBlaze boot images

## Important APIs, Types, and Functions

Source read size: 2 lines, 70 bytes.

## Control Flow and Behavior

the assembler source includes the generated DTB binary so early boot can find platform description
data without external firmware handoff

## State and Persistence

persistent state is the linked .dtb image inside the kernel binary

## Dependencies and Integration Points

integrates with boot/dts Makefile rules, vmlinux linking, and early device-tree unflattening

## Risks and Test Signals

section naming or missing DTB input prevents early platform discovery; dtbs and boot image builds
are signals
