# subset-b-000834 research

Grouped research for SH architecture board, boot, DMA, PCI, and asm support files in the Ceph client source tree. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/setup.c -->

# sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/setup.c



Source read size: 270 lines, 5800 bytes.



Purpose: board file for the Renesas SH-X3 prototype board. It registers fixed platform devices for the heartbeat LED register, SMC91x Ethernet, R8A66597 USB host, M66592 USB peripheral, and GPIO-key baseboard buttons.

Important APIs/types/functions: `x3proto_devices_setup()`, `x3proto_init_irq()`, `x3proto_setup()`, the `mv_x3proto` machine vector, platform-device/resource tables, `smc91x_platdata`, `r8a66597_platdata`, `m66592_platdata`, and `gpio_keys_platform_data`.

Control flow: the machine vector setup registers SH-X3 SMP operations; the device initcall switches INTC pins to IRL mode, enables level mode in ICR0, initializes baseboard GPIOs, assigns dynamic GPIO numbers to the key table, maps ILSEL sources for LAN/USB interrupts, then calls `platform_add_devices()`.

State and persistence: device/resource tables are static kernel state; ILSEL allocations and GPIO base numbers become boot-time hardware routing state; no persistent storage is touched.

Dependencies and integration points: depends on X3Proto GPIO/ILSEL machine headers, SH interrupt pin setup, platform bus, SMC91x, Renesas USB host/peripheral drivers, gpio-keys, and SH-X3 SMP operations.

Risks and test signals: hard-coded physical addresses and ILSEL IDs must match the board wiring; interrupt polarity for USB host is low-triggered; button GPIO numbering depends on `x3proto_gpio_chip.base`. Test by booting the board, checking platform-device creation, LAN/USB interrupts, GPIO keys, heartbeat LED, and SMP bring-up.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-x3proto/setup.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/of-generic.c -->

# sources/distributed-fs/ceph-client/arch/sh/boards/of-generic.c



Source read size: 174 lines, 3562 bytes.



Purpose: generic SH board support for booting from a flattened device tree instead of a board-specific machine vector.

Important APIs/types/functions: `sh_of_generic_mv`, `sh_of_setup()`, `sh_of_smp_probe()`, dummy SMP callbacks, `sh_of_mem_reserve()`, `sh_of_init_irq()`, `sh_of_clk_init()`, weak `arch_init_clk_ops()` and `plat_irq_setup()` fallbacks, and `__cpu_method_of_table` matching.

Control flow: early memory reservation reserves the FDT and `/reserved-memory`; setup reads the root `model`, scans CPU nodes, selects SMP operations from `enable-method`, or installs dummy SMP operations; interrupt setup delegates to `irqchip_init()` and common-clock setup optionally calls `of_clk_init()`.

State and persistence: mutates `sh_mv.mv_name`, CPU possible/present masks and logical maps, and reserved-memory state. It has no disk persistence.

Dependencies and integration points: integrates Open Firmware parsing, irqchip drivers, clock providers, SH machine vectors, SMP registration, RTC/clock hooks, and DT CPU enable-method tables.

Risks and test signals: missing or mismatched `enable-method` silently falls back to dummy SMP; the IRQ demux is a temporary identity function; common clock probing is compiled but disabled pending framework migration. Test with DT boot logs, reserved-memory nodes, CPU hotplug/SMP, irqchip interrupts, and clock provider probing.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/of-generic.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/boot/Makefile



Source read size: 115 lines, 3344 bytes.



Purpose: top-level SH boot-image build rules for compressed `zImage`, ROM images, raw and compressed `vmlinux.bin`, Motorola S-records, and U-Boot `uImage` variants.

Important APIs/types/functions: Kbuild targets `zImage`, `romImage`, `uImage`, `vmlinux.bin.*`, exported address variables `KERNEL_MEMORY`, `KERNEL_LOAD`, `KERNEL_ENTRY`, and compression suffix selection from `CONFIG_KERNEL_*`.

Control flow: Kbuild builds `compressed/vmlinux`, objcopies it to `zImage`, optionally wraps it as `romImage`, derives binary/compressed payloads from `vmlinux`, then creates U-Boot images with load/entry addresses computed from page, memory, and zero-page offsets.

State and persistence: generated boot artifacts are build outputs; the Makefile only exports address/config variables to subdirectories.

Dependencies and integration points: depends on Kbuild `if_changed`, objcopy, gzip/bzip2/lzma/xz/lzo helpers, mkimage/uimage rules, and `arch/sh/boot/compressed` plus `romimage` subbuilds.

Risks and test signals: wrong load or entry calculations produce unbootable images; dummy defaults can mask missing config values. Test by building every configured compression format, checking `uImage` headers, objdumping load addresses, and booting zImage/romImage on target hardware or emulator.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/Makefile



Source read size: 57 lines, 1708 bytes.



Purpose: builds the self-extracting SH compressed kernel loader and binary payload object.

Important APIs/types/functions: object list `head_32.o`, `misc.o`, `piggy.o`, compiler libgcc helper wrappers, `IMAGE_OFFSET`, `LDFLAGS_vmlinux`, compression-specific `*_with_size` rules, and binary `piggy.o` linker conversion.

Control flow: computes the loader link address differently for 32-bit and 64-bit SH, links the startup/decompressor/libgcc stubs at `startup`, objcopies to binary, compresses with the selected algorithm, and links the compressed payload through `vmlinux.scr` as `piggy.o`.

State and persistence: produces build artifacts only; it removes mcount profiling and branch profiling to keep the loader minimal.

Dependencies and integration points: depends on kernel linker script, Kbuild compression helpers, `CONFIG_MEMORY_START`, `CONFIG_BOOT_LINK_OFFSET`, `CONFIG_PAGE_OFFSET`, and helper routines included from `arch/sh/lib` and `lib/` decompressors.

Risks and test signals: address arithmetic, profiling instrumentation, or missing helper stubs can break early boot before diagnostics. Test each compression format and inspect that `.empty_zero_page` is removed from the compressed image.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashiftrt.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashiftrt.S



Source read size: 2 lines, 76 bytes.



Purpose: tiny compressed-loader wrapper that includes the SH assembly helper `ashiftrt` from `arch/sh/lib` so the standalone decompressor can satisfy compiler-generated shift operations.

Important APIs/types/functions: the included helper provides the runtime symbol normally supplied by `arch/sh/lib/ashiftrt.S`; this wrapper exports no additional code of its own.

Control flow: Kbuild compiles the wrapper into the compressed image; any decompressor C code that emits the corresponding shift helper call resolves to the included assembly routine.

State and persistence: no local state; only executable helper text is linked into the transient boot loader.

Dependencies and integration points: depends on the relative include path to `arch/sh/lib`, the compressed loader object list, and compiler code-generation for arithmetic shifts.

Risks and test signals: missing helper inclusion causes link failures or early decompressor crashes on helper calls. Test by building compressed kernels with compiler options that emit libgcc-style shifts.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashiftrt.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashldi3.c -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashldi3.c



Source read size: 2 lines, 82 bytes.



Purpose: compressed-loader wrapper for the 64-bit arithmetic left-shift helper normally provided by SH libgcc/kernel support.

Important APIs/types/functions: includes `arch/sh/lib/ashldi3.c`, providing the `__ashldi3`-style helper needed by 32-bit builds that manipulate 64-bit values in early decompression code.

Control flow: the helper is compiled into the standalone compressed image and is invoked only if generated C code needs a 64-bit left shift.

State and persistence: stateless arithmetic helper text only.

Dependencies and integration points: depends on the shared SH helper implementation and compressed Kbuild object list.

Risks and test signals: wrong include path or ABI mismatch breaks the boot-loader link. Test by building 32-bit compressed kernels with decompressor algorithms using 64-bit arithmetic.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashldi3.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashlsi3.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashlsi3.S



Source read size: 2 lines, 75 bytes.



Purpose: tiny compressed-loader wrapper that includes the SH assembly helper `ashlsi3` from `arch/sh/lib` so the standalone decompressor can satisfy compiler-generated shift operations.

Important APIs/types/functions: the included helper provides the runtime symbol normally supplied by `arch/sh/lib/ashlsi3.S`; this wrapper exports no additional code of its own.

Control flow: Kbuild compiles the wrapper into the compressed image; any decompressor C code that emits the corresponding shift helper call resolves to the included assembly routine.

State and persistence: no local state; only executable helper text is linked into the transient boot loader.

Dependencies and integration points: depends on the relative include path to `arch/sh/lib`, the compressed loader object list, and compiler code-generation for arithmetic shifts.

Risks and test signals: missing helper inclusion causes link failures or early decompressor crashes on helper calls. Test by building compressed kernels with compiler options that emit libgcc-style shifts.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashlsi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashrsi3.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashrsi3.S



Source read size: 2 lines, 75 bytes.



Purpose: tiny compressed-loader wrapper that includes the SH assembly helper `ashrsi3` from `arch/sh/lib` so the standalone decompressor can satisfy compiler-generated shift operations.

Important APIs/types/functions: the included helper provides the runtime symbol normally supplied by `arch/sh/lib/ashrsi3.S`; this wrapper exports no additional code of its own.

Control flow: Kbuild compiles the wrapper into the compressed image; any decompressor C code that emits the corresponding shift helper call resolves to the included assembly routine.

