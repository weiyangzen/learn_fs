# subset-b-000764 Research

Grouped research report for the requested PowerPC boot-wrapper and crypto subset. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/div64.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/div64.S

Purpose: implements 32-bit boot-wrapper helper routines for 64-bit division and 64-bit shifts that the freestanding C code needs before libgcc is available.

Important APIs/types/functions: assembly labels/symbols `__div64_32`, `__ashrdi3`, `__ashldi3`, `__lshrdi3`. Source size is 107 lines / 3131 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/div64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/Makefile

Purpose: declares the PowerPC boot device-tree source inventory for the kernel build system.

Important APIs/types/functions: build variables/targets `subdir-y`, `dtb-$(CONFIG_OF_ALL_DTBS)`. Source size is 5 lines / 139 bytes.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/fsl/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/fsl/Makefile

Purpose: declares the PowerPC boot device-tree source inventory for the kernel build system.

Important APIs/types/functions: build variables/targets `dtb-$(CONFIG_OF_ALL_DTBS)`. Source size is 3 lines / 122 bytes.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/fsl/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ebony.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ebony.c

Purpose: performs IBM Ebony 440GP boot-wrapper fixups, especially flash-bank selection and early board initialization.

Important APIs/types/functions: functions `ebony_flashsel_fixup`, `ebony_fixups`, `ebony_init`; macros `EBONY_FPGA_PATH`, `EBONY_FPGA_FLASH_SEL`, `EBONY_SMALL_FLASH_PATH`. Source size is 88 lines / 2294 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ebony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/elf.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/elf.h

Purpose: defines the minimal ELF32/ELF64 data structures and constants consumed by the boot wrapper's ELF parser.

Important APIs/types/functions: types `elf32_hdr`, `elf64_hdr`, `elf32_phdr`, `elf64_phdr`, `elf_info`; macros `_PPC_BOOT_ELF_H_`, `PT_NULL`, `PT_LOAD`, `PT_DYNAMIC`, `PT_INTERP`, `PT_NOTE`, `PT_SHLIB`, `PT_PHDR`, `PT_TLS`, `PT_LOOS`, `PT_HIOS`, `PT_LOPROC`, `PT_HIPROC`, `PT_GNU_EH_FRAME`, `PT_GNU_STACK`, `ET_NONE`, `ET_REL`, `ET_EXEC`, and 38 more. Source size is 158 lines / 4046 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/elf_util.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/elf_util.c

Purpose: parses compressed or uncompressed kernel ELF headers and derives load offsets, load sizes, and memory footprint.

Important APIs/types/functions: functions `parse_elf64`, `parse_elf32`. Source size is 78 lines / 2217 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `elf.h`, `page.h`, `string.h`, `stdio.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/elf_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ep8248e.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ep8248e.c

Purpose: initializes the Embedded Planet EP8248E PlanetCore boot path and applies PQ2 clock, MAC, and stdout fixups.

Important APIs/types/functions: functions `platform_fixups`, `platform_init`. Source size is 52 lines / 1111 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `planetcore.h`, `pq2.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ep8248e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ep88xc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ep88xc.c

Purpose: initializes the Embedded Planet EP88xC PlanetCore boot path and applies MPC8xx clock, MAC, and stdout fixups.

Important APIs/types/functions: functions `platform_fixups`, `platform_init`. Source size is 51 lines / 1100 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `planetcore.h`, `mpc8xx.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ep88xc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr-wrapper.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr-wrapper.c

Purpose: provides the ePAPR platform wrapper entry that forwards firmware-provided arguments into the common ePAPR init path.

Important APIs/types/functions: functions `platform_init`. Source size is 10 lines / 328 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr-wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr.c

Purpose: adapts ePAPR firmware entry state to boot-wrapper device-tree and console setup.

Important APIs/types/functions: functions `platform_fixups`, `epapr_platform_init`; macros `EPAPR_SMAGIC`, `EPAPR_EMAGIC`. Source size is 63 lines / 1752 bytes.

Implementation notes: The code checks ePAPR magic values, records loader-provided initrd and command line, initializes an FDT, and selects serial console support before common start().

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `io.h`, `libfdt.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fixed-head.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/fixed-head.S

Purpose: provides a minimal fixed-address boot entry label used by raw/binary wrapper targets.

Important APIs/types/functions: assembly labels/symbols `_zimage_start`. Source size is 5 lines / 105 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fixed-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fixup-headers.sed -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/fixup-headers.sed

Purpose: rewrites exported kernel headers into a form usable by the standalone boot wrapper build.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 12 lines / 379 bytes.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fixup-headers.sed -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.c

Purpose: implements Freescale SoC device-tree helpers for CPM/IMMR register translation and clock discovery.

Important APIs/types/functions: assembly labels/symbols `err`. Source size is 54 lines / 966 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `types.h`, `fsl-soc.h`, `stdio.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.h

Purpose: declares the shared Freescale SoC clock and IMMR fixup helpers used by board wrappers.

Important APIs/types/functions: macros `_PPC_BOOT_FSL_SOC_H_`. Source size is 9 lines / 151 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube-head.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube-head.S

Purpose: sets up the Nintendo GameCube low-level entry path, MMU state, and handoff to C wrapper code.

Important APIs/types/functions: assembly labels/symbols `_zimage_start`, `_mmu_off`, `_mmu_on`. Source size is 106 lines / 2232 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube.c

Purpose: initializes the Nintendo GameCube wrapper heap, flat device tree, and USB Gecko console when present.

Important APIs/types/functions: functions `platform_init`. Source size is 30 lines / 599 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `types.h`, `io.h`, `ops.h`, `ugecon.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/hack-coff.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/hack-coff.c

Purpose: post-processes AIX COFF zImage output so legacy RS/6000 firmware accepts the boot image.

Important APIs/types/functions: types `external_filehdr`, `external_scnhdr`; functions `main`; assembly labels/symbols `readerr`; macros `AOUT_MAGIC`, `get_16be(x)`, `put_16be(x, v)`, `get_32be(x)`. Source size is 80 lines / 2187 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdio.h`, `stdlib.h`, `unistd.h`, `fcntl.h`, `string.h`, `rs6000.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/hack-coff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/holly.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/holly.c

Purpose: initializes the Holly board wrapper with FDT setup and early serial console support.

