# subset-b-005347 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_version.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_version.h

## Purpose
`ql4_version.h` is a small version header for the QLogic iSCSI HBA driver family. It defines the kernel driver version string consumed by the qla4xxx driver sources and build metadata.

## Important APIs, Types, And Functions
The only exported definition is `QLA4XXX_DRIVER_VERSION`, currently `"5.04.00-k6"`. There are no functions, types, storage objects, or control paths.

## Control Flow
This file participates through C preprocessing. Any qla4xxx source including it embeds the version literal into module information, diagnostics, or adapter reporting paths.

## State And Persistence
There is no runtime state. The version macro is compile-time state baked into the built module and persists only as part of the resulting binary.

## Dependencies And Integration Points
The header depends only on include ordering by qla4xxx sources. Its integration point is the qla4xxx driver build and any module/version display logic that refers to `QLA4XXX_DRIVER_VERSION`.

## Risks And Edge Cases
The main risk is metadata drift: updating the driver without updating this macro can mislead support tooling, logs, and user reports. Because it lacks an include guard, repeated inclusion is harmless for a macro with the same value but would warn or fail if a caller defines the macro differently first.

## Test Signals
Builds of the qla4xxx module should compile without macro redefinition warnings. Runtime checks are version-string visibility in module metadata, dmesg banner paths, or qla4xxx diagnostic output that reports `"5.04.00-k6"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla4xxx/ql4_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas.c

## Purpose
`qlogicfas.c` is the ISA-board wrapper for QLogic FAS408 SCSI controllers. It handles module parameters, I/O-port reservation, IRQ registration, SCSI host allocation, and SCSI mid-layer registration while delegating command execution and hardware protocol details to `qlogicfas408.c`.

## Important APIs, Types, And Functions
The central probe helper is `__qlogicfas_detect()`, which validates `iobase`/`irq`, reserves 16 I/O ports, calls `qlogicfas408_detect()`, initializes the chip with `qlogicfas408_setup()`, allocates a `Scsi_Host`, fills `struct qlogicfas408_priv`, requests the IRQ, adds the host, and scans it. `qlogicfas_detect()` iterates up to `MAX_QLOGICFAS` module-parameter slots and chains detected `qlogicfas408_priv` objects in `cards`. `qlogicfas_release()` removes a host and frees IRQ, port, and host resources. The `qlogicfas_driver_template` wires `qlogicfas408_info`, `qlogicfas408_queuecommand`, `qlogicfas408_abort`, `qlogicfas408_host_reset`, and `qlogicfas408_biosparam` into the SCSI mid-layer.

## Control Flow
Module init calls `qlogicfas_detect()`. For each configured pair of `iobase[]` and `irq[]`, detection reserves the region, probes the chip, reads chip type, chooses initiator ID 7 when the template has `this_id < 0`, programs the FAS408 registers, allocates the SCSI host private area, installs the interrupt handler, registers with `scsi_add_host()`, and starts `scsi_scan_host()`. A failed step unwinds in reverse order. Module exit walks `cards` and calls `qlogicfas_release()` for each host.

## State And Persistence
Runtime state is per-adapter `struct qlogicfas408_priv`: base port, IRQ, initiator ID, interrupt type, current command pointer, info string, owning host, and next pointer. Global state is the `cards` list plus module parameter arrays. The driver writes no persistent configuration; hardware configuration is inferred from caller-provided module parameters and volatile chip registers.

## Dependencies And Integration Points
This file depends on legacy ISA I/O port APIs, IRQ registration, SCSI host allocation/scanning/removal, and the shared FAS408 core in `qlogicfas408.h`. User integration is through module parameters `iobase=` and `irq=`. It also depends on `qlogicfas408_ihandl()` being safe under the SCSI host lock taken by the shared interrupt wrapper.

## Risks And Edge Cases
Autoprobing is not attempted: missing or invalid module parameters yield no devices. The exit loop follows `priv->next` after `qlogicfas_release()` calls `scsi_host_put()`, so correctness depends on the private memory remaining readable until the loop advances. The driver has `can_queue = 1`, but command serialization still relies on the shared core's `qlcmd` polling. IRQ and I/O resource cleanup paths are narrow and should be checked when probe fails after partial initialization.

## Test Signals
Useful signals include module load with no parameters returning `-ENODEV`, successful load for known `iobase`/`irq`, busy I/O-port rejection, failed chip probe cleanup, SCSI scan after `scsi_add_host()`, interrupt-driven command completion through the FAS408 core, abort/reset behavior via the template handlers, and unload freeing IRQ and I/O region without stale hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.c

## Purpose
`qlogicfas408.c` implements the shared low-level command engine for QLogic FAS408-compatible SCSI controllers. It is used by wrappers such as the ISA `qlogicfas` driver and PCMCIA-style integrations to program registers, perform PIO pseudo-DMA transfers, process interrupts, map SCSI status, and expose SCSI error-handling callbacks.

## Important APIs, Types, And Functions
Exported entry points are `qlogicfas408_info()`, `qlogicfas408_queuecommand()`, `qlogicfas408_abort()`, `qlogicfas408_host_reset()`, `qlogicfas408_biosparam()`, `qlogicfas408_ihandl()`, `qlogicfas408_get_chip_type()`, `qlogicfas408_setup()`, `qlogicfas408_detect()`, and `qlogicfas408_disable_ints()`. Internal helpers include `ql_zap()` for chip/SCSI reset, `ql_pdma()` for pseudo-DMA FIFO transfer, `ql_wai()` for polled interrupt/status waits, `ql_icmd()` to program and launch a command, `ql_pcmd()` to complete data/status/message phases, and `ql_ihandl()` to bridge hardware interrupt state to `scsi_done()`.

## Control Flow
The SCSI mid-layer enters `qlogicfas408_queuecommand_lck()`. It rejects commands addressed to the initiator ID, busy-waits until no command is active, then calls `ql_icmd()` to clear stale interrupts/FIFO state, program transfer and timing registers, write the CDB, store `priv->qlcmd`, and issue select-and-send-command. The IRQ handler takes the host lock, verifies the adapter interrupt bit, retrieves `priv->qlcmd`, calls `ql_pcmd()`, clears the active command, and completes the command.

`ql_pcmd()` validates selection/command completion status, clears residual FIFO data, programs the transfer count for data phases, iterates the scatterlist with `ql_pdma()`, waits for bus service, retrieves status and message bytes, disconnects, waits for bus-free indication, and fills host/status/message result fields. Error paths set `DID_NO_CONNECT`, `DID_BAD_INTR`, `DID_ERROR`, `DID_PARITY`, `DID_TIME_OUT`, `DID_ABORT`, or `DID_RESET`.

## State And Persistence
The core stores volatile adapter state in `struct qlogicfas408_priv`: current command, abort/reset flag, base port, initiator ID, IRQ, interrupt type, and info string. Static configuration words (`qlcfg5`, `qlcfg6`, `qlcfg7`, `qlcfg8`, `qlcfg9`, `qlcfgc`) derive from header macros for clock, parity, sync, and cable timing. No persistent storage is modified; all state is hardware register state or in-memory SCSI host private data.

## Dependencies And Integration Points
The code depends on port I/O (`inb`, `outb`, `insl`, `outsl`), jiffies timeouts, scatterlist helpers, SCSI command result helpers, SCSI host locking, and the macros/types in `qlogicfas408.h`. Wrappers must allocate host private storage of `struct qlogicfas408_priv`, fill `qbase`, `qinitid`, `int_type`, and IRQ information, and route interrupts to `qlogicfas408_ihandl()`.

## Risks And Edge Cases
Several waits are busy loops against hardware registers; the file itself notes historic concern about non-terminating hardware waits. Transfers above 16 MiB are not supported by the 24-bit transfer count. `ql_pdma()` may stop early on interrupt bits and does not report residual length directly. Abort/reset is communicated through `qabort`, so races with active pseudo-DMA or status phase handling are delicate. `qlogicfas408_detect()` uses repeated reads and XOR comparisons that are terse and hardware-specific. The reset callback assumes `cmd` is non-NULL despite a comment that a PCMCIA stub historically called it with `NULL`.

## Test Signals
Signals include successful chip detection and setup, one-command-at-a-time queueing, CDB launch to non-initiator targets, scatter-gather reads and writes through pseudo-DMA, status/message handling for good and check-condition completions, timeout handling in `ql_wai()` and status-phase waits, abort and host reset during an active command, parity/error interrupt handling invoking `ql_zap()`, BIOS geometry output for small and large capacities, and unload paths calling `qlogicfas408_disable_ints()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.h

