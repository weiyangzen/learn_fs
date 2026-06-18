# Research: subset-b-000726

Grouped research for MIPS ARC/CFE/SNI firmware support, generic MIPS machine glue, FIT image fragments, and early MIPS architecture headers. Each section preserves the source path and is bounded by reconciliation markers for deterministic splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/arc_con.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/arc_con.c

**Purpose:** Registers an early ARC firmware-backed Linux console named `arc`. It lets boot messages reach firmware console output before normal tty/serial drivers are available.

**Important APIs/types/functions:** `prom_console_write()` emits characters through `prom_putchar()`, translating `\n` into CRLF. `prom_console_setup()` gates activation on `PROM_FLAG_USE_AS_CONSOLE`. `arc_cons` is the `struct console`, and `arc_console_init()` registers it with `console_initcall`.

**Control flow:** Console init always calls `register_console()`. The console core invokes setup, which returns `-ENODEV` unless platform identification set the relevant PROM flag. Writes are synchronous character loops into ARC firmware.

**State, dependencies, integration:** Reads global `prom_flags` from ARC identification and calls `prom_putchar()` from promlib. It integrates with Linux console registration and ARC firmware I/O.

**Risks and test signals:** Firmware calls are slow and unsafe after PROM memory is freed, so this is early-console only. Test by booting an ARC machine with and without `PROM_FLAG_USE_AS_CONSOLE`, checking CRLF output and no duplicate console when normal drivers register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/arc_con.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/cmdline.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/cmdline.c

**Purpose:** Builds `arcs_cmdline` from ARC/ARCS firmware argv values while converting selected firmware parameters into Linux kernel arguments.

**Important APIs/types/functions:** `prom_init_cmdline()` is the exported initializer. `move_firmware_args()` moves `OSLoadPartition=` to `root=` and appends `OSLoadOptions=` early. `ignored[]` filters firmware-only keys such as console handles and loader names.

**Control flow:** The code ignores argv[0], first copies converted firmware variables so later explicit arguments can override them, then appends non-ignored argv strings separated by spaces and trims the trailing space.

**State, dependencies, integration:** Mutates global `arcs_cmdline` and uses ARC 32-bit pointer sign extension through `prom_argv()`. It is called from ARC `prom_init()` before generic command-line parsing.

**Risks and test signals:** It uses `strcat()`/`memcpy()` without local bounds checks, relying on boot firmware arguments fitting `COMMAND_LINE_SIZE`. Test with ARC argv containing ignored keys, `OSLoadPartition`, `OSLoadOptions`, empty values, and override ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/env.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/env.c

**Purpose:** Provides a thin ARC firmware environment lookup wrapper.

**Important APIs/types/functions:** `ArcGetEnvironmentVariable(CHAR *name)` calls the ROM vector `get_evar` service through `ARC_CALL1` and returns a firmware string pointer.

**Control flow:** There is no local parsing or caching. Callers provide the name, the macro dispatches into firmware, and the returned pointer is passed through.

**State, dependencies, integration:** Depends on ARC type definitions and `asm/sgialib.h` ROM call macros. It integrates with PROM users that need ARC environment data during boot.

**Risks and test signals:** Returned storage belongs to firmware and may be invalid after PROM cleanup; callers must copy data they need later. Test by querying existing and missing environment variables on ARC firmware and verifying pointer lifetime assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/env.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/file.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/file.c

**Purpose:** Implements minimal ARC firmware file/device read and write wrappers.

**Important APIs/types/functions:** `ArcRead()` dispatches `read` with file ID, buffer, byte count, and returned count pointer. `ArcWrite()` dispatches `write` similarly.

**Control flow:** Each wrapper creates no state and immediately invokes the ROM vector through `ARC_CALL4`, returning the firmware status code.

**State, dependencies, integration:** Used by `prom_putchar()`, `prom_getchar()`, and early PROM debugging paths. It depends on ARC firmware pointer and integer type conventions.

**Risks and test signals:** Firmware calls may require cache handling and valid low-memory buffers on 64-bit kernels using 32-bit ARC. Test standard handles 0/1 for console input/output and count propagation on partial reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/identify.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/identify.c

**Purpose:** Identifies ARC/ARCS machine type from the root firmware component and sets Linux system type and PROM behavior flags.

**Important APIs/types/functions:** `mach_table[]` maps ARC names to Linux names and flags. `string_to_mach()` resolves names or panics. `prom_identify_arch()` reads the root child component via `ArcGetChild()`. `get_system_type()` returns `system_type`.

**Control flow:** During ARC init, the code obtains the first child of `PROM_NULL_COMPONENT`, uses its `iname`, prints it, maps it, and stores `system_type` plus `prom_flags`.

**State, dependencies, integration:** Owns globals `prom_flags` and `system_type`. Flags drive console enablement, ARCS memory type interpretation, and whether temporary PROM memory may be freed.

**Risks and test signals:** Unknown firmware identifiers panic, so new ARC platforms require table updates. Test each known SGI, Jazz, and SNI identifier, plus failure behavior for unknown strings and null component handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/identify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/init.c

**Purpose:** Performs ARC PROM library initialization for MIPS platforms.

**Important APIs/types/functions:** `prom_init()` validates the ARC system parameter block magic, stores `romvec`, initializes the command line, identifies the architecture, logs firmware version/revision, and calls `prom_meminit()`. `romvec` and optional `o32_stk` are exported state.

**Control flow:** Boot enters `prom_init()`, pulls `PROMBLOCK` and `ROMVECTOR`, hard-loops on invalid magic, then runs ordered setup before generic memory setup.

**State, dependencies, integration:** Initializes global firmware dispatch state consumed by `ARC_CALL*` users. It depends on boot arguments `fw_arg0/fw_arg1`, ARC command-line parsing, platform identification, and memory descriptor import.

**Risks and test signals:** Bad PROM magic leaves the system spinning before panic infrastructure may work. Test valid/invalid magic, 32-bit ARC with 64-bit kernels, and that memory descriptors become available before `memblock` setup completes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/memory.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/memory.c

**Purpose:** Converts ARC/ARCS firmware memory descriptors into Linux `memblock` regions and later frees temporary PROM memory when safe.

**Important APIs/types/functions:** `prom_meminit()` walks `ArcGetMemoryDescriptor()`. `prom_memtype_classify()` selects ARC versus ARCS memory type rules using `prom_flags`. `prom_free_prom_memory()` frees recorded firmware temporary regions unless `PROM_FLAG_DONT_FREE_TEMP` is set. `prom_cleanup()` is a weak platform hook.

**Control flow:** Descriptor pages are shifted by `ARC_PAGE_SHIFT` to bytes, mirrored RAM below `PHYS_OFFSET` is ignored, all regions are added to memblock, reserved and firmware-temporary regions are reserved, and up to five temporary regions are remembered for later freeing.

**State, dependencies, integration:** Maintains `prom_mem_base[]`, `prom_mem_size[]`, and `nr_prom_mem` in initdata. It integrates ARC firmware descriptors with Linux memblock and init-memory freeing.

**Risks and test signals:** More than five temporary regions logs errors and leaks them reserved. Misclassified ARC versus ARCS type values can either reserve usable RAM or free firmware-owned pages. Test descriptor permutations, mirrored IP28/IP30 RAM, `DONT_FREE_TEMP`, and weak platform overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/misc.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/misc.c

**Purpose:** Supplies miscellaneous ARC PROM service wrappers for interactive mode and display status.

**Important APIs/types/functions:** `ArcEnterInteractiveMode()` disables board cache and local IRQs, calls firmware `imode`, and is marked `__noreturn`. `ArcGetDisplayStatus()` calls `GetDisplayStatus` for a file ID.

**Control flow:** Interactive mode intentionally never returns to the kernel. Display status is a direct firmware query.

**State, dependencies, integration:** Uses board-cache control, IRQ disabling, ARC call macros, and ARC display types. It supports reboot/debug paths and firmware console/display users.

**Risks and test signals:** Calling interactive mode after PROM resources are invalid is unsafe. Test that IRQ/cache disabling happens before firmware entry and that display status calls use valid file handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/promlib.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/promlib.c

**Purpose:** Implements ARC firmware character I/O helpers used by early console and PROM code.

**Important APIs/types/functions:** `prom_putchar()` writes one character to ARC handle 1. `prom_getchar()` reads one character from ARC handle 0. On 64-bit kernels with 32-bit ARC, `O32_STATIC` ensures firmware buffers live in a low static segment.

**Control flow:** Both helpers disable board cache, perform one ARC read/write, then re-enable board cache.

**State, dependencies, integration:** Depends on `ArcRead`, `ArcWrite`, `bc_disable`, `bc_enable`, and CONFIG-specific O32 pointer constraints. Integrated with `arc_con.c` and early debug paths.

**Risks and test signals:** The helpers are synchronous and assume fixed firmware standard handles. Test console input/output with board cache enabled and disabled, plus 64-bit/ARC32 builds where stack pointers may not be firmware-addressable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/promlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/fw/cfe/Makefile

**Purpose:** Builds Broadcom Common Firmware Environment support into the MIPS firmware library.

