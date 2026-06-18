<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/bootp/Makefile

## Purpose
This Makefile links the legacy ARM BOOTP wrapper that combines a zImage with an initrd and ATAG parameter setup.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `add_hex`, `PARAMS_PHYS`, `initrd_offset-$(CONFIG_ARCH_FOOTBRIDGE)`, `initrd_offset-$(CONFIG_ARCH_SA1100)`, `initrd_offset-$(CONFIG_ARCH_RPC)`, `INITRD_OFFSET`, `INITRD_PHYS`, `PHONY`, `LDFLAGS_bootp`, `AFLAGS_initrd.o`, `targets`. Conditional gates include none.

## Control Flow
It derives `PARAMS_PHYS` and sometimes `INITRD_PHYS` from `PHYS_OFFSET`, validates `INITRD`, builds `init.o`, `kernel.o`, and `initrd.o`, and links them with `bootp.lds`. The resulting binary is later objcopied by the parent boot Makefile.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are missing `INITRD`, invalid `PARAMS_PHYS` or `INITRD_PHYS`, untracked `.incbin` inputs, and load addresses that put the initrd outside usable RAM.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 59 lines, 1823 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/bootp/Makefile -->