## Purpose
`qlogicfas408.h` defines the shared configuration, private state, register-bank macros, and exported function prototypes for QLogic FAS408-compatible SCSI controller support. It is the contract between the low-level FAS408 engine and board-specific wrappers.

## Important APIs, Types, And Functions
`struct qlogicfas408_priv` is the key host-private structure and contains I/O base, initiator ID, abort/reset flag, IRQ, interrupt type, info buffer, active `scsi_cmnd`, host pointer, and linked-list pointer. Configuration macros include `QL_TURBO_PDMA`, `QL_ENABLE_PARITY`, `QL_RESET_AT_START`, `XTALFREQ`, `SLOWCABLE`, `FASTSCSI`, `FASTCLK`, `SYNCXFRPD`, `SYNCOFFST`, and `WATCHDOG`. `REG0` and `REG1` switch the chip register map using `qbase` and `int_type`. `get_priv_by_cmd()` and `get_priv_by_host()` retrieve private state from SCSI objects. The prototypes expose queueing, interrupt, BIOS geometry, abort/reset, setup, detect, chip-type, and interrupt-disable routines.

## Control Flow
The header has no executable flow by itself, but the `REG0`/`REG1` macros have side effects: they read and write adapter registers to switch register banks. Callers must have local variables named `qbase` and, for `REG1`, `int_type`, matching the macro assumptions.

