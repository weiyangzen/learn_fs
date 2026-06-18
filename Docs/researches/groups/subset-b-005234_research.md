# subset-b-005234 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_scan.l -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_scan.l

Purpose: flex lexer for the host-side aic7xxx/aic79xx sequencer assembler. It tokenizes register definition files, sequencer assembly, C-style conditional expressions, include directives, string literals, and assembler-local `#define` macros before handing tokens to `aicasm_gram.y`.

Important APIs/types/functions: scanner start conditions include `COMMENT`, `CEXPR`, `INCLUDE`, `STRING`, `MACRODEF`, `MACROARGLIST`, `MACROCALLARGS`, and `MACROBODY`. `include_file()` opens source or include files, pushes scanner buffers on an `SLIST` include stack, and resets `yylineno`/`yyfilename`. `expand_macro()` expands macro bodies by `unput()`ing replacement text backwards. `next_substitution()` uses compiled regexes from macro arguments to locate argument substitutions. `yywrap()` unwinds include buffers and closes input files.

Control flow: top-level rules discard comments and whitespace, return parser tokens for assembler keywords/opcodes/register-definition keywords, parse octal/decimal/hex numbers, capture strings, and create or look up symbols through `symtable_get()`. Include rules switch into include parsing until `>` or the closing quote. Macro definitions capture either simple or argument macros; macro invocations temporarily run the macro-argument parser, then expand the stored macro body back into the scanner input stream.

State and persistence: scanner state is process-local: `string_buf`, `parren_count`, `quote_count`, include-stack entries, current file name, and flex buffers. No persistent state is written directly; it populates parser values and symbol-table references used by later generated outputs.

Dependencies and integration: depends on flex, the generated grammar header, `aicasm_symbol` symbol table, `queue.h` list macros, `search_path`, `includes_search_curdir`, and fatal `stop()` handling from `aicasm.c`.

Risks and test signals: fixed `MAX_STR_CONST` and unchecked `string_buf_ptr++` writes can overflow on very long strings, macro bodies, or expressions. Macro expansion depends on reverse `unput()` ordering and regex substitutions, so nested/argument macros are high-risk. Include behavior should be tested for quoted versus bracket includes, missing files, nested includes, comments, escaped macro newlines, numeric formats, and invalid-character diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_scan.l -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.c

Purpose: implements the assembler symbol table and generated register/debug header emission for the aic7xxx sequencer build tools.

Important APIs/types/functions: `symtable_open()` creates an in-memory Berkeley DB hash table. `symtable_get()` returns existing symbols or creates `UNINITIALIZED` symbols while tracking reference counts. `symbol_delete()` frees type-specific payloads. `symlist_add()`, `symlist_search()`, `symlist_free()`, and `symlist_merge()` manage symbol lists. `symtable_dump()` emits generated `#define`s, downloaded constants, exported labels, and optional debug register print helpers through `aic_print_*()` helpers.

Control flow: parsing code creates and mutates `symbol_t` records. At dump time the DB is iterated into sorted buckets for registers, masks/fields/enums, constants, downloaded constants, aliases, and exported labels. Debug print tables are emitted before masks and aliases are folded next to their parent register entries. The final output is ordered register/address definitions, field/mask definitions, constants, download constants, and label offsets.

State and persistence: runtime state is the static `DB *symtable` and heap-owned `symbol_t` payloads. Persistence is indirect: generated C/header output is written to caller-supplied `FILE *` handles, while `symtable_close()` walks and deletes all stored symbols.

Dependencies and integration: depends on `aicdb.h`/`dbopen`, `queue.h`, symbol metadata from `aicasm_symbol.h`, global `versions`, `prefix`, `stock_include_file`, and `appname` from the assembler.