Important APIs/types/functions: functions `platform_init`. Source size is 30 lines / 641 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/holly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/install.sh

Purpose: installs a built PowerPC kernel image, map, and config through the user's installkernel hook or a local fallback.

Important APIs/types/functions: build variables/targets `image_name`. Source size is 37 lines / 966 bytes.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/io.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/io.h

Purpose: provides freestanding MMIO accessors, endian-aware loads/stores, and memory-ordering barriers for boot code.

Important APIs/types/functions: functions `in_8`, `out_8`, `in_le16`, `in_be16`, `out_le16`, `out_be16`, `in_le32`, `in_be32`, `out_le32`, `out_be32`, `sync`, `eieio`, `barrier`; macros `_IO_H`. Source size is 103 lines / 2168 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt-wrapper.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt-wrapper.c

Purpose: binds libfdt operations to the boot wrapper's generic dt_ops interface and grows the FDT buffer on demand.

Important APIs/types/functions: functions `expand_buf`, `fdt_wrapper_getprop`, `fdt_wrapper_setprop`, `fdt_wrapper_del_node`, `fdt_wrapper_finalize`, `fdt_init`; macros `DEBUG`, `BAD_ERROR(err)`, `check_err(err)`, `offset_devp(off)`, `devp_offset_find(devp)`, `devp_offset(devp)`, `EXPAND_GRANULARITY`. Source size is 185 lines / 4520 bytes.

Implementation notes: Device handles are encoded as offset+1. setprop/create_node retry after expanding the FDT buffer, finalize packs the tree, and fdt_init installs every dt_ops callback after copying the incoming blob to malloc-backed storage.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state includes dt_ops callbacks, the relocated FDT buffer or PROM pointer, and loader_info fields used until final kernel entry.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `page.h`, `libfdt.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt-wrapper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt_env.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt_env.h

Purpose: supplies the minimal libfdt environment, integer limits, endian conversion, and unaligned helpers for boot builds.

Important APIs/types/functions: macros `_ARCH_POWERPC_BOOT_LIBFDT_ENV_H`, `INT_MAX`, `UINT32_MAX`, `INT32_MAX`, `fdt16_to_cpu(x)`, `cpu_to_fdt16(x)`, `fdt32_to_cpu(x)`, `cpu_to_fdt32(x)`, `fdt64_to_cpu(x)`, `cpu_to_fdt64(x)`. Source size is 27 lines / 680 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`, `string.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/main.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/main.c

Purpose: is the common zImage boot-wrapper orchestrator that prepares the kernel, initrd, ESM blob, command line, device tree, and final kernel jump.

Important APIs/types/functions: types `addr_range`, `elf_info`, `platform_ops`, `dt_ops`, `console_ops`, `loader_info`, `addr_range`; functions `prep_kernel`, `prep_initrd`, `prep_esm_blob`, `prep_esm_blob`, `prep_cmdline`, `start`; assembly labels/symbols `out`. Source size is 284 lines / 8616 bytes.

Implementation notes: prep_kernel samples or copies the ELF header, validates ELF32/ELF64, allocates or validates the target range, decompresses the payload, and flushes the cache. prep_initrd and prep_esm_blob relocate low payloads and write /chosen properties. start wires platform fixups, /chosen creation, command-line editing, FDT finalization, console close, and the final kernel ABI call.

Control flow is start() -> platform fixups -> /chosen preparation -> kernel decompression/copy -> initrd/ESM relocation -> command-line update -> device-tree finalization -> console close -> kernel entry.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `elf.h`, `page.h`, `string.h`, `stdio.h`, `ops.h`, `reg.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include decompression length mismatches, low-memory overlap between wrapper/kernel/FDT/initrd, 32-bit truncation of initrd/ESM properties, cache flush omissions, and wrong kernel entry ABI. Test signals are compressed/uncompressed zImage boots, initrd and no-initrd boots, command-line editing, FDT validation, and negative decompressor/ELF tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/microwatt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/microwatt.c

Purpose: initializes the Microwatt boot wrapper with a fixed heap, FDT, and serial console.

Important APIs/types/functions: functions `platform_init`. Source size is 24 lines / 549 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `types.h`, `io.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/microwatt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mktree.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/mktree.c

Purpose: converts an ELF zImage into the treeboot image format with a compact binary header.

Important APIs/types/functions: types `boot_block`, `stat`; functions `main`; macros `IMGBLK`. Source size is 151 lines / 3620 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `fcntl.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/stat.h`, `unistd.h`, `netinet/in.h`, `inttypes.h`, `stdint.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mktree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/motload-head.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/motload-head.S

Purpose: provides the MOTLoad-oriented wrapper entry that establishes the stack and branches into C platform code.

Important APIs/types/functions: assembly labels/symbols `_zimage_start`. Source size is 12 lines / 219 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/motload-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc52xx-psc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc52xx-psc.c

Purpose: implements an MPC5200 PSC UART backend for the generic boot-wrapper serial console.

Important APIs/types/functions: functions `psc_open`, `psc_putc`, `psc_tstc`, `psc_getc`, `mpc5200_psc_console_init`; macros `MPC52xx_PSC_SR`, `MPC52xx_PSC_SR_RXRDY`, `MPC52xx_PSC_SR_RXFULL`, `MPC52xx_PSC_SR_TXRDY`, `MPC52xx_PSC_SR_TXEMP`, `MPC52xx_PSC_BUFFER`. Source size is 65 lines / 1503 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `types.h`, `io.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc52xx-psc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc8xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc8xx.c

Purpose: derives MPC8xx clocks from reset/control registers and patches CPU, bus, timebase, and baud-rate properties.

Important APIs/types/functions: functions `mpc885_get_clock`, `mpc8xx_set_clocks`, `mpc885_fixup_clocks`; macros `MPC8XX_PLPRCR`. Source size is 78 lines / 1511 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `types.h`, `fsl-soc.h`, `mpc8xx.h`, `stdio.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc8xx.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc8xx.h

Purpose: declares MPC8xx clock fixup entry points for MPC8xx board wrappers.

Important APIs/types/functions: macros `_PPC_BOOT_MPC8xx_H_`. Source size is 12 lines / 234 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mpc8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mvme5100.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/mvme5100.c

Purpose: initializes the MVME5100 raw wrapper with heap, FDT, and serial console support.