State and persistence: no local state; only executable helper text is linked into the transient boot loader.

Dependencies and integration points: depends on the relative include path to `arch/sh/lib`, the compressed loader object list, and compiler code-generation for arithmetic shifts.

Risks and test signals: missing helper inclusion causes link failures or early decompressor crashes on helper calls. Test by building compressed kernels with compiler options that emit libgcc-style shifts.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/ashrsi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_32.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_32.S



Source read size: 126 lines, 2430 bytes.



Purpose: 32-bit SH compressed-kernel entry code. It establishes the initial status register, relocates the loader if needed, clears BSS, calls the C decompressor, and jumps to the decompressed kernel.

Important APIs/types/functions: global `startup`, labels `clear_bss`, `stack_start`, `decompress_kernel`, `___pa(_text + PAGE_SIZE)`, cache writeback via `ocbwb`, and the fake bzImage header block.

Control flow: set privileged SR, compare current and linked addresses, copy the loader backward in cache-line chunks when relocated, clear BSS, load the bootstrap stack, call `decompress_kernel()`, then jump to the physical or linked kernel start depending on 32-bit mode.

State and persistence: mutates CPU SR, stack pointer, BSS, and instruction/data cache state; no persistent data beyond boot memory layout.

Dependencies and integration points: coupled to `vmlinux.lds`, `misc.c`, SH cache instructions, kexec zImage parsing magic, page constants, and the compressed payload object.

Risks and test signals: relocation overlap, cache writeback, SR masking, and kernel-start physical translation are fragile. Test with relocated and non-relocated zImage loads, kexec parsing, SH4 cache-enabled systems, and all compression formats.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_32.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_64.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_64.S



Source read size: 159 lines, 4021 bytes.



Purpose: SHmedia/SH-5 compressed-kernel startup code that installs fixed TLB mappings, enables caches and MMU, runs decompression, disables MMU, and branches to the decompressed image.

Important APIs/types/functions: global `startup`, fixed ITLB/DTLB constants, ICCR/OCCR cache register setup, `decompress_kernel`, `stack_start`, and target branch to `CONFIG_MEMORY_START + 0x2000`.

Control flow: clears branch target registers to avoid speculative device fetches, invalidates ITLB/DTLB entries, creates 512 MiB cached mappings, enables instruction and operand caches, enters MMU mode through SSR/SPC/RTE, clears BSS, calls decompression, disables MMU, then jumps to the kernel.

State and persistence: initializes TLB, cache controller registers, SR/MMU state, stack, and BSS. These are transient boot states before the main kernel takes over.

Dependencies and integration points: depends on SHmedia cache/TLB/register definitions, memory-start config, linker labels, and the C decompressor.

Risks and test signals: early TLB/cache register errors can hang before console output; the final entry address is hard-coded relative to memory start. Test on SHmedia configurations with cache/TLB tracing or emulator support.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/head_64.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/lshrsi3.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/lshrsi3.S



Source read size: 2 lines, 75 bytes.



Purpose: tiny compressed-loader wrapper that includes the SH assembly helper `lshrsi3` from `arch/sh/lib` so the standalone decompressor can satisfy compiler-generated shift operations.

Important APIs/types/functions: the included helper provides the runtime symbol normally supplied by `arch/sh/lib/lshrsi3.S`; this wrapper exports no additional code of its own.

Control flow: Kbuild compiles the wrapper into the compressed image; any decompressor C code that emits the corresponding shift helper call resolves to the included assembly routine.

State and persistence: no local state; only executable helper text is linked into the transient boot loader.

Dependencies and integration points: depends on the relative include path to `arch/sh/lib`, the compressed loader object list, and compiler code-generation for arithmetic shifts.

Risks and test signals: missing helper inclusion causes link failures or early decompressor crashes on helper calls. Test by building compressed kernels with compiler options that emit libgcc-style shifts.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/lshrsi3.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.c -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.c



Source read size: 141 lines, 2710 bytes.



Purpose: minimal C decompressor runtime for SH zImage, including tiny libc routines, stack protector hooks, ftrace stubs, heap setup, and selected compression backends.

Important APIs/types/functions: `decompress_kernel()`, `puts()`, local `memset()`/`memcpy()`, `error()`, `__stack_chk_guard`, `__stack_chk_fail()`, `ftrace_stub()`, `arch_ftrace_ops_list_func()`, `input_data`, `input_len`, and `__decompress()`.

Control flow: `decompress_kernel()` computes the output address at `_text + PAGE_SIZE`, applies P2 segment mapping for 29-bit mode, sets a small or bzip2-sized heap after `_end`, invokes the selected decompressor, and returns to assembly to jump into the kernel.

State and persistence: owns transient boot heap pointers, output pointer, and bootstrap stack array; on error it loops forever after optional messages.

Dependencies and integration points: includes decompressor source files directly from `lib/`, uses `__pa`, segment helpers, linker symbols, and is called by `head_32.S`/`head_64.S`.

Risks and test signals: no real console output is implemented; heap sizing must satisfy decompressor requirements; wrong 29-bit address conversion corrupts output. Test every compression algorithm, stack protector builds, and 29-bit versus full-address configs.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.h -->

# sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.h



Source read size: 9 lines, 183 bytes.



Purpose: local declarations shared by compressed-loader assembly/C code.

Important APIs/types/functions: declares `decompress_kernel()`, `ftrace_stub()`, and `arch_ftrace_ops_list_func()`.

Control flow: no runtime flow; it provides prototypes so the loader links cleanly when generic linker scripts or instrumentation references ftrace symbols.

State and persistence: none.

Dependencies and integration points: used by `misc.c` and the compressed boot link; shields the early loader from full kernel headers.

Risks and test signals: missing prototypes or ftrace stubs can cause early boot link failures. Test by building compressed kernels with and without ftrace/profile options.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/compressed/misc.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/dts/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/boot/dts/Makefile



Source read size: 2 lines, 117 bytes.



Purpose: Kbuild hook for built-in SH device-tree blobs.

Important APIs/types/functions: `obj-$(CONFIG_BUILTIN_DTB)` adds `$(CONFIG_BUILTIN_DTB_NAME).dtb.o` to the boot build.

Control flow: when built-in DTB support is enabled, Kbuild converts the named DTB into an object and links it into the kernel image.

State and persistence: generated DTB object becomes immutable boot-time firmware data embedded in the image.

Dependencies and integration points: depends on `CONFIG_BUILTIN_DTB` and `CONFIG_BUILTIN_DTB_NAME`, DTS build rules, and SH DT boot support.

Risks and test signals: an incorrect name silently selects the wrong or missing DTB object. Test built-in DTB boot and compare `/proc/device-tree/model` with the expected board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/dts/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/romimage/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/boot/romimage/Makefile



Source read size: 30 lines, 902 bytes.



Purpose: builds SH `romImage` artifacts suitable for flash/MMC boot by combining early ROM setup, zero-page contents, optional MMCIF loader, and the existing zImage.

Important APIs/types/functions: targets `vmlinux`, `zeropage.bin`, `piggy.o`, load address selection, `CONFIG_ROMIMAGE_MMCIF`, and SH7724 ILRAM load address `0xe5200000`.

Control flow: links `head.o`, optional board loader object, and a binary payload built from `.empty_zero_page` plus `arch/sh/boot/zImage`; objcopy extracts the zero page for the embedded payload.

State and persistence: produces ROM boot artifacts only; load address selection determines where the temporary loader executes.

Dependencies and integration points: depends on Kbuild binary linker rules, the SH kernel linker script, `mach/romimage.h`, optional SH7724 MMCIF boot helper, and the zImage target.

Risks and test signals: incorrect load address or zero-page extraction breaks ROM boot. Test by building `CONFIG_ROMIMAGE_MMCIF`, checking `romstart` entry, and booting from flash or MMC at the documented sector offset.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/romimage/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/romimage/head.S -->

# sources/distributed-fs/ceph-client/arch/sh/boot/romimage/head.S



Source read size: 85 lines, 1637 bytes.



Purpose: ROM-image entry trampoline that performs board-specific setup, optionally loads the image from MMCIF, copies the zero page to the kernel's expected location, and jumps to zImage.

Important APIs/types/functions: global `romstart`, included `mach/romimage.h`, optional `mmcif_loader`, labels `loaded_code`, `empty_zero_page_dst`, `extra_data_pos`, and `zero_page_pos` from the linked payload.

Control flow: run board setup, optionally call the MMCIF loader with destination above the zero page and jump into the loaded code, copy one page of zero-page data in 16-byte chunks to `_text`, then branch to the zImage positioned after the zero-page payload.

State and persistence: manipulates early registers, stack pointer during MMCIF load, and the in-memory zero page; no runtime state persists after kernel entry.

Dependencies and integration points: coupled to `romimage/Makefile`, `mach/romimage.h`, page constants, and optional SH7724 MMCIF loader.

Risks and test signals: payload offset math and zero-page copy order are boot-critical. Test ROM boot with and without MMCIF, verify zero-page contents, and check board-specific setup code paths.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/romimage/head.S -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/romimage/mmcif-sh7724.c -->

# sources/distributed-fs/ceph-client/arch/sh/boot/romimage/mmcif-sh7724.c



Source read size: 78 lines, 2086 bytes.



Purpose: SH7724-specific MMCIF boot loader used by ROM images to fetch the zImage payload from an MMC card.