Risks and test signals: the DB stores raw symbol pointers, so ownership/lifetime bugs corrupt all later generation. `symtable_get()` increments `count` on each lookup, and debug generation uses `count == 1` to suppress unused register definitions, making accidental extra lookups behaviorally visible. Tests should cover duplicate symbols, sorted field/register emission, aliases, exported labels, macro symbols, cleanup after partial parse failure, and generated debug code with and without `dfile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.h

Purpose: shared type contract for the aic sequencer assembler symbol table, expression metadata, macro metadata, labels, conditionals, critical sections, and patch scopes.

Important APIs/types/functions: `symtype` distinguishes registers, aliases, SCB/SRAM locations, fields, masks, enums, constants, labels, conditionals, and macros. `struct reg_info`, `field_info`, `const_info`, `alias_info`, `label_info`, `cond_info`, and `macro_info` define symbol payloads. `expression_t`, `symbol_ref_t`, `critical_section_t`, `patch_info_t`, and `scope_t` describe parser/compiler state. Prototypes expose symbol-table and symbol-list operations plus `symtable_dump()`.

Control flow: no executable control flow lives here, but parser and code-generation files use these structures to build scopes, track referenced symbols, record generated instruction patch sites, and emit register definitions. The list head declarations fix which BSD-style queue primitive each state structure uses.

State and persistence: this header defines heap-owned structures persisted for the assembler process lifetime. Symbols point to one active union payload according to `type`; macro args own regex and replacement strings; scopes carry patch arrays and nested scope queues.

Dependencies and integration: includes local `queue.h` and requires standard regex and `FILE` declarations through including C files. It is consumed by the scanner, grammar, macro grammar, symbol implementation, and main assembler.

Risks and test signals: the union payload is not self-validating, so every `type` transition must allocate/free the matching payload. Macro arg regex lifetime and replacement text cleanup rely on scanner/parser discipline. Compile tests for the host tool plus assembler fixture inputs covering conditionals, nested scopes, critical sections, aliases, enums, and macros are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aicasm/aicasm_symbol.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aiclib.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aiclib.h

Purpose: compatibility helper header for aic7xxx/aic79xx code, carrying SCSI sense structures/constants, endian byte conversion, disk geometry division, and PCI ID table generation macros.

Important APIs/types/functions: `struct scsi_sense` and `struct scsi_sense_data` define legacy SCSI REQUEST SENSE layouts and sense-key flags. `aic_sector_div()` wraps Linux `sector_div()` for capacity geometry math. `scsi_4btoul()` converts four big-endian bytes to a host `uint32_t`. `GETID`, `ID_C`, `ID2C`, `IDIROC`, and `ID16` help generate compressed PCI ID table entries for related Adaptec devices.

Control flow: only inline helpers and macros execute. `aic_sector_div()` destructively divides a local sector count and returns the quotient. `scsi_4btoul()` is used by SCSI IU helpers for lengths and packet-failure codes.

State and persistence: no mutable state or persistence. The header defines constants compiled into the driver.

Dependencies and integration: expects Linux kernel types such as `sector_t`, `uint8_t`, PCI class constants, and the aic driver’s `ID()`/mask macros to be available from including files.

Risks and test signals: `scsi_4btoul()` assumes byte pointers contain at least four bytes and shifts `uint8_t` values through integer promotion. PCI ID macros are dense and easy to misuse if bit packing changes. Build coverage of aic7xxx/aic79xx PCI tables, sense-data consumers, and large-disk geometry paths are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aiclib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/cam.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/cam.h

Purpose: Linux-port compatibility header for FreeBSD CAM status, async notification, and data-direction values used by aic7xxx/aic79xx driver code.

Important APIs/types/functions: `cam_status` enumerates request completion, abort, timeout, SCSI status, queue freeze, requeue, and host/bus error codes. `ac_code` enumerates asynchronous events such as device found/lost, bus reset, transfer negotiation, and inquiry changes. `ccb_flags` maps CAM transfer directions onto Linux DMA constants.

Control flow: no runtime flow; constants are consumed by driver logic that was originally structured around CAM status names.

State and persistence: no mutable state. Status values are compiled into command-completion and error-handling paths.

Dependencies and integration: includes `<linux/types.h>` and depends on Linux DMA direction constants. It integrates legacy CAM naming with Linux SCSI midlayer behavior in surrounding aic driver files.

Risks and test signals: semantic drift between CAM names and Linux SCSI error handling can cause incorrect queueing or retry behavior if callers assume FreeBSD semantics. Regression signals are command timeout handling, queue-freeze/requeue cases, bus reset notifications, and transfer-negotiation event paths in aic7xxx/aic79xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/cam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/queue.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/queue.h

Purpose: local copy of BSD `queue.h` macros used by the aic assembler host tools and imported driver code for intrusive linked-list data structures.

Important APIs/types/functions: defines `SLIST_*`, `STAILQ_*`, `BSD_LIST_*`/`LIST_*`, `TAILQ_*`, and `CIRCLEQ_*` head/entry/access/manipulation macros. Operations include initialization, empty checks, traversal, head/tail/after/before insertion, removal, and forward/reverse iteration where supported.

Control flow: all behavior is macro-expanded at call sites. Singly linked lists and tail queues require traversal for arbitrary removal; doubly linked list/tail/circle queues remove in O(1) using embedded back pointers.

State and persistence: state is embedded in user structs through entry macros and in caller-owned head structs. The macros do not allocate, free, lock, or persist anything.

Dependencies and integration: standalone C preprocessor header. The aicasm scanner/symbol code relies on `SLIST`, `STAILQ`, and `TAILQ` declarations for include stacks, symbol lists, macro args, critical sections, and scopes.

Risks and test signals: macros perform no validation, can evaluate arguments multiple times in some patterns, and corrupt lists if entries are double-inserted or removed from the wrong list. `BSD_LIST_HEAD` is renamed to avoid Linux `LIST_HEAD` conflicts while still defining `LIST_*` operation names. Test signals are host-tool compilation, parser fixtures exercising list insert/remove/merge paths, and sanitizer/debug builds that catch corrupted intrusive links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_iu.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_iu.h

Purpose: defines SCSI information-unit status header layout and constants for packetized SCSI status, sense data, packet-failure codes, and task-management flags.

Important APIs/types/functions: `struct scsi_status_iu_header` models a status IU with flags, status, sense length, packet-failure length, and variable packet-failure data. `SIU_PKTFAIL_CODE()` uses `scsi_4btoul()` to decode packet failure codes. `SIU_SENSE_OFFSET()` calculates sense-data offset depending on `SIU_RSPVALID`. Constants define packet-failure reasons and task-management function bits.

Control flow: no functions beyond macros. Consumers inspect IU flags, compute offsets, and branch on task-management or packet-failure values.

State and persistence: no state; this is a wire-format contract.

Dependencies and integration: depends on `u_int8_t` and `scsi_4btoul()` from the aic support headers. Used by packetized SCSI handling in aic7xxx/aic79xx code.

Risks and test signals: variable-length IU parsing is bounds-sensitive; callers must ensure buffers contain the advertised packet-failure and sense lengths before using the offsets. Tests should include status IUs with response data absent/present, malformed lengths, packet-failure codes, and task-management responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_iu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_message.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_message.h

Purpose: public-domain SCSI parallel interface message constant header used by aic7xxx/aic79xx negotiation and message-in/message-out handling.

Important APIs/types/functions: defines one-byte messages such as save/restore data pointer, disconnect, reject, and noop; two-byte tagged queue and wide-residue messages; identify-message helpers `MSG_IDENTIFY()`, `MSG_ISIDENTIFY()`, and `MSG_IDENTIFY_LUNMASK`; and extended message lengths/option bits for SDTR, WDTR, and PPR negotiation.

Control flow: no executable code. Macros encode and decode message bytes in protocol state machines.

State and persistence: no mutable state; constants reflect SCSI bus protocol values.

Dependencies and integration: consumed by low-level aic SCSI message negotiation code and sequencer interaction paths.

Risks and test signals: incorrect constants directly break SCSI negotiation. `MSG_IDENTIFY(lun, disc)` assumes the caller masks or bounds LUN values appropriately. Protocol tests should cover identify messages, tagged queue messages, sync/wide/PPR negotiation combinations, message reject fallback, and legacy devices that do not support optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/scsi_message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Kconfig

Purpose: declares build-time configuration for the Adaptec AIC94xx SAS/SATA 3Gb/s PCI-X driver.

Important APIs/types/functions: `SCSI_AIC94XX` is a tristate driver symbol depending on `PCI` and `HAS_IOPORT`; it selects `SCSI_SAS_LIBSAS` and `FW_LOADER`. `AIC94XX_DEBUG` is a boolean depending on the driver and defaults to enabled.

Control flow: no runtime flow. Kconfig selects whether the driver is built in, modular, or omitted and whether debug instrumentation is compiled.

State and persistence: state is persisted in the kernel `.config`. Enabling debug changes compile flags through the Makefile and exposes extra console logging/dump code.

Dependencies and integration: integrates the driver with PCI, libsas, and firmware loading infrastructure. The selected firmware loader is required for BIOS/sequence-related firmware paths in the driver.

Risks and test signals: missing dependencies show as link/build failures in libsas or firmware APIs. Debug defaulting to `y` increases kernel log verbosity. Build tests should cover `SCSI_AIC94XX=m/y`, `PCI=n`, `HAS_IOPORT=n`, `FW_LOADER` availability, and debug on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Makefile

Purpose: Kbuild recipe for the composite `aic94xx` kernel module/object.

Important APIs/types/functions: `ccflags-$(CONFIG_AIC94XX_DEBUG)` defines `ASD_DEBUG` and `ASD_ENTER_EXIT`. `obj-$(CONFIG_SCSI_AIC94XX)` builds `aic94xx.o`. `aic94xx-y` links init, hardware interface, register access, SDS/flash, sequencer, dump, SCB, device, TMF, and task files.

Control flow: no runtime flow; Kbuild evaluates the object list and compile flags.

State and persistence: build graph state is derived from `.config`; no runtime state.

Dependencies and integration: this file is the folder-level integration point joining the driver’s PCI/libsas core, hardware bring-up, firmware/SDS parsing, command building, task management, and debug dumping into one module.

Risks and test signals: object-list drift causes unresolved symbols such as `asd_execute_task()`, `asd_read_ocm()`, `asd_init_seqs()`, or TMF callbacks. Build tests with debug enabled/disabled and module/built-in variants are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx.h

Purpose: top-level public internal header for the aic94xx driver, providing driver identity, debug macros, shared cache declarations, and cross-file libsas callback prototypes.

Important APIs/types/functions: defines `ASD_DRIVER_NAME`, `ASD_DRIVER_DESCRIPTION`, `asd_printk()`, `ENTER`/`EXIT`, `ASD_DPRINTK`, and `AIC94XX_SCB_TIMEOUT`. Declares `asd_dma_token_cache`, `asd_ascb_cache`, opaque `asd_ha_struct`/`asd_ascb`, SDS readers, device found/gone hooks, task execution, DMA mode setup, TMFs, nexus clear functions, and PHY control.

Control flow: no direct runtime flow. Macros compile into logging paths and timeouts used by SCB posting and error recovery.

State and persistence: exposes global slab caches created at module init and destroyed at module exit. All other state is held by structures declared in lower headers.

Dependencies and integration: includes Linux slab/ctype and `<scsi/libsas.h>`. It is included by all aic94xx implementation files to keep callbacks and driver naming consistent.

Risks and test signals: prototype drift across implementation files breaks module builds. Debug macro configuration materially changes logging volume. Integration tests should verify libsas callback registration, SCB timeout behavior, and debug/no-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dev.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dev.c

Purpose: manages hardware Device Descriptor Blocks (DDBs) for libsas domain devices discovered behind an AIC94xx adapter.

Important APIs/types/functions: `asd_dev_found()` and `asd_dev_gone()` are libsas callbacks. `asd_get_ddb()` allocates and clears a DDB bitmap entry. `asd_free_ddb()` marks a DDB unused. `asd_init_target_ddb()`, `asd_init_sata_pm_ddb()`, `asd_init_sata_pm_port_ddb()`, `asd_init_sata_tag_ddb()`, and `asd_init_sata_pm_table_ddb()` write target, SATA, NCQ tag, and port-multiplier context fields. `asd_set_dmamode()` configures SATA NCQ tag masks/depth.

Control flow: on discovery, `asd_dev_found()` takes `ddb_lock`, selects initialization by `dev_type`/protocol, writes DDB site fields through register helpers, and stores the DDB number in `dev->lldd_dev`. SATA/STP devices get SATA status and NCQ state; port multipliers get companion table/port DDBs. On removal, sister DDBs are freed before the primary context and `lldd_dev` is cleared.

State and persistence: DDB allocation state lives in `hw_prof.ddb_bitmap` and hardware DDB context memory. The software pointer `domain_device->lldd_dev` persists until device removal. No disk persistence exists.

Dependencies and integration: depends on libsas domain devices, libata NCQ helpers, SMP report-phy-SATA data, DDB structure offsets from `aic94xx_sas.h`, and register helpers from `aic94xx_reg.h`.

Risks and test signals: DDB allocation/freeing must stay balanced, especially for SATA tag and PM sister DDBs. `asd_set_dmamode()` disables NCQ if tag-DDB allocation fails, making low-memory behavior visible. Tests should cover SAS targets, STP/SATA, SATA PM and PM ports, NCQ capable/incapable devices, device removal, and DDB exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.c

Purpose: debug-only register and frame dump implementation for AIC94xx central sequencer (CSEQ), link sequencers (LSEQ), scratch pages, mode pages, and received frames.

Important APIs/types/functions: compiled under `ASD_DEBUG`. `asd_dump_seq_state()` dumps CSEQ plus selected LSEQs. `asd_dump_cseq_state()` prints ARP2, IOP, CIO, scratch, MIP, and MDP registers. `asd_dump_lseq_state()` prints per-link sequencer state across common and mode-specific pages. `asd_print_lseq_cio_reg()` handles table-driven LSEQ CIO register widths. `asd_dump_frame_rcvd()` logs IDENTIFY/FIS frame bytes under `frame_rcvd_lock`.

Control flow: error handlers call `asd_dump_seq_state()` after DMA/sequencer failures. It always dumps CSEQ and iterates `lseq_mask` through `for_each_sequencer()` for LSEQ state. Register print macros read byte/word/dword/qword values through the normal register accessor layer.

State and persistence: no persistent state. It observes live hardware registers and PHY `frame_rcvd` buffers, then writes kernel log output.

Dependencies and integration: depends on generated register definitions, `aic94xx_reg` accessors, `aic94xx_sas` structures, debug logging macros, and ISR error paths in `aic94xx_hwi.c`.

Risks and test signals: dump routines read large numbers of hardware registers, so using them on wedged hardware can amplify faults or log volume. Width/mode tables must match silicon register layout. Signals include debug builds, forced sequencer errors, frame-received dumps for SSP/STP, and ensuring no dump code is emitted when `ASD_DEBUG` is off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.h

Purpose: conditional interface for AIC94xx debug dump helpers.

Important APIs/types/functions: declares `asd_dump_seq_state()` and `asd_dump_frame_rcvd()` when `ASD_DEBUG` is compiled. Otherwise provides static inline no-op versions with the same signatures.

Control flow: no runtime control beyond compile-time selection. Callers can invoke dump helpers unconditionally without wrapping their own `#ifdef ASD_DEBUG`.

