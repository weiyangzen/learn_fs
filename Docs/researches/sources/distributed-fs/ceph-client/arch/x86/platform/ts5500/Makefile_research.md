<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/Makefile

## Purpose
Builds Technologic Systems TS-5500 platform support.

## Important APIs, Types, And Functions
`ts5500.o` is selected by `CONFIG_TS5500`.

## Control Flow
Kbuild includes the platform detector and device registration code when configured.

## State And Persistence
No runtime state exists here.

## Dependencies And Integration Points
The object integrates with platform devices, GPIO lookup, and DMI/BIOS detection in `ts5500.c`.

## Risks And Edge Cases
Incorrect config selection can add legacy board probing to unrelated kernels, though runtime detection self-filters.

## Test Signals
Config build and TS-5500 boot probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/ts5500/Makefile -->