Important APIs/types/functions: `mmcif_loader()`, `mmcif_update_progress()`, `sh_mmcif_boot_init()`, `sh_mmcif_boot_do_read()`, register constants for MSTPCR2, pin control, Hi-Z, drive strength, and `MMCIF_BASE`.

Control flow: reports progress, enables the MMCIF clock, configures D0-D7/CLK/CMD pinmux and drive state, initializes the MMCIF block, reads blocks starting at sector 512 into the caller-provided buffer, disables the clock, and reports completion.

State and persistence: mutates SoC clock, pinmux, drive-strength, and MMCIF controller registers during the boot phase only.

Dependencies and integration points: depends on SH7724 `mach/romimage.h`, platform MMCIF boot helpers, raw MMIO accessors, and the ROM image layout documented by the `dd ... seek=512` comment.

Risks and test signals: hard-coded sector 512, pinmux values, and clock register bits must match the boot medium and board wiring. Test with an MMC image at the documented offset, progress hooks, and failed-card timeout scenarios.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boot/romimage/mmcif-sh7724.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/cchips/Kconfig -->

# sources/distributed-fs/ceph-client/arch/sh/cchips/Kconfig



Source read size: 46 lines, 1041 bytes.



Purpose: Kconfig menu for SuperH companion chips, currently the Hitachi HD6446x/HD64461 family and its IRQ/PCMCIA options.

Important APIs/types/functions: symbols `HD6446X_SERIES`, `HD64461`, `HD64461_IRQ`, and `HD64461_ENABLER`.

Control flow: enabling a board that selects HD6446x exposes the HD64461 choice; users can configure the parent IRQ number and optional PCMCIA enabler.

State and persistence: compile-time configuration only; selected symbols control which driver code and constants enter the kernel.

Dependencies and integration points: feeds `hd6446x/Makefile`, `hd64461.c`, IRQ descriptor setup, and PCMCIA board behavior.

Risks and test signals: wrong IRQ configuration prevents child interrupt demux; enabling PCMCIA on unsupported wiring can clear wrong status. Test Kconfig dependencies and boot with configured parent IRQ.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/cchips/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/Makefile



Source read size: 4 lines, 97 bytes.



Purpose: builds HD64461 companion-chip support when selected.

Important APIs/types/functions: `obj-$(CONFIG_HD64461) += hd64461.o` and `ccflags-y := -Werror`.

Control flow: Kbuild includes `hd64461.o` only for HD64461-enabled configurations and treats warnings in this directory as errors.

State and persistence: build-time object selection only.

Dependencies and integration points: tied to the companion-chip Kconfig and generic SH driver build.

Risks and test signals: `-Werror` can turn compiler-version warning drift into build failures. Test HD64461 and non-HD64461 configs.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/hd64461.c -->

# sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/hd64461.c



Source read size: 112 lines, 2669 bytes.



Purpose: interrupt-controller support for the Hitachi HD64461 companion chip, including optional PCMCIA interrupt clearing.

Important APIs/types/functions: `setup_hd64461()`, `hd64461_irq_demux()`, mask/unmask/mask_ack callbacks, `hd64461_irq_chip`, `irq_alloc_descs()`, `irq_set_chip_and_handler()`, and `irq_set_chained_handler()`.

Control flow: module init masks HD64461 interrupts, allocates 16 Linux IRQ descriptors at `HD64461_IRQBASE`, installs level handlers, chains the configured parent IRQ to the demuxer, sets parent trigger low-level, and optionally enables PCMCIA status interrupts. The demuxer reads NIRR and dispatches each asserted child bit through `generic_handle_irq()`.

State and persistence: chip mask registers, IRQ descriptors, chained parent handler, and optional PCMCIA control status remain active for the booted kernel.

Dependencies and integration points: depends on `asm/hd64461.h`, SH7709 interrupt control for one CPU subtype, generic IRQ core, and optional HD64461 PCMCIA enabler.

Risks and test signals: fixed IRQ base/parent values are board-specific; mask/ack ordering can lose level interrupts; PCMCIA clear only handles IRQ 13. Test by triggering each child IRQ, PCMCIA events, and booting SH7709 companion-chip boards.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/cchips/hd6446x/hd64461.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/Kconfig -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/Kconfig



Source read size: 20 lines, 583 bytes.



Purpose: SH-specific driver Kconfig aggregation for DMA, companion chips, heartbeat LEDs, and push-switch framework.

Important APIs/types/functions: sources `arch/sh/drivers/dma/Kconfig` and `arch/sh/cchips/Kconfig`; defines `HEARTBEAT` and `PUSH_SWITCH`.

Control flow: selected symbols determine whether SH-specific platform drivers and legacy DMA support are compiled.

State and persistence: build-time configuration only.

Dependencies and integration points: feeds `arch/sh/drivers/Makefile`, board platform devices, and optional modules.

Risks and test signals: selecting old SH drivers without matching board platform data gives dead devices or build-only coverage. Test defconfigs using heartbeat and push-switch.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/Makefile



Source read size: 10 lines, 240 bytes.



Purpose: top-level SH driver object selection.

Important APIs/types/functions: always builds `dma/` and `platform_early.o`; conditionally builds `pci/`, `push-switch.o`, and `heartbeat.o`.

Control flow: Kbuild descends into driver subdirectories according to architecture and feature symbols.

State and persistence: build graph only.

Dependencies and integration points: integrates Kconfig symbols with SH platform, PCI, DMA, and board support code.

Risks and test signals: unconditional `dma/` directory descent still relies on subdirectory symbols. Test SH allnoconfig/defconfig/allmodconfig builds.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Kconfig -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Kconfig



Source read size: 76 lines, 2290 bytes.



Purpose: legacy SH DMA Kconfig menu covering on-chip DMAC, channel counts, API-vs-DMAengine selection, SH7760 DMABRG, Dreamcast PVR2, and G2 DMA.

Important APIs/types/functions: `SH_DMA`, `SH_DMA_IRQ_MULTI`, `SH_DMA_API`, `NR_ONCHIP_DMA_CHANNELS`, `SH_DMABRG`, `PVR2_DMA`, and `G2_DMA`.

Control flow: CPU subtype selects default channel counts and IRQ layout; `SH_DMA_API` enables legacy API users while warning against simultaneous DMAengine use.

State and persistence: compile-time feature matrix only.

Dependencies and integration points: drives `dma/Makefile`, CPU-specific DMAC register definitions, Dreamcast support, and SH7760 audio/USB DMA.

Risks and test signals: wrong channel count or IRQ-multi setting corrupts DMAC indexing; enabling legacy API with DMAengine can conflict. Test representative CPU subtype builds and DMA transfer smoke tests.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Kconfig -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Makefile



Source read size: 9 lines, 286 bytes.



Purpose: Kbuild selection for legacy SH DMA provider objects.

Important APIs/types/functions: builds `dma-sh.o`, `dma-api.o`, `dma-sysfs.o` for `SH_DMA_API`, plus optional `dma-pvr2.o`, `dma-g2.o`, and `dmabrg.o`.

Control flow: object inclusion follows Kconfig symbols for on-chip DMAC, Dreamcast peripherals, and SH7760 bridge DMA.

State and persistence: build graph only.

Dependencies and integration points: connects the legacy DMA API header contracts to controller implementations.

Risks and test signals: provider objects depend on CPU/board headers that may only exist for matching configs. Test enabled and disabled combinations.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-api.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-api.c



Source read size: 274 lines, 6103 bytes.



Purpose: legacy SuperH DMA management API that registers DMAC providers, exposes virtual channels, handles request/free/configure/transfer/wait, and publishes `/proc/dma`.

Important APIs/types/functions: `register_dmac()`, `unregister_dmac()`, `request_dma()`, `free_dma()`, `dma_xfer()`, `dma_wait_for_completion()`, `get_dma_info()`, `get_dma_channel()`, `get_dma_residue()`, `dma_configure_channel()`, `registered_dmac_list`, and `dma_spin_lock`.

Control flow: DMAC drivers register `struct dma_info`; registration allocates or accepts channel tables, assigns virtual channel numbers, initializes waitqueues/sysfs entries, and adds the controller to a global list. Clients request a channel atomically, configure optional CHCR flags, start a transfer through provider ops, then wait by TEI waitqueue or polling residue.

State and persistence: in-memory global list of controllers, per-channel busy flags, device IDs, waitqueues, mode/address/count fields, proc and sysfs exposure. No disk persistence.

Dependencies and integration points: integrates SH on-chip, Dreamcast G2/PVR2, and DMABRG-era DMA users with platform devices, procfs, sysfs, waitqueues, and provider-specific MMIO drivers.

Risks and test signals: callers assume valid channels before dereferencing; global list traversal is not visibly locked; sysfs `dev_id` store uses `strcpy`; legacy API conflicts with DMAengine if both are enabled. Test request/free races, invalid channels, TEI wakeups, proc/sysfs output, and module unload of registered DMACs.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-api.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-g2.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-g2.c



Source read size: 197 lines, 4649 bytes.



Purpose: Sega Dreamcast G2 bus DMA provider for the legacy SH DMA API.

Important APIs/types/functions: packed/aligned `g2_channel`, `g2_status`, `g2_dma_info`, `g2_xfer_dma()`, `g2_dma_interrupt()`, `g2_get_residue()`, and `g2_dma_init()`.