State and persistence: no state. Debug builds emit kernel logs; non-debug builds do nothing.

Dependencies and integration: requires visible `struct asd_ha_struct`, `struct asd_phy`, and `struct done_list_struct` declarations from surrounding headers. Used by hardware interrupt/error paths.

Risks and test signals: signatures must remain aligned with `aic94xx_dump.c` and call sites. Build tests with `CONFIG_AIC94XX_DEBUG=y` and disabled are the core signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_dump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.c

Purpose: hardware interface implementation for AIC94xx initialization, context memory setup, PHY enablement, SCB allocation/posting, done-list processing, interrupt handling, LED control, and chip reset.

Important APIs/types/functions: exported functions include `asd_init_hw()`, `asd_chip_hardrst()`, `asd_hw_isr()`, `asd_ascb_alloc_list()`, `asd_post_ascb_list()`, `asd_post_escb_list()`, `asd_enable_phys()`, `asd_turn_led()`, and `asd_control_led()`. Major internal helpers initialize sliding windows, phys, ports, SCB queues, done lists, empty data buffers, empty SCBs, sequencer firmware, and extended command/device context memory.

Control flow: `asd_init_hw()` configures PCI sliding windows, disables split-completion timer, reads OCM/flash, sizes/extends SCB and DDB context memory, obtains SAS addresses, initializes PHYs/ports/SCB/done/ESCB resources, hard-resets the chip, downloads sequencer code, and starts sequencers. Runtime interrupts read/ack `CHIMINT`, schedule done-list tasklets, and dispatch COM/DEV/INIT/HOST error handlers. Done-list tasklet entries find `asd_ascb`s by `tc_index`, stop timers, remove pending SCBs, and invoke completion callbacks.