Important APIs/types/functions: functions `platform_init`. Source size is 23 lines / 496 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `types.h`, `ops.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mvme5100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mvme7100.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/mvme7100.c

Purpose: initializes MVME7100 MOTLoad/cuBoot style metadata and device-tree fixups.

Important APIs/types/functions: functions `mvme7100_fixups`, `platform_init`; macros `TARGET_86xx`, `TARGET_HAS_ETH1`, `TARGET_HAS_ETH2`, `TARGET_HAS_ETH3`. Source size is 54 lines / 1354 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `cuboot.h`, `ppcboot.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/mvme7100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ns16550.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ns16550.c

Purpose: implements the boot wrapper NS16550-compatible UART backend.

Important APIs/types/functions: functions `ns16550_open`, `ns16550_putc`, `ns16550_getc`, `ns16550_tstc`, `ns16550_console_init`; macros `UART_DLL`, `UART_DLM`, `UART_FCR`, `UART_LCR`, `UART_MCR`, `UART_LSR`, `UART_LSR_THRE`, `UART_LSR_DR`, `UART_MSR`, `UART_SCR`. Source size is 84 lines / 2137 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `string.h`, `stdio.h`, `io.h`, `ops.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ns16550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/of.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/of.c

Purpose: initializes Open Firmware based booting and selects OF/FDT behavior for common start().

Important APIs/types/functions: functions `of_image_hdr`, `of_platform_init`, `platform_init`; macros `PROG_START`, `RAM_END`, `ONE_MB`. Source size is 93 lines / 2129 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state includes dt_ops callbacks, the relocated FDT buffer or PROM pointer, and loader_info fields used until final kernel entry.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/of.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/of.h

Purpose: declares Open Firmware handles, PROM call wrappers, endian conversion, and OF dt_ops entry points.

Important APIs/types/functions: macros `_PPC_BOOT_OF_H_`, `cpu_to_be16(x)`, `be16_to_cpu(x)`, `cpu_to_be32(x)`, `be32_to_cpu(x)`, `cpu_to_be64(x)`, `be64_to_cpu(x)`, `cpu_to_be16(x)`, `be16_to_cpu(x)`, `cpu_to_be32(x)`, `be32_to_cpu(x)`, `cpu_to_be64(x)`, `be64_to_cpu(x)`, `PROM_ERROR`. Source size is 47 lines / 1199 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `swab.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/of.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ofconsole.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ofconsole.c

Purpose: implements console_ops using Open Firmware stdout services.

Important APIs/types/functions: functions `of_console_open`, `of_console_write`, `of_console_init`. Source size is 43 lines / 830 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ofconsole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/oflib.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/oflib.c

Purpose: implements raw Open Firmware client-interface calls, allocation/claim handling, and OF property wrappers.

Important APIs/types/functions: types `prom_args`, `prom_args`, `prom_args`; functions `of_init`, `of_call_prom`, `of_call_prom_ret`, `string_match`, `check_of_version`, `of_claim`, `of_exit`, `of_getprop`, `of_setprop`; macros `ADDR(x)`. Source size is 219 lines / 5210 bytes.

Implementation notes: PROM calls are marshalled through big-endian prom_args. Older OF versions may require separate physical and virtual claims plus an explicit map call before vmlinux allocation.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state includes dt_ops callbacks, the relocated FDT buffer or PROM pointer, and loader_info fields used until final kernel entry.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/oflib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/opal-calls.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/opal-calls.S

Purpose: contains low-level OPAL call stubs used by the boot wrapper to invoke OPAL services.

Important APIs/types/functions: assembly labels/symbols `opal_kentry`, `name`, `opal_call`, `opal_return`; macros `OPAL_CALL(name, token)`. Source size is 67 lines / 1203 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`, `../include/asm/opal-api.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/opal-calls.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/opal.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/opal.c

Purpose: implements an OPAL console backend for PowerNV boot-wrapper output.

Important APIs/types/functions: types `opal`; functions `opal_con_open`, `opal_con_putc`, `opal_con_close`, `opal_init`, `opal_console_init`. Source size is 97 lines / 2284 bytes.

Implementation notes: OPAL console setup finds a raw OPAL console node, opens it, sends bytes through OPAL_CONSOLE_WRITE, and closes it through OPAL_CONSOLE_CLOSE.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `io.h`, `libfdt.h`, `../include/asm/opal-api.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/opal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ops.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ops.h

Purpose: defines the boot wrapper's central operation tables, loader metadata, device-tree helpers, console API, allocator API, and exported linker symbols.

Important APIs/types/functions: types `platform_ops`, `dt_ops`, `console_ops`, `serial_console_data`, `loader_info`; functions `getprop`, `setprop`, `setprop_str`, `del_node`, `free`, `exit`, `__attribute__`; macros `_PPC_BOOT_OPS_H_`, `BOOT_COMMAND_LINE_SIZE`, `MAX_PATH_LEN`, `MAX_PROP_LEN`, `setprop_val(devp, name, val)`, `dt_fixup_mac_addresses(...)`, `fatal(args...)`, `BSS_STACK(size)`. Source size is 259 lines / 7437 bytes.

Implementation notes: The important contracts are struct platform_ops, dt_ops, console_ops, serial_console_data, loader_info, the finddevice/getprop/setprop wrappers, dt_fixup declarations, simple_alloc_init, partial_decompress, and linker-provided payload symbols.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `string.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/page.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/page.h

Purpose: defines page size and alignment helpers for boot-wrapper allocation, decompression, and linker layout.

Important APIs/types/functions: macros `_PPC_BOOT_PAGE_H`, `ASM_CONST(x)`, `__ASM_CONST(x)`, `ASM_CONST(x)`, `PAGE_SHIFT`, `PAGE_SIZE`, `PAGE_MASK`, `_ALIGN_UP(addr, size)`, `_ALIGN_DOWN(addr, size)`, `_ALIGN(addr,size)`, `PAGE_ALIGN(addr)`. Source size is 30 lines / 896 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.c

Purpose: parses PlanetCore firmware key/value tables and applies board, MAC, memory, clock, and stdout fixups.

Important APIs/types/functions: functions `planetcore_prepare_table`, `planetcore_get_decimal`, `planetcore_get_hex`, `planetcore_set_mac_addrs`, `planetcore_set_stdout_path`. Source size is 130 lines / 2554 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdio.h`, `stdlib.h`, `ops.h`, `planetcore.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.h