Control flow: init requests the G2 DMA hardware event, writes wait-state/magic values, and registers four TEI-capable channels. Transfer validates 32-byte source/destination alignment, rounds size, maps destination into the G2 address window, flips direction semantics, flushes cache, programs the channel/status registers, and enables transfer. Interrupt checks completion status and wakes the channel waitqueue.

State and persistence: hardware DMA descriptor/status area at `0xa05f7800`, channel waitqueues, and registered DMA channel state persist while loaded.

Dependencies and integration points: depends on Dreamcast `sysasic` event IDs, `mach/dma.h`, SH cacheflush, and legacy DMA API.

Risks and test signals: undocumented control bits and magic values are hardware-sensitive; unaligned buffers are rejected; cache flush uses source/count assumptions. Test with G2 peripherals, aligned/unaligned transfers, IRQ completion, and residue polling.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-g2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-pvr2.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-pvr2.c



Source read size: 102 lines, 2272 bytes.



Purpose: Dreamcast NEC PowerVR2 DMA provider layered on the on-chip DMAC cascade channel.

Important APIs/types/functions: `pvr2_dma_interrupt()`, `pvr2_request_dma()`, `pvr2_xfer_dma()`, `pvr2_get_dma_residue()`, `pvr2_dma_info`, and cascade channel `PVR2_CASCADE_CHAN`.

Control flow: init requests the PVR2 DMA event, reserves the cascade channel, and registers one TEI-capable channel. Request rejects busy PVR2 mode. Transfer requires no source and a valid destination, resets completion state, and writes PVR2 address/count/mode. Interrupt waits for the SH DMAC cascade residue to drain, marks completion, and wakes waiters via residue semantics.

State and persistence: global `xfer_complete`, debug interrupt counter, PVR2 DMA MMIO registers, and reserved cascade DMA channel.

Dependencies and integration points: depends on Dreamcast hardware event definitions, PVR2 register macros, SH on-chip DMAC, and the legacy DMA API.

Risks and test signals: completion is a global flag for a single channel; cascade failures can stall in interrupt context waiting for completion. Test framebuffer DMA paths, busy-mode rejection, cascade residue behavior, and module unload cleanup.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-pvr2.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sh.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sh.c



Source read size: 425 lines, 9253 bytes.



Purpose: legacy SH on-chip DMAC provider implementing channel programming, transfer-end interrupts, residue calculation, DMAOR reset, and address-error handling.

Important APIs/types/functions: `sh_dmac_init()`, `sh_dmac_xfer_dma()`, `sh_dmac_configure_channel()`, `sh_dmac_get_dma_residue()`, `dma_tei()`, `dmaor_reset()`, `dmae_irq_init()`, register helpers `dma_base_addr()`/`dma_find_base()`, and `sh_dmac_ops`.

Control flow: init installs optional DMA error IRQs, resets one or two DMAOR blocks, and registers channels. Request installs per-channel TEI IRQs. Transfers configure defaults if needed, disable the channel, write SAR/DAR only when safe for the channel mode, program TCR based on transmit-size shift, then enable DE/IE. TEI IRQ clears TE/DE/IE and wakes waiters; error IRQ resets DMAOR and disables the error IRQ.

State and persistence: DMAC CHCR/SAR/DAR/TCR/DMAOR registers, IRQ registrations, channel flags, and waitqueues persist during runtime.

Dependencies and integration points: depends on CPU-specific `dma-register.h`, Dreamcast cascade quirks, SH interrupt numbering, legacy DMA API, and 29-bit/SoC-specific DMAC topology.

Risks and test signals: single-address mode can fault if SAR/DAR are written incorrectly; transmit-size shift table must match CHCR encoding; shared/multi IRQ mapping varies by CPU subtype. Test memory-to-memory and peripheral DMA modes, TEI wait, error IRQ recovery, Dreamcast PVR2 cascade, and dual-DMAC SoCs.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sh.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sysfs.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sysfs.c



Source read size: 170 lines, 4296 bytes.



Purpose: sysfs exposure for the legacy SH DMA API.

Important APIs/types/functions: `dma_subsys_init()`, root `devices` attribute, per-channel `dev_id`, `config`, `mode`, `count`, `flags` attributes, `dma_create_sysfs_files()`, and `dma_remove_sysfs_files()`.

Control flow: postcore init registers a `dma` bus and root summary attribute. Each DMAC registration creates a device per channel, attaches attributes, and symlinks the channel from the provider platform device; unregister removes files, link, and device.

State and persistence: runtime sysfs devices mirror `struct dma_channel` fields. Writes to `config`, `mode`, and `dev_id` immediately mutate channel state only for the running kernel.

Dependencies and integration points: depends on platform devices from `register_dmac()`, `to_dma_channel()`, and legacy DMA API configuration callbacks.

Risks and test signals: `dev_id` writes use unbounded `strcpy`; root `devices` loops only first 16 virtual channels; partial attribute creation failures leave registered devices. Test sysfs reads/writes, invalid config values, channel removal, and large `dev_id` input.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sysfs.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dmabrg.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dmabrg.c



Source read size: 195 lines, 5287 bytes.



Purpose: SH7760 DMABRG interrupt broker for USB and audio DMA events independent of the traditional SH DMAC.

Important APIs/types/functions: `dmabrg_request_irq()`, `dmabrg_free_irq()`, `dmabrg_irq()`, `dmabrg_enable_irq()`, `dmabrg_disable_irq()`, `dmabrg_handlers`, and DMABRGCR/DMAOR/DMARSRA register programming.

Control flow: init allocates ten handler slots, reserves DMAC channel 0 when possible, enables bridge mode in DMAOR, and requests three hardware IRQ lines. The shared handler reads and acknowledges DMABRGCR, masks disabled events, dispatches USB completion/error first, then iterates audio full/half events and calls registered callbacks.

State and persistence: global handler table, DMABRG enable/status register bits, DMAC channel 0 reservation, and IRQ registrations persist after subsys init.

Dependencies and integration points: integrates SH7760 USB/audio drivers through `asm/dmabrg.h`, raw MMIO, generic IRQs, and optional legacy SH DMA reservation.

Risks and test signals: no locking around handler registration versus interrupt dispatch; calling a NULL handler would fault if an enabled event fires after free; bridge mode blocks DMAC0 use. Test USB/audio DMA interrupts, request/free races, masked events, and DMAC0 reservation conflict.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dmabrg.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/heartbeat.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/heartbeat.c



Source read size: 152 lines, 3628 bytes.



Purpose: platform driver that toggles a board LED bank as a load-average heartbeat.

Important APIs/types/functions: `heartbeat_drv_probe()`, `heartbeat_timer()`, `heartbeat_toggle_bit()`, `struct heartbeat_data`, default bit positions, and `heartbeat_driver`.

Control flow: probe validates one MMIO resource, uses platform data or allocates defaults, maps the register, derives bit mask and register width, installs a timer, and starts it. The timer toggles one LED bit, bounces between bit positions, and reschedules itself using a period based on the 5-minute load average.

State and persistence: timer state, mapped MMIO base, bit position/mask/regsize, and static scan direction persist while the driver is bound; LED register contents are hardware state.

Dependencies and integration points: depends on board platform devices, `asm/heartbeat.h`, load average accounting, timers, and raw I/O accessors.

Risks and test signals: no remove path unmaps or stops the timer; static `bit`/`up` are shared across devices; invalid platform data can target wrong bits. Test LED cadence under load, 8/16/32-bit resources, inverted mode, and platform-device binding.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/heartbeat.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/Makefile -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/Makefile



Source read size: 27 lines, 1181 bytes.



Purpose: object selection for SH PCI and PCIe host controller support plus board fixups.

Important APIs/types/functions: always builds `common.o` and `pci.o`; CPU subtype selects SH7751, SH7780/SH7763/SH7785, or SH7786 PCIe controller code; board symbols select IRQ/resource fixups.

Control flow: Kbuild links generic core plus exactly the CPU controller ops and any board-specific fixup files needed by the configured machine.

State and persistence: build-time object graph only.

Dependencies and integration points: ties CPU Kconfig, board Kconfig, PCI host bridge registration, and platform IRQ maps.

Risks and test signals: missing fixup object leaves weak/default IRQ or PCIC setup. Test every board defconfig with PCI enabled.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/Makefile -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/common.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/common.c



Source read size: 160 lines, 3926 bytes.



Purpose: shared SH PCI helper code for early config access, 66 MHz capability probing, error timers, and PCI status error handling.

Important APIs/types/functions: `early_read/write_config_{byte,word,dword}()`, `pci_is_66mhz_capable()`, `pcibios_enable_timers()`, `pcibios_handle_status_errors()`, and fake `pci_dev`/`pci_bus` construction.

Control flow: early helpers synthesize a minimal bus/device around a `pci_channel` before enumeration; capability probing scans bus device functions; error handlers report and clear PCI status bits and temporarily disable noisy IRQs via timers.

State and persistence: static fake objects are reused only during early calls; per-controller error timers and IRQ numbers persist in `pci_channel`.

Dependencies and integration points: used by SH7751/SH7780 setup and generic `pcibios_report_status`; depends on Linux PCI config accessors, timers, and interrupt APIs.