**Important APIs/types/functions:** The only object rule is `lib-y += cfe_api.o`, so this directory contributes the CFE IOCB wrapper implementation whenever included by the parent build.

**Control flow:** Kbuild adds `cfe_api.o` to the built-in library; no conditional logic exists in this file.

**State, dependencies, integration:** Integrates CFE wrappers with the arch library build. Selection is controlled by higher-level Makefiles/Kconfig, not this file.

**Risks and test signals:** Build failures here indicate missing CFE headers or wrong directory inclusion. Test by enabling a CFE-using Broadcom MIPS configuration and confirming `cfe_api.o` links once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api.c

**Purpose:** Provides Linux-side stubs for the Broadcom CFE IOCB firmware API.

**Important APIs/types/functions:** `cfe_init()` stores the dispatch entry and handle. `cfe_iocb_dispatch()` invokes firmware. Device APIs include `cfe_open`, `cfe_close`, `cfe_read{,blk}`, `cfe_write{,blk}`, `cfe_ioctl`, `cfe_inpstat`, `cfe_getstdhandle`, and `cfe_getdevinfo`. Firmware APIs include CPU start/stop, environment get/set/enum, memory enum, ticks, cache flush, exit, firmware info, and `cfe_die()`.

**Control flow:** Each API fills a `struct cfe_xiocb` with a function code, status, handle, flags, parameter size, and union payload, dispatches it, then returns status or a payload result. `cfe_die()` prints through CFE if the entry seal and Broadcom PRId checks pass, applies BMIPS register workarounds, delays, and exits firmware.

**State, dependencies, integration:** Static `cfe_dispfunc` and `cfe_handle` are persistent early firmware state; `cfe_seal` validates the entry point. The file depends on CFE public/internal headers, MIPS PRId registers, memory barriers, and BMIPS CPU conditionals.

**Risks and test signals:** Pointer width is fragile, hence the `intptr_t` dispatch signature and `cfe_xptr_t` casts. `cfe_die()` uses `vsprintf()` into 128 bytes and must be kept to short fatal messages. Test every IOCB command on a CFE emulator/board, 32/64-bit pointer conversions, CFE absence fallback to panic, and BMIPS XKS01 disabling paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api_int.h -->
## sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api_int.h

**Purpose:** Defines internal Broadcom CFE IOCB command numbers and parameter block layouts used by `cfe_api.c`.

**Important APIs/types/functions:** Provides `CFE_CMD_*` constants, `cfe_xptr_t`, payload structs for buffer, input status, environment, CPU control, time, exit status, memory info, firmware info, and the top-level `struct cfe_xiocb`.

**Control flow:** No executable code; firmware wrappers populate these structs and CFE fills status/result fields.

**State, dependencies, integration:** The ABI is persistent across firmware calls: all fields use fixed signed/unsigned 64-bit sizes, and pointer fields are signed `cfe_xptr_t`.

**Risks and test signals:** Layout drift breaks firmware calls silently. Test with compile-time size/offset checks if available and runtime smoke tests for each command family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/cfe/cfe_api_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/fw/lib/Makefile

**Purpose:** Builds shared generic firmware monitor helpers for MIPS.

**Important APIs/types/functions:** Always builds `cmdline.o`; builds `call_o32.o` only for `CONFIG_64BIT`.

**Control flow:** Kbuild conditionally adds objects to the arch library; no runtime logic exists.

**State, dependencies, integration:** Integrates generic boot argument parsing and the 64-bit-to-O32 call bridge with firmware-specific users.

**Risks and test signals:** Missing `call_o32.o` on 64-bit firmware paths breaks 32-bit PROM calls. Test 32-bit and 64-bit MIPS builds with firmware code using `call_o32`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/call_o32.S -->
## sources/distributed-fs/ceph-client/arch/mips/fw/lib/call_o32.S

**Purpose:** Provides `call_o32`, an assembly dispatcher that lets 64-bit or N32 kernels call 32-bit O32 firmware routines.

**Important APIs/types/functions:** `call_o32` accepts a firmware function pointer in `a0`, optional alternate stack in `a1`, first six firmware arguments in `a2-a7`, and remaining arguments on the caller stack. It preserves static registers, `gp`, `fp`, and returns firmware `v0`.

**Control flow:** The dispatcher saves registers, optionally switches to a supplied O32 stack, truncates/places arguments into an O32 argument frame, calls the firmware function with `jalr`, restores the original stack and saved registers, and returns.

**State, dependencies, integration:** Depends on MIPS assembler macros from `asm.h`. It is used by PROM paths that cannot pass 64-bit kernel stack pointers to 32-bit firmware.

**Risks and test signals:** It supports up to 32 O32 arguments and requires called firmware to restore `sp`/`ra` as expected. Test with stack and non-stack calls, argument truncation, static register preservation, and firmware pointers in addressable KSEG/KUSEG regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/call_o32.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/cmdline.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/lib/cmdline.c

**Purpose:** Provides generic firmware command-line and environment parsing for non-ARC MIPS bootloaders.

**Important APIs/types/functions:** Globals `fw_argc`, `_fw_argv`, and `_fw_envp` store validated boot data. `fw_init_cmdline()` builds `arcs_cmdline`. `fw_getcmdline()` returns it. `fw_getenv()` supports YAMON name/value pairs and U-Boot name=value strings. `fw_getenvl()` parses an environment variable as `unsigned long`.

**Control flow:** Initialization validates argument and environment pointers against CKSEG0 expectations, then concatenates argv entries 1..argc-1. Environment lookup detects format from the first entry and scans by one or two slots.

**State, dependencies, integration:** Mutates boot command-line globals and relies on `fw_arg0..fw_arg2`. Used by generic board fixups, YAMON DT helpers, and Realtek initrd fixups.

**Risks and test signals:** Pointer validation is heuristic and assumes bootloader conventions. Test U-Boot and YAMON env formats, invalid pointers, large command lines, and numeric conversion failure returning zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/lib/cmdline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/fw/sni/Makefile

**Purpose:** Conditionally builds SNI PROM monitor routines.

**Important APIs/types/functions:** `lib-$(CONFIG_FW_SNIPROM) += sniprom.o` links SNI PROM support when the configuration selects it.

**Control flow:** Kbuild-only conditional object selection.

**State, dependencies, integration:** Ties SNI RM firmware support to the MIPS firmware build.

**Risks and test signals:** Incorrect config selection either omits required PROM support or links unused firmware code. Test SNI RM defconfig/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/sniprom.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/sni/sniprom.c

**Purpose:** Implements PROM access, memory detection, command-line construction, and system type reporting for big-endian SNI RM machines.

**Important APIs/types/functions:** Firmware entry macros map calls at `PROM_VEC`. `prom_putchar()`, `prom_getenv()`, and `prom_get_hwconf()` wrap PROM services. `sni_mem_init()` imports memory banks. `prom_init()` initializes memory and command line. `get_system_type()` returns `system_type`.

**Control flow:** On 64-bit kernels, PROM calls route through `call_o32` with a static O32 stack. Memory init reads IDPROM size and PROM bank layout, adjusts PCI tower windows, and adds banks to memblock. Command-line init copies argv entries from CKSEG0 addresses.

**State, dependencies, integration:** Uses firmware vectors at physical ROM, IDPROM constants, memblock, boot args, and optional O32 bridge. It supplies platform-specific `prom_init`.

**Risks and test signals:** Some PROM functions are version-dependent, and memory bank fixups are board-type specific. Test old/new PROM versions, PCI tower base adjustment, 64-bit O32 calls, `hwconf == 0xffffffff`, and command-line copy bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/sni/sniprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Kconfig -->
## sources/distributed-fs/ceph-client/arch/mips/generic/Kconfig

**Purpose:** Defines configuration switches for the generic MIPS kernel's legacy boards, FIT-embedded FDTs, and selected SoC/virtual boards.

**Important APIs/types/functions:** Symbols include `LEGACY_BOARDS`, `YAMON_DT_SHIM`, `LEGACY_BOARD_SEAD3`, `LEGACY_BOARD_OCELOT`, `SOC_VCOREIII`, multiple `FIT_IMAGE_FDT_*` options, `BOARD_INGENIC`, and `VIRT_BOARD_RANCHU`.

**Control flow:** Kconfig `select` and `depends on` relationships decide which board C files, DT shims, SOC support, and early printk helpers compile.

**State, dependencies, integration:** Drives `arch/mips/generic/Makefile`, FIT image fragments, and machine registration code.

**Risks and test signals:** `select` can pull low-level support unexpectedly; Ocelot is mutually constrained with SEAD3. Test all board option combinations that the comments call out, especially Ocelot versus SEAD3 and SOC_VCOREIII dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Makefile -->
## sources/distributed-fs/ceph-client/arch/mips/generic/Makefile

**Purpose:** Selects objects for the generic MIPS machine support directory.

**Important APIs/types/functions:** Core objects `init.o`, `irq.o`, and `proc.o` depend on `CONFIG_MACH_GENERIC_CORE`; board/shim objects depend on their Kconfig symbols.

**Control flow:** Kbuild links the correct machine support files for selected boards.

