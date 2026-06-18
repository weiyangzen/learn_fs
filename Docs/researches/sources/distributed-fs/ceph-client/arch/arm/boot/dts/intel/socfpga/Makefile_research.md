<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/socfpga/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/socfpga/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `socfpga`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_INTEL_SOCFPGA)`. Conditional gates include `CONFIG_ARCH_INTEL_SOCFPGA`. It lists 39 DTB targets, including `socfpga_arria5_socdk.dtb`, `socfpga_arria10_chameleonv3.dtb`, `socfpga_arria10_mercury_aa1_pe1_emmc.dtb`, `socfpga_arria10_mercury_aa1_pe1_qspi.dtb`, `socfpga_arria10_mercury_aa1_pe1_sdmmc.dtb`, `socfpga_arria10_mercury_aa1_pe3_emmc.dtb`, `socfpga_arria10_mercury_aa1_pe3_qspi.dtb`, `socfpga_arria10_mercury_aa1_pe3_sdmmc.dtb`, `socfpga_arria10_mercury_aa1_st1_emmc.dtb`, `socfpga_arria10_mercury_aa1_st1_qspi.dtb`, `socfpga_arria10_mercury_aa1_st1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe1_emmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe1_qspi.dtb`, `socfpga_cyclone5_mercury_sa1_pe1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe3_emmc.dtb`, `socfpga_cyclone5_mercury_sa1_pe3_qspi.dtb`, `socfpga_cyclone5_mercury_sa1_pe3_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa1_st1_emmc.dtb`, `socfpga_cyclone5_mercury_sa1_st1_qspi.dtb`, `socfpga_cyclone5_mercury_sa1_st1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa2_pe1_qspi.dtb`, `socfpga_cyclone5_mercury_sa2_pe1_sdmmc.dtb`, `socfpga_cyclone5_mercury_sa2_pe3_qspi.dtb`, `socfpga_cyclone5_mercury_sa2_pe3_sdmmc.dtb`, and 15 more.

## Control Flow
The ARM DTS build descends into this directory from the parent `arch/arm/boot/dts/Makefile`. Enabled `dtb-$(CONFIG_...)` assignments add board DTBs to the dtbs target; `DTC_FLAGS_*` entries customize dtc invocation, commonly `-@` for overlay symbol generation; composite `*-dtbs` variables describe board-plus-overlay bundles.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are DTB entries gated by the wrong Kconfig symbol, stale board filenames after DTS renames, missing `DTC_FLAGS` for overlay-capable boards, duplicate target entries, and parent Makefiles not descending into the subdirectory.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 41 lines, 1632 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/intel/socfpga/Makefile -->
