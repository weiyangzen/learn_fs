<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/Makefile

## Purpose
This Makefile builds the self-relocating ARM zImage decompressor and links it with compressed kernel payload data.

## Important APIs, Types, and Functions
Important Make/Kbuild symbols include `OBJS`, `HEAD`, `AFLAGS_head.o`, `CFLAGS_string.o`, `ZTEXTADDR`, `ZBSSADDR`, `MALLOC_SIZE`, `CPPFLAGS_vmlinux.lds`, `compress-$(CONFIG_KERNEL_GZIP)`, `compress-$(CONFIG_KERNEL_LZO)`, `compress-$(CONFIG_KERNEL_LZMA)`, `compress-$(CONFIG_KERNEL_XZ)`, `compress-$(CONFIG_KERNEL_LZ4)`, `libfdt_objs`, `CFLAGS_REMOVE_atags_to_fdt.o`, `CFLAGS_atags_to_fdt.o`, `targets`, `KBUILD_CFLAGS`, `ccflags-y`, `ccflags-remove-$(CONFIG_FUNCTION_TRACER)`, `asflags-y`, `KBSS_SZ`, `LDFLAGS_vmlinux`, `check_for_bad_syms`, `bad_syms`, `check_for_multiple_zreladdr`, `efi-obj-$(CONFIG_EFI_STUB)`, `CFLAGS_font.o`. Conditional gates include `CONFIG_DEBUG_UNCOMPRESS`, `CONFIG_ARM_VIRT_EXT`, `CONFIG_ARCH_ACORN`, `CONFIG_ARCH_SA1100`, `CONFIG_CPU_XSCALE`, `CONFIG_PXA_SHARPSL_DETECT_MACH_ID`, `CONFIG_CPU_ENDIAN_BE32`, `CONFIG_CPU_CP15`, `CONFIG_ZBOOT_ROM`, `CONFIG_ARM_ATAG_DTB_COMPAT`, `CONFIG_USE_OF`, `CONFIG_CPU_ENDIAN_BE8`.

## Control Flow
It selects head and helper objects based on debug, virtualization, platform, endian, ATAG/FDT, and compression configuration; sets PIC and freestanding C flags; generates `piggy_data` with the chosen compressor; links decompressor `vmlinux` with `vmlinux.lds`; validates `ZRELADDR`; and rejects local/private BSS symbols that the runtime GOT relocation code cannot safely fix up.

## State and Persistence Behavior
Makefiles do not persist runtime state. Their outputs are build artifacts, generated dependency files, linked images, DTBs, and exported make variables. The selected targets remain effective only for the current build/configuration but influence bootable images and DTB inventories consumed by bootloaders and tests.

## Dependencies and Integration Points
Integration points include the top-level Kbuild system, generated `.config`, `scripts/Makefile.*` rules, objcopy/ld/dtc/compressor tools, architecture linker scripts, DTS source files, bootloader image formats, and clean rules for generated artifacts.

## Risks
Risks are non-PIC references, bad BSS/GOT relocation, unsupported compressor object selection, incorrect `_kernel_bss_size`, multiple `ZRELADDR` values without `AUTO_ZRELADDR`, and missing libfdt or helper symbols in the constrained decompressor environment.

## Test Signals
Run the relevant `make ARCH=arm` or `make ARCH=arc` image/DTB targets with `V=1` to inspect expanded commands. For DTS Makefiles, run `make ARCH=arm dtbs` and targeted `dtbs_check` on listed boards. For boot Makefiles, test `Image`, `zImage`, `uImage`, `bootpImage`, and XIP-specific targets under representative configurations.

Source read size: 160 lines, 4673 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/Makefile -->