**State, dependencies, integration:** Integrates generic FDT boot, IRQ helpers, proc system type, YAMON fixups, and board-specific machine descriptors into the kernel image.

**Risks and test signals:** Missing object selection prevents `MIPS_MACHINE` descriptors or platform hooks from linking. Test representative configs for generic core, each legacy board, Ingenic, Ranchu, and Realtek.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-boston.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-boston.its.S

**Purpose:** FIT image source fragment embedding the Boston board FDT.

**Important APIs/types/functions:** Defines `fdt-boston` with `/incbin/("boot/dts/img/boston.dtb")`, SHA1 hash, and `conf-boston` selecting `kernel` plus the Boston FDT.

**Control flow:** Build tooling preprocesses this into a FIT image; runtime bootloader chooses the configuration.

**State, dependencies, integration:** Depends on the built DTB path and the common `kernel` FIT image node.

**Risks and test signals:** DTB path or configuration name drift breaks FIT generation/boot selection. Test `make` FIT image generation with `FIT_IMAGE_FDT_BOSTON` and inspect `dumpimage` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-boston.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ingenic.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ingenic.c

**Purpose:** Provides generic machine support for Ingenic SoCs.

**Important APIs/types/functions:** `ingenic_of_match[]` maps compatible strings to `MACH_INGENIC_*` IDs. `ingenic_fixup_fdt()` sets `mips_machtype`, `system_type`, adds legacy qi,lb60 memory if missing, and adjusts external oscillator dividers. `MIPS_MACHINE(ingenic)` registers the machine. Late PM init installs suspend/halt support for XBurst.

**Control flow:** Generic FDT selection matches root compatible, runs fixup, potentially writes CGU CPCCR bits for 12 MHz external clock, then later installs wait-based halt/suspend.

**State, dependencies, integration:** Uses FDT APIs, raw MMIO ioremap, bootinfo mach types, `system_type`, and platform PM hooks.

**Risks and test signals:** Direct CGU writes are SoC-specific and happen very early; wrong compatible data mislabels the platform. Test all compatible mappings, qi,lb60 missing memory fallback, 12/24 MHz oscillator behavior, and XBurst suspend/halt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ingenic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-jaguar2.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-jaguar2.its.S

**Purpose:** FIT fragment for Microsemi Jaguar2 PCB110 and PCB111 boards.

**Important APIs/types/functions:** Embeds `jaguar2_pcb110.dtb` and `jaguar2_pcb111.dtb`, each with SHA1 hashes, and defines configurations `pcb110` and `pcb111` using kernel, matching FDT, and `ramdisk`.

**Control flow:** Build creates FIT nodes; bootloader selects the board-specific config.

**State, dependencies, integration:** Depends on MSCC DTBs and common FIT kernel/ramdisk nodes.

**Risks and test signals:** Missing ramdisk node or DTB path breaks config validation. Test FIT build and bootloader selection for both PCB variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-jaguar2.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-luton.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-luton.its.S

**Purpose:** FIT fragment embedding the Microsemi Luton PCB091 FDT.

**Important APIs/types/functions:** Defines `fdt-luton_pcb091` from `boot/dts/mscc/luton_pcb091.dtb` and `pcb091` configuration using the shared kernel.

**Control flow:** Pure image metadata consumed at FIT build and boot selection time.

**State, dependencies, integration:** Tied to `FIT_IMAGE_FDT_LUTON` and SOC_VCOREIII configuration.

**Risks and test signals:** DTB rename or missing hash generation breaks image assembly. Test FIT generation and boot with U-Boot on Luton hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-luton.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-marduk.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-marduk.its.S

**Purpose:** FIT fragment embedding the IMG Pistachio Marduk/CI40 FDT.

**Important APIs/types/functions:** Defines `fdt-marduk` from `boot/dts/img/pistachio_marduk.dtb` and `conf-marduk`.

**Control flow:** Used by FIT image tooling; no kernel runtime code.

**State, dependencies, integration:** Depends on the DTB path and common kernel node.

**Risks and test signals:** Ensure configuration naming matches bootloader expectations. Test with `FIT_IMAGE_FDT_MARDUK` and inspect FIT contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-marduk.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ni169445.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ni169445.its.S

**Purpose:** FIT fragment embedding the National Instruments 169445 FDT.

**Important APIs/types/functions:** Defines `fdt-ni169445` from `boot/dts/ni/169445.dtb` and `conf-ni169445`.

**Control flow:** Build-time image metadata only.

**State, dependencies, integration:** Tied to `FIT_IMAGE_FDT_NI169445`.

**Risks and test signals:** DTB path and board description must stay aligned with device tree sources. Test FIT generation and board boot config lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ni169445.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.c

**Purpose:** Supports legacy Microsemi Ocelot boot without UHI/FIT-provided FDT.

**Important APIs/types/functions:** `ocelot_detect()` probes a RedBoot-created TLB mapping and chip ID, optionally copies bootloader command line, and returns board match. `ocelot_fixup_fdt()` installs `late_time_init` for early 8250 printk setup. `MIPS_MACHINE(ocelot)` registers built-in DTB, detect, and fixup hooks.

**Control flow:** Legacy generic boot calls detect functions; Ocelot checks TLB presence before reading chip ID. If matched, generic code uses the built-in DTB and later sets up early printk through `ioremap`.

**State, dependencies, integration:** Uses CP0 TLB probe registers, raw MMIO chip ID, `arcs_cmdline`, early printk setup, and `__dtb_ocelot_pcb123_begin`.

**Risks and test signals:** Assumes RedBoot TLB mapping is valid and firmware argv pointer shape is sane. Test no-TLB fallback, wrong part ID, command-line import, and early printk register mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.its.S

**Purpose:** FIT fragment for Microsemi Ocelot PCB123 and PCB120 boards.

**Important APIs/types/functions:** Embeds `ocelot_pcb123.dtb` and `ocelot_pcb120.dtb`, with configurations `conf-ocelot_pcb123` and `conf-ocelot_pcb120`.

**Control flow:** Build-time FIT metadata, selected by bootloader.

**State, dependencies, integration:** Used when booting Ocelot with U-Boot/FIT rather than legacy RedBoot path.

**Risks and test signals:** FIT and legacy Ocelot paths must use compatible DTBs. Test both PCB configurations in generated FIT output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ocelot.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ranchu.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-ranchu.c

**Purpose:** Provides support for the virtual MIPS Ranchu board used by Android emulator/QEMU.

**Important APIs/types/functions:** `read_rtc_time()` reads Goldfish RTC low/high registers. `ranchu_measure_hpt_freq()` calibrates CP0 count frequency over one RTC second and rounds to 10 kHz. `MIPS_MACHINE(ranchu)` registers compatible `mti,ranchu` and measure hook.

**Control flow:** Time init calls the machine frequency hook, which finds and maps the RTC DT node, reads CP0 count before/after one nanosecond-resolution second, rounds, unmaps, and returns the frequency.

**State, dependencies, integration:** Depends on OF node lookup, MMIO mapping, CP0 count, and MIPS generic time init.

**Risks and test signals:** Panics if RTC node or mapping is missing; calibration busy-waits for one second. Test DT compatibility, RTC latch semantics, repeatability of rounded frequency, and panic paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-ranchu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-realtek.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-realtek.c

**Purpose:** Adds generic Realtek RTL9302 MIPS board FDT fixups, especially initrd location from firmware environment.

**Important APIs/types/functions:** `realtek_add_initrd()` reads `initrd_start` and `initrd_size` via `fw_getenvl()` and writes `/chosen` `linux,initrd-start/end`. `realtek_fixup_fdt()` validates and copies/fixes the FDT. `MIPS_MACHINE(realtek)` matches `realtek,rtl9302-soc`.

**Control flow:** Fixup initializes command line, applies a small list of FDT fixups into a static 16 KiB buffer, and returns the new FDT.

**State, dependencies, integration:** Depends on generic firmware env parsing, libfdt mutation, and generic machine fixup infrastructure.

**Risks and test signals:** The fixed FDT buffer can overflow if source DT grows beyond 16 KiB with fixups. Zero start and size suppress initrd. Test missing `/chosen`, no initrd env, valid initrd env, malformed FDT, and buffer sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-realtek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-sead3.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-sead3.c

**Purpose:** Supports legacy MIPS SEAD-3 FPGA boards with YAMON boot data and board-specific FDT fixups.

**Important APIs/types/functions:** `sead3_detect()` checks revision register. FDT fixups append command line, memory, remove GIC if absent, and set serial config. `remove_gic()` rewrites interrupt parents/properties for UART, Ethernet, and EHCI when no GIC is present. `sead3_measure_hpt_freq()` calibrates CP0 count using a sampling status bit. `MIPS_MACHINE(sead3)` registers DTB, detect, fixup, and timer hooks.

**Control flow:** Legacy detection selects built-in DTB, fixup validates root compatible and applies YAMON transformations, and time init measures the counter over 100 10 ms transitions.

**State, dependencies, integration:** Uses raw CKSEG1 registers, libfdt, YAMON DT helpers, generic firmware command line, and built-in `__dtb_sead3_begin`.

