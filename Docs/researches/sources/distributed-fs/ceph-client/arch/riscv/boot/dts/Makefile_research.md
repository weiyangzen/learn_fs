<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/boot/dts/Makefile

## Purpose
Declares vendor subdirectories that contain RISC-V devicetree sources.

## Important APIs, Types, And Functions
The only API is the ordered `subdir-y` list: allwinner, andes, anlogic, canaan, eswin, microchip, renesas, sifive, sophgo, spacemit, starfive, tenstorrent, and thead.

## Control Flow
Kbuild descends into each listed subdirectory during DTB builds so that vendor Makefiles can add config-gated DTB targets.

## State And Persistence
State is build graph traversal state only.

## Dependencies And Integration Points
Depends on kbuild DTB recursion and the presence of each vendor Makefile.

## Risks And Edge Cases
Omitting a vendor directory prevents its DTBs from being built. Adding a directory without a valid Makefile breaks `make dtbs`.

## Test Signals
Signals are `make ARCH=riscv dtbs` descending into all listed vendor directories.

Source read size: 14 lines, 296 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/boot/dts/Makefile -->