Risks and test signals: fake static objects are not reentrant; error IRQ backoff must re-enable reliably. Test early config reads before bus scan, 66 MHz-capable devices, parity/master/target abort injection, and timer re-enable.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/common.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-dreamcast.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-dreamcast.c



Source read size: 84 lines, 2413 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `dreamcast` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `dreamcast`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-dreamcast.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-landisk.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-landisk.c



Source read size: 57 lines, 1457 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `landisk` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `landisk`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-landisk.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-r7780rp.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-r7780rp.c



Source read size: 18 lines, 414 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `r7780rp` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `r7780rp`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-r7780rp.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-rts7751r2d.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-rts7751r2d.c



Source read size: 64 lines, 1604 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `rts7751r2d` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `rts7751r2d`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-rts7751r2d.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sdk7780.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sdk7780.c



Source read size: 40 lines, 1124 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `sdk7780` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `sdk7780`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sdk7780.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sdk7786.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sdk7786.c



Source read size: 64 lines, 1621 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `sdk7786` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `sdk7786`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sdk7786.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-se7751.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-se7751.c



Source read size: 113 lines, 4216 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `se7751` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `se7751`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-se7751.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sh03.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sh03.c



Source read size: 33 lines, 855 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `sh03` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `sh03`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-sh03.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-snapgear.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-snapgear.c



Source read size: 37 lines, 1002 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `snapgear` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `snapgear`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-snapgear.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-titan.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-titan.c



Source read size: 36 lines, 821 bytes.



Purpose: board-specific SH PCI fixup and IRQ-routing code for `titan` platforms.

Important APIs/types/functions: `pcibios_map_platform_irq()` is the common hook; some boards also override `pci_fixup_pcic()` to program SH7751 PCIC/BSC timing, local address registers, interrupt masks, and config BARs.

Control flow: generic PCI enumeration calls the IRQ mapper for each device slot/pin. Boards with `pci_fixup_pcic()` run during controller initialization to mirror memory-controller settings and set PCI local/memory/I/O windows before bus scan.

State and persistence: IRQ mapping tables, PCIC control registers, memory-controller mirror values, and optional resource/DMA coherent-memory fixups persist after boot.

Dependencies and integration points: selected by the board Kconfig object for `titan`, integrates with `pci-sh4.h`, machine IRQ constants or `evt2irq()`, and the generic SH PCI core.

Risks and test signals: fixed slot/pin tables can return -1 or wrong IRQs; PCIC register magic is board timing-specific; Dreamcast additionally fixes a nonstandard BAR/DMA window. Test PCI interrupt delivery for each slot, boot-time PCIC setup, and resource assignment on the configured board.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/fixups-titan.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-dreamcast.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-dreamcast.c



Source read size: 79 lines, 2501 bytes.



Purpose: PCI config-space operations for the Dreamcast GAPSPCI bridge and Broadband Adapter.

Important APIs/types/functions: `gapspci_pci_ops`, `gapspci_read()`, `gapspci_write()`, and `gapspci_config_access()`.

Control flow: accepts only bus 0/devfn 0, reads or writes byte/word/dword config values directly through GAPSPCI BBA config I/O offsets, and returns device-not-found for all other targets.

State and persistence: no local state; all effects are GAPSPCI config-space I/O.

Dependencies and integration points: used by `pci-dreamcast.c` host controller registration and Dreamcast PCI fixups.

Risks and test signals: assumes a single device and no type-1 config cycles; accidental extra devfn access is hidden as not found. Test BBA enumeration and config read/write sizes.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-dreamcast.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh4.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh4.c



Source read size: 105 lines, 2385 bytes.



Purpose: generic SH4/SH4A PCI configuration-space access for SH7751 and SH7780-family PCIC controllers.

Important APIs/types/functions: `sh4_pci_ops`, `sh4_pci_read()`, `sh4_pci_write()`, `CONFIG_CMD()`, global `pci_config_lock`, and weak `pci_fixup_pcic()`.

Control flow: read writes PCIPAR with type-1 config address, reads PCIPDR under raw spinlock, then extracts byte/word/dword fields. Write performs a read-modify-write for sub-dword sizes because PCIPDR only supports 32-bit accesses.

State and persistence: serializes hardware config access through `pci_config_lock`; writes mutate device/controller PCI config space.

Dependencies and integration points: used by SH7751/SH7780 host setup, board `pci_fixup_pcic()` overrides, and generic PCI enumeration.

Risks and test signals: unaligned subword writes rely on correct endian/shift math; weak fixup must be replaced on boards requiring PCIC setup. Test config byte/word/dword accesses and board-specific fixups.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh4.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh7786.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh7786.c



Source read size: 168 lines, 4623 bytes.



Purpose: PCIe configuration-space operations for SH7786 root-complex ports.

Important APIs/types/functions: `sh7786_pci_ops`, `sh7786_pcie_config_access()`, `sh7786_pcie_read()`, `sh7786_pcie_write()`, root-bus self-enumeration handling, and SH4A PCIEPAR/PCTLR/PDR/ERRFR registers.

Control flow: validates bus/dev/function/offset, handles root bus devfn 0 through direct controller config registers, otherwise clears errors, programs PIO address/type, enables config access, checks completer/master/target aborts, transfers data, and disables access. Public read/write wrappers serialize with `pci_config_lock` and handle byte/word extraction or merging.

State and persistence: writes mutate PCIe controller and endpoint config space; error flags are cleared per access.

Dependencies and integration points: used by `pcie-sh7786.c`, generic PCI core, SH7786 register definitions, and PCI config locking.

Risks and test signals: root-complex self-access is special-cased because normal config transactions abort; write path performs read-modify-write and must preserve other bytes. Test root port enumeration, endpoint config cycles, absent-device errors, and unaligned access rejection.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh7786.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-dreamcast.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-dreamcast.c



Source read size: 97 lines, 2339 bytes.



Purpose: initializes and registers the Dreamcast GAPSPCI host bridge for the Sega Broadband Adapter.

Important APIs/types/functions: `gapspci_init()`, `dreamcast_pci_controller`, GAPSPCI resource windows, register handshake at `GAPSPCI_REGS`, and BBA config initialization.

Control flow: verifies the bridge ID string, performs a magic unlock/handshake, programs DMA window registers, enables the bridge and BBA config registers, then registers one PCI controller.

State and persistence: GAPSPCI bridge registers, BBA config space, resource reservations, and controller registration persist after arch init.

Dependencies and integration points: depends on Dreamcast `mach/pci.h`, `gapspci_pci_ops`, `fixups-dreamcast.c`, and SH PCI core.

Risks and test signals: undocumented magic values and busy-wait timing are hardware-specific; only the BBA is supported. Test boot with and without BBA, bridge ID mismatch, and resource fixup/DMA coherent allocation.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-dreamcast.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh4.h -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh4.h



Source read size: 182 lines, 9591 bytes.



Purpose: common SH4 PCIC register definitions, register access helpers, and controller address-map structures shared by SH7751 and SH7780-family PCI code.

Important APIs/types/functions: SH4_PCICR/PCIINT/PCIAINT/DMA/config/I/O register offsets and bit masks, `struct sh4_pci_address_space`, `struct sh4_pci_address_map`, `pci_read_reg()`, `pci_write_reg()`, `sh4_pci_ops`, and `pci_fixup_pcic()` declaration.

Control flow: no direct flow; host-controller and ops files include this header to issue raw MMIO register accesses and interpret status/error bits.

State and persistence: constants map to live PCIC hardware state; inline helpers mutate controller registers.

Dependencies and integration points: conditionally includes SH7751 or SH7780-specific headers and depends on `asm/io.h`.

Risks and test signals: common offsets must match each CPU subtype include; wrong bit masks break reset, error handling, DMA, or config access. Test SH7751/SH7780 builds and PCI enumeration/error handling.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh4.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.c



Source read size: 179 lines, 5343 bytes.



Purpose: low-level PCI host controller initialization for SH7751/SH7751R.

Important APIs/types/functions: `sh7751_pci_init()`, `__area_sdram_check()`, `sh7751_pci_controller`, `sh7751_pci_map`, `pci_fixup_pcic()`, and SH7751 BCR/WCR/MCR/PCICONF registers.

Control flow: verifies controller vendor/device ID, enables PCI access in BCR, wakes clocks, clears powerdown IRQs, sets command/class/window registers, mirrors SDRAM timing into PCIC registers, applies board fixups, marks central-function init complete, and registers the controller.

State and persistence: PCIC registers, BSC mirror registers, memory/I/O windows, and PCI controller resource state persist for runtime PCI.

Dependencies and integration points: depends on `pci-sh4.h`, SH7751 register definitions, board `pci_fixup_pcic()` implementations, and generic SH PCI core.

Risks and test signals: SDRAM area validation and one-to-one window assumptions are strict; wrong BCR/WCR values can break memory or PCI. Test SH7751 boards, resource windows, config cycles, and board fixup variants.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.h -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.h



Source read size: 126 lines, 7757 bytes.



Purpose: SH7751-specific PCI host-controller register and resource constants.

Important APIs/types/functions: vendor/device IDs, config-space base/size, memory and I/O window base/size, PCIC register base, config register offsets, memory-controller register addresses, and BAR/window mask constants.

Control flow: no runtime flow; included by `pci-sh4.h` and controller init code.

State and persistence: constants describe controller and memory-controller MMIO state programmed during PCI initialization.