State and persistence: maintains `MBAR0_SWB_SIZE`, `hw_prof` limits/bitmaps, PHY identify-frame DMA buffers, `seq` pending queue, `tc_index` map, done-list ring/toggle, EDB/ESCB arrays, context extension DMA tokens, and hardware registers. State is volatile and rebuilt on probe; firmware/flash data is read but not persisted here.

Dependencies and integration: depends on PCI config space, DMA pools/coherent memory, libsas PHY structures, sequencer firmware helpers in `aic94xx_seq.c`, SDS readers, register accessors, tasklet/timer APIs, and dump helpers.

Risks and test signals: initialization has many partial-allocation paths and `asd_init_hw()` callers must clean up through `asd_destroy_ha_caches()`. Error handlers mostly hard-reset and leave recovery marked `XXX`, so injected parity/DMA/ARP2 errors are high risk. SCB posting relies on pending counts, head swapping, DMA next pointers, and timers. Signals include probe/remove stress, interrupt storms, SCB timeout tests, DDB/SCB max module parameters, MSI/shared IRQ behavior, PHY enablement, and DMA-mask fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.h

Purpose: central hardware-interface data model for the AIC94xx driver, defining host adapter state, hardware profile, DMA tokens, active SCBs, sequencer queues, ports, and inline allocation/index helpers.

