# Research: subset-b-005233

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.c

Purpose: Linux OS integration for the Adaptec AIC77xx/AIC78xx `aic7xxx` SCSI driver. It adapts the portable `ahc` core to Linux SCSI mid-layer, SPI transport, module parameters, DMA APIs, interrupts, host registration, error recovery, and command completion.

Important APIs, types, and functions: the file exports `aic7xxx_driver_template`, `ahc_linux_register_host()`, `ahc_platform_alloc()`, `ahc_platform_free()`, `ahc_linux_isr()`, `ahc_done()`, `ahc_send_async()`, DMA wrapper functions, low-level `ahc_inb/outb/insb/outsb()`, and module init/exit. Internal control points include `ahc_linux_queue_lck()`, `ahc_linux_run_command()`, `ahc_linux_queue_recovery_cmd()`, `ahc_linux_handle_scsi_status()`, queue-freeze helpers, transport setters for width/period/offset/DT, and boot/module option parsing.

Control flow: module init parses `aic7xxx=...`, attaches SPI transport, reserves per-device transport data, then initializes PCI/EISA probing. Probe code later calls `ahc_linux_register_host()`, which allocates a `Scsi_Host`, initializes bus state, enables interrupts, adds the host, and scans it. Command submission enters `queuecommand`, locks the adapter, maps the request with `scsi_dma_map()`, allocates an SCB, fills CDB/SCSI ID/negotiation/SG fields, updates `ahc_linux_device` counters, and calls `ahc_queue_scb()`. Interrupts call `ahc_intr()`. Completion removes pending/untagged links, unmaps DMA, handles status and sense, adjusts adaptive tag depth, frees the SCB, maps CAM status to Linux DID status, and calls `scsi_done()`. Error recovery finds pending SCBs, pauses/flushed the chip, tries QINFIFO removal or message delivery for abort/reset, and waits on a completion.

State and persistence: persistent runtime state lives in module parameters, global tag-depth table, per-adapter `platform_data`, per-target SPI transport attributes, per-device queue counters, pending SCB lists, and SCSI command `result`/sense buffers. No disk persistence is used; SEEPROM persistence is delegated to proc/PCI helpers.

Dependencies and integration: depends on Linux SCSI/SPI transport APIs, DMA mapping/coherent APIs, module/init APIs, spinlocks/completions, `aic7xxx_core`, register definitions, inline helpers, and PCI/EISA glue. It is the main boundary between Linux and the portable CAM-like core.

Risks: hardware-facing concurrency is delicate; queue freeze/unfreeze has a noted race with the mid-layer. DMA segment accounting can panic if `AHC_NSEG` is insufficient. Error recovery depends on exact sequencer state and can time out. Adaptive tag throttling can misbehave with unusual devices. Module options are global across controllers. Disabled IU/QAS code documents unsupported sequencer behavior.

Test signals: build with SCSI/SPI transport and PCI/EISA configs, boot/probe supported adapters, verify queueing and completion under tagged and untagged devices, run abort/device reset/bus reset paths, test module parameters (`tag_info`, `global_tag_depth`, `no_reset`, `seltime`, `allow_memio`), inspect SPI negotiation attributes, and exercise suspend/resume through PCI glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.h

Purpose: Linux OS mapping header for the `aic7xxx` core. It defines Linux-facing aliases, DMA/bus-space abstractions, per-device/per-SCB/per-adapter platform storage, locking helpers, PCI/EISA entry points, SCSI result wrappers, and integration declarations used by the core and bus-specific files.

Important APIs, types, and functions: key types are `ahc_dev_softc_t`, `ahc_io_ctx_t`, `bus_space_tag_t`, `bus_space_handle_t`, `bus_dma_segment_t`, `bus_dma_tag_t`, `struct ahc_linux_dma_tag`, `struct ahc_linux_device`, `struct scb_platform_data`, and `struct ahc_platform_data`. It declares DMA functions, low-level I/O functions, `ahc_linux_register_host()`, PCI/EISA mapping functions, proc functions, `ahc_platform_*()` hooks, `ahc_linux_isr()`, `ahc_done()`, `ahc_send_async()`, and `ahc_print_path()`.