Dependencies and integration points: used by `SH7751` low-level setup, SH4 config ops, and board fixup code.

Risks and test signals: address constants and masks define the PCI resource ABI for the board. Test against datasheet values, resource registration, and config access on matching CPU subtypes.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.c



Source read size: 407 lines, 11184 bytes.



Purpose: low-level PCI host controller initialization and error handling for SH7763/SH7780/SH7781/SH7785 PCIC.

Important APIs/types/functions: `sh7780_pci_init()`, `sh7780_pci_setup_irqs()`, `sh7780_pci_err_irq()`, `sh7780_pci_serr_irq()`, `sh7780_pci66_init()`, `sh7780_pci_controller`, error descriptor tables, and PCIC memory-window registers.

Control flow: enables PCIC register access, resets controller, validates Renesas ID, maps low memory through LAR/LSR windows, requests SERR/ERR IRQs, disables cache snoop windows for noncoherent DMA, programs PCI memory and I/O BAR windows, enables command bits, registers the controller, and optionally enables 66 MHz mode if all devices support it.

State and persistence: controller reset/config registers, memory/I/O windows, error IRQ timers, registered host bridge, and PCI status bits persist.

Dependencies and integration points: depends on SH4 PCI ops, generic PCI error helpers, memory_start/end, CPU 29-bit mode, `evt2irq`, and board IRQ fixups.

Risks and test signals: memory-size rounding and 29-bit resource pruning affect DMA visibility; IRQ backoff must not hide persistent errors; 66 MHz mode requires all devices capable. Test PCI enumeration, error IRQ injection, 33/66 MHz negotiation, large memory, and 29-bit mode.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.h -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.h



Source read size: 43 lines, 1652 bytes.



Purpose: SH7780-specific PCI host-controller register and resource constants.

Important APIs/types/functions: vendor/device IDs, config-space base/size, memory and I/O window base/size, PCIC register base, config register offsets, memory-controller register addresses, and BAR/window mask constants.

Control flow: no runtime flow; included by `pci-sh4.h` and controller init code.

State and persistence: constants describe controller and memory-controller MMIO state programmed during PCI initialization.

Dependencies and integration points: used by `SH7780` low-level setup, SH4 config ops, and board fixup code.

Risks and test signals: address constants and masks define the PCI resource ABI for the board. Test against datasheet values, resource registration, and config access on matching CPU subtypes.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7780.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci.c



Source read size: 302 lines, 7047 bytes.



Purpose: generic SH PCI host bridge registration, root-bus scanning, resource alignment, status reporting, and legacy I/O mapping.

Important APIs/types/functions: `register_pci_controller()`, `pcibios_scanbus()`, `pcibios_init()`, `pcibios_align_resource()`, `pcibios_report_status()`, `__pci_ioport_map()`, exported `PCIBIOS_MIN_IO` and `PCIBIOS_MIN_MEM`, `pci_config_lock`, and `pci_scan_mutex`.

Control flow: controllers register resources and are chained into a hose list; subsys init scans each hose with `pci_scan_root_bus_bridge()`, sizes/assigns bridge resources, and adds devices. Late registrations scan under a mutex. Status reporting walks either early config space or enumerated bus trees.

State and persistence: global hose list, next bus number/domain flag, initialized flag, resource reservations, bus pointers, and I/O map bases persist for runtime PCI access.

Dependencies and integration points: integrates SH `pci_channel` controllers with generic PCI core, resource trees, swizzle/map IRQ hooks, and non-generic I/O port mapping.

Risks and test signals: multiple domains require valid `io_map_base`; bus-number rollover toggles domain info; resource conflicts skip scanning. Test multi-controller systems, late controller registration, I/O port mapping, resource alignment, and error status reporting.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.c



Source read size: 607 lines, 14972 bytes.



Purpose: full SH7786 PCI Express root-complex initialization, including port discovery, clocks, PHY programming, link training, address windows, DMA offsets, and host registration.

Important APIs/types/functions: `sh7786_pcie_init()`, `sh7786_pcie_core_init()`, `sh7786_pcie_init_hw()`, `pcie_clk_init()`, `phy_init()`, `pcie_init()`, `pcie_reset()`, `phy_write_reg()`, `pci_wait_for_irq()`, `pcibios_bus_add_device()`, `pcibios_map_platform_irq()`, and the root-complex BAR fixup.

Control flow: arch init selects hardware ops, derives port count from mode pins, optionally enables a platform clock, prunes unavailable memory windows, schedules asynchronous per-port initialization, and waits for all ports. Each port sets up function/PHY clocks, writes PHY tuning registers, resets the core, configures PCIe capabilities and memory inbound windows, trains the link, sets transaction parameters, programs outbound windows for each resource, then registers the PCI controller in order.

State and persistence: global port array, port clocks, PHY state, PCIe controller config space, inbound/outbound address windows, link state, and DMA direct offsets persist for devices.

Dependencies and integration points: depends on SH7786 CPG clocks, mode pins, async init, PCI core, DMA direct mapping, `pcie-sh7786.h`, memory_start/end, and board FPGA clock/mux setup.

Risks and test signals: PHY magic constants, asynchronous port ordering, memory-window pruning, and DMA offset calculations are all hardware-sensitive; link-down ports still register for future hotplug. Test all port-count modes, endpoint/root-complex mode, link-up/down, DMA to system RAM, resource windows, and SDK7786 slot mux.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.h -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.h



Source read size: 577 lines, 25785 bytes.



Purpose: SH7786 PCI Express register map and bitfield catalog used by SH7786 PCIe config and initialization code.

Important APIs/types/functions: base addresses for the three controllers, config-space offsets, PHY command/ack bits, interrupt masks such as `MASK_INT_TX_CTRL`, inbound `PCIELAR/LAMR` windows, outbound `PCIEPAR/PAMR/PTCTLR` macros, PCIe capability register offsets, DMA register offsets, and inline `pci_read_reg()`/`pci_write_reg()`.

Control flow: no runtime control flow; macros are consumed by `ops-sh7786.c` and `pcie-sh7786.c` to program controller, PHY, MSI, DMA, link, and translation registers.

State and persistence: constants describe MMIO-backed hardware state; inline helpers perform raw 32-bit register accesses.

Dependencies and integration points: tightly coupled to the SH7786 hardware manual, PCIe root-complex driver, and SH raw I/O accessors.

Risks and test signals: any offset or bit error can corrupt PCIe training, config access, or address translation. Test by comparing register traces against datasheet values, enumerating devices on each port, and exercising memory/I/O windows.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pcie-sh7786.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/platform_early.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/platform_early.c



Source read size: 336 lines, 8899 bytes.



Purpose: SH-specific early platform driver/device framework used before the normal platform bus and full driver core are available.

Important APIs/types/functions: `sh_early_platform_driver_register()`, `sh_early_platform_add_devices()`, `sh_early_platform_driver_register_all()`, `sh_early_platform_driver_probe()`, `early_platform_cleanup()`, matching helpers, and early PM initialization.

Control flow: early drivers are registered into an initdata list, command-line parameters can prioritize and select requested IDs and copy option buffers, devices are stored through their `devres_head` list node, probe iterates requested IDs first then numeric IDs, creates `init_name` when possible, calls probe directly, and cleanup restores device list heads.

State and persistence: init-only global lists hold early drivers/devices; requested IDs and option buffers persist through early probing; cleanup erases temporary list membership.

Dependencies and integration points: integrates early console/clock/platform devices with kernel `early_param()` parsing, platform-driver ID matching, PM runtime fields, and later normal driver core handoff.

Risks and test signals: reusing `devres_head` as a list node is fragile; requested-id parsing errors can suppress probing; `init_name` allocation depends on slab availability. Test early console selection, duplicate command-line options, user-only probing, multiple IDs, and cleanup before normal platform registration.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/platform_early.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/push-switch.c -->

# sources/distributed-fs/ceph-client/arch/sh/drivers/push-switch.c



Source read size: 135 lines, 3012 bytes.



Purpose: small platform-driver framework for board push switches with debounce timer, workqueue notification, and optional sysfs name exposure.

Important APIs/types/functions: `switch_drv_probe()`, `switch_drv_remove()`, `switch_timer()`, `switch_work_handler()`, read-only `switch` attribute, `struct push_switch`, and `struct push_switch_platform_info`.

Control flow: probe allocates state, fetches the platform IRQ, requests the board-provided IRQ handler, creates the name attribute when present, initializes work and debounce timer, and stores drvdata. Timer schedules work; work clears state and emits `KOBJ_CHANGE`. Remove tears down attribute, timer, work, IRQ, and allocation.

State and persistence: per-device state, debounce timer, work item, IRQ registration, and sysfs attribute persist while bound.

Dependencies and integration points: depends on board-supplied platform data and IRQ handler, platform bus, sysfs, workqueues, timers, and uevent consumers.

Risks and test signals: `BUG_ON(!platform_data)` makes bad board data fatal; state clearing is generic while actual IRQ handler is external; debounce scheduling is platform-specific. Test IRQ firing, debounce timer behavior, uevents, sysfs attribute, and remove while work is pending.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/drivers/push-switch.c -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/Kbuild -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/Kbuild



Source read size: 6 lines, 170 bytes.



Purpose: SH asm header export/generation manifest for Kbuild.

Important APIs/types/functions: generates `syscall_table.h` and delegates several headers to generic implementations: `kvm_para.h`, `mcs_spinlock.h`, `parport.h`, and `text-patching.h`.

