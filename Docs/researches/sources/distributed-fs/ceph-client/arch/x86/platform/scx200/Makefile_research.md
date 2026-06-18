<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/scx200/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/scx200/Makefile

## Purpose
Builds National Semiconductor SCx200 support.

## Important APIs, Types, And Functions
`scx200.o` is selected by `CONFIG_SCx200` and currently consists of `scx200_32.o`.

## Control Flow
Kbuild aggregates the 32-bit implementation into the platform object.

## State And Persistence
No runtime state is stored in this file.

## Dependencies And Integration Points
Integrates with PCI and SCx200 GPIO/configuration-block users through symbols exported by `scx200_32.c`.

## Risks And Edge Cases
The implementation is 32-bit-oriented; build selection must match supported architectures.

## Test Signals
SCx200 config build and module load coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/scx200/Makefile -->
