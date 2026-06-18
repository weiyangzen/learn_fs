<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/broadcom/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/broadcom/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `broadcom`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `DTC_FLAGS_bcm2835-rpi-b`, `DTC_FLAGS_bcm2835-rpi-a`, `DTC_FLAGS_bcm2835-rpi-b-rev2`, `DTC_FLAGS_bcm2835-rpi-b-plus`, `DTC_FLAGS_bcm2835-rpi-a-plus`, `DTC_FLAGS_bcm2835-rpi-cm1-io1`, `DTC_FLAGS_bcm2836-rpi-2-b`, `DTC_FLAGS_bcm2837-rpi-2-b`, `DTC_FLAGS_bcm2837-rpi-3-a-plus`, `DTC_FLAGS_bcm2837-rpi-3-b`, `DTC_FLAGS_bcm2837-rpi-3-b-plus`, `DTC_FLAGS_bcm2837-rpi-cm3-io3`, `DTC_FLAGS_bcm2837-rpi-zero-2-w`, `DTC_FLAGS_bcm2711-rpi-400`, `DTC_FLAGS_bcm2711-rpi-4-b`, `DTC_FLAGS_bcm2711-rpi-cm4-io`, `DTC_FLAGS_bcm2835-rpi-zero`, `DTC_FLAGS_bcm2835-rpi-zero-w`, `dtb-$(CONFIG_ARCH_BCM2835)`, `dtb-$(CONFIG_ARCH_BCMBCA)`, `dtb-$(CONFIG_ARCH_BCM_5301X)`, `dtb-$(CONFIG_ARCH_BCM_53573)`, `dtb-$(CONFIG_ARCH_BCM_CYGNUS)`, `dtb-$(CONFIG_ARCH_BCM_HR2)`, `dtb-$(CONFIG_ARCH_BCM_MOBILE)`, `dtb-$(CONFIG_ARCH_BCM_NSP)`, `dtb-$(CONFIG_ARCH_BRCMSTB)`. Conditional gates include `CONFIG_ARCH_BCM2835`, `CONFIG_ARCH_BCMBCA`, `CONFIG_ARCH_BCM_5301X`, `CONFIG_ARCH_BCM_53573`, `CONFIG_ARCH_BCM_CYGNUS`, `CONFIG_ARCH_BCM_HR2`, `CONFIG_ARCH_BCM_MOBILE`, `CONFIG_ARCH_BCM_NSP`, `CONFIG_ARCH_BRCMSTB`. It lists 103 DTB targets, including `bcm2835-rpi-b.dtb`, `bcm2835-rpi-a.dtb`, `bcm2835-rpi-b-rev2.dtb`, `bcm2835-rpi-b-plus.dtb`, `bcm2835-rpi-a-plus.dtb`, `bcm2835-rpi-cm1-io1.dtb`, `bcm2836-rpi-2-b.dtb`, `bcm2837-rpi-2-b.dtb`, `bcm2837-rpi-3-a-plus.dtb`, `bcm2837-rpi-3-b.dtb`, `bcm2837-rpi-3-b-plus.dtb`, `bcm2837-rpi-cm3-io3.dtb`, `bcm2837-rpi-zero-2-w.dtb`, `bcm2711-rpi-400.dtb`, `bcm2711-rpi-4-b.dtb`, `bcm2711-rpi-cm4-io.dtb`, `bcm2835-rpi-zero.dtb`, `bcm2835-rpi-zero-w.dtb`, `bcm6846-genexis-xg6846b.dtb`, `bcm947622.dtb`, `bcm963138.dtb`, `bcm963138dvt.dtb`, `bcm963148.dtb`, `bcm963178.dtb`, and 79 more.

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

Source read size: 132 lines, 3694 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/broadcom/Makefile -->