Control flow: during header generation Kbuild emits generated syscall table headers and creates generic wrapper links as needed.

State and persistence: build-time generated headers only.

Dependencies and integration points: affects users of architecture asm headers, syscall table generation, and generic kernel facilities.

Risks and test signals: missing generated or generic headers break architecture builds and exported UAPI assumptions. Test `headers_install` and SH defconfig builds.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/Kbuild -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/adc.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/adc.h



Source read size: 12 lines, 211 bytes.



Purpose: ADC access facade.

Important APIs/types/functions: `adc_single()` and CPU-specific `<cpu/adc.h>`.

Control flow: callers request one conversion from a CPU-provided ADC implementation.

State and persistence: ADC hardware state is external.

Dependencies and integration points: CPU ADC drivers and board sensor users.

Risks and test signals: channel numbering and CPU header availability. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/adc.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/addrspace.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/addrspace.h



Source read size: 63 lines, 1896 bytes.



Purpose: SH privileged segment address helper.

Important APIs/types/functions: `PXSEG`, `P1SEGADDR`, `P2SEGADDR`, `P3SEGADDR`, `P4SEGADDR`, `IS_29BIT`, `P3_ADDR_MAX`.

Control flow: macros translate physical/virtual addresses for segmented SH CPUs or BUG outside 29-bit mode.

State and persistence: no storage; address interpretation affects all MMIO/cache paths.

Dependencies and integration points: MMU, cache, boot, DMA, and PCI code.

Risks and test signals: wrong segment conversion corrupts memory or MMIO. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/addrspace.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/alignment.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/alignment.h



Source read size: 22 lines, 654 bytes.



Purpose: unaligned access accounting and policy declarations.

Important APIs/types/functions: increment helpers, `UM_WARN`, `UM_FIXUP`, `UM_SIGNAL`, `unaligned_user_action()`, `unaligned_fixups_notify()`.

Control flow: trap/fixup code updates counters and consults user policy.

State and persistence: global counters/policy live in trap code.

Dependencies and integration points: exception handling, proc/sysctl policy, user signal delivery.

Risks and test signals: policy mistakes can hide faults or signal valid code. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/alignment.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/asm-offsets.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/asm-offsets.h



Source read size: 2 lines, 74 bytes.



Purpose: wrapper for generated assembly offsets.

Important APIs/types/functions: `<generated/asm-offsets.h>`.

Control flow: assembly includes generated C structure offsets.

State and persistence: generated build artifact only.

Dependencies and integration points: low-level assembly entry/context code.

Risks and test signals: stale offsets corrupt register frames. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/asm-offsets.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-grb.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-grb.h



Source read size: 95 lines, 3045 bytes.



Purpose: GUSA restartable-block atomic backend.

Important APIs/types/functions: restartable inline assembly for add/sub/and/or/xor.

Control flow: temporarily encodes block size in r15, updates memory, restores stack pointer.

State and persistence: mutates caller atomic_t and transient r15/r0/r1.

Dependencies and integration points: GUSA_RB CPUs and signal/restart machinery.

Risks and test signals: r15 manipulation and compiler constraints are fragile. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-grb.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-irq.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-irq.h



Source read size: 81 lines, 2055 bytes.



Purpose: IRQ-masked atomic backend.

Important APIs/types/functions: `arch_atomic_add/sub/and/or/xor` and fetch/return variants.

Control flow: saves local IRQs, updates `counter`, restores IRQs.

State and persistence: mutates caller atomic_t only.

Dependencies and integration points: UP or older SH cores lacking LL/SC.

Risks and test signals: not SMP-safe without stronger exclusion. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-irq.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-llsc.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-llsc.h



Source read size: 97 lines, 2554 bytes.



Purpose: SH4A LL/SC atomic backend.

Important APIs/types/functions: `movli.l`/`movco.l` loops for arithmetic and bitwise atomics.

Control flow: retry loop until conditional store succeeds, with `synco` on return/fetch variants.

State and persistence: mutates caller atomic_t only.

Dependencies and integration points: SH4A SMP/atomic users.

Risks and test signals: inline asm constraints and missing barriers are high risk. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic-llsc.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic.h



Source read size: 35 lines, 693 bytes.



Purpose: top-level SH atomic operation selector.

Important APIs/types/functions: `arch_atomic_read/set` plus GRB, SH4A LL/SC, IRQ, or generic J2 implementation.

Control flow: preprocessor selects the atomic backend for the CPU/config.

State and persistence: atomic variables are caller-owned.

Dependencies and integration points: refcounting, locks, bitops/cmpxchg.

Risks and test signals: wrong backend breaks SMP atomicity. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/atomic.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/barrier.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/barrier.h



Source read size: 45 lines, 1503 bytes.



Purpose: SH memory/control barrier definitions.

Important APIs/types/functions: `mb/rmb/wmb`, `ctrl_barrier`, `__smp_*`, `__smp_store_mb`.

Control flow: maps barriers to `synco`, `icbi`, CAS trick, or nop sequence depending on CPU.

State and persistence: no storage; orders CPU/register effects.

Dependencies and integration points: MMU/CCR writes, SMP locking, atomics.

Risks and test signals: weak barrier selection causes ordering bugs. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/barrier.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-cas.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-cas.h



Source read size: 94 lines, 1770 bytes.



Purpose: CAS-loop atomic bitops for J2 SMP.

Important APIs/types/functions: `set_bit`, `clear_bit`, `change_bit`, test-and variants, `__bo_cas()`.

Control flow: uses `cas.l` retry loops on 32-bit words.

State and persistence: mutates caller bitmaps.

Dependencies and integration points: J2 SMP bitops and generic non-atomic helpers.

Risks and test signals: alignment/endian and CAS constraints. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-cas.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-grb.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-grb.h



Source read size: 173 lines, 6364 bytes.



Purpose: GUSA restartable-block atomic bitops.

Important APIs/types/functions: set/clear/change/test-and operations.

Control flow: uses r15 restartable block login/logout around word updates.

State and persistence: caller bitmap plus transient register state.

Dependencies and integration points: GUSA_RB systems.

Risks and test signals: signal/restart and inline asm fragility. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-grb.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-llsc.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-llsc.h



Source read size: 147 lines, 2858 bytes.



Purpose: SH4A LL/SC atomic bitops.

Important APIs/types/functions: set/clear/change/test-and operations using `movli.l`/`movco.l`.

Control flow: retry loop until conditional store succeeds.

State and persistence: caller bitmap only.

Dependencies and integration points: SH4A atomic bitmap users.

Risks and test signals: barrier placement and r0 constraints. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-llsc.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-op32.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-op32.h



Source read size: 143 lines, 3915 bytes.



Purpose: SH-2A optimized non-atomic bitops.

Important APIs/types/functions: `arch___set_bit`, `arch___clear_bit`, `arch___change_bit`, test-and variants.

Control flow: constant bit numbers use byte bit instructions; variable cases fall back to word masks.

State and persistence: caller bitmap only.

Dependencies and integration points: generic non-instrumented non-atomic bitops.

Risks and test signals: non-atomic semantics require external locking. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops-op32.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops.h



Source read size: 72 lines, 1656 bytes.



Purpose: top-level SH bit operations selector.

Important APIs/types/functions: backend includes, `ffz()`, `__ffs()`, generic ffs/hweight/lock/le helpers.

Control flow: selects atomic bitop implementation by CPU/config and provides inline bit scanning.

State and persistence: caller-owned bitmaps only.

Dependencies and integration points: scheduler, locks, filesystems, memory management.

Risks and test signals: backend mismatch breaks bitmap atomicity or endian semantics. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bitops.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit.h



Source read size: 2 lines, 66 bytes.



Purpose: BL-bit helper include wrapper.

Important APIs/types/functions: `<asm/bl_bit_32.h>`.

Control flow: delegates to 32-bit status-register helpers.

State and persistence: CPU status register state.

Dependencies and integration points: exception/interrupt masking code.

Risks and test signals: wrong include affects BL manipulation. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit_32.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit_32.h



Source read size: 34 lines, 639 bytes.



Purpose: 32-bit SH status-register BL bit helpers.

Important APIs/types/functions: `set_bl_bit()` and `clear_bl_bit()`.

Control flow: reads SR, sets or clears BL and interrupt-mask bits, writes SR.

State and persistence: mutates CPU SR.

Dependencies and integration points: trap/interrupt critical sections.

Risks and test signals: incorrect SR masks can block interrupts or exceptions. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bl_bit_32.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bug.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/bug.h



Source read size: 121 lines, 2871 bytes.



Purpose: SH BUG/WARN trap encoding.

Important APIs/types/functions: `BUG`, `WARN_ON`, `UNWINDER_BUG`, bug-table emission, trap opcode `trapa #0x3e`, `die*()` declarations.

Control flow: inline asm emits trap and metadata into `__bug_table`.

State and persistence: bug table metadata persists in kernel image.

Dependencies and integration points: generic bug framework, unwinder, trap handling.

Risks and test signals: bad metadata breaks diagnostics/unwinding. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/bug.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cache.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cache.h



Source read size: 52 lines, 1343 bytes.



Purpose: SH cache geometry definitions.