Important APIs/types/functions: defines `ASD_MAX_PHYS`, `struct asd_ha_addrspace`, `bios_struct`, `unit_element_struct`, `flash_struct`, `asd_phy_desc`, `asd_dma_tok`, `hw_profile`, `asd_ascb`, `asd_seq_data`, `asd_port`, and `asd_ha_struct`. Inline helpers allocate/free coherent DMA tokens, initialize ASCBS, manage `tc_index` bitmaps, and free single/list ASCBS. Prototypes expose hardware init, ISR, SCB posting, ESCB posting, PHY control, LED control, timeout, and reset functions.

Control flow: inline allocation helpers wrap slab and DMA APIs. `asd_tc_index_get/release/find()` are lock-required index-map operations used when posting and completing SCBs. `asd_ascb_free()` asserts list removal, releases the index, frees the DMA SCB, and returns the ASCB to cache.

State and persistence: `asd_ha_struct` owns PCI device binding, libsas HA, IO windows, hardware profile, PHY/port arrays, SCB DMA pool, sequencer state, BIOS status, and loaded firmware pointer. This is per-adapter runtime state, freed on remove.

Dependencies and integration: includes interrupts, PCI, DMA mapping, libsas, top-level aic94xx declarations, and SAS hardware structure definitions. It is shared by init, hwi, reg, task, TMF, SDS, and dump code.