Purpose: defines PlanetCore key identifiers and table structures shared by EP8248E/EP88xC wrapper code.

Important APIs/types/functions: macros `_PPC_BOOT_PLANETCORE_H_`, `PLANETCORE_KEY_BOARD_TYPE`, `PLANETCORE_KEY_BOARD_REV`, `PLANETCORE_KEY_MB_RAM`, `PLANETCORE_KEY_MAC_ADDR`, `PLANETCORE_KEY_FLASH_SPEED`, `PLANETCORE_KEY_IP_ADDR`, `PLANETCORE_KEY_KB_NVRAM`, `PLANETCORE_KEY_PROCESSOR`, `PLANETCORE_KEY_PROC_VARIANT`, `PLANETCORE_KEY_SERIAL_BAUD`, `PLANETCORE_KEY_SERIAL_PORT`, `PLANETCORE_KEY_SWITCH`, `PLANETCORE_KEY_TEMP_OFFSET`, `PLANETCORE_KEY_TARGET_IP`, `PLANETCORE_KEY_CRYSTAL_HZ`. Source size is 47 lines / 1554 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ppc_asm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ppc_asm.h

Purpose: provides register aliases and linkage macros for PowerPC boot assembly sources.

Important APIs/types/functions: macros `_PPC64_PPC_ASM_H`, `cr0`, `cr1`, `cr2`, `cr3`, `cr4`, `cr5`, `cr6`, `cr7`, `r0`, `r1`, `r2`, `r3`, `r4`, `r5`, `r6`, `r7`, `r8`, and 35 more. Source size is 97 lines / 2089 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ppc_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ppcboot.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ppcboot.h

Purpose: defines legacy PPCBoot/U-Boot board-info structures consumed by cuBoot and MOTLoad wrappers.

Important APIs/types/functions: types `bd_info`; macros `__PPCBOOT_H__`, `HAVE_ENET1ADDR`, `HAVE_ENET2ADDR`, `HAVE_ENET3ADDR`, `bi_tbfreq`. Source size is 95 lines / 3325 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ppcboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.c

Purpose: derives PowerQUICC II clocks and patches CPU, bus, timebase, brg, and CPM clock properties.

Important APIs/types/functions: functions `pq2_get_clocks`, `pq2_set_clocks`, `pq2_fixup_clocks`; macros `PQ2_SCCR`, `PQ2_SCMR`. Source size is 99 lines / 2273 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `types.h`, `fsl-soc.h`, `pq2.h`, `stdio.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.h

Purpose: declares PowerQUICC II clock fixup entry points.

Important APIs/types/functions: macros `_PPC_BOOT_PQ2_H_`. Source size is 12 lines / 338 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/pq2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3-head.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3-head.S

Purpose: lays out the PS3 system reset overlay and kernel-vector restoration entry code.

Important APIs/types/functions: assembly labels/symbols `__system_reset_overlay`, `__system_reset_kernel`. Source size is 72 lines / 1475 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3-hvcall.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3-hvcall.S

Purpose: defines PS3 LV1 hypervisor call assembly wrappers.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 174 lines / 2365 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3-hvcall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3.c

Purpose: implements PS3 boot-wrapper console, command-line, memory repository, vector-copy, and platform init logic.

Important APIs/types/functions: functions `prep_cmdline`, `ps3_console_write`, `ps3_exit`, `ps3_repository_read_rm_size`, `ps3_copy_vectors`, `platform_init`. Source size is 139 lines / 3090 bytes.

Implementation notes: The platform copies reset vectors for the PS3 loader, reads LV1 repository memory sizing, writes through hypervisor console calls, handles a PS3-specific command line, and exits via hypervisor calls.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/pseries-head.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/pseries-head.S

Purpose: provides the pSeries wrapper entry label used by OF/ePAPR pSeries images.

Important APIs/types/functions: assembly labels/symbols `_zimage_start`. Source size is 9 lines / 141 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/pseries-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot-83xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot-83xx.c

Purpose: initializes RedBoot-provided MPC83xx metadata and patches clocks, memory, and Ethernet addresses.

Important APIs/types/functions: functions `platform_fixups`, `platform_init`; macros `MHZ(x)`. Source size is 57 lines / 1297 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `redboot.h`, `fsl-soc.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot-83xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot-8xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot-8xx.c

Purpose: initializes RedBoot-provided MPC8xx metadata and patches clocks, memory, and Ethernet addresses.

Important APIs/types/functions: functions `platform_fixups`, `platform_init`; macros `MHZ(x)`. Source size is 55 lines / 1305 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `redboot.h`, `fsl-soc.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot-8xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot.h

Purpose: defines RedBoot board-info layouts and compatibility macros.

Important APIs/types/functions: types `bd_info`; macros `_PPC_REDBOOT_H`, `BI_REV`, `bi_pci_busfreq`, `bi_immr_base`; build variables/targets `//`. Source size is 57 lines / 2729 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/redboot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/reg.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/reg.h

Purpose: provides inline special-purpose-register accessors and stack-pointer helpers for boot C code.

Important APIs/types/functions: functions `mfpvr`; macros `_PPC_BOOT_REG_H`, `__stringify_1(x)`, `__stringify(x)`, `mfspr(rn)`, `mtspr(rn, v)`, `get_sp()`. Source size is 26 lines / 624 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/rs6000.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/rs6000.h

Purpose: defines AIX COFF, a.out, section, symbol, relocation, and loader structures for hack-coff.

Important APIs/types/functions: types `external_filehdr`, `external_scnhdr`, `external_lineno`, `external_syment`, `external_reloc`; macros `U802WRMAGIC`, `U802ROMAGIC`, `U802TOCMAGIC`, `BADMAG(x)`, `FILHDR`, `FILHSZ`, `AOUTSZ`, `SMALL_AOUTSZ`, `AOUTHDRSZ`, `RS6K_AOUTHDR_OMAGIC`, `RS6K_AOUTHDR_NMAGIC`, `RS6K_AOUTHDR_ZMAGIC`, `_TEXT`, `_DATA`, `_BSS`, `_PAD`, `_LOADER`, `SCNHDR`, and 25 more. Source size is 240 lines / 6939 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/rs6000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/serial.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/serial.c

Purpose: selects and exposes the proper serial backend as generic console_ops and supports command-line editing.

