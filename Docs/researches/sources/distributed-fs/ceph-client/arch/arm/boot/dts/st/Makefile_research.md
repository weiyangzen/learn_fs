<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/Makefile

## Purpose
Build manifest for STMicroelectronics, ST-Ericsson, SPEAr, Nomadik, U8500, STI, and STM32 ARM devicetree blobs and overlays. It maps SoC Kconfig selections to concrete `.dtb` and `.dtbo` outputs consumed by the ARM `dtbs` build.

## Important APIs/types/functions
- Kbuild variables: `dtb-$(CONFIG_ARCH_NOMADIK)`, `dtb-$(CONFIG_ARCH_SPEAR13XX)`, `dtb-$(CONFIG_ARCH_SPEAR3XX)`, `dtb-$(CONFIG_ARCH_SPEAR6XX)`, `dtb-$(CONFIG_ARCH_STI)`, `dtb-$(CONFIG_ARCH_STM32)`, and `dtb-$(CONFIG_ARCH_U8500)`.
- Overlay aggregation variables such as `stm32mp15xx-avenger96-overlay-...-dtbs` pair a base board `.dtb` with one `.dtbo`.
- Build products include classic board DTBs and overlay DTBs/DTBOs for STM32MP13/15 expansion boards, LCD panels, CAN, EEPROM, camera, Wi-Fi, and Raspberry Pi display adapters.

## Control flow
There is no runtime control flow. Kbuild expands the active `dtb-*` lists from enabled configuration symbols; composite `*-dtbs` targets cause `scripts/Makefile.lib` to build merged overlay targets from the listed base and overlay inputs. `make dtbs` or `make ARCH=arm dtbs` is the entry point.

## State and persistence behavior
The file persists the source-to-binary DT build contract. It stores no kernel runtime state, but it decides which DTBs enter build artifacts, install trees, and CI output. Overlay pairing names are durable target names and must remain aligned with corresponding `.dts` and `.dtso` files.

## Dependencies and integration points
Depends on the ARM devicetree Kbuild infrastructure, DTC overlay support, SoC Kconfig symbols, and matching source files in the same directory. Integrates with board firmware/bootloaders that select the generated DTB/DTBO names.

## Risks and edge cases
Missing or misspelled DTB names fail the `dtbs` build. Incorrect overlay pairings can produce a syntactically valid DTB with resources for the wrong board. Composite overlay targets require the base and overlay names to remain synchronized; stale targets are easy to leave behind when board DTS files are renamed.

## Test signals
Run `make ARCH=arm dtbs` for relevant `ARCH_STM32`, `ARCH_U8500`, `ARCH_STI`, `ARCH_SPEAR*`, and `ARCH_NOMADIK` configurations. `make ARCH=arm dtbs_check` should validate the resulting DTBs against binding schemas, especially STM32MP overlay combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/st/Makefile -->