## State And Persistence
Compile-time macro choices control runtime hardware programming. `struct qlogicfas408_priv` is volatile per-host state allocated inside `Scsi_Host` private storage. No persistent state is defined.

## Dependencies And Integration Points
The header depends on Linux SCSI types such as `struct scsi_cmnd`, `struct scsi_device`, `struct Scsi_Host`, `struct gendisk`, and `sector_t`, plus port I/O helpers through the C files that include it. It integrates the shared implementation with `qlogicfas.c` and any PCMCIA wrapper that uses the same function exports.

## Risks And Edge Cases
The register-bank macros are statement-expression-like comma expressions with hidden local-variable dependencies, making misuse easy during refactoring. Many configuration settings are compile-time constants rather than module parameters, so board-specific timing, parity, and reset behavior require rebuilds. `get_priv_by_cmd()` assumes the SCSI command and device/host links are valid. `WATCHDOG` is described as microseconds but used by the implementation as a jiffies delta, which is a documentation or unit mismatch to keep in mind.

## Test Signals
Build coverage should include all wrappers that include this header. Runtime signals are correct private-state retrieval, successful register-bank switching under both ISA-style `INT_TYPE = 2` and PCMCIA-style `0`, expected behavior when toggling parity/reset/sync macros, and no compile regressions when prototypes are used by external board drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.c

## Purpose
`qlogicpti.c` is the SBUS platform driver for Performance Technologies and QLogic ISP SCSI adapters on SPARC systems. It loads ISP1000 firmware, initializes adapter mailbox and DMA queues, translates SCSI commands into firmware request entries, handles firmware response entries, and integrates with the SCSI mid-layer and Open Firmware platform probing.

## Important APIs, Types, And Functions
The platform lifecycle is `qpti_sbus_probe()` and `qpti_sbus_remove()` through `module_platform_driver()`. Hardware setup flows through `qpti_map_regs()`, `qpti_register_irq()`, `qpti_get_scsi_id()`, `qpti_get_bursts()`, `qpti_get_clock()`, `qpti_map_queues()`, `qlogicpti_load_firmware()`, `qlogicpti_verify_tmon()`, and `qlogicpti_reset_hardware()`. Mailbox communication is centralized in `qlogicpti_mbox_command()`. SCSI integration is `qpti_template`, with `qlogicpti_queuecommand()`, `qlogicpti_sdev_configure()`, `qlogicpti_abort()`, and `qlogicpti_reset()`.

Command construction helpers are `marker_frob()`, `cmd_frob()`, `load_cmd()`, and `update_can_queue()`. Interrupt completion is handled by `qpti_intr()`, `qlogicpti_intr_handler()`, and `qlogicpti_return_status()`. Global adapter chaining uses `qpti_chain_add()` and `qpti_chain_del()`.

## Control Flow
Probe rejects devices with IRQ zero, allocates a SCSI host plus `struct qlogicpti`, maps registers, requests a shared IRQ, reads Open Firmware initiator ID, burst sizes, and clock, allocates coherent request/response rings, loads firmware from `qlogic/isp1000.bin`, checks PTI environmental status when applicable, resets hardware, initializes firmware queues and target parameters, adds the SCSI host, links the adapter into the global chain, and scans.

