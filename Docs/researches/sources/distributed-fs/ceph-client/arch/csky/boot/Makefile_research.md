# sources/distributed-fs/ceph-client/arch/csky/boot/Makefile

## Purpose

builds C-SKY boot images and delegates devicetree blob generation

## Important APIs, Types, and Functions

Source read size: 24 lines, 674 bytes.

## Control Flow and Behavior

rules create Image/vmlinuz-style targets and wire install/clean behavior into the architecture build

## State and Persistence

state is generated boot artifacts

## Dependencies and Integration Points

integrates vmlinux, compression, dtb, and install targets for C-SKY

## Risks and Test Signals

incorrect target dependencies produce stale or missing boot images; make Image, make dtbs, and
install tests are signals
