<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/parisc/Kbuild

## Purpose
Declares PA-RISC architecture subdirectories built by Kbuild.

## Important APIs, Types, And Functions
Adds `mm/`, `kernel/`, `math-emu/`, and `net/` to `obj-y`, and lists `boot` as a non-recursive subdir.

## Control Flow
Kbuild descends into these directories during architecture builds; boot artifacts are handled separately.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Works with `arch/parisc/Makefile` and per-directory Makefiles for core architecture subsystems.

## Risks
Directory omissions drop required architecture code or boot image generation support.

## Test Signals
PA-RISC allmodconfig/defconfig builds and boot image target availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/Kbuild -->