Queueing reads the firmware request out pointer from `MBOX4`, reserves request ring entries, optionally emits a `SYNC_ALL` marker after reset events, fills a command entry from the SCSI CDB, maps scatter-gather data, writes continuation entries for more than four SG segments, stores the SCSI command in `cmd_slots[handle]`, increments per-target command count, updates `MBOX4`, and adjusts mid-layer queue/SG limits. Interrupt handling checks `SBUS_STAT_RINT`, reads the response producer pointer from `MBOX5`, acknowledges firmware interrupts, handles async reset/error mailbox events, walks response entries, looks up commands by handle, copies sense data, maps completion status to SCSI result, unmaps DMA, decrements command counts, advances `MBOX5`, chains completions through `host_scribble`, and calls `scsi_done()` after the ring walk.

## State And Persistence
Persistent host-side state is runtime-only: MMIO mappings, coherent request/response queues and DVMA addresses, queue indices, firmware version fields, target parameters, command slots, per-target command counts/tag-age timestamps, Open Firmware-derived IDs and clock/burst settings, PTI status-register shadow, and flags such as `send_marker`, `ultra`, `differential`, and `is_pti`. Firmware is loaded into adapter RAM on probe but not persisted across reset/power cycles. The global `qptichain` records live adapters for module lifetime.

## Dependencies And Integration Points
The driver depends on SPARC SBUS/Open Firmware APIs, platform devices, IRQs, coherent DMA allocation, firmware loading, SCSI mid-layer command and error handling, and register/entry definitions from `qlogicpti.h`. It integrates with firmware through mailbox commands, request/response rings, and async events. Device-tree match names include `ptisp`, `PTI,ptisp`, `QLGC,isp`, and `SUNW,isp`.

## Risks And Edge Cases
Mailbox waits are bounded by loop counts but often only log timeout and continue, so partial hardware failure can cascade. `qlogicpti_mbox_command()` indexes `mbox_param[param[0]]` before an explicit bounds check, so callers must pass valid command codes. `load_cmd()` maps SG data before verifying enough continuation slots for every segment; on queue exhaustion it can return failure after mapping, so DMA-unmap behavior is a risk. The abort path searches all command slots and does not explicitly handle a not-found command before building the cookie. Queue-depth adjustment contains a large workaround subtraction and can affect SG limits under pressure. Firmware load is word-by-word mailbox I/O, making probe slow and sensitive to firmware availability and checksum correctness.

## Test Signals
Signals include platform match/probe for PTI and QLGC names, missing firmware failure, checksum failure, successful firmware version reporting, differential/single-ended and Ultra/Fast messages, coherent queue allocation/free on probe failure and remove, target parameter programming in `sdev_configure()`, marker insertion after bus reset async events, SG continuation handling at 4, 5, and large SG counts, queue-full/toss-command behavior, status mapping for all completion codes, sense copy on `SF_GOT_SENSE`, abort and bus reset mailbox commands, shared IRQ behavior, and clean remove with IRQ, DMA, and MMIO resources released.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.h

## Purpose
`qlogicpti.h` defines the hardware register map, firmware mailbox protocol, queue entry formats, SCSI status constants, and software state for the QLogic/PTI SBUS ISP driver. It is the ABI-like contract between `qlogicpti.c`, the ISP firmware, and the SBUS register layout.

## Important APIs, Types, And Functions
Important structures include `Entry_header`, `dataseg`, `Command_Entry`, `Ext_Command_Entry`, `Continuation_Entry`, `Marker_Entry`, `Status_Entry`, `host_param`, `dev_param`, `pti_queue_entry`, and `struct qlogicpti`. Constants cover SBUS, DMA, mailbox, CPU/RISC, and host-control register offsets and bit definitions; request/response ring lengths; entry types; control flags; completion statuses; state/status flags; async events; and mailbox commands. Ring helpers `NEXT_REQ_PTR()`, `NEXT_RES_PTR()`, `PREV_REQ_PTR()`, and `PREV_RES_PTR()` implement wrapping over power-of-two-minus-one masks.

## Control Flow
The header has no direct execution, but its data formats drive all command flow. `Command_Entry` and `Continuation_Entry` describe outbound requests, `Status_Entry` describes inbound completions, and `Marker_Entry` synchronizes firmware after reset. Endianness-specific field ordering is encoded in several structures, allowing the same C field names to represent firmware byte layout on big- and little-endian builds.