Risks and test signals: helpers assume required locks and valid indices; freeing an ASCB with `tc_index == -1` or while still linked trips bugs or corrupts bitmaps. Per-adapter cleanup must mirror all allocations. Build and runtime tests should cover probe/remove, SCB allocation exhaustion, completion after timeout, EDB/ESCB teardown, and multiple adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_hwi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_init.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_init.c

Purpose: PCI driver, module lifecycle, libsas transport registration, sysfs attributes, BIOS update interface, resource mapping, and probe/remove orchestration for the AIC94xx driver.

Important APIs/types/functions: `aic94xx_init()` creates global caches, attaches the SAS transport, registers the PCI driver, and creates a driver `version` attribute. `asd_pci_probe()` enables PCI, allocates SCSI host and `asd_ha_struct`, sets DMA mask, maps BARs/IO ports, creates DMA pools, calls `asd_init_hw()`, requests IRQ/MSI, posts ESCBs, creates device attrs, registers the SAS HA, and starts scanning. `asd_pci_remove()` reverses those resources. `asd_store_update_bios()` validates requested firmware and calls flash update/verify helpers.

Control flow: probe is a staged setup with labeled error unwinding. Scan start enables configured PHYs; scan finish waits at least one second then drains libsas work. Remove unregisters libsas, disables interrupts, kills done-list tasklet, removes attrs, frees IRQ/MSI, turns off LEDs, hard-resets chip, frees pending queues/caches, unmaps IO, and disables PCI.

