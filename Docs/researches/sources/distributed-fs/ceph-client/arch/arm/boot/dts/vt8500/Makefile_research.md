<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/vt8500/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/vt8500/Makefile

## Purpose
Kbuild manifest for VIA/WonderMedia VT8500-family board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_VT8500)` lists VT8500, WM8505, WM8650, WM8750, WM8850, and WM8950 boards.

## Control flow
The DTBs are included in the build when `CONFIG_ARCH_VT8500` is enabled.

## State and persistence behavior
No runtime state. The persistent artifact is the set of generated DTB names.

## Dependencies and integration points
Depends on matching DTS files, VT8500 Kconfig, DTC, and platform binding schemas.

## Risks and edge cases
Legacy boards may receive less CI coverage; missing schema coverage can hide resource mismatches until boot.

## Test signals
Run `make ARCH=arm dtbs` and `dtbs_check` with VT8500 enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/vt8500/Makefile -->