## State And Persistence
`struct qlogicpti` defines all live adapter state: MMIO register pointers, coherent request/response queues, queue indices, marker flag, platform device, per-target command/tag state, command pointer slots, firmware revision, SCSI host, adapter identity, IRQ, device-tree settings, host and target parameters, PTI status register mapping/shadow, and bitflags. This state is allocated per SCSI host and is not persistent across driver unload or hardware reset.

## Dependencies And Integration Points
The header depends on Linux integer types, SCSI command declarations, platform-device concepts, DMA address types, and architecture endianness macros. It integrates tightly with ISP firmware expectations: queue entry size is fixed at 64 bytes, request and response queue lengths are 255 plus one actual slot, and mailbox status/event constants must match firmware.

## Risks And Edge Cases
Because this file encodes hardware and firmware layout, field-size or endian mistakes can corrupt DMA rings. `QLOGICPTI_MAX_SG(ql)` ties SG capacity to free request slots; callers must recompute queue capacity carefully. Several comments document hardware quirks, such as 64-byte burst unreliability and 32-bit firmware handles requiring an in-driver command-slot table. The header also redefines `MAX_TARGETS`/`MAX_LUNS` values also present in the C file, creating drift risk.

## Test Signals
Build tests should cover endian-sensitive structure layouts and all users of mailbox/entry constants. Runtime signals include correct firmware command parsing, request and response ring wraparound at slot 255, SG capacity calculation as free slots change, command handle lookup through `cmd_slots`, differential/terminator status interpretation, and register bit programming for SBUS burst, reset, interrupt, and RISC control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qlogicpti.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/raid_class.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/raid_class.c

## Purpose
`raid_class.c` implements a generic RAID visualization transport class. It lets RAID-capable lower-level drivers expose RAID attributes through a common sysfs transport container independent of the specific hardware or software RAID implementation.

## Important APIs, Types, And Functions
`struct raid_internal` wraps public `struct raid_template`, the provider's `raid_function_template`, and three attributes. `struct raid_component` represents component devices linked under `raid_data`. The public exports are `raid_class_attach()` and `raid_class_release()`. Matching/setup/removal is handled by `raid_match()`, `raid_setup()`, and `raid_remove()`. Attribute helpers map enum values through `raid_state_name()` and `raid_level_name()`, and generated sysfs show methods expose `level`, `resync`, and `state`.

## Control Flow
Module init registers the `raid_class` transport class. A RAID provider calls `raid_class_attach()` with callbacks and a cookie; this allocates internal state, sets the attribute-container class/match/attrs fields, registers the container, and publishes the three attributes. When transport matching sees a SCSI device, `raid_match()` verifies the provider cookie matches the SCSI host template and calls `is_raid()`. `raid_setup()` allocates `struct raid_data` and initializes its component list. `raid_remove()` unregisters all component devices, detaches driver data, and frees the RAID data. Release unregisters the attribute container and frees `raid_internal`.

## State And Persistence
State is in memory only. Per-template state records provider callbacks and sysfs attributes. Per-class-device state is `struct raid_data`, including level/state/resync values and a component list managed by other RAID code. The class does not persist RAID configuration; it reflects state supplied by the provider callbacks and device data.

## Dependencies And Integration Points
The file depends on Linux transport class/attribute container infrastructure, sysfs device attributes, list handling, allocation, and SCSI device/host helpers. Its primary integration point is `include/linux/raid_class.h` providers that supply `cookie`, `is_raid()`, and optional `get_resync()`/`get_state()` callbacks.

## Risks And Edge Cases
`raid_remove()` logs removal at error severity, which can be noisy for normal teardown. Attribute show helpers assume `dev_get_drvdata()` returns a valid `raid_data`. `raid_state_name()` and `raid_level_name()` return `NULL` for unknown enum values not in the tables, which could feed a `%s` sysfs print. The matching path currently only handles SCSI devices and explicitly leaves other subsystems as a FIXME. `BUG_ON()` is used for unexpected registration/unregistration and attribute-count failures.

## Test Signals
Signals include successful class registration/unregistration, provider attach/release, SCSI RAID device matching by cookie and `is_raid()`, sysfs `level`, `resync`, and `state` reads with and without provider update callbacks, component list cleanup on device removal, and behavior for unknown RAID level/state enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/raid_class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/script_asm.pl -->
# sources/distributed-fs/ceph-client/drivers/scsi/script_asm.pl