**Risks and test signals:** Missing expected DT nodes causes fixup failures; timer calibration busy-waits with IRQs disabled. Test GIC-present and no-GIC boards, UART loop rewriting, memory env parsing, and HPT frequency measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-sead3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-serval.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-serval.its.S

**Purpose:** FIT fragment for Microsemi Serval PCB105.

**Important APIs/types/functions:** Embeds `serval_pcb105.dtb` and defines `pcb105` configuration with kernel, FDT, and ramdisk.

**Control flow:** Build-time FIT metadata only.

**State, dependencies, integration:** Tied to `FIT_IMAGE_FDT_SERVAL` and common FIT nodes.

**Risks and test signals:** Missing ramdisk node or DTB path breaks image validation. Test FIT generation and bootloader config selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-serval.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-xilfpga.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/board-xilfpga.its.S

**Purpose:** FIT fragment embedding the MIPSfpga/Xilfpga Nexys4DDR FDT.

**Important APIs/types/functions:** Defines `fdt-xilfpga` from `boot/dts/xilfpga/nexys4ddr.dtb` and `conf-xilfpga`.

**Control flow:** Build-time FIT metadata only.

**State, dependencies, integration:** Used by `FIT_IMAGE_FDT_XILFPGA`.

**Risks and test signals:** Keep DTB path aligned with DTS build outputs. Test FIT generation and Xilfpga boot config selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/board-xilfpga.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/init.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/init.c

**Purpose:** Implements generic MIPS platform boot, FDT selection, FDT fixups, memory setup, device-tree init, time init, and IRQ init.

**Important APIs/types/functions:** `prom_init()`, `plat_get_fdt()`, `plat_fdt_relocated()`, `plat_mem_setup()`, `device_tree_init()`, `apply_mips_fdt_fixups()`, `plat_time_init()`, and `arch_init_irq()`.

**Control flow:** Boot obtains an FDT from appended/UHI/built-in sources or legacy machine detection. Memory setup applies machine fixups, initializes command line, and calls `__dt_setup_arch`. Device-tree init copies/unflattens the tree and chooses SMP ops. Time init derives counter frequency from a machine hook or CPU clock and then probes timers. IRQ init initializes CPU IRQs if needed and calls `irqchip_init()`.

**State, dependencies, integration:** Caches selected `fdt`, `mach`, and match data in initconst globals. Integrates `MIPS_MACHINE` descriptors, OF/libfdt, firmware args, CPS/vSMP/UP SMP ops, clock framework, and irqchip drivers.

**Risks and test signals:** Bad FDT handling can fail before console is stable; legacy detection requires exactly one matching machine in practice. Test UHI, appended DTB, built-in DTB, legacy board detection, relocation, fixup failure propagation, CPU clock fallback, and GIC/CPU IRQ combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/irq.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/irq.c

**Purpose:** Provides generic helpers to resolve CP0 FDC, performance counter, and compare interrupt numbers.

**Important APIs/types/functions:** `get_c0_fdc_int()`, `get_c0_perfcount_int()`, and `get_c0_compare_int()` choose GIC-provided interrupt lines, VEIC panic placeholders, or MIPS CPU IRQ base offsets.

**Control flow:** Each function first checks `mips_gic_present()`, then VEIC, then configured CP0 interrupt fields, returning `-1` for unavailable optional interrupts.

**State, dependencies, integration:** Uses global CP0 interrupt configuration variables and GIC helper APIs. Called by timer/perf/FDC setup code.

**Risks and test signals:** VEIC paths are unimplemented and panic. Test with GIC, non-GIC CPU IRQ, no optional irq, and VEIC configurations to expose unsupported paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/proc.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/proc.c

**Purpose:** Supplies `/proc/cpuinfo` system type reporting for generic MIPS machines.

**Important APIs/types/functions:** Global `system_type` can be set by board code. `get_system_type()` returns it, else root DT `model`, else first root `compatible`, else `"Unknown"`.

**Control flow:** Lookup is lazy and read-only except for external `system_type` assignments.

**State, dependencies, integration:** Depends on OF root node and bootinfo. Used by proc CPU information formatting.

**Risks and test signals:** Missing OF root data degrades to `"Unknown"`. Test explicit board override, model-only DT, compatible-only DT, and empty DT properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/vmlinux.its.S -->
## sources/distributed-fs/ceph-client/arch/mips/generic/vmlinux.its.S

**Purpose:** Base FIT image source for a generic MIPS kernel.

**Important APIs/types/functions:** Defines `/dts-v1/`, kernel image node with preprocessor-provided `KERNEL_NAME`, `VMLINUX_BINARY`, compression, load and entry addresses, and default configuration `conf-default`.

**Control flow:** Build tooling preprocesses constants and incbins the kernel binary into FIT metadata.

**State, dependencies, integration:** Board-specific ITS fragments add FDT configurations referencing the `kernel` node.

**Risks and test signals:** Incorrect address cell size or load/entry macros creates unbootable images. Test FIT generation for 32/64-bit address settings and compression variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/vmlinux.its.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/yamon-dt.c -->
## sources/distributed-fs/ceph-client/arch/mips/generic/yamon-dt.c

**Purpose:** Converts YAMON bootloader command-line, memory, and serial environment into FDT properties for legacy boards.

**Important APIs/types/functions:** `yamon_dt_append_cmdline()` writes `/chosen/bootargs`. `yamon_dt_append_memory()` creates/updates `/memory` `reg` and `linux,usable-memory`. `yamon_dt_serial_config()` writes `/chosen/stdout-path`. Helper `gen_fdt_mem_array()` maps memory regions and discard gaps.

**Control flow:** Memory fixup reads `ememsize` or `memsize`, defaults to 32 MiB, applies command-line override, creates memory arrays with at most two entries, and writes big-endian cells. Serial fixup parses `yamontty` and `modettyN`, normalizes baud/parity/stop/flow, and writes a serial path.

**State, dependencies, integration:** Depends on generic firmware environment access, `arcs_cmdline`, libfdt mutation, and `struct yamon_mem_region` board tables.

**Risks and test signals:** Limited memory entry count can truncate region descriptions; parser accepts malformed serial modes by falling back. Test both env variable names, command-line memory override, region discard behavior, missing chosen/memory nodes, and serial mode variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/generic/yamon-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/Kbuild

**Purpose:** Declares generated and generic header exports for the MIPS asm include tree.

**Important APIs/types/functions:** `generated-y` lists generated syscall table and syscall count headers for n32, n64, and o32 ABIs. `generic-y` imports generic headers such as qspinlock, qrwlock, user, kvm_para, and text-patching.

**Control flow:** Kbuild uses this metadata when preparing architecture headers.

**State, dependencies, integration:** Integrates generated syscall headers with UAPI/build products and falls back to asm-generic implementations for selected facilities.

**Risks and test signals:** Missing generated headers break syscall builds; wrong generic fallback changes ABI-visible behavior. Test `headers_install` and full MIPS build for all three ABIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/abi.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/abi.h

**Purpose:** Defines the per-ABI signal and vDSO operations table used by MIPS signal delivery.

**Important APIs/types/functions:** `struct mips_abi` holds `setup_frame`, `setup_rt_frame`, restart trampoline address, signal context offsets for FPU state, and a `struct mips_vdso_image *`.

**Control flow:** Signal code selects a `mips_abi` for the current task ABI and calls its frame builders.

**State, dependencies, integration:** Depends on signal, siginfo, pt_regs, and vDSO types. It integrates native and compat ABI signal layout code.

**Risks and test signals:** Offset mismatches corrupt user signal frames and restarts. Test signal delivery/return for o32, n32, n64, FPU-used and no-FPU tasks, and vDSO selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/addrspace.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/addrspace.h

**Purpose:** Defines MIPS virtual address segments and conversion macros between physical, compatibility, CKSEG, KSEG, XKSEG, and XKPHYS addresses.

**Important APIs/types/functions:** Key macros include `KSEGX`, `CPHYSADDR`, `XPHYSADDR`, `CKSEG*ADDR`, `KSEG*ADDR`, `PHYS_TO_XKPHYS`, `PHYS_TO_XKSEG_*`, `XKPHYS_TO_PHYS`, `KDM_TO_PHYS`, and cache mode constants.

**Control flow:** Header-only macro expansion adapts constants for assembler versus C and 32-bit versus 64-bit builds.

**State, dependencies, integration:** Includes generated `spaces.h` and is widely used by MMU, IO, firmware, and board code.

**Risks and test signals:** Incorrect casts can truncate or sign-extend addresses incorrectly, especially in 64-bit compatibility segments. Test macro values in 32/64-bit builds and firmware pointer conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/addrspace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/amon.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/amon.h

**Purpose:** Declares Arbitrary Monitor (AMON) CPU availability and startup hooks.

**Important APIs/types/functions:** `amon_cpu_avail(int cpu)` reports monitor CPU availability; `amon_cpu_start(int cpu, unsigned long pc, unsigned long sp, unsigned long gp, unsigned long a0)` starts a CPU at a supplied context.

**Control flow:** Header only; platform SMP code calls the monitor implementation.

**State, dependencies, integration:** Integrates boot monitor CPU control with MIPS SMP bring-up.