State and persistence: module globals include `use_msi`, transport template, and slab caches. Per-device state includes BAR mappings, SCSI host, sysfs attributes, BIOS status, and firmware image pointer. BIOS update/verify can persistently alter adapter flash via SDS helpers.

Dependencies and integration: integrates Linux PCI, SCSI host, libsas, sas_ata sysfs groups, firmware loader, DMA masks/pools, interrupts, and the hwi/SDS/seq/task/TMF implementation files.

Risks and test signals: BIOS update parsing uses sysfs input and firmware bytes; validation of PCI IDs, length, and checksum is critical. Probe unwinding must remain balanced across many labels. `asd_unregister_sas_ha()` calls both `sas_unregister_ha()` and host removal/put, so ordering matters. Test signals include module load/unload, probe failure injection at every stage, MSI and shared IRQ paths, sysfs attr reads, BIOS verify/update failure codes, and scan/discovery timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.c

Purpose: implements serialized register and internal-memory access for AIC94xx MMIO or legacy PIO mappings, including sliding-window management.

Important APIs/types/functions: public accessors are `asd_read_reg_byte/word/dword()`, `asd_write_reg_byte/word/dword()`, `asd_read_reg_string()`, and `asd_write_reg_string()`. Internal helpers perform raw byte/word/dword IO, compute SWA/SWB/SWC offsets, generate window-specific accessors, and `asd_move_swb()` pages sliding window B through PCI config space.

Control flow: reads/writes validate the internal address range, take `iolock`, choose SWA/SWB/SWC when the requested register is already mapped, or move SWB to cover the target register before accessing it. String reads/writes keep the lock while iterating byte accesses through private unlocked helpers.

State and persistence: updates `io_handle[0].swb_base` whenever SWB moves. Register writes mutate hardware state; no software persistence beyond current window base.

Dependencies and integration: depends on PCI config access, Linux IO primitives, memory barriers, `aic94xx_reg.h` constants, and `asd_ha_struct` IO mappings initialized in `aic94xx_init.c`/`aic94xx_hwi.c`.

Risks and test signals: all callers share one sliding window, so locking is essential. `BUG_ON()` range checks can crash the kernel on bad register constants. PIO mode masks offsets with `0xFF`, so it only works for the intended access window. Test signals include register access under concurrent interrupts/task paths, SWB movement across boundaries, string access crossing windows, MMIO versus IO-port mapping, and memory-barrier-sensitive hardware operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.h

Purpose: register-access contract and inline helpers for AIC94xx internal memory, PCI BAR sliding windows, DDB/SCB context sites, atomic DDB updates, context sizing, interrupt enable/disable, and DMA address writes.

Important APIs/types/functions: defines internal base addresses, BAR sizes, PCI config offsets, `OCM_BASE_ADDR`, and access prototypes. Macro-generated helpers implement OCM, DDB site, and SCB site byte/word/dword reads/writes. `asd_ddbsite_update_word()` and `_byte()` perform atomic compare/update via hardware atomic registers. `asd_write_reg_addr()` writes 64-bit DMA addresses. `asd_get_cmdctx_size()` and `asd_get_devctx_size()` derive context-memory sizes. `asd_disable_ints()` and `asd_enable_ints()` control interrupt masks.

Control flow: site helpers program `ALTCIOADR` plus `ADDBPTR` or `ASCBPTR`, then access `CTXACCESS`. Byte writes read/modify/write enclosing words. Atomic updates first verify old value, program old/new registers, poll `ATOMICSTATCTL`, and return success, parity error, or retry.

State and persistence: no standalone state, but helpers mutate hardware windows, context memory, interrupt masks, and DDB/SCB sites. `MBAR0_SWB_SIZE` is external state initialized during hardware setup.

Dependencies and integration: includes Linux IO, `aic94xx_hwi.h`, and generated `aic94xx_reg_def.h`. Used across device management, SCB/task/TMF, sequencer setup, interrupt handling, and debug dumps.

Risks and test signals: site access is non-atomic unless callers serialize correctly; byte helpers can race with other word updates. Atomic update polling has no timeout. Interrupt enablement must match ISR expectations. Tests should cover DDB/SCB field access, atomic-update conflict and parity cases, context-size detection, interrupt mask programming, and 32-bit/64-bit DMA address writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.h -->