Control flow role: this header lets portable code call FreeBSD/CAM-style primitives while Linux-specific implementations live in `aic7xxx_osm.c` and `aic7xxx_osm_pci.c`. Inline helpers translate Linux `scsi_cmnd` fields into CAM-like transaction and SCSI status, transfer length/direction/residual accessors, autosense behavior, and SCB freeze semantics. Lock helpers wrap `spin_lock_irqsave()` around adapter state.

State and persistence: `struct ahc_linux_device` tracks live queue depth, freeze counts, active commands, issued command count, tag throttling, and ordered-tag starvation counters. `struct scb_platform_data` links an SCB to device state and stores DMA transfer length and autosense residual. `struct ahc_platform_data` stores target pointers, lock, controller freeze count, error-handler completion, Linux `Scsi_Host`, IRQ, BIOS address, and MMIO bus address. All are runtime-only.

Dependencies and integration: includes Linux block, PCI, interrupt, module, I/O, and SCSI/SPI transport headers plus local `cam.h`, `queue.h`, `scsi_message.h`, `aiclib.h`, and `aic7xxx.h`. It exposes PCI config register constants used by the portable PCI layer.

Risks: many macros/inline wrappers encode Linux mid-layer assumptions, for example always performing autosense and treating coherent DMA sync as no-op. `ahc_freeze_scb()` modifies command result bits and device freeze counters inline, so misuse affects completion. The header is widely included; ABI or field changes can break multiple bus/core files.

Test signals: compile all AIC7XXX variants with/without PCI/EISA/debug/pretty-print options, validate structure field use across `aic7xxx_osm.c`, `aic7xxx_pci.c`, and `aic7770_osm.c`, run sparse/build checks for address-space annotations, and exercise queue-depth/status/residual wrappers through normal I/O and error completions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm_pci.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm_pci.c

Purpose: Linux PCI attachment glue for `aic7xxx` adapters. It binds PCI IDs to the kernel PCI driver model, allocates and configures `ahc_softc` instances, maps register resources, hooks interrupts, handles power management, and forwards PCI config access for the portable PCI logic.

Important APIs and functions: `ahc_linux_pci_id_table`, `aic7xxx_pci_driver`, `ahc_linux_pci_init()`, `ahc_linux_pci_exit()`, `ahc_linux_pci_dev_probe()`, `ahc_linux_pci_dev_remove()`, suspend/resume callbacks, `ahc_pci_read_config()`, `ahc_pci_write_config()`, `ahc_pci_map_registers()`, and `ahc_pci_map_int()`.

Control flow: PCI core matches IDs, probe calls `ahc_find_pci_device()`, allocates a named `ahc_softc`, enables the device, sets bus mastering, chooses 39-bit DMA when supported or falls back to 32-bit DMA, assigns device pointers, calls `ahc_pci_config()`, inherits BIOS/channel flags for secondary multifunction devices, stores drvdata, and registers the SCSI host. Removal unregisters the SCSI host, disables interrupts under lock, and frees the adapter. Register mapping prefers MMIO BAR1, validates it with `ahc_pci_test_register_access()`, and falls back to PIO BAR0. IRQ mapping requests a shared interrupt and stores the assigned IRQ.

State and persistence: runtime state is held in PCI drvdata, `ahc->dev_softc`, `ahc->dev`, bus-space tag/handle, `platform_data->mem_busaddr`, and `platform_data->irq`. No persistence is written. PM resume restores through `ahc_pci_resume()` and core resume.

Dependencies and integration: uses Linux PCI driver, DMA mask, resource, ioremap, IRQ, and PM APIs. It depends on ID constants from `aic7xxx_pci.h`, common hardware configuration in `aic7xxx_pci.c`, and SCSI host registration from `aic7xxx_osm.c`.

Risks: probe error paths must free allocations after `ahc_alloc()`/`pci_enable_device()`; incorrect DMA mask selection can break high-memory transfers; MMIO validation must detect broken mappings before enabling memory access; multifunction inheritance assumes function 0 is already bound. The IO-region helper is gated by `aic7xxx_allow_memio`, despite being the PIO fallback, so option semantics deserve attention.