**Risks and test signals:** Register argument order must match monitor firmware. Test secondary CPU startup with known PC/SP/GP/A0 values and unavailable CPU reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/amon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/arch_hweight.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/arch_hweight.h

**Purpose:** Provides architecture hweight/popcount helpers when compiler builtins are usable, otherwise delegates to generic bitops.

**Important APIs/types/functions:** Defines `__arch_hweight8/16/32/64` using `__builtin_popcount`/`__builtin_popcountll` under `ARCH_HAS_USABLE_BUILTIN_POPCOUNT`.

**Control flow:** Compile-time conditional chooses builtin or generic implementation.

**State, dependencies, integration:** Used by Linux bitops hweight APIs.

**Risks and test signals:** Builtin availability must match toolchain codegen support. Test popcount results for all widths and configs with/without builtin support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-eva.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-eva.h

**Purpose:** Supplies assembly string and assembler macros for kernel versus user memory/cache accesses, selecting EVA instructions when configured.

**Important APIs/types/functions:** Defines `kernel_*` operations for cache, pref, ll/sc, loads, and stores; `user_*` variants become EVA instructions such as `lwe`, `swe`, `cachee`, and `prefe` under `CONFIG_EVA`, or kernel equivalents otherwise.

**Control flow:** Preprocessor emits either C inline-asm strings or assembler macros depending on `__ASSEMBLER__`, and adapts doubleword operations for 32-bit builds.

**State, dependencies, integration:** Used by low-level user access, cache, atomic, and assembly code paths that must work in Enhanced Virtual Addressing mode.

**Risks and test signals:** Wrong user/kernel opcode selection can fault or access the wrong address space. Test EVA and non-EVA builds, 32/64-bit doubleword fallbacks, and assembler/C macro expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-eva.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-offsets.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-offsets.h

**Purpose:** Provides the standard include point for generated MIPS assembly offsets.

**Important APIs/types/functions:** Includes `<generated/asm-offsets.h>`.

**Control flow:** No local logic; build-generated constants are made visible to assembly and C headers.

**State, dependencies, integration:** Required by assembler macros that use structure offsets such as `THREAD_FPR*` and `THREAD_REG*`.

**Risks and test signals:** Generated offsets must match compiled C structures. Test by rebuilding after structure changes and compiling assembly users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-prototypes.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-prototypes.h

**Purpose:** Collects C prototypes needed by MIPS assembly files and modversion generation.

**Important APIs/types/functions:** Includes checksum, page, FPU, generic asm prototypes, uaccess, ftrace, and mmu context headers. Declares `clear_page_cpu()` and `copy_page_cpu()`.

**Control flow:** Header-only declarations.

**State, dependencies, integration:** Bridges assembly implementations with C symbol prototypes and modversions.

**Risks and test signals:** Missing prototypes can break CFI/modversions or hide ABI mismatches. Test allmodconfig builds and symbol version generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asm.h

**Purpose:** Defines common MIPS assembler macros for function declarations, CFI, pointer/register-size abstraction, panic/print helpers, CP0 access names, LL/SC branch workaround, and cache barriers.

**Important APIs/types/functions:** `LEAF`, `NESTED`, `END`, `EXPORT`, `FEXPORT`, `ASM_PANIC`, `ASM_PRINT`, `REG_*`, `INT_*`, `LONG_*`, `PTR_*`, `MFC0`, `MTC0`, `SC_BEQZ`, and `R10KCBARRIER`.

**Control flow:** Compile-time macros select ABI32/N32/ABI64 instruction forms and MIPS ISA capabilities.

**State, dependencies, integration:** Included by nearly all MIPS assembly and some inline asm code. It depends on sgidefs, EVA, and ISA revision definitions.

**Risks and test signals:** A macro bug affects many low-level paths, including stack frames, unwinding, and atomics. Test 32-bit, n32, and 64-bit assembly builds, microMIPS/VDSO CFI behavior, and R10000 LL/SC workaround codegen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-32.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-32.h

**Purpose:** Defines 32-bit MIPS assembly macros for FPU state save/restore and nonscratch CPU register context operations.

**Important APIs/types/functions:** `fpu_save_single`, `fpu_restore_single`, `cpu_save_nonscratch`, and `cpu_restore_nonscratch`.

**Control flow:** Assembly macro expansion stores/restores FPR even registers and FCR31, and saves/restores callee-saved GPRs plus stack/frame/return registers.

**State, dependencies, integration:** Depends on generated thread offsets and register definitions. Used by context switch and FPU handling code.

**Risks and test signals:** Offset or register omissions corrupt task context. Test context switching with FPU users, signal delivery, and 32-bit ABI preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-64.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-64.h

**Purpose:** Defines 64-bit MIPS assembly macros for saving and restoring nonscratch CPU registers.

**Important APIs/types/functions:** `cpu_save_nonscratch` and `cpu_restore_nonscratch` operate on thread register save slots.

**Control flow:** Macro expansion stores/restores s0-s7, sp, fp, and restore also loads ra.

**State, dependencies, integration:** Used by low-level context switch paths and depends on generated thread offsets.

**Risks and test signals:** Register-save ABI mistakes cause rare task corruption. Test 64-bit context switching, preemption, and exception return under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro-64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro.h

**Purpose:** Provides high-level assembler macros for IRQ enable/disable, FPU save/restore, MIPS MT raw encodings, MSA access/save/restore, and MSA upper-lane initialization.

**Important APIs/types/functions:** Includes 32/64-specific macros, defines `local_irq_enable/disable`, `fpu_save_16even/16odd/double`, `fpu_restore_*`, `_EXT`, `DMT/EMT/DVPE/EVPE/MFTR/MTTR`, MSA load/store/control helpers, `msa_save_all`, `msa_restore_all`, and `msa_init_all_upper`.

**Control flow:** Macro expansion adapts to CPU_HAS_DIEI, preemption, MIPS ISA revision, microMIPS, toolchain MSA support, and 32/64-bit builds.

**State, dependencies, integration:** Uses thread offsets, hazard macros, MSA definitions, and toolchain feature symbols. It underpins exception, context switch, FPU/MSA, and MIPS MT assembly.

**Risks and test signals:** Raw instruction encodings must match ISA and microMIPS modes; MSA save paths use `$1` and `noat`. Test with and without toolchain MSA mnemonics, MSA user tasks, preemptible IRQ disable paths, and microMIPS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/asmmacro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/atomic.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/atomic.h

**Purpose:** Implements MIPS architecture atomic integer operations.

**Important APIs/types/functions:** Defines `arch_atomic_read/set`, arithmetic and bitwise operations, relaxed return/fetch variants, 64-bit variants under `CONFIG_64BIT`, and `arch_atomic_sub_if_positive`/`dec_if_positive`.

**Control flow:** If LL/SC is unavailable, operations disable local IRQs and update memory directly. Otherwise inline assembly loops with `ll/sc` or `lld/scd`, sync barriers, and `SC_BEQZ` retry until store succeeds.

**State, dependencies, integration:** Relies on `kernel_uses_llsc`, sync/barrier macros, compiler asm constraints, and Loongson3 workarounds. Used throughout kernel refcounts/counters.

**Risks and test signals:** Memory ordering is subtle; some operations are relaxed while others add explicit barriers. Test atomic litmus cases on SMP, 32/64-bit builds, no-LLSC fallback, Loongson workaround configs, and `sub_if_positive` negative path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/barrier.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/barrier.h

**Purpose:** Defines MIPS memory, IO, SMP, LL/SC, and global-invalidate barriers.

**Important APIs/types/functions:** `__sync`, `rmb`, `wmb`, `fast_mb`, `fast_iob`, `mb`, `iob`, `__smp_mb/rmb/wmb`, `smp_llsc_mb`, `smp_mb__before_llsc`, `nudge_writes`, `__smp_mb__before/after_atomic`, and `sync_ginv`.

**Control flow:** Compile-time configuration selects write-buffer flush versus sync, Octeon and SGI IP28 special paths, weak-ordering SMP barriers, and LL/SC compiler clobber behavior.

**State, dependencies, integration:** Used by atomics, bitops, IO access, locking, and cache code. Depends on `addrspace.h` and `sync.h`.

**Risks and test signals:** Incorrect barriers produce SMP-only data races or IO ordering failures. Test memory-model litmus tests, device IO on weakly ordered CPUs, Octeon/IP28 special cases, and LL/SC ordering configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bcache.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bcache.h

**Purpose:** Abstracts board-level secondary/cache controller operations for older MIPS systems.

**Important APIs/types/functions:** `struct bcache_ops` contains enable, disable, writeback-invalidate, invalidate, and prefetch operations. Inline wrappers call `bcops` under `CONFIG_BOARD_SCACHE`; otherwise they compile to no-ops.

**Control flow:** Runtime board cache users call wrappers that dispatch through `bcops` only when board cache support exists.

**State, dependencies, integration:** `bcops` is global platform state; `indy_sc_init()` initializes SGI Indy secondary cache support. ARC PROM I/O disables board cache through this API.

