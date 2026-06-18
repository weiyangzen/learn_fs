<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/gemini/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/dts/gemini/Makefile

## Purpose
This DTS Makefile enumerates ARM devicetree blob build targets for `gemini`. It maps Kconfig platform symbols to `.dtb` outputs and, where present, DTC overlay flags or composite DTB relationships.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `dtb-$(CONFIG_ARCH_GEMINI)`. Conditional gates include `CONFIG_ARCH_GEMINI`. It lists 10 DTB targets, including `gemini-dlink-dir-685.dtb`, `gemini-dlink-dns-313.dtb`, `gemini-nas4220b.dtb`, `gemini-ns2502.dtb`, `gemini-rut1xx.dtb`, `gemini-sl93512r.dtb`, `gemini-sq201.dtb`, `gemini-ssi1328.dtb`, `gemini-wbd111.dtb`, `gemini-wbd222.dtb`.

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

Source read size: 12 lines, 292 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/dts/gemini/Makefile -->