Test signals: PCI ID table coverage, probe/remove cycles, MMIO and forced- PIO mapping, shared IRQ delivery, DMA mask behavior on >32-bit systems, suspend/resume, multifunction adapters, and failure injection around resource requests and `scsi_add_host()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_osm_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.c

Purpose: product-specific PCI identification and hardware initialization for AIC7xxx-family controllers. It maps device/subsystem IDs to setup routines, configures chip features/bugs, initializes PCI/chip registers, reads SEEPROM or BIOS scratch settings, controls termination, probes external SCB RAM, handles PCI errors, and restores PCI-side state after reset/resume.

Important APIs and functions: public entry points include `ahc_find_pci_device()`, `ahc_pci_config()`, `ahc_pci_test_register_access()`, `ahc_acquire_seeprom()`, `ahc_release_seeprom()`, and `ahc_pci_resume()`. Internal functions include `check_extport()`, `ahc_parse_pci_eeprom()`, `configure_termination()`, cable-detect helpers, board-control read/write helpers, `ahc_pci_intr()`, `ahc_pci_chip_init()`, SCB RAM probe/config helpers, and many `ahc_*_setup()` routines.

Control flow: bus glue locates an identity via `ahc_find_pci_device()`, which composes a 64-bit ID and matches masks while rejecting unsupported or unconnected functions. `ahc_pci_config()` runs the selected setup, powers D0, maps registers, disables interrupts, enables bus mastering and optional DAC, initializes the softc, records BIOS/default state, resets the chip, configures DT/CRC and DMA/cache settings, checks SEEPROM/external port data, applies defaults if needed, probes external SCB RAM, snapshots PCI/chip registers, calls `ahc_init()`, and maps interrupts.

State and persistence: runtime state includes `ahc->chip`, `features`, `bugs`, `flags`, channel, instruction RAM size, SCSI IDs, termination flags, SEEPROM copy, PCI cache size, parity counters, and `bus_softc.pci_softc` snapshots. It reads SEEPROM and may later support writes through proc code; this file itself primarily reads and configures hardware registers.

Dependencies and integration: depends on local register definitions, inline accessors, 93cx6 SEEPROM helpers, PCI config wrappers from OS glue, and core initialization/reset functions. It feeds the SCSI-facing layer with hardware capabilities and saved state.

Risks: broad hardware matrix with many revision-specific bug flags; ID mask mistakes can bind unsupported RAID/SISL devices; termination and cable detection directly affect bus electrical stability; SEEPROM checksum/default fallback can alter negotiation and reset behavior; external SCB RAM probing intentionally toggles parity/error registers; PCI parity storm handling disables checking after a threshold.

Test signals: adapter/revision matrix probing, unknown generic ID handling, SEEPROM checksum success/failure, BIOS scratch fallback, Ultra/Ultra2/Ultra160 negotiation defaults, cable/termination combinations, external SRAM presence/absence, register-access validation, PCI parity interrupt path, reset/resume restoration, and unsupported RAID ID rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.h

Purpose: PCI identity constant catalog for AIC7xxx-supported Adaptec controllers and chips. It defines the 64-bit composed IDs and masks consumed by Linux PCI ID tables and the common PCI identity matcher.

Important APIs/types/functions: this header has no functions or structs; it exports macros such as `ID_ALL_MASK`, `ID_DEV_VENDOR_MASK`, `ID_9005_GENERIC_MASK`, `ID_9005_SISL_MASK`, `ID_AIC7850`, `ID_AHA_2940`, `ID_AIC7890`, `ID_AHA_29160`, `ID_AIC7899`, and many board-specific subsystem IDs. Each ID packs device, vendor, subsystem device, and subsystem vendor into the format produced by `ahc_compose_id()` in `aic7xxx_pci.c`.

Control flow role: `aic7xxx_osm_pci.c` uses these macros to build the kernel-facing `pci_device_id` table. `aic7xxx_pci.c` uses the same macros in `ahc_pci_ident_table` with masks and setup callbacks. Exact IDs match known boards; vendor/device masks permit generic chip probes; special masks exclude SISL/container RAID-style devices.

State and persistence: none. These are compile-time constants that determine probe eligibility and variant identification.

Dependencies and integration: included by both OS PCI glue and common PCI setup code. The constants must remain synchronized with Linux PCI matching macros such as `ID_C()`/`ID16()` and the composed-ID layout in `ahc_compose_id()`.

Risks: a wrong constant or mask can prevent a supported adapter from binding or cause the driver to bind hardware that needs different firmware/termination rules. Generic masks trade coverage for specificity, so ordering in `ahc_pci_ident_table` matters. Some names represent board families rather than single revisions, so feature setup must be validated in the matching C file.

Test signals: compile-time reference checks from both PCI tables, PCI modalias generation, boot probing on representative boards, negative tests for SISL/RAID IDs, and comparison against known device/subsystem ID inventories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_proc.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_proc.c

Purpose: `/proc`/host info support for the `aic7xxx` driver. It formats adapter, SEEPROM, negotiation, and per-device queue state for userspace and implements a write path for replacing serial EEPROM configuration.

Important APIs and functions: external functions are `ahc_proc_write_seeprom()` and `ahc_linux_show_info()`. Internal helpers are `ahc_calc_syncsrate()`, `ahc_format_transinfo()`, `ahc_dump_target_state()`, and `ahc_dump_device_state()`. It also carries the SCSI sync-rate exception table used for display formatting.

Control flow: `ahc_linux_show_info()` prints driver version, controller description, controller info, allocated SCBs, SG length, raw SEEPROM words if present, and then iterates targets/channels to dump user/goal/current transfer settings plus active LUN queue statistics. Device lookup is through `scsi_device_lookup_by_target()`. `ahc_proc_write_seeprom()` locks and pauses the adapter, validates buffer size and checksum, prepares a PCI or VL SEEPROM descriptor, acquires the SEEPROM if needed, writes the provided config, rereads it into `ahc->seep_config`, releases resources, unpauses, and returns bytes written or an error.

State and persistence: show path reads runtime negotiation state, `ahc->seep_config`, SCB counts, and `ahc_linux_device` counters. The write path persists data to serial EEPROM hardware and updates the in-memory copy. It mutates adapter pause state while writing.

Dependencies and integration: uses Linux `seq_file` output, SCSI target/device APIs, `aic7xxx_93cx6` SEEPROM helpers, register definitions for PCI/VL SEEPROM control, and host template `.show_info`/`.write_info` hooks from `aic7xxx_osm.c`.

Risks: SEEPROM writes are hardware-persistent and can make adapters misconfigured if the caller supplies wrong but checksummed data. The function requires exact `struct seeprom_config` size and checksum but not semantic validation. Proper pause/unpause and lock handling are critical. `scsi_device_lookup_by_target()` references should normally be paired with put operations; this legacy code does not show that in the loop.

Test signals: read `/proc/scsi/aic7xxx/*` with and without SEEPROM, verify transfer formatting for async/sync/wide/DT modes, exercise multi-channel target iteration, test rejected writes for wrong length/checksum/unsupported adapter/no SEEPROM, and validate successful write/reread on controlled hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/Makefile

Purpose: host-tool build recipe for `aicasm`, the userland assembler that converts AIC7xxx sequencer source into generated firmware/register artifacts used by the kernel driver.

Important targets and variables: `PROG=aicasm`, `OUTDIR`, `CSRCS`, `YSRCS`, `LSRCS`, `GENHDRS`, `GENSRCS`, `SRCS`, `LIBS=-ldb`, `AICASM_CFLAGS`, `LEX=flex`, `YACC=bison`, and `YFLAGS=-d`. Targets build `$(PROG)`, create `$(OUTDIR)`, generate `aicdb.h`, clean generated files, run bison for `aicasm_gram.y` and `aicasm_macro_gram.y`, and run flex for `aicasm_scan.l` and `aicasm_macro_scan.l`.

Control flow: building `$(PROG)` depends on output directory, generated headers, and all C/generated sources. `aicdb.h` is generated by probing common Berkeley DB 1.85 compatibility header locations under `/usr/include`. Bison emits parser C and headers, with the macro parser using prefix `mm`; flex emits scanners, with the macro scanner using prefix `mm`. `DEBUG` adds parser/scanner debug flags and symbols.

State and persistence: generated files are written under `OUTDIR`, including parser/scanner outputs, `aicdb.h`, and the `aicasm` binary. `clean-files` enumerates generated artifacts removed by `clean`.

Dependencies and integration: depends on host C compiler (`HOSTCC` preferred), flex, bison, Berkeley DB compatibility library/header, standard userland includes, and local source files. It deliberately overrides kernel CFLAGS because the assembler is a host userland program, not a kernel object.

Risks: host environments without `db_185.h` still create an `aicdb.h` containing only an error message line, likely causing later compile failure rather than failing immediately. The recipe assumes system include paths and `-ldb` ABI compatibility. Generated files under configurable `OUTDIR` must be visible to CFLAGS and dependencies.

Test signals: clean host build, build with `OUTDIR` outside source directory, build with `HOSTCC`, build with `DEBUG=1`, missing Berkeley DB dev package behavior, and regeneration after grammar/scanner edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.c

Purpose: main program for the AIC7xxx sequencer assembler. It parses command-line options, opens outputs, drives the lexer/parser, tracks generated instructions, conditional patch metadata, critical sections, include paths, and emits generated C/register/listing files.

Important APIs/types/functions: defines `patch_t`, global output/search/scope/program state, and functions `main()`, `usage()`, `back_patch()`, `output_code()`, `dump_scope()`, `emit_patch()`, `output_listing()`, `check_patch()`, `stop()`, `seq_alloc()`, `cs_alloc()`, `scope_alloc()`, and `process_scope()`. Externally visible helpers are declared in `aicasm.h`.

Control flow: `main()` initializes queues/stacks, creates root scope, parses options (`-I`, `-o`, `-r`, `-p`, `-i`, `-l`, debug), opens the symbol table, includes the source file, and runs `yyparse()`. On success it validates scope closure, processes/dumps scopes to build patch entries, backpatches forward branches, emits code/register/listing outputs as requested, and exits through `stop()`. `output_code()` writes `seqprog[]`, patch function wrappers for conditionals, patch table, and critical-section table. `output_listing()` optionally asks for conditional values and prints source with generated instruction bytes after patch filtering.

State and persistence: in-memory state includes `seq_program`, `patches`, `cs_tailq`, `scope_stack`, `patch_functions`, include search paths, mode globals, and output file handles. Persistent outputs are generated C code, register dumps, diagnostic functions, and listings. On error, `stop()` closes and unlinks partially generated output files.

Dependencies and integration: depends on parsers/scanners generated from `aicasm_gram.y` and scanner files, symbol-table functions in `aicasm_symbol.c`, instruction formats from `aicasm_insformat.h`, BSD queue macros, regex and DB support indirectly, and host stdio/unistd.

Risks: listing generation can block for interactive conditional answers. Include-path list insertion is head-first, which affects search order. Error cleanup relies on global filename/file pointers. Patch skip math in `process_scope()` is subtle and directly controls runtime firmware patching.

Test signals: assemble known `.seq` files, compare generated `seqprog[]` and patch tables to shipped outputs, test forward labels and nested if/else scopes, exercise partial-output cleanup on parse errors, generate listings non-interactively, and run with/without optional outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.h

Purpose: shared interface for the `aicasm` assembler program, parser, scanner, macro expander, and symbol code. It exposes global assembly state and allocator/processing functions used across generated and handwritten components.

Important APIs and types: defines `path_entry_t`, `include_type` (`QUOTED_INCLUDE`, `BRACKETED_INCLUDE`, `SOURCE_FILE`), `SLIST_HEAD(path_list, path_entry)`, and extern globals `search_path`, `cs_tailq`, `scope_stack`, `patch_functions`, `includes_search_curdir`, `appname`, `stock_include_file`, `yylineno`, `yyfilename`, `prefix`, `patch_arg_list`, `versions`, `src_mode`, and `dst_mode`. Declared functions include `stop()`, `include_file()`, `expand_macro()`, `seq_alloc()`, `cs_alloc()`, `scope_alloc()`, and `process_scope()`.

Control flow role: generated parsers call these declarations to allocate instructions, scopes, and critical sections; scanners call `include_file()` and macro expansion paths; all components use `stop()` for fatal diagnostics and cleanup. The include type enum lets scanner/parser code distinguish quote includes, bracket includes, and top-level source inclusion.

State and persistence: only declares state. The actual state is owned mostly by `aicasm.c` and parser/scanner modules. Persistent behavior is indirect through output files managed by the main program.

Dependencies and integration: includes local BSD-style `queue.h` and forward-declares `struct symbol` so it can reference symbol APIs without forcing full symbol definitions. It is included by `aicasm.c`, grammars, scanners, and symbol/macro code.

Risks: broad extern global state couples all assembler modules and makes reentrancy impossible. Parser-generated code and handwritten code must agree on global names such as `src_mode`/`dst_mode` and `yyfilename`. `stop()` is noreturn; callers depend on it for control-flow termination after errors.

Test signals: full host build after parser/scanner generation, warnings for missing prototypes or mismatched globals, assemble sources with includes/macros/conditionals, and failure-path tests confirming `stop()` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_gram.y -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_gram.y

Purpose: primary Bison grammar and semantic engine for AIC7xxx sequencer assembly language. It parses register definitions, constants, macros, SRAM/SCB layouts, labels, conditionals, critical sections, and sequencer instructions, then constructs typed symbols and encoded instruction objects.

Important APIs and functions: grammar tokens cover directives (`include`, `prefix`, `patch_arg_list`, `version`), register fields/masks/enums, macros, memory regions, labels, conditionals, and opcodes. Semantic helpers include `process_field()`, `initialize_symbol()`, `add_macro_arg()`, `add_macro_body()`, `process_register()`, `format_1_instr()`, `format_2_instr()`, `format_3_instr()`, `test_readable_symbol()`, `test_writable_symbol()`, `type_check()`, `make_expression()`, `add_conditional()`, `add_version()`, `is_download_const()`, and `is_location_address()`.

Control flow: parser actions build symbols as declarations are parsed, maintain current register/SRAM/SCB context, track source/destination register modes, increment `instruction_ptr` as instructions are emitted, and push/pop scopes for conditional firmware patches. ALU, move, shift, branch, test, compare, and pseudo-instructions are normalized into instruction formats. Forward branch labels are recorded for later backpatching by `aicasm.c`.

State and persistence: grammar-owned globals include current symbol/context pointers, special register references (`A`, mode pointer, allones/allzeros/none/sindex), instruction pointer, SRAM/SCB offsets, downloaded constant count, critical-section flag, enum counters, prefix, patch argument list, version text, and filename. It persists only through objects appended to main-program queues and generated output later.

Dependencies and integration: depends on the lexer for tokens, symbol table APIs, instruction bitfield definitions, queue macros, and `stop()` for fatal errors. Its symbol metadata feeds register dump and generated firmware patch tables.

Risks: expression values are largely 8-bit masked in instruction contexts; incorrect type masks can reject valid firmware or permit invalid register bits. Mode tracking is updated only for recognized mode-pointer operations. Scope/patch semantics are sensitive to nested if/else structure. Several diagnostics exit immediately, so parser recovery is minimal.

Test signals: parse known `aic7xxx.seq`/`.reg` inputs, compare generated instruction bytes, validate field/mask type checking, test undefined/redefined symbols, register mode restrictions, forward/backward branches, downloaded constants, nested conditionals, macro definitions, and critical-section balance errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_gram.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_insformat.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_insformat.h

Purpose: binary instruction layout definitions for the AIC7xxx sequencer assembler. It maps assembler semantic fields into endian-sensitive 32-bit instruction encodings and defines opcode constants used by grammar formatting functions.

Important APIs and types: defines `struct ins_format1` through `struct ins_format6` for 8-bit ALU, shift/rotate, branch, 16-bit ALU, 16-bit branch, and far branch formats. `union ins_formats` overlays these formats with raw bytes and integer access. `struct instruction` stores an encoded instruction, source line, optional patch label, and queue linkage. Opcode macros include `AIC_OP_OR`, `AND`, `XOR`, `ADD`, `ADC`, `ROL`, `BMOV`, `MVI16`, branch opcodes, pseudo shift/rotate opcodes, 16-bit opcodes, far branch opcodes, and `AIC_OP_CMPXCHG`.

Control flow role: `aicasm_gram.y` allocates `struct instruction` objects and fills the appropriate bitfield format in `format_1_instr()`, `format_2_instr()`, and `format_3_instr()`. `aicasm.c` later emits `format.bytes[]` in host-endian-aware order to generated C output and listings.

State and persistence: each instruction object carries the generated encoding and metadata needed for listings and backpatching. No global state is defined here.

Dependencies and integration: includes `<asm/byteorder.h>` and uses `__LITTLE_ENDIAN` to choose bitfield ordering. It depends on queue macros indirectly through `STAILQ_ENTRY` availability from including contexts and on `struct symbol` forward visibility through included assembler headers.

Risks: C bitfield layout is compiler- and endian-sensitive; the code mitigates endian order but still assumes compatible compiler behavior. Opcode constants must match sequencer hardware. Emission order must stay synchronized with bitfield definitions. Incorrect parity bit use affects downloaded constants.

Test signals: assemble small opcode fixtures and compare exact bytes on little- and big-endian hosts, validate branch address field limits, compare generated shipped sequencer headers, and build with compilers used for kernel host tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_insformat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_gram.y -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_gram.y

Purpose: secondary Bison parser for macro invocations in the AIC7xxx assembler. It parses a single macro call, validates argument count, and records replacement text for each formal macro argument.

Important APIs and functions: token inputs are `T_SYMBOL` for the macro symbol and `T_ARG` for raw argument text. Grammar nonterminals are `macrocall` and `macro_arglist`. Helpers are `add_macro_arg()`, `mmlex()`, and `mmerror()`, with parser prefix `mm` from the Makefile.

Control flow: the scanner returns a macro symbol followed by `(`, argument tokens, commas, and `)`. The parser stores the macro in `macro_symbol`, accumulates argument count, calls `add_macro_arg()` for each argument position, checks the count against `macro_symbol->info.macroinfo->narg`, clears state, and accepts. `add_macro_arg()` walks the macro's formal argument queue to the requested position and stores duplicated replacement text.

State and persistence: transient `macro_symbol` points at the macro being invoked. Persistent mutation is per-argument `replacement_text` inside the macro symbol's `macroinfo` argument list, consumed by macro expansion code outside this file.

Dependencies and integration: includes assembler globals, symbol definitions, instruction format header, and queue macros. It depends on `aicasm_macro_scan.l` for raw argument tokenization and on macro definitions created by the primary grammar.

Risks: replacement text is stored on the macro symbol itself, so nested or concurrent macro expansion would be unsafe. Argument count errors distinguish too few after parse and too many inside `add_macro_arg()`. Diagnostics use `stop()`, so no parser recovery is attempted.

Test signals: macro calls with zero, one, and multiple arguments; too many/few arguments; arguments containing nested parentheses; invalid non-macro symbol invocation; repeated macro expansion verifying replacement text refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_gram.y -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_scan.l -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_scan.l

Purpose: flex scanner for the macro-invocation sub-parser. It tokenizes macro call text, preserving raw argument strings while respecting nested parentheses.

Important APIs and state: defines `MAX_STR_CONST`, `string_buf`, `string_buf_ptr`, `parren_count`, `buf`, and `mmlineno`. Lexical state `ARGLIST` handles tokens inside macro parentheses. It returns `T_SYMBOL`, `T_ARG`, punctuation tokens, and reports fatal errors through `stop()`. `mmwrap()` treats EOF in a macro call as an error.

Control flow: initial state recognizes `WORD(`, looks up the symbol, verifies it is a `MACRO`, pushes back `(`, resets parenthesis count, enters `ARGLIST`, and returns `T_SYMBOL`. In `ARGLIST`, whitespace is skipped, the first `(` starts argument collection, nested parentheses are copied into the current argument, `)` either returns a pending `T_ARG` by pushing the paren back or closes the call, comma similarly returns pending argument text or the comma token, and `MCARG` appends raw non-delimiter text to `string_buf`.

State and persistence: scanner state is transient per macro call. It writes argument text into a fixed buffer and exposes it via `mmlval.str`; persistence happens later when the parser duplicates the text into macro metadata.

Dependencies and integration: includes `aicasm.h`, `aicasm_symbol.h`, generated `aicasm_macro_gram.h`, queue macros, and C regex/stdio headers. It is generated with the `mm` prefix so it can coexist with the primary scanner/parser.

Risks: fixed `MAX_STR_CONST` and no explicit bounds checks while appending argument text can overflow on very long macro arguments. The argument token pattern excludes spaces and delimiters, so formatting-sensitive macro arguments may not survive. EOF is fatal by design. Replacement parsing is not reentrant.

Test signals: macro invocations with nested parentheses, empty argument list, comma handling, invalid characters, non-macro symbols, EOF/truncated call, and long argument fuzzing to expose buffer limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_macro_scan.l -->