Important APIs/types/functions: types `serial_console_data`, `serial_console_data`, `serial_console_data`, `serial_console_data`; functions `serial_open`, `serial_write`, `serial_edit_cmdline`, `serial_close`, `serial_console_init`; assembly labels/symbols `err_out`, `err_out`. Source size is 153 lines / 3489 bytes.

Implementation notes: The dispatcher follows /chosen stdout-path, checks device_type and compatible strings, initializes ns16550/CPM/PSC/OPAL backends, and exposes write/open/close/edit_cmdline through console_ops.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `string.h`, `stdio.h`, `io.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/simple_alloc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/simple_alloc.c

Purpose: implements a small fixed-region malloc/free/realloc allocator used before the kernel is entered.

Important APIs/types/functions: types `alloc_info`, `alloc_info`, `alloc_info`, `alloc_info`; functions `simple_free`; assembly labels/symbols `err_out`; macros `ENTRY_BEEN_USED`, `ENTRY_IN_USE`. Source size is 151 lines / 3482 bytes.

Implementation notes: Allocation state is a static table with been-used and in-use flags; freed entries can be reused only if the requested size fits the original block, and realloc copies to a new block when growth is required.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state is the allocation table, next heap base, free-space counter, and platform_ops allocator hooks; it is intentionally not returned to firmware.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `page.h`, `string.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/simple_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/simpleboot.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/simpleboot.c

Purpose: initializes simpleboot platforms from an embedded FDT and optional loader-provided initrd/cmdline.

Important APIs/types/functions: functions `platform_init`. Source size is 87 lines / 2736 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `types.h`, `io.h`, `stdio.h`, `libfdt.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/simpleboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdbool.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdbool.h

Purpose: provides boolean definitions for the freestanding boot-wrapper C environment.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 9 lines / 228 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdbool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdint.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdint.h

Purpose: provides standard integer typedef access through the boot wrapper's local types header.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 9 lines / 227 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.c

Purpose: implements minimal printf/sprintf/vsprintf and numeric formatting for the boot wrapper.

Important APIs/types/functions: functions `strnlen`, `skip_atoi`, `number`, `vsprintf`, `sprintf`, `printf`; macros `do_div(n, base)`, `do_div(n,base)`, `ZEROPAD`, `SIGN`, `PLUS`, `SPACE`, `LEFT`, `SPECIAL`, `LARGE`. Source size is 354 lines / 7190 bytes.

Implementation notes: Formatting supports common integer, string, character, pointer, width, precision, and qualifier cases. On 32-bit builds 64-bit division is delegated to div64.S.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `string.h`, `stdio.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.h

Purpose: declares the boot-wrapper stdio API and local errno values.

Important APIs/types/functions: macros `_PPC_BOOT_STDIO_H_`, `ENOMEM`, `EINVAL`, `ENOSPC`, `fprintf(fmt, args...)`. Source size is 20 lines / 562 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `stdarg.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdlib.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdlib.c

Purpose: implements the boot-wrapper strtoull parser.

Important APIs/types/functions: functions `strtoull`; assembly labels/symbols `out`. Source size is 42 lines / 785 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdlib.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdlib.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/stdlib.h

Purpose: declares strtoull for freestanding boot-wrapper code.

Important APIs/types/functions: macros `_PPC_BOOT_STDLIB_H_`. Source size is 7 lines / 176 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/stdlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/string.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/string.S

Purpose: implements core string/memory routines and cache flushing in PowerPC assembly.

Important APIs/types/functions: assembly labels/symbols `strcpy`, `strncpy`, `strcat`, `strchr`, `strcmp`, `strncmp`, `strlen`, `memset`, `memmove`, `memcpy`, `backwards_memcpy`, `memchr`, `memcmp`, `flush_cache`. Source size is 265 lines / 3603 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/string.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/string.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/string.h

Purpose: declares the freestanding string/memory API consumed by boot-wrapper C code.

Important APIs/types/functions: macros `_PPC_BOOT_STRING_H_`. Source size is 22 lines / 897 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `stddef.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/swab.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/swab.h

Purpose: implements byte-swap helpers for 16-, 32-, and 64-bit values.

Important APIs/types/functions: functions `swab16`, `swab32`, `swab64`; macros `_PPC_BOOT_SWAB_H_`. Source size is 30 lines / 855 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-akebono.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-akebono.c

Purpose: initializes IBM Akebono treeboot images, detects DDR3 memory size, handles PIBS command-line MAC data, and patches FDT state.

Important APIs/types/functions: functions `ibm_akebono_detect_memsize`, `ibm_akebono_fixups`, `platform_init`; macros `SPRN_PIR`, `USERDATA_LEN`, `MAX_RANKS`, `DDR3_MR0CF`, `CCTL0_MCO2`, `CCTL0_MCO3`, `CCTL0_MCO4`, `CCTL0_MCO5`, `CCTL0_MCO6`. Source size is 159 lines / 3905 bytes.

Implementation notes: The code scans PIBS userdata for local-mac-addr, removes that token from the command line, reads DDR rank size from DCRs, disables broken SD high-speed mode, sets boot CPU ID, and initializes FDT/serial.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdlib.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`, and 1 more. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-akebono.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-bamboo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-bamboo.c

Purpose: initializes Bamboo treeboot images and extracts PIBS MAC addresses for FDT fixups.

Important APIs/types/functions: functions `read_pibs_mac`, `platform_init`; macros `PIBS_MAC0`, `PIBS_MAC1`. Source size is 40 lines / 877 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `44x.h`, `stdlib.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-bamboo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-currituck.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-currituck.c

Purpose: initializes IBM Currituck treeboot images, detects memory size, and patches PCI dma-ranges.

Important APIs/types/functions: functions `ibm_currituck_detect_memsize`, `ibm_currituck_fixups`, `platform_init`; macros `MAX_RANKS`, `DDR3_MR0CF`, `SPRN_PIR`. Source size is 115 lines / 2855 bytes.

Implementation notes: The code reads DDR rank size from DCRs, fixes /memory, updates every PCI dma-ranges size to match detected memory, sets boot CPU ID, and initializes FDT/serial.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`, `libfdt.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-currituck.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-ebony.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-ebony.c

Purpose: initializes Ebony treeboot images and imports OpenBIOS MAC addresses into the FDT.

