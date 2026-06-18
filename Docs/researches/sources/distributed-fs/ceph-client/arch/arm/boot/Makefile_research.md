<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/Makefile

## Purpose
This Makefile builds ARM boot images: raw `Image`, compressed `zImage`, XIP `xipImage`, U-Boot `uImage`, and BOOTP-wrapped `bootpImage`.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `OBJCOPYFLAGS`, `add_hex`, `ZRELADDR`, `PHYS_OFFSET`, `targets`, `cmd_deflate_xip_data`, `quiet_cmd_mkxip`, `cmd_mkxip`, `check_for_multiple_loadaddr`, `subdir-`. Conditional gates include `CONFIG_XIP_KERNEL`, `CONFIG_XIP_DEFLATED_DATA`.

## Control Flow
For non-XIP builds it objcopies `vmlinux` to `Image`, builds `compressed/vmlinux`, and objcopies that to `zImage`. For XIP builds it creates `xipImage`, optionally runs `deflate_xip_data.sh`, and rejects incompatible `Image`/`zImage` targets. `uImage` validates a single load address, while `bootpImage` delegates to the `bootp` subdirectory.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are inconsistent `PHYS_OFFSET`, `TEXT_OFFSET`, `ZRELADDR`, or `LOADADDR`, unsupported XIP target combinations, and BOOTP/uImage load addresses that do not match the bootloader.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 92 lines, 2412 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/Makefile -->