## Purpose
`script_asm.pl` is a Perl assembler for NCR/Symbios SCSI SCRIPTS programs. It reads SCRIPTS-like assembly from standard input and emits C header files containing a `u32 SCRIPT[]` array, label and external patch metadata, entry-point defines, and an undef header for generated symbols.

## Important APIs, Types, And Functions
The script is organized around global tables and parser helpers. `%scsi_phases`, `%operators`, and `%registers` define instruction encodings, with alternate register/operator sets under `-ncr7x0_family`. `%symbol_values`, `%symbol_references`, and `%forward` implement a single-pass symbol table with later patching. `patch()` modifies byte fields inside generated 32-bit words. `parse_value()` records absolute/relative/external references and patches immediate values. `parse_conditional()` encodes IF/WHEN conditional clauses for transfer-control instructions. The main loop parses labels, `ABSOLUTE`, `RELATIVE`, `EXTERNAL`, `ENTRY`, `MOVE`, `SELECT`, `RESELECT`, `WAIT`, `SET`, `CLEAR`, `JUMP`, `CALL`, `INT`, `RETURN`, `INTFLY`, `DISCONNECT`, and `NOP`.

## Control Flow
Command-line arguments choose output header paths, while Perl `-s` options can set flags such as `-prefix` or `-ncr7x0_family`. For each input line, the script stores the original line for optional comments, strips semicolon comments, parses declarations or instructions, appends one or more 32-bit words to `@code`, and advances the instruction address. After input, it rejects unresolved forward references, patches absolute symbols, records external patches, resolves label references as absolute or 24-bit relative offsets, then writes `script.h` and `scriptu.h` style outputs.

## State And Persistence
All assembler state is in global Perl variables for one process run: generated words, symbol tables, label/entry/external lists, source listing comments, address, and line number. Persistent outputs are the two generated header files. No repository state is modified except those output paths when the script is run.

## Dependencies And Integration Points
The script depends on `/usr/bin/perl -s` behavior, C consumers expecting `static u32 <prefix>SCRIPT[]`, patch arrays, and generated `#define` names, and SCSI driver build rules that pipe script source into it. It integrates with NCR53c7xx/8xx-style drivers that patch absolute and external addresses after including the generated header.

## Risks And Edge Cases
The parser relies heavily on regular expressions, global variables, and `eval` for numeric expressions, so malformed input can fail late or unexpectedly. It is single-pass and intentionally lacks features such as `PASS`, data-relative `REL`, and multi-script starts. Output files are opened directly for writing rather than atomically. Several diagnostics use stale variable names in error text. Relative addressing is limited to 24 bits and external references must be full-word absolute references. The script emits generated C that depends on `u32` and compiler support for `__attribute((unused))`.

## Test Signals
Signals include assembling known NCR script sources for both default and `-ncr7x0_family` modes, verifying generated instruction words and patch arrays, forward and undefined-symbol diagnostics, absolute/relative/external patch handling, conditional forms with phases/data/masks, `MOVE MEMORY` three-word output, prefix namespacing, generated undef header content, and build success of C drivers that include the generated headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/script_asm.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi.c

## Purpose
`scsi.c` is a core SCSI mid-layer implementation file. It provides logging hooks, command completion handoff, queue-depth management, VPD discovery/cache helpers, command-duration-limit detection/enabling, device reference and lookup helpers, and module initialization/teardown for the SCSI subsystem.

## Important APIs, Types, And Functions
Exported helpers include `scsi_finish_command()`, `scsi_change_queue_depth()`, `scsi_track_queue_full()`, `scsi_get_vpd_page()`, `scsi_report_opcode()`, `scsi_device_get()`, `scsi_device_put()`, `__scsi_iterate_devices()`, `starget_for_each_device()`, `__starget_for_each_device()`, `__scsi_device_lookup_by_target()`, `scsi_device_lookup_by_target()`, `__scsi_device_lookup()`, and `scsi_device_lookup()`. Internal VPD helpers include `scsi_vpd_inquiry()`, `scsi_get_vpd_size()`, `scsi_get_vpd_buf()`, and `scsi_update_vpd_page()`. CDL helpers include `scsi_cdl_check_cmd()`, `scsi_cdl_check()`, and `scsi_cdl_enable()`. When logging is enabled, `scsi_log_send()` and `scsi_log_completion()` print command and completion details.