Important APIs/types/functions: functions `platform_init`; macros `OPENBIOS_MAC_BASE`, `OPENBIOS_MAC_OFFSET`. Source size is 29 lines / 695 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `44x.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-ebony.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-iss4xx.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-iss4xx.c

Purpose: initializes ISS 4xx treeboot images and sets the boot CPU ID in the FDT.

Important APIs/types/functions: functions `iss_4xx_fixups`, `platform_init`; macros `SPRN_PIR`. Source size is 73 lines / 1812 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`, `libfdt.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-iss4xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/types.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/types.h

Purpose: defines the boot wrapper's fixed-width integer aliases, bool compatibility, and small utility macros.

Important APIs/types/functions: macros `_TYPES_H_`, `ARRAY_SIZE(x)`, `min(x,y)`, `max(x,y)`, `min_t(type, a, b)`, `max_t(type, a, b)`, `true`, `false`. Source size is 52 lines / 1012 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `stdbool.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ugecon.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ugecon.c

Purpose: implements USB Gecko console probing and transmit support through Nintendo EXI transactions.

Important APIs/types/functions: functions `ug_io_transaction`, `ug_is_txfifo_ready`, `ug_raw_putc`, `ug_putc`, `ug_console_write`, `ug_is_adapter_present`; assembly labels/symbols `err_out`; macros `EXI_CLK_32MHZ`, `EXI_CSR`, `EXI_CSR_CLKMASK`, `EXI_CSR_CLK_32MHZ`, `EXI_CSR_CSMASK`, `EXI_CSR_CS_0`, `EXI_CR`, `EXI_CR_TSTART`, `EXI_CR_WRITE`, `EXI_CR_READ_WRITE`, `EXI_CR_TLEN(len)`, `EXI_DATA`. Source size is 142 lines / 2698 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `types.h`, `io.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ugecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ugecon.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/ugecon.h

Purpose: declares the USB Gecko probe and console write entry points.

Important APIs/types/functions: macros `__UGECON_H`. Source size is 19 lines / 403 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/ugecon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/util.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/util.S

Purpose: implements timebase-period storage and a busy-wait udelay helper.

Important APIs/types/functions: assembly labels/symbols `timebase_period_ns`, `udelay`; macros `SPRN_PVR`. Source size is 67 lines / 1682 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/util.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/wii-head.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/wii-head.S

Purpose: sets up the Nintendo Wii low-level entry path, MMU state, and handoff to C wrapper code.

Important APIs/types/functions: assembly labels/symbols `_zimage_start`, `_mmu_off`, `_mmu_on`. Source size is 137 lines / 2970 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/wii-head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/wii.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/wii.c

Purpose: initializes the Wii wrapper, enables EXI, probes USB Gecko, and trims MEM2 around mini firmware.

Important APIs/types/functions: types `mipc_infohdr`, `mipc_infohdr`, `mipc_infohdr`; functions `mipc_check_address`, `mipc_get_mem2_boundary`, `platform_fixups`, `platform_init`; assembly labels/symbols `out`, `out`, `out`; macros `HW_REG(x)`, `EXI_CTRL`, `EXI_CTRL_ENABLE`, `MEM2_TOP`, `FIRMWARE_DEFAULT_SIZE`. Source size is 153 lines / 3008 bytes.

Implementation notes: The wrapper validates mini IPC pointers in MEM2, obtains the firmware memory boundary when available, shrinks the second memory bank, enables EXI, and uses USB Gecko for early output.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `types.h`, `io.h`, `ops.h`, `ugecon.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/wii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/wrapper -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/wrapper

Purpose: is the shell build driver that turns vmlinux plus optional initrd/FDT/ESM blobs into platform-specific PowerPC zImage formats.

Important APIs/types/functions: functions `ld_version`, `addsec`; build variables/targets `kernel`, `ofile`, `platform`, `initrd`, `dtb`, `dts`, `esm_blob`, `cacheit`, `binary`, `compression`, `uboot_comp`, `pie`, and 29 more. Source size is 577 lines / 14058 bytes.

Implementation notes: The script parses platform, compression, object directory, working directory, initrd, dtb/dts, and ESM options; derives the ELF format; selects platform objects/linker scripts; strips/compresses vmlinux; adds payload sections with objcopy; links; then post-processes uboot, cuBoot, treeboot, PS3, pSeries, CHRP, and COFF outputs.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/wrapper -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/xz_config.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/xz_config.h

Purpose: adapts the kernel XZ decompressor to the boot wrapper's freestanding environment.

Important APIs/types/functions: functions `swab32p`, `be32_to_cpup`, `be32_to_cpup`, `get_unaligned_be32`, `put_unaligned_be32`; macros `__XZ_CONFIG_H__`, `get_le32(p)`, `cpu_to_be32(x)`, `get_le32(p)`, `cpu_to_be32(x)`, `memeq(a, b, size)`, `memzero(buf, size)`, `DECOMPR_MM_H`, `memmove`. Source size is 57 lines / 1199 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`, `swab.h`, `../../../include/linux/xz.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/xz_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.coff.lds.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.coff.lds.S

Purpose: links COFF zImage wrappers with the sections and symbols expected by the common boot code.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 50 lines / 688 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.coff.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.lds.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.lds.S

