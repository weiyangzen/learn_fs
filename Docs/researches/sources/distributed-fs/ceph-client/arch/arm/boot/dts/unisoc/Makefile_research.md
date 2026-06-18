<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/unisoc/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/unisoc/Makefile

## Purpose
Kbuild manifest for Unisoc/RDA ARM DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_RDA)` lists Orange Pi 2G-IoT and Orange Pi i96 DTBs based on RDA8810PL.

## Control flow
Kbuild builds the listed DTBs when `CONFIG_ARCH_RDA` is enabled.

## State and persistence behavior
No runtime state; it persists board DTB output names.

## Dependencies and integration points
Depends on RDA DTS files, `ARCH_RDA`, and ARM DTC build rules.

## Risks and edge cases
Stale DTB names break the build; absent entries reduce board coverage.

## Test signals
Run `make ARCH=arm dtbs` and `dtbs_check` with RDA enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/unisoc/Makefile -->