## Control Flow
Completion flow enters `scsi_finish_command()`, marks the device unbusy, clears host/target/device blocked counters, optionally lets the upper SCSI driver adjust good-byte count through `drv->done()`, subtracts residuals when appropriate, and calls `scsi_io_completion()`. Queue-full flow coalesces events by jiffies bucket, tracks repeated depth values, and after enough repeated events calls `scsi_change_queue_depth()`.

VPD flow issues INQUIRY EVPD commands, validates supported page lists and lengths, allocates/caches selected VPD pages under `inquiry_mutex` using RCU replacement, and frees old pages with `kfree_rcu()`. RSOC/CDL flow uses MAINTENANCE IN to check opcode support and command duration limit bits, then may force READ/WRITE(16) usage and enable ATA CDL through mode sense/select. Device lookup flows take `host_lock`, skip deleted devices, and return either borrowed or refcounted SCSI devices.

Subsystem init registers procfs, devinfo, hosts, sysctl, sysfs, and netlink in order; failure unwinds previously initialized layers. Exit reverses those registrations.

## State And Persistence
Global state includes `scsi_logging_level` and subsystem registrations. Per-device state updated here includes queue depth, budget maps, queue-full counters, VPD RCU pointers, CDL support/enable flags, command-size behavior flags, and device references. No persistent disk state is written, but SCSI MODE SELECT may change volatile or device-defined CDL feature state for ATA-backed devices.

## Dependencies And Integration Points
This file depends on block queues, SCSI command execution, SCSI device/target/host structures, RCU, mutexes, spinlocks, sysfs/proc/sysctl/netlink initialization, tracepoints, and optional logging support. It is a central integration point for lower-level drivers, upper SCSI device drivers, user-visible SCSI subsystem initialization, and standards-driven VPD/RSOC/CDL device capabilities.

## Risks And Edge Cases
VPD probing must handle devices that lie about page support or length; the code uses conservative header probes, warnings, and retries. `scsi_change_queue_depth()` returns `-EINVAL` without a budget map, so low-level callers must handle unsupported depth changes. CDL enabling for ATA devices rewrites mode data and can reset device CDL statistics. Lookup helpers have strict locking/reference semantics; misuse can lead to use-after-free or module unload races. Initialization failure paths must stay paired with subsystem registration order.

## Test Signals
Signals include SCSI subsystem init and failure unwinds, logging-level output, normal command completion with driver `done()` and residual adjustment, queue-full depth reduction after repeated events, VPD page 0/0x80/0x83/0x89/0xb0/0xb1/0xb2/0xb7 attachment, long/short/missing VPD handling, RSOC support and illegal-request handling, CDL enable/disable for ATA and non-ATA devices, device get/put during deletion or module unload, locked and refcounted device lookup helpers, and clean subsystem exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_bsg.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_bsg.c

## Purpose
`scsi_bsg.c` registers SCSI block SG (BSG) command handling for SCSI devices. It supports traditional `sg_io_v4` request submission and newer `io_uring` passthrough commands, mapping user CDB/data buffers into block requests and returning SCSI status, host status, residuals, and sense data.

## Important APIs, Types, And Functions
The public registration function is `scsi_bsg_register_queue()`. The synchronous sg_io path is `scsi_bsg_sg_io_fn()`. The io_uring path is `scsi_bsg_uring_cmd()`, `scsi_bsg_map_user_buffer()`, `scsi_bsg_uring_cmd_done()`, and `scsi_bsg_uring_task_cb()`. `struct scsi_bsg_uring_cmd_pdu` stores per-command temporary state inside `io_uring_cmd.pdu`: mapped bio, request pointer, and response buffer address.

## Control Flow
For sg_io, the handler validates BSG protocol/subprotocol, rejects bidirectional transfers, allocates a SCSI driver request for input or output, copies the user CDB, checks command permissions with `scsi_cmd_allowed()`, maps one user data buffer if present, executes the request synchronously, fills `sg_io_v4` status fields and residuals, copies sense data to the response buffer when present, unmaps the bio, and frees the request.

