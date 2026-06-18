<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/sunplus/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/sunplus/Makefile

## Purpose
Kbuild manifest for Sunplus SP7021 ARM devicetree output.

## Important APIs/types/functions
- `dtb-$(CONFIG_SOC_SP7021)` appends `sunplus-sp7021-demo-v3.dtb`.

## Control flow
Kbuild includes the DTB when `CONFIG_SOC_SP7021` is enabled.

## State and persistence behavior
No runtime state. The persistent contract is the output DTB name used by installers, CI, and bootloaders.

## Dependencies and integration points
Depends on `sunplus-sp7021-demo-v3.dts`, the Sunplus SoC Kconfig symbol, and ARM DTC build rules.

## Risks and edge cases
The DTB is listed twice under the same config in this file, which can cause duplicate build-list entries and should be watched in build output. A renamed DTS must update both lines.

## Test signals
Run `make ARCH=arm dtbs` with `CONFIG_SOC_SP7021=y` and check for duplicate-target warnings; run `dtbs_check` for the SP7021 board.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/sunplus/Makefile -->