Purpose: links normal zImage wrappers and defines embedded kernel, initrd, dtb, ESM, BSS, stack, and discard layout.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 97 lines / 1416 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `asm-generic/vmlinux.lds.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.ps3.lds.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.ps3.lds.S

Purpose: links the PS3 binary wrapper with reset-overlay sections and embedded payload layout.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 51 lines / 779 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/boot/zImage.ps3.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/Kconfig

Purpose: declares PowerPC crypto acceleration configuration choices and CPU feature dependencies.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 64 lines / 2103 bytes.

Control flow is Kconfig/Makefile selection: CPU feature symbols choose which objects are compiled, Perl generators emit assembly, and module registration code later exposes the algorithms to the crypto API.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include wrong CPU feature dependencies, missing generated objects, module alias conflicts, or stale assembly generator output. Test signals are all relevant PowerPC crypto Kconfig build combinations and crypto selftest availability at boot/module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/Makefile

Purpose: builds PowerPC crypto accelerated objects and generated assembly based on enabled Kconfig options.

Important APIs/types/functions: build variables/targets `obj-$(CONFIG_CRYPTO_AES_PPC_SPE)`, `obj-$(CONFIG_CRYPTO_AES_GCM_P10)`, `obj-$(CONFIG_CRYPTO_DEV_VMX_ENCRYPT)`, `aes-ppc-spe-y`, `aes-gcm-p10-crypto-y`, `vmx-crypto-objs`, `quiet_cmd_perl`, `targets`, `OBJECT_FILES_NON_STANDARD_aesp10-ppc.o`, `OBJECT_FILES_NON_STANDARD_ghashp10-ppc.o`. Source size is 35 lines / 933 bytes.

Control flow is Kconfig/Makefile selection: CPU feature symbols choose which objects are compiled, Perl generators emit assembly, and module registration code later exposes the algorithms to the crypto API.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include wrong CPU feature dependencies, missing generated objects, module alias conflicts, or stale assembly generator output. Test signals are all relevant PowerPC crypto Kconfig build combinations and crypto selftest availability at boot/module load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10-glue.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10-glue.c

Purpose: registers and drives ppc64le Power10 stitched AES-GCM/RFC4106 AEAD implementations.

Important APIs/types/functions: types `p10_aes_key`, `gcm_ctx`, `Hash_ctx`, `p10_aes_gcm_ctx`, `p10_aes_key`, `Hash_ctx`, `crypto_tfm`, `p10_aes_gcm_ctx`, `crypto_tfm`, `p10_aes_gcm_ctx`, and 8 more; functions `vsx_begin`, `vsx_end`, `set_subkey`, `set_aad`, `gcmp10_init`, `finish_tag`, `set_authsize`, `p10_aes_gcm_setkey`, `p10_aes_gcm_crypt`, `rfc4106_setkey`, `rfc4106_setauthsize`, `rfc4106_encrypt`, `rfc4106_decrypt`, `p10_aes_gcm_encrypt`, `p10_aes_gcm_decrypt`, `p10_init`, `p10_exit`; macros `PPC_ALIGN`, `GCM_IV_SIZE`, `RFC4106_NONCE_SIZE`. Source size is 433 lines / 10724 bytes.

Implementation notes: The glue validates auth sizes and keys, manages kernel VSX enable/disable, linearizes AAD when needed, initializes H tables and counters, walks AEAD scatterlists, invokes aes_p10_gcm_encrypt/decrypt, computes/verifies tags, and registers normal GCM plus RFC4106 variants.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `linux/unaligned.h`, `asm/simd.h`, `asm/switch_to.h`, `crypto/gcm.h`, `crypto/aes.h`, `crypto/algapi.h`, `crypto/b128ops.h`, `crypto/gf128mul.h`, `crypto/internal/simd.h`, `crypto/internal/aead.h`, `crypto/internal/hash.h`, `crypto/internal/skcipher.h`, `crypto/scatterwalk.h`, `linux/cpufeature.h`, and 3 more. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10.S

Purpose: implements the Power10 VSX/crypto stitched AES-GCM encrypt/decrypt and GHASH update hot paths.

Important APIs/types/functions: assembly labels/symbols `__More_1x`, `__Loop_1x`, `__Loop_aes_1state`, `__Encrypt_1x`, `__Loop_aes_pstate`, `__Write_partial`, `__Encrypt_partial`, `__Inp_msg_less16`, `__Combine_continue`, `__Loop_aes_cpstate`, `__Write_combine_partial`, `__Encrypt_combine_partial`, `__Update_partial_ghash`, `__Clear_partial_flag`, `__no_update`, `__Process_encrypt`, `__Process_8x_enc`, `__PreLoop_aes_state`, and 15 more. Source size is 1236 lines / 25925 bytes.

Control flow is straight-line and loop-heavy assembly generated or hand written for crypto hot paths: callers enter exported symbols with pre-expanded keys/state, the code processes full blocks in vectorized loops, handles partial/tail cases where supported, and returns updated counters, hashes, or key schedules.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `asm/ppc_asm.h`, `linux/linkage.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include register clobbering, endian mistakes, counter/hash update errors, partial-block bugs, generated assembler drift, and CPU feature mismatches. Test signals are known-answer AES/GCM/GHASH vectors, objdump symbol checks, crypto manager selftests, and stress with unaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-gcm-p10.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-spe-glue.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-spe-glue.c

Purpose: registers and drives SPE accelerated AES ECB/CBC/CTR/XTS skcipher implementations on e500-class cores.

Important APIs/types/functions: types `ppc_aes_ctx`, `ppc_xts_ctx`, `ppc_aes_ctx`, `ppc_xts_ctx`, `crypto_skcipher`, `ppc_aes_ctx`, `skcipher_walk`, `crypto_skcipher`, `ppc_aes_ctx`, `skcipher_walk`, and 12 more; functions `spe_begin`, `spe_end`, `ppc_aes_setkey_skcipher`, `ppc_xts_setkey`, `ppc_ecb_crypt`, `ppc_ecb_encrypt`, `ppc_ecb_decrypt`, `ppc_cbc_crypt`, `ppc_cbc_encrypt`, `ppc_cbc_decrypt`, `ppc_ctr_crypt`, `ppc_xts_crypt`, `ppc_xts_encrypt`, `ppc_xts_decrypt`, `ppc_aes_mod_init`, `ppc_aes_mod_fini`; macros `MAX_BYTES`. Source size is 444 lines / 11804 bytes.

Implementation notes: The module keeps SPE sections short with MAX_BYTES, expands encrypt/decrypt/tweak keys, walks skcipher requests for ECB/CBC/CTR/XTS, updates IVs and tweaks, and registers algorithms with crypto priorities and module init/exit hooks.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `crypto/aes.h`, `linux/module.h`, `linux/init.h`, `linux/types.h`, `linux/errno.h`, `linux/crypto.h`, `asm/byteorder.h`, `asm/switch_to.h`, `crypto/algapi.h`, `crypto/internal/skcipher.h`, `crypto/xts.h`, `crypto/gf128mul.h`, `crypto/scatterwalk.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes-spe-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_cbc.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_cbc.c

Purpose: registers the Power8 VSX AES-CBC skcipher with fallback handling.

Important APIs/types/functions: types `p8_aes_cbc_ctx`, `crypto_skcipher`, `p8_aes_key`, `p8_aes_key`, `p8_aes_cbc_ctx`, `crypto_skcipher`, `p8_aes_cbc_ctx`, `p8_aes_cbc_ctx`, `crypto_skcipher`, `skcipher_walk`, and 2 more; functions `p8_aes_cbc_init`, `p8_aes_cbc_exit`, `p8_aes_cbc_setkey`, `p8_aes_cbc_crypt`, `p8_aes_cbc_encrypt`, `p8_aes_cbc_decrypt`. Source size is 137 lines / 3580 bytes.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `asm/simd.h`, `asm/switch_to.h`, `crypto/aes.h`, `crypto/internal/simd.h`, `crypto/internal/skcipher.h`, `linux/err.h`, `linux/kernel.h`, `linux/module.h`, `linux/uaccess.h`, `aesp8-ppc.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_cbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_ctr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_ctr.c

