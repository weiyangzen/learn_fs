<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/Makefile

## Purpose
Large Kbuild manifest for TI OMAP, AM33xx, AM43xx, DRA7xx, OMAP5, and TI81xx ARM DTBs and selected overlays.

## Important APIs/types/functions
- Kconfig-gated DTB lists: `CONFIG_ARCH_OMAP2`, `CONFIG_ARCH_OMAP3`, `CONFIG_ARCH_OMAP4`, `CONFIG_SOC_AM33XX`, `CONFIG_SOC_AM43XX`, `CONFIG_SOC_DRA7XX`, `CONFIG_SOC_OMAP5`, and `CONFIG_SOC_TI81XX`.
- Composite overlay targets: `am335x-bonegreen-hdmi-00a0-dtbs`, `am57xx-evm-dtbs`, `am57xx-evm-reva3-dtbs`, `am571x-idk-overlays-dtbs`, and `am572x-idk-overlays-dtbs`.
- `DTC_FLAGS_am335x-* += -@` enables symbol generation required by overlays for BeagleBone-family base DTBs.
- `dtb- += ...` entries mark build-time overlay test targets enabled by `CONFIG_OF_ALL_DTBS`.

## Control flow
Kbuild evaluates enabled SoC symbols to build the matching board DTBs. Composite `*-dtbs` rules combine base DTB and overlay DTBO dependencies. DTC flags are applied per base target before overlay builds.

## State and persistence behavior
No runtime state. This file persists the canonical list of generated TI board DTBs and overlay-enabled base targets, which affects release artifacts and downstream bootloader references.

## Dependencies and integration points
Depends on DTS/DTSO sources in `ti/omap`, DTC overlay support, TI SoC Kconfig, and binding schemas. Integrates with board packaging and U-Boot/extlinux DTB naming for OMAP/AM/DRA platforms.

## Risks and edge cases
Overlay targets require `-@` on matching bases; missing flags break phandle symbol resolution. `dtb- +=` test-only targets may be built only under all-DTB modes, so normal builds may miss overlay regressions. Long board lists are prone to stale entries and missing new boards.

## Test signals
Run `make ARCH=arm dtbs` across OMAP/AM/DRA configs and `make ARCH=arm dtbs_check`. Include `CONFIG_OF_ALL_DTBS=y` or equivalent all-DTB builds to exercise test-only overlay compositions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/ti/omap/Makefile -->