**Risks and test signals:** Null `bcops` under enabled config would crash; missing disable around firmware calls can corrupt IO. Test board-cache configs and no-op configs, plus prefetch optional callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bcache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitops.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bitops.h

**Purpose:** Implements MIPS atomic and non-atomic bit operations plus bit-scan helpers.

**Important APIs/types/functions:** Atomic APIs include `set_bit`, `clear_bit`, `change_bit`, `test_and_set_bit{,_lock}`, `test_and_clear_bit`, `test_and_change_bit`, and `xor_unlock_is_negative_byte`. Bit scan helpers include `__fls`, `__ffs`, `fls`, and `ffs`.

**Control flow:** Atomic operations use LL/SC loops with sync and R10000/Loongson workarounds when available; otherwise they call slower IRQ-disabled out-of-line functions. MIPSr2 constant-bit cases use `ins/ext` optimizations.

**State, dependencies, integration:** Depends on CPU feature macros, barriers, endian/generic bitops, and out-of-line helpers in bitops implementation files.

**Risks and test signals:** Lock semantics depend on before/after barriers, and bit numbering must match generic expectations. Test atomic bit lock/unlock on SMP, no-LLSC fallback, MIPSr2 constant optimizations, and 32/64-bit scan results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitrev.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bitrev.h

**Purpose:** Provides MIPS arch-optimized bit-reversal helpers.

**Important APIs/types/functions:** `__arch_bitrev32`, `__arch_bitrev16`, and `__arch_bitrev8` use the `bitswap` instruction combined with byte swaps for 16/32-bit widths.

**Control flow:** Header-only inline assembly returns reversed bit order.

**State, dependencies, integration:** Used by generic bitrev APIs when architecture support is enabled.

**Risks and test signals:** Requires CPU/toolchain support for `bitswap`. Test known bit patterns for all widths and build on CPUs/configs that select this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bitrev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips-spaces.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips-spaces.h

**Purpose:** Overrides fixed-address top placement for BMIPS3300 systems.

**Important APIs/types/functions:** Defines `FIXADDR_TOP` as `0xff000000` to avoid collisions with the BMIPS system base register region.

**Control flow:** Compile-time address-layout override only.

**State, dependencies, integration:** Included by MIPS virtual address layout code for BMIPS configurations.

**Risks and test signals:** Wrong fixed mapping placement can overlap hardware regions. Test BMIPS3300 boot, fixmap users, and highmem/vmalloc layout sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips-spaces.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips.h

**Purpose:** Defines Broadcom BMIPS register offsets, SMP operations, reset vectors, shared state, and ZSCM register access helpers.

**Important APIs/types/functions:** `BMIPS_GET_CBR`, many BMIPS register offsets, `register_bmips_smp_ops()`, external reset/SMP vectors, `bmips_*` globals/functions, and `bmips_read_zscm_reg`/`bmips_write_zscm_reg`.

**Control flow:** SMP registration selects UP, BMIPS43xx, or BMIPS5000 ops based on `current_cpu_type()` when CPU_BMIPS and SMP are enabled. ZSCM access uses cache tag operations with sync/nop hazards.

**State, dependencies, integration:** Integrates BMIPS platform setup, SMP bring-up, CP0 registers, cache operations, and shared masks/offsets.

**Risks and test signals:** Cache-op-based ZSCM access is hazard-sensitive; CBR can point above 0xff000000. Test all BMIPS CPU types, SMP boot, reset vector copying, and ZSCM read/write ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bootinfo.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bootinfo.h

**Purpose:** Declares MIPS machine IDs, global boot state, PROM/platform hooks, command-line storage, firmware arguments, and FDT discovery helpers.

**Important APIs/types/functions:** Defines `MACH_*` constants/enums for DEC, Mikrotik, Loongson, and Ingenic. Declares `system_type`, `mips_machtype`, `prom_init`, `prom_free_prom_memory`, `plat_mem_setup`, `arcs_cmdline`, `fw_arg0..fw_arg3`, and `get_fdt()`.

**Control flow:** `get_fdt()` checks appended DTB, UHI `fw_arg0 == -2`, and built-in DTB in order when OF is enabled.

**State, dependencies, integration:** Central contract between firmware entry, platform setup, generic FDT boot, memory init, and proc reporting.

**Risks and test signals:** Boot argument conventions vary widely; FDT source priority affects boot behavior. Test appended/raw/ELF DTB, UHI, built-in DTB, and no-DTB fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bootinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/branch.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/branch.h

**Purpose:** Declares and wraps MIPS branch/delay-slot exception PC computation helpers.

**Important APIs/types/functions:** Externs include `__compute_return_epc*`, microMIPS and MIPS16e variants, and branch instruction testers. Inline helpers include `delay_slot`, `set_delay_slot`, `clear_delay_slot`, `exception_epc`, `compute_return_epc`, and `MIPS16e_compute_return_epc`.

**Control flow:** Exception handling advances EPC directly for simple non-delay cases, dispatches to ISA-specific decoders for delay slots or compressed ISA modes, and handles branch-likely flags.

**State, dependencies, integration:** Operates on `struct pt_regs` CP0 EPC/cause fields and CPU ISA feature macros. Used by signal, exception, ptrace, and emulation code.

**Risks and test signals:** Incorrect EPC advancement causes repeated exceptions or skipped instructions. Test normal, delay-slot, branch-likely, microMIPS, and MIPS16e exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/branch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/break.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/break.h

**Purpose:** Defines MIPS kernel-internal break instruction codes.

**Important APIs/types/functions:** Includes UAPI break codes and defines `BRK_KDB`, `BRK_MEMU`, `BRK_KPROBE_BP`, `BRK_KPROBE_SSTEPBP`, and `BRK_MULOVF`.

**Control flow:** No executable logic; low-level debug, emulator, kprobe, and overflow code emits or decodes these break codes.

**State, dependencies, integration:** Ties trap handling to specific break code values.

**Risks and test signals:** Code collisions misroute break exceptions. Test kprobe breakpoint/single-step, KDB entry, FPU emulator break, and multiply overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/break.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bug.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bug.h

**Purpose:** Provides MIPS-specific `BUG()` and optimized `BUG_ON()` implementations.

**Important APIs/types/functions:** `BUG()` emits `break BRK_BUG` and marks unreachable. For ISA greater than MIPS1, `__BUG_ON()` uses constant folding or `tne` trap with `BRK_BUG`.

**Control flow:** Compile-time config `CONFIG_BUG` enables arch trap implementations before including generic bug support.

**State, dependencies, integration:** Used by kernel assertions and trap handling.

**Risks and test signals:** Trap code must match exception decoding and must not be emitted on unsupported ISA. Test BUG/BUG_ON disassembly and runtime trap reporting on MIPS1 and newer builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bugs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bugs.h

**Purpose:** Declares CPU bug detection hooks and R4x00 daddiu bug state.

**Important APIs/types/functions:** Externs `daddiu_bug`, `check_bugs64_early`, `check_bugs32`, and `check_bugs64`; inline `r4k_daddiu_bug()` validates and returns bug status when configured.

**Control flow:** Boot CPU bug detection populates state; later code queries it.

**State, dependencies, integration:** Depends on CPU info and SMP headers. Used during CPU setup and errata workarounds.

**Risks and test signals:** Querying before detection warns; missing workaround on affected CPUs causes arithmetic faults. Test configured/unconfigured R4x00 errata and ordering of early bug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bugs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cache.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cache.h

**Purpose:** Defines MIPS cache line constants and cache initialization/probing function declarations.

