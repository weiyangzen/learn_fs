<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/Makefile

## Purpose
Kbuild manifest for TI DaVinci ARM board DTBs.

## Important APIs/types/functions
- `dtb-$(CONFIG_ARCH_DAVINCI)` lists `da850-lcdk.dtb`, `da850-enbw-cmc.dtb`, `da850-evm.dtb`, and `da850-lego-ev3.dtb`.

## Control flow
Kbuild appends DaVinci board DTBs when `CONFIG_ARCH_DAVINCI` is enabled.

## State and persistence behavior
No runtime state; it persists the board DTB output set.

## Dependencies and integration points
Depends on DaVinci DTS files and the ARM DTC pipeline. Bootloaders and board packaging use these exact DTB names.

## Risks and edge cases
Missing board entries prevent DTB generation; stale names break `dtbs`. DaVinci boards often rely on legacy platform integration, so schema regressions may surface in peripheral probe failures.

## Test signals
Run `make ARCH=arm dtbs` with DaVinci enabled; run `dtbs_check` for DA850 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/davinci/Makefile -->