For io_uring, submission validates protocol, CDB pointer/length, no bidi, and no iovec mode, chooses NOWAIT/GFP_NOWAIT when requested, allocates a request, copies and authorizes the CDB, records response state, maps fixed or normal user buffers, sets timeout/end_io data, and starts `blk_execute_rq_nowait()`. Completion schedules task work; task work unmaps the bio, copies sense data if needed, builds the packed BSG `res2` status value, frees the request, and completes the io_uring command.

## State And Persistence
No long-lived state is stored in this file. Per-command state lives in the request, SCSI command PDU, mapped bio, user header, and io_uring PDU until completion. There is no persistent storage behavior.

## Dependencies And Integration Points
The file depends on block request allocation/execution, BSG queue registration, SCSI command permission filtering, uaccess, SG/BSG UAPI structures, and io_uring command/task-work APIs. It integrates with each `scsi_device` request queue through `bsg_register_queue()`.

## Risks And Edge Cases
Bidirectional BSG support is explicitly removed and returns `-EOPNOTSUPP`. The io_uring path does not support iovec counts, only a single fixed or normal buffer. User pointers and CDB lengths are security-sensitive; permission checks depend on `open_for_write`. Sense copying can fail after the device command has completed, producing `-EFAULT` while still reporting packed status. Nonblocking allocation/map paths can fail under memory pressure. Correct lifetime depends on request freeing only after task-work completion in the io_uring path.

## Test Signals
Signals include BSG queue registration per SCSI device, valid INQUIRY/TEST UNIT READY passthrough through sg_io and io_uring, rejection of invalid protocol/subprotocol, missing CDB, overlong CDB, bidi transfers, iovec mode, and disallowed commands for read-only opens, user data mapping for input and output, fixed-buffer io_uring mapping, timeout propagation, sense data copy on check condition, residual reporting, and request/bio cleanup on all error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_bsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_common.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/scsi_common.c

## Purpose
`scsi_common.c` contains SCSI helper routines shared by initiator and target code. It provides command-size lookup, device-type names, persistent-reservation type conversion, LUN packing/unpacking, and sense-buffer parsing/building helpers.

## Important APIs, Types, And Functions
Exports include `scsi_command_size_tbl`, `scsi_device_type()`, `scsi_pr_type_to_block()`, `block_pr_type_to_scsi()`, `scsilun_to_int()`, `int_to_scsilun()`, `scsi_normalize_sense()`, `scsi_sense_desc_find()`, `scsi_build_sense_buffer()`, `scsi_set_sense_information()`, and `scsi_set_sense_field_pointer()`. These functions operate on UAPI PR enums, `struct scsi_lun`, raw sense buffers, and `struct scsi_sense_hdr`.

## Control Flow
Lookup helpers are table or switch based. LUN conversion packs/unpacks the 8-byte SCSI LUN representation two bytes at a time into host-endian `u64`. Sense normalization clears the destination header, validates the response code, then extracts sense key/ASC/ASCQ/additional length from descriptor or fixed sense format. Descriptor search walks descriptor-format sense data from byte 8 using each descriptor's length. Sense builders initialize fixed or descriptor sense formats and optionally append or update information and field-pointer descriptors.

## State And Persistence
The only static state is immutable lookup tables for command sizes and device type names. All other state is caller-provided buffers. No persistent system or device state is changed.

## Dependencies And Integration Points
This file depends on generic kernel helpers, unaligned big-endian accessors, SCSI common headers, and block persistent-reservation UAPI enums. It is used broadly by SCSI initiator, target, error handling, passthrough, and diagnostics code that needs common SCSI data-format handling.

## Risks And Edge Cases
Device type strings are ABI-visible through `/proc/scsi/scsi`, so existing entries must not change. `scsi_set_sense_information()` and `scsi_set_sense_field_pointer()` grow descriptor sense data but rely on caller-provided `buf_len`; boundary checks are critical. Fixed-format information can only mark VALID for 32-bit values. Descriptor parsing must tolerate short or malformed descriptors. Unknown PR type mappings return zero, so callers must treat zero as invalid/unsupported where appropriate.

## Test Signals
Signals include command-size results for all opcode groups, stable device type strings including well-known LUN and no-device values, PR type round trips, LUN conversion round trips for single- and multi-level LUNs, normalization of fixed and descriptor sense buffers, malformed/short sense rejection, descriptor lookup with multiple descriptors, building fixed and descriptor sense data, setting 32-bit and 64-bit information fields, and field-pointer sense-key-specific data with command/data and bit-pointer variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/scsi_common.c -->