**Important APIs/types/functions:** `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `__read_mostly`, and declarations for R3K/R4K/Octeon cache init plus cache size/line helpers.

**Control flow:** Header-only constants and externs.

**State, dependencies, integration:** Used by memory allocators, alignment, CPU cache setup, and architecture data placement.

**Risks and test signals:** Wrong L1 cache shift affects alignment and performance. Test cache init on supported CPU families and cache line constants in build configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheflush.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheflush.h

**Purpose:** Declares and wraps MIPS cache flush operations for memory management, user pages, vmaps, and instruction/data coherency.

**Important APIs/types/functions:** Function pointers cover full/mm/range/page flushes, icache flushes, vmap/vunmap, and kernel vmap range flushes. Inline helpers include `flush_dcache_folio`, `flush_dcache_page`, `flush_anon_page`, `flush_cache_vmap`, `flush_cache_vunmap`, `flush_kernel_vmap_range`, and `invalidate_kernel_vmap_range`.

**Control flow:** Runtime CPU feature flags determine whether to flush aliasing D-cache lines immediately or mark folios `PG_dcache_dirty`.

**State, dependencies, integration:** Depends on CPU cache flags and MM folio/page state. Used by mmap, exec, copy-to-user-page, and vmalloc paths.

**Risks and test signals:** Cache alias bugs show as stale I-cache/D-cache data. Test executable page writes, aliasing-cache CPUs, non-ic-fills-from-dcache CPUs, vmalloc/vmap, and anon page flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheops.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheops.h

**Purpose:** Defines numeric encodings for MIPS `cache` instruction operations across processor families.

**Important APIs/types/functions:** Constants identify I/D/T/S/V caches, operation fields, R4000-style ops, R5000/RM7000/R10000/Loongson-specific ops, and `Cache_Barrier`.

**Control flow:** No code; other assembly/C cache helpers combine constants into `cache` instructions.

**State, dependencies, integration:** Used by cache management, BMIPS ZSCM access, and CPU errata workarounds.

**Risks and test signals:** Wrong opcode constants can invalidate/write back the wrong cache. Test cache flush routines on relevant CPU families and inspect emitted cache op values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cacheops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cachetype.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cachetype.h

**Purpose:** Exposes MIPS cache aliasing information through the generic cachetype interface.

**Important APIs/types/functions:** `cpu_dcache_is_aliasing()` maps to `cpu_has_dc_aliases`.

**Control flow:** Inline macro only.

**State, dependencies, integration:** Depends on CPU feature detection and is consumed by generic cache/MM code.

**Risks and test signals:** Incorrect alias reporting leads to missing flushes or unnecessary overhead. Test on aliasing and non-aliasing D-cache CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cachetype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cdmm.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cdmm.h

**Purpose:** Defines the MIPS Common Device Memory Map bus and driver interfaces.

**Important APIs/types/functions:** `struct mips_cdmm_device`, `struct mips_cdmm_driver`, `mips_cdmm_phys_base()`, `mips_cdmm_bustype`, `mips_cdmm_early_probe()`, driver register/unregister helpers, `module_mips_cdmm_driver`, `builtin_mips_cdmm_driver`, and optional early FDC console setup.

**Control flow:** Driver core matches CDMM devices by ID tables and calls probe/remove/shutdown/CPU hotplug callbacks.

**State, dependencies, integration:** Integrates CPU-local CDMM devices with Linux driver model and CPU hotplug. Used by EJTAG FDC early console and other CDMM devices.

**Risks and test signals:** CDMM base must be 32 KiB aligned and platform-reserved; CPU-local hotplug callbacks must quiesce pinned work. Test early probe, module and builtin registration, CPU up/down callbacks, and early FDC console config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cdmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cevt-r4k.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cevt-r4k.h

**Purpose:** Declares common CP0 Count/Compare clock event support.

**Important APIs/types/functions:** Declares per-CPU `mips_clockevent_device`, `mips_event_handler`, `c0_compare_int_usable`, `c0_compare_interrupt`, and global `cp0_timer_irq_installed`.

**Control flow:** Timer setup installs compare IRQ and clockevent handlers using these declarations.

**State, dependencies, integration:** Integrates MIPS R4K-style CP0 timer with Linux clockevents and interrupts.

**Risks and test signals:** Incorrect compare interrupt usability causes lost ticks. Test timer interrupt install, per-CPU clockevent registration, and CPUs without usable compare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cevt-r4k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/checksum.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/checksum.h

**Purpose:** Provides MIPS-optimized IP checksum operations unless `CONFIG_GENERIC_CSUM` is selected.

**Important APIs/types/functions:** Declares `csum_partial`, user copy/checksum helpers, `csum_fold`, `ip_fast_csum`, `csum_tcpudp_nofold`, `ip_compute_csum`, and `csum_ipv6_magic`.

**Control flow:** User copy helpers validate access and call assembly helpers. Inline checksum functions perform one's-complement carry folding and use inline assembly for IPv6 pseudo-header summing.

**State, dependencies, integration:** Used by networking stack and user copy paths. Depends on endian config, 32/64-bit arithmetic, and uaccess.

**Risks and test signals:** Carry handling and endian shifts are easy to break. Test IPv4/IPv6 checksum vectors, odd-length fragments, user access failure returning zero, 32/64-bit builds, and little/big endian.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/clocksource.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/clocksource.h

**Purpose:** Exposes MIPS vDSO clocksource definitions through the architecture clocksource include.

**Important APIs/types/functions:** Includes `<asm/vdso/clocksource.h>`.

**Control flow:** Header forwarding only.

**State, dependencies, integration:** Connects arch clocksource users to vDSO clocksource data structures.

**Risks and test signals:** Include path drift can break vDSO/time builds. Test MIPS vDSO clocksource compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cmp.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cmp.h

**Purpose:** Placeholder header for MIPS CMP multitasking definitions.

**Important APIs/types/functions:** Forward-declares `struct task_struct`.

**Control flow:** No runtime logic.

**State, dependencies, integration:** Provides a stable include for code expecting CMP architecture definitions.

**Risks and test signals:** Low risk; test by compiling CMP-related code that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cmpxchg.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cmpxchg.h

**Purpose:** Implements MIPS `xchg`, `cmpxchg`, and `cmpxchg64` primitives.

**Important APIs/types/functions:** `__arch_xchg`, `arch_xchg`, `__cmpxchg`, `arch_cmpxchg_local`, `arch_cmpxchg`, and 64-bit variants. Small 1/2-byte operations are delegated to out-of-line helpers; bad sizes call compile-time error stubs.

**Control flow:** LL/SC loops implement 4/8-byte exchanges when available; fallback disables IRQs locally. 32-bit SMP `cmpxchg64` uses `lld/scd`, disables interrupts to protect 64-bit register halves, and requires CPU 64-bit capability.

**State, dependencies, integration:** Core synchronization primitive for locks, atomics, and reference updates. Depends on barriers, CPU features, asm constraints, and Loongson workarounds.

**Risks and test signals:** Size handling, memory ordering, and 32-bit `cmpxchg64` register splitting are high-risk. Test all operand sizes, SMP stress, no-LLSC fallback, unsupported `cmpxchg64` build errors, and Loongson workaround codegen.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat-signal.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/compat-signal.h

**Purpose:** Converts signal sets between native and compat user layouts.

**Important APIs/types/functions:** `__copy_conv_sigset_to_user()` uses `put_compat_sigset`; `__copy_conv_sigset_from_user()` uses `get_compat_sigset`.

**Control flow:** Compile-time assertions ensure compat and native signal set sizes match and `_NSIG_WORDS == 2`.

**State, dependencies, integration:** Used by compat signal delivery and return paths.

**Risks and test signals:** Signal mask layout mismatches break 32-bit tasks on 64-bit kernels. Test compat signal mask save/restore and build assertions after signal type changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat-signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/compat.h

**Purpose:** Defines MIPS 32-bit compatibility types, data layouts, and compat task detection for 64-bit kernels.

**Important APIs/types/functions:** Provides compat UID/GID typedefs, signal constants, `COMPAT_RLIM_INFINITY`, `COMPAT_UTS_MACHINE`, `struct compat_stat`, `compat_statfs`, IPC structures, compat SysV sem/msg/shm layouts, `compat_stack_t`, and `is_compat_task()`.

**Control flow:** Structure definitions adapt field ordering for endianness in message queues. `is_compat_task()` checks `TIF_32BIT_ADDR`.

**State, dependencies, integration:** Used by compat syscalls, signal altstack, stat/statfs, IPC, and personality handling.

**Risks and test signals:** ABI layout is user-visible and cannot drift. Test 32-bit userspace syscall ABI on 64-bit kernels, big/little endian IPC times, stat/statfs binary layouts, and compat altstack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compiler.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/compiler.h

**Purpose:** Provides MIPS compiler workarounds, inline-asm constraints, and ISA level strings.

**Important APIs/types/functions:** Overrides `barrier_before_unreachable()` with `.insn`, defines `GCC_OFF_SMALL_ASM()`, `MIPS_ISA_LEVEL`, `MIPS_ISA_ARCH_LEVEL`, and raw ISA tokens for MIPSR6/R5/default R2 builds.

**Control flow:** Compile-time selection handles GCC unreachable delay-slot bugs and suboptimal noreturn stack behavior.

**State, dependencies, integration:** Used by inline assembly across atomics, bitops, cmpxchg, and generated code.

**Risks and test signals:** Changing constraints or ISA strings can break assembler acceptance or code scheduling. Test affected GCC versions, microMIPS link requirements, and inline asm builds for R5/R6/default configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cop2.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cop2.h

**Purpose:** Abstracts COP2 state handling and CU2 exception notification.

**Important APIs/types/functions:** Defines `cop2_present`, `cop2_lazy_restore`, `cop2_save`, and `cop2_restore` differently for Octeon, Loongson64, or no COP2. Provides `enum cu2_ops`, `register_cu2_notifier`, `cu2_notifier_call_chain`, and `cu2_notifier` helper macro.

**Control flow:** CPU-specific configs select save/restore behavior; CU2 exception code calls notifier chain for interested handlers.

**State, dependencies, integration:** Integrates Octeon COP2 thread state, Loongson lazy handling, and generic notifier infrastructure.

**Risks and test signals:** Missing save/restore corrupts COP2 state across context switches. Test Octeon COP2 workloads, Loongson64 lazy restore, and notifier ordering for CU2 load/store exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cop2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-features.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-features.h

**Purpose:** Converts probed `cpu_data[0]` ISA, ASE, option, cache, and guest fields into feature macros used throughout MIPS code.

**Important APIs/types/functions:** Defines feature predicates such as `cpu_has_tlb`, `cpu_has_fpu`, `cpu_has_llsc`, `cpu_has_mips32r2`, `cpu_has_mips64`, `cpu_has_mmips`, `cpu_has_dc_aliases`, `cpu_has_msa`, `cpu_has_vz`, `cpu_has_mmid`, guest feature predicates, cache line helpers, and many errata/ISA shortcut macros.

**Control flow:** Most macros prefer override definitions from `cpu-feature-overrides.h`, else derive from `cpu_data[0]`, compile-time `MIPS_ISA_REV`, config symbols, or `boot_cpu_type()` switch expressions.

**State, dependencies, integration:** Central dependency for cache, atomics, MMU, FPU, virtualization, SMP, timer, and exception code. Assumes CPU0 options are a superset on SMP.

**Risks and test signals:** Overstating features can emit unsupported instructions; understating features disables needed fast paths. Test CPU probe data against macros on all supported CPU families, override configs, no-FPU boot option, SMP heterogeneous assumptions, and guest dynamic feature paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-info.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-info.h

**Purpose:** Defines the runtime CPU descriptor structures and helpers for MIPS.

**Important APIs/types/functions:** `struct cache_desc`, `struct guest_info`, and `struct cpuinfo_mips` hold ASID, features, FPU/MSA IDs, CPU type, TLB/cache descriptors, package/global topology, watch registers, write-combine CCA, HTW state, guest capabilities, and optional Loongson CPUCFG data. Helpers include `cpu_cluster`, `cpu_core`, `cpu_vpe_id`, `cpus_are_siblings`, `cpu_asid_inc`, `cpu_asid_mask`, and notifier registration.

**Control flow:** CPU probe populates `cpu_data[]`; feature macros and proc code read it. Topology helpers decode `globalnumber`.

**State, dependencies, integration:** `cpu_data[]`, `current_cpu_data`, `raw_current_cpu_data`, and `boot_cpu_data` are global CPU state used across architecture code.

**Risks and test signals:** Alignment and field correctness affect per-CPU cacheline sharing and all feature tests. Test CPU probe/report, proc cpuinfo notifiers, topology decoding, ASID masks, and watch register exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-type.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-type.h

**Purpose:** Provides config-filtered helpers for retrieving current and boot CPU type.

**Important APIs/types/functions:** `__get_cpu_type()` validates a CPU type against enabled `CONFIG_SYS_HAS_CPU_*` families, while `current_cpu_type()` and `boot_cpu_type()` read `cpu_data`.

**Control flow:** Switch cases are compiled only for selected CPU families; default is `unreachable()`.

**State, dependencies, integration:** Depends on `current_cpu_data` and `cpu_data[0]`. Used by feature and platform code to choose CPU-specific behavior.

**Risks and test signals:** Probe returning a CPU type not enabled in config reaches unreachable behavior. Test defconfigs for every enabled CPU family and QEMU generic selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-type.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu.h

**Purpose:** Defines MIPS PRId/FPU ID encodings, CPU type enum, ISA level flags, CPU option bits, and ASE bits.

**Important APIs/types/functions:** Includes company IDs, implementation IDs for legacy/MIPS/Broadcom/Cavium/Ingenic/Netlogic/Loongson and others, revision constants, `enum cpu_type_enum`, `MIPS_CPU_ISA_*`, `MIPS_CPU_*` option flags, and `MIPS_ASE_*`.

**Control flow:** Header constants are consumed by CPU probe and feature macros.

**State, dependencies, integration:** Provides the stable numeric vocabulary for CPU detection, errata checks, feature probing, `/proc/cpuinfo`, and module matching.

**Risks and test signals:** Wrong PRId constants misidentify CPUs and select wrong workarounds. Test CPU probe tables against hardware/QEMU PRId values and feature bit assignment uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpufeature.h

**Purpose:** Provides module CPU feature matching helpers based on MIPS ELF hardware capabilities.

**Important APIs/types/functions:** `MAX_CPU_FEATURES`, `cpu_feature(x)` maps an HWCAP name to bit index, and `cpu_have_feature()` tests `elf_hwcap`.

**Control flow:** Header-only bit tests for module loader feature matching.

**State, dependencies, integration:** Depends on UAPI hwcap definitions and `elf_hwcap` from ELF setup.

**Risks and test signals:** HWCAP bit mismatch prevents modules from loading or lets incompatible modules load. Test module_cpu_feature_match users and HWCAP exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/debug.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/debug.h

**Purpose:** Declares the top-level MIPS debugfs directory.

**Important APIs/types/functions:** Extern `struct dentry *mips_debugfs_dir`.

**Control flow:** No code; MIPS debugfs users create files below this dentry.

**State, dependencies, integration:** Integrates architecture debug facilities with Linux debugfs.

**Risks and test signals:** Users must handle debugfs disabled or directory not initialized. Test debugfs entry creation/removal and CONFIG_DEBUG_FS off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ecc.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ecc.h

**Purpose:** Defines DECstation/DECsystem ECC error register bit layouts and ECC handler declarations.

**Important APIs/types/functions:** `KN0X_EAR_*` defines error address register bits; `KN0X_ESR_*` defines syndrome register bits. Declares `dec_ecc_be_init`, `dec_ecc_be_handler`, and `dec_ecc_be_interrupt`.

**Control flow:** Header constants guide bus-error and interrupt handlers that decode/clear ECC status.

**State, dependencies, integration:** Used by DEC memory/bus error handling on KN02/KN03/KN05 class systems.

**Risks and test signals:** Register bits are write-clear; wrong handling loses diagnostic data. Test single/double-bit ECC reports, timeout/overrun, IRQ path, and bus-error fixup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ecc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/interrupts.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/interrupts.h

**Purpose:** Defines DECstation interrupt numbers, CPU interrupt masks, interrupt mapping tables, and common handler prototypes.

**Important APIs/types/functions:** `DEC_IRQ_*` enumerates ordinary, I/O ASIC DMA, TURBOchannel, and timer/video interrupts. `DEC_NR_INTS`, `DEC_MAX_CPU_INTS`, `DEC_MAX_ASIC_INTS`, CPU IRQ mask macros, `int_ptr`, and extern mapping tables/handlers are declared.

**Control flow:** Platform interrupt setup populates/use mapping tables and dispatches to handlers such as `kn02_io_int`, `asic_dma_int`, and `cpu_all_int`.

**State, dependencies, integration:** Integrates DEC CPU interrupt lines, I/O ASIC masks, and Linux IRQ numbers.

**Risks and test signals:** Misnumbered IRQs attach drivers to wrong lines. Test each DEC machine family interrupt map, FPU IRQ, DMA IRQs, and unimplemented handler paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/interrupts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic.h

**Purpose:** Provides DEC I/O ASIC register accessors and initialization declarations.

**Important APIs/types/functions:** Externs `ioasic_ssr_lock` and `ioasic_base`; inline `ioasic_write()` and `ioasic_read()` index MMIO registers by byte offset/4. Declares `init_ioasic_irqs()` and `dec_ioasic_clocksource_init()`.

**Control flow:** Callers read/write volatile register slots directly through the base pointer.

**State, dependencies, integration:** Shared I/O ASIC base and SSR lock coordinate register access across DEC platform code and drivers.

**Risks and test signals:** Base pointer must be mapped before access; SSR requires lock discipline. Test register read/write offsets, IRQ init, and clocksource initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_addrs.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_addrs.h

**Purpose:** Defines DEC I/O ASIC slot address ranges, register offsets, and system support register bits.

**Important APIs/types/functions:** Constants include `IOASIC_SLOT_SIZE`, device slot offsets for ROM, IOCTL, LANCE, SCC, VDAC, RTC, ISDN, ECC, SCSI, DMA areas, `IO_REG_*` register offsets, `IO_SSR_*` DMA bits, and `KN0X_IO_SSR_*` reset/diagnostic bits.

**Control flow:** Header constants are used by platform and driver code to compute MMIO addresses and manipulate DMA/control bits.

**State, dependencies, integration:** Encodes board-specific address maps for Maxine and non-Maxine DEC I/O ASIC variants.

**Risks and test signals:** Overlapping aliases are intentional for different systems; wrong machine use targets the wrong device. Test address constants against DEC hardware docs and driver probe on Maxine/3max+ variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_addrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_ints.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_ints.h

**Purpose:** Defines DEC I/O ASIC interrupt status/mask bit numbers and IRQ-number conversion macros.

**Important APIs/types/functions:** `IO_INR_*` names DMA/error interrupt bit positions for SCC, ASC, LANCE, ACCESS.bus, floppy, and ISDN. `IO_IRQ_BASE`, `IO_IRQ_LINES`, `IO_IRQ_NR`, `IO_IRQ_MASK`, `IO_IRQ_ALL`, and `IO_IRQ_DMA` map bits to Linux IRQs.

**Control flow:** Interrupt dispatch code reads status bits, masks them, and converts to IRQ numbers using these macros.

**State, dependencies, integration:** Complements `interrupts.h` and `ioasic_addrs.h` for DEC I/O ASIC IRQ setup.

**Risks and test signals:** Upper/lower bit partition differs for Maxine versus other systems. Test DMA interrupt dispatch for each device class and mask handling for system-specific lower bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/dec/ioasic_ints.h -->