Important APIs/types/functions: `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `struct cache_info`, `__read_mostly`.

Control flow: no flow; consumed by cache and DMA code.

State and persistence: boot CPU cache descriptors live elsewhere.

Dependencies and integration points: allocator alignment, DMA, cacheflush.

Risks and test signals: wrong line size or alias mask causes DMA/cache corruption. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cache.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns.h



Source read size: 2 lines, 71 bytes.



Purpose: cache instruction wrapper include.

Important APIs/types/functions: `<asm/cache_insns_32.h>`.

Control flow: delegates to 32-bit cache instruction helpers.

State and persistence: none.

Dependencies and integration points: barriers and cacheflush code.

Risks and test signals: missing helper breaks cache operations. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns_32.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns_32.h



Source read size: 22 lines, 642 bytes.



Purpose: inline SH cache instructions.

Important APIs/types/functions: `__icbi`, `__ocbp`, `__ocbi`, `__ocbwb`, `register_align()`.

Control flow: emits cache block invalidate/purge/writeback instructions or fallback barrier.

State and persistence: mutates cache state for addressed lines.

Dependencies and integration points: cache flush, boot relocation, control barriers.

Risks and test signals: wrong instruction on unsupported CPU faults. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cache_insns_32.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cacheflush.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cacheflush.h



Source read size: 126 lines, 4322 bytes.



Purpose: SH cache flush API declarations and helpers.

Important APIs/types/functions: flush-cache function pointers, `flush_cache_*`, `flush_dcache_folio`, `flush_icache_range/pages`, vmap helpers, kmap coherent APIs, CPU cache init hooks.

Control flow: callers route through CPU-selected local flush functions and alias-aware anon-page handling.

State and persistence: function pointers and page clean bits persist after CPU cache init.

Dependencies and integration points: MM, DMA, JIT/signal trampolines, vmalloc, kmap.

Risks and test signals: aliasing and 29-bit mapping errors corrupt data/instructions. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cacheflush.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cachetype.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cachetype.h



Source read size: 9 lines, 170 bytes.



Purpose: cache type predicate.

Important APIs/types/functions: `cpu_dcache_is_aliasing()` returns true.

Control flow: compile-time inline decision.

State and persistence: none.

Dependencies and integration points: generic cache alias handling.

Risks and test signals: over-conservative but safe; wrong false would be dangerous. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cachetype.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/checksum.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/checksum.h



Source read size: 2 lines, 68 bytes.



Purpose: checksum wrapper include.

Important APIs/types/functions: `<asm/checksum_32.h>`.

Control flow: delegates to 32-bit checksum implementation.

State and persistence: none.

Dependencies and integration points: network stack.

Risks and test signals: include mismatch breaks checksum APIs. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/checksum.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/checksum_32.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/checksum_32.h



Source read size: 204 lines, 5038 bytes.



Purpose: SH optimized Internet checksum helpers.

Important APIs/types/functions: `csum_partial`, `csum_partial_copy_generic`, `csum_fold`, `ip_fast_csum`, TCP/UDP/IPv6 magic checksums, copy-to/from-user checksum helpers.

Control flow: inline asm folds carries and accumulates headers/pseudoheaders; user copy helpers validate access then call generic copy/checksum assembly.

State and persistence: no persistent state; may fault through user access paths.

Dependencies and integration points: IPv4/IPv6/TCP/UDP/ICMP, user copy, networking.

Risks and test signals: carry/endian/user fault handling affects packet correctness. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/checksum_32.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/clock.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/clock.h



Source read size: 17 lines, 436 bytes.



Purpose: SH clock initialization declarations.

Important APIs/types/functions: `arch_init_clk_ops`, `arch_clk_init`, `cpg_clk_init`, `clk_init`.

Control flow: platform/CPU clock init calls these during boot.

State and persistence: clock framework state lives in implementation.

Dependencies and integration points: SH CPG/common clock and board setup.

Risks and test signals: deprecated hooks can hide missing COMMON_CLK migration. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/clock.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-cas.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-cas.h



Source read size: 25 lines, 549 bytes.



Purpose: J2 CAS backend for cmpxchg/xchg.

Important APIs/types/functions: `__cmpxchg_u32`, `xchg_u32`, subword xchg include.

Control flow: uses `cas.l` loop for 32-bit exchange/compare-exchange.

State and persistence: caller memory only.

Dependencies and integration points: J2 SMP atomic primitives.

Risks and test signals: CAS inline asm constraints and alignment. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-cas.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-grb.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-grb.h



Source read size: 95 lines, 2869 bytes.



Purpose: GUSA restartable-block xchg/cmpxchg backend.

Important APIs/types/functions: `xchg_u32/u16/u8`, `__cmpxchg_u32`.

Control flow: uses r15 login/logout restartable blocks around memory updates.

State and persistence: caller memory and transient registers.

Dependencies and integration points: GUSA_RB atomic primitive users.

Risks and test signals: stack-pointer manipulation and signal restart coupling. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-grb.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-irq.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-irq.h



Source read size: 54 lines, 1065 bytes.



Purpose: IRQ-masked xchg/cmpxchg backend.

Important APIs/types/functions: `xchg_u32/u16/u8`, `__cmpxchg_u32`.

Control flow: disables local IRQs around load/store or compare/store.

State and persistence: caller memory only.

Dependencies and integration points: UP/legacy CPU atomic users.

Risks and test signals: not sufficient for true SMP without global exclusion. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-irq.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-llsc.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-llsc.h



Source read size: 53 lines, 1085 bytes.



Purpose: SH4A LL/SC xchg/cmpxchg backend.

Important APIs/types/functions: `xchg_u32`, `__cmpxchg_u32`.

Control flow: uses `movli.l`/`movco.l` retry loops with `synco`.

State and persistence: caller memory only.

Dependencies and integration points: SH4A atomic primitives.

Risks and test signals: conditional-store loop and barrier correctness. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-llsc.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-xchg.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-xchg.h



Source read size: 50 lines, 1274 bytes.



Purpose: portable subword xchg built on 32-bit cmpxchg.

Important APIs/types/functions: `__xchg_cmpxchg`, `xchg_u16`, `xchg_u8`.

Control flow: aligns to containing u32, masks/shifts by endian, retries cmpxchg until update succeeds.

State and persistence: caller memory word.

Dependencies and integration points: CAS/LLSC backends needing byte/halfword xchg.

Risks and test signals: unaligned pointer and endian bit offset mistakes. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg-xchg.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg.h



Source read size: 86 lines, 2142 bytes.



Purpose: top-level SH xchg/cmpxchg selector and typed wrappers.

Important APIs/types/functions: `arch_xchg`, `arch_cmpxchg`, `__cmpxchg`, backend includes, generic local cmpxchg.

Control flow: selects GRB, LL/SC, CAS, or IRQ backend; dispatches xchg by operand size and cmpxchg for 1/4 bytes.

State and persistence: mutates caller memory atomically.

Dependencies and integration points: atomics, locks, barriers, bitops.

Risks and test signals: unsupported sizes link to bad-pointer sentinels. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/cmpxchg.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/device.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/device.h



Source read size: 17 lines, 442 bytes.



Purpose: SH device extension declarations.

Important APIs/types/functions: `platform_resource_setup_memory()` and `plat_early_device_setup()`.

Control flow: platform code calls helpers to allocate contiguous memory resources and register early devices.

State and persistence: resources and platform devices persist elsewhere.

Dependencies and integration points: platform bus, early platform code, board setup.

Risks and test signals: wrong resource setup can overlap memory. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/device.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dma-register.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/dma-register.h



Source read size: 50 lines, 1708 bytes.



Purpose: common SH DMAC register offsets and CHCR/DMAOR bit definitions.

Important APIs/types/functions: SAR/DAR/TCR/CHCR/DMAOR offsets, DMAOR flags, request/address increment modes, CHCR enable/end/interrupt bits.

Control flow: no flow; controller code combines bitfields and writes MMIO.

State and persistence: hardware register state.

Dependencies and integration points: legacy DMA and dmaengine SH drivers.

Risks and test signals: bitfield errors break DMA direction/size/interrupts. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dma-register.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dma.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/dma.h



Source read size: 133 lines, 3161 bytes.



Purpose: legacy SH DMA API contract.

Important APIs/types/functions: `struct dma_ops`, `struct dma_channel`, `struct dma_info`, mode/flag enums, `dma_xfer`, `dma_read/write`, channel lookup, wait/configure/register APIs, sysfs hooks.

Control flow: clients request/configure/start/wait on virtual channels provided by DMAC drivers.

State and persistence: per-channel state, busy flags, waitqueues, device objects.

Dependencies and integration points: legacy SH DMA drivers and consumers.

Risks and test signals: API is legacy and conflicts with DMAengine; channel lifetime matters. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dma.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dmabrg.h -->

# sources/distributed-fs/ceph-client/arch/sh/include/asm/dmabrg.h



Source read size: 24 lines, 536 bytes.



Purpose: SH7760 DMABRG public IRQ API.

Important APIs/types/functions: DMABRG IRQ source constants and `dmabrg_request_irq()`/`dmabrg_free_irq()`.

Control flow: drivers register callbacks for USB/audio bridge events.

State and persistence: handler storage lives in dmabrg.c.

Dependencies and integration points: SH7760 USB/audio DMA users.

Risks and test signals: wrong source ID dispatches incorrect callback. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.



<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/asm/dmabrg.h -->