Purpose: registers the Power8 VSX AES-CTR skcipher with fallback and partial-block handling.

Important APIs/types/functions: types `p8_aes_ctr_ctx`, `crypto_skcipher`, `p8_aes_key`, `p8_aes_ctr_ctx`, `crypto_skcipher`, `p8_aes_ctr_ctx`, `p8_aes_ctr_ctx`, `skcipher_walk`, `crypto_skcipher`, `skcipher_walk`, and 2 more; functions `p8_aes_ctr_init`, `p8_aes_ctr_exit`, `p8_aes_ctr_setkey`, `p8_aes_ctr_final`, `p8_aes_ctr_crypt`. Source size is 153 lines / 3935 bytes.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `asm/simd.h`, `asm/switch_to.h`, `crypto/aes.h`, `crypto/internal/simd.h`, `crypto/internal/skcipher.h`, `linux/err.h`, `linux/kernel.h`, `linux/module.h`, `linux/uaccess.h`, `aesp8-ppc.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_ctr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_xts.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_xts.c

Purpose: registers the Power8 VSX AES-XTS skcipher with fallback for unsupported request shapes.

Important APIs/types/functions: types `p8_aes_xts_ctx`, `crypto_skcipher`, `p8_aes_key`, `p8_aes_key`, `p8_aes_key`, `p8_aes_xts_ctx`, `crypto_skcipher`, `p8_aes_xts_ctx`, `p8_aes_xts_ctx`, `crypto_skcipher`, and 3 more; functions `p8_aes_xts_init`, `p8_aes_xts_exit`, `p8_aes_xts_setkey`, `p8_aes_xts_crypt`, `p8_aes_xts_encrypt`, `p8_aes_xts_decrypt`. Source size is 166 lines / 4279 bytes.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `asm/simd.h`, `asm/switch_to.h`, `crypto/aes.h`, `crypto/internal/simd.h`, `crypto/internal/skcipher.h`, `crypto/xts.h`, `linux/err.h`, `linux/kernel.h`, `linux/module.h`, `linux/uaccess.h`, `aesp8-ppc.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aes_xts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp10-ppc.pl -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp10-ppc.pl

Purpose: generates Power10 AES key schedule and block encrypt assembly through the ppc-xlate translator.

Important APIs/types/functions: functions `gen_block`; assembly labels/symbols `rcon`, `Lconsts`, `Lset_encrypt_key`, `Loop128`, `L192`, `Loop192`, `L256`, `Loop256`, `Ldone`, `Lenc_key_abort`, `Ldeckey`, `Ldec_key_abort`; build variables/targets `$flavour`, `$LITTLE_ENDIAN`, `$0`, `$FRAME`, `$prefix`, `$sp`, `$vrsave`, `$code.`, `$code.`. Source size is 585 lines / 15452 bytes.

Control flow is straight-line and loop-heavy assembly generated or hand written for crypto hot paths: callers enter exported symbols with pre-expanded keys/state, the code processes full blocks in vectorized loops, handles partial/tail cases where supported, and returns updated counters, hashes, or key schedules.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include register clobbering, endian mistakes, counter/hash update errors, partial-block bugs, generated assembler drift, and CPU feature mismatches. Test signals are known-answer AES/GCM/GHASH vectors, objdump symbol checks, crypto manager selftests, and stress with unaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp10-ppc.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp8-ppc.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp8-ppc.h

Purpose: declares shared Power8 AES assembly entry points and key structures for CBC/CTR/XTS glue.

Important APIs/types/functions: no exported symbols; behavior is expressed through build rules or linker script sections. Source size is 7 lines / 218 bytes.

Control flow enters through Linux crypto API setkey/encrypt/decrypt callbacks, validates request constraints, enables the relevant PowerPC vector/SPE facility only around accelerated blocks, walks scatterlists, and falls back to generic algorithms when SIMD cannot be used safely.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: `linux/types.h`, `crypto/aes.h`. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include using vector/SPE state when preemption or page faults are unsafe, fallback recursion or request-size mistakes, bad IV/tag handling, scatterlist tail bugs, and key validation gaps. Test signals are crypto selftests, tcrypt vectors, AF_ALG tests, forced !crypto_simd_usable fallback, invalid key/auth-size cases, scatterlist fragmentation, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/aesp8-ppc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/ghashp10-ppc.pl -->
# sources/distributed-fs/ceph-client/arch/powerpc/crypto/ghashp10-ppc.pl

Purpose: generates Power10 GHASH table and update assembly through the ppc-xlate translator.

Important APIs/types/functions: functions `foreach`; assembly labels/symbols `Loop`; build variables/targets `$flavour`, `$output`, `$0`, `$code`. Source size is 370 lines / 8679 bytes.

Control flow is straight-line and loop-heavy assembly generated or hand written for crypto hot paths: callers enter exported symbols with pre-expanded keys/state, the code processes full blocks in vectorized loops, handles partial/tail cases where supported, and returns updated counters, hashes, or key schedules.

State and persistence: State is per-transform key material, per-request IV/tweak/tag/hash state, and CPU vector/SPE enable state; persistent registration state lives in the crypto API until module exit.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the Linux crypto API, PowerPC CPU feature checks, vector/SPE save-restore helpers, generated assembly symbols, scatterwalk/skcipher/aead walkers, and module registration.

Risks and test signals: Risks include register clobbering, endian mistakes, counter/hash update errors, partial-block bugs, generated assembler drift, and CPU feature mismatches. Test signals are known-answer AES/GCM/GHASH vectors, objdump symbol checks, crypto manager selftests, and stress with unaligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/crypto/ghashp10-ppc.pl -->
