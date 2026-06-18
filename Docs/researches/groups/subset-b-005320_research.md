# subset-b-005320 research

Grouped research report for the requested SCSI driver files. Each section preserves the original source path in its title and is wrapped with the required reconciliation sentinels.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/nsp32.c

Purpose: implements the Workbit NinjaSCSI-32Bi/UDE PCI/CardBus SCSI host adapter driver. It registers a PCI driver, allocates a SCSI host, initializes the ASIC, builds DMA/autoparameter state, negotiates synchronous transfer parameters, drives SCSI selection and AutoSCSI phases, and handles PCI/CardBus suspend/resume.

Important APIs and functions: module parameters `trans_mode`, `auto_param`, and `disc_priv` tune transfer and message behavior. `nsp32_probe()`, `nsp32_detect()`, `nsp32_remove()`, and `nsp32_release()` own PCI and SCSI-host lifecycle. The SCSI template exposes `nsp32_queuecommand()`, `nsp32_show_info()`, `nsp32_info()`, `nsp32_eh_abort()`, and `nsp32_eh_host_reset()`. Command execution uses `nsp32_setup_sg_table()`, `nsp32_selection_autopara()`, `nsp32_selection_autoscsi()`, `nsp32_arbitration()`, `do_nsp32_isr()`, `nsp32_busfree_occur()`, `nsp32_msgin_occur()`, `nsp32_msgout_occur()`, and `nsp32_scsi_done()`. EEPROM and SDTR support flow through `nsp32_getprom_param()`, `nsp32_getprom_at24()`, `nsp32_getprom_c16()`, `nsp32_analyze_sdtr()`, and the sync-table helpers.

Control flow: module init registers `nsp32_driver`; PCI probe enables the device, maps BARs, sets bus mastering, then `nsp32_detect()` allocates coherent autoparameter and SG memory, seeds per-target/per-LUN state, reads EEPROM limits, initializes the ASIC, resets the SCSI bus, requests IRQ and I/O regions, and scans. Queueing is single-command: it rejects an occupied `CurrentSC`, maps SG, builds IDENTIFY plus optional SDTR, selects via AutoParameter or direct AutoSCSI, and returns completion through interrupts. The ISR masks interrupts, decodes AutoSCSI, FIFO, phase-change, reset, timer, and PCI/BMCNT status, advances message/data/status phases, adjusts saved data pointers on disconnect, and completes or restarts commands.

State and persistence: runtime state lives in `nsp32_hw_data`, including `CurrentSC`, `cur_target`, `cur_lunt`, per-target SDTR registers/flags, per-LUN SG tables, message buffers, clock/sync table selection, and coherent DMA addresses. EEPROM contents are read at attach time only and influence reset delay and per-target sync limits; the driver does not persist new settings.

Dependencies and integration: depends on Linux PCI, SCSI midlayer, DMA mapping, interrupt, I/O port/MMIO helpers, and `nsp32.h`/`nsp32_io.h`; optional debug code comes from `nsp32_debug.c`. It integrates as a `struct pci_driver` plus `struct scsi_host_template` and exposes `/proc`-style host info through `show_info`.

Risks: legacy direct hardware sequencing has busy waits, single-command concurrency, and complex message/reselection edge cases. SG entries over 64 KiB fail. MMIO/PIO transfer paths are mostly not supported in this driver despite register helpers. Several comments mark TODOs around SCSI-3 compliance, illegal phase recovery, BMCNT error handling, and disconnect pointer handling. Test signals are successful module load/probe, `scsi_scan_host()` discovery, interrupt-driven command completion, SDTR status in host info, reset/abort error-handler recovery, suspend/resume reset behavior, and fault injection for selection timeout, unexpected bus free, EEPROM absence, and card removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/nsp32.h

Purpose: central hardware contract for the NinjaSCSI-32Bi/UDE driver. It defines supported PCI IDs and model names, normal and indexed register offsets, bit definitions, bus-phase masks, DMA/autoparameter layouts, target/LUN runtime structures, transfer-mode flags, SDTR constants, and timing values consumed by `nsp32.c` and debug/I/O helpers.

Important APIs and types: key register groups include IRQ/transfer control, SCSI bus control/monitor, command control/data, arbitration, sync/ack width, FIFO/BM/SGT registers, EEPROM control, and MISC/BM cycle indexed registers. `nsp32_sgtable`, `nsp32_sglun`, and `nsp32_autoparam` are packed hardware-facing little-endian DMA structures. `nsp32_lunt` tracks one outstanding command per target/LUN and its SG progress. `nsp32_target` stores SDTR state, negotiated period/offset, sync register, ack width, limit entry, and sample register. `nsp32_hw_data` is the per-host state object. `nsp32_priv()` returns per-command private SCSI status.

Control flow support: constants such as `BUSMON_*`, `BUSPHASE_*`, `COMMAND_PHASE`, `DATA_IN_PHASE`, `MSGIN_00_VALID`, and `AUTOSCSI_BUSY` let the ISR map hardware status to SCSI protocol phases. SDTR macros `ASYNC_OFFSET`, `SYNC_OFFSET`, and `TO_SYNCREG()` convert negotiated values to ASIC registers. Timeouts bound reset, selection, arbitration, and REQ/SACK handshake waits.

State and persistence: this header does not persist data, but it defines all in-memory state that persists across commands during device attachment: coherent SG/autoparam pools, current nexus pointers, per-target negotiation outcomes, EEPROM-derived transfer limits, and message buffers. Hardware-visible fields are explicitly little-endian and packed.

Dependencies and integration: requires Linux integer types, bit macros, SCSI definitions, PCI IDs, DMA addresses, and register access from `nsp32_io.h`. It is tightly integrated with `nsp32.c`; changing offsets, packing, or array dimensions can break hardware DMA.

Risks: hardware comments warn against double-word access to selected registers. `MAX_LUN` remains 8 despite a note about SPI-3 supporting more. `NSP32_SG_TABLE_SIZE` is computed from SG table dimensions and must match the allocation and per-LUN pointer arithmetic. Test signals include compile-time structure packing compatibility, successful DMA with SG lists, correct register reads in host info, and stable SDTR negotiation across reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32_debug.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/nsp32_debug.c

Purpose: optional debug support included only when `NSP32_DEBUG` is enabled. It prints SCSI command opcodes, command bytes, decoded LBA/length for 6/10/12-byte CDBs, bus phases, AutoSCSI executed-phase flags, and selected ASIC registers.

Important APIs and functions: `print_opcodek()` maps opcode groups to static command-name tables. `print_commandk()` dumps the CDB and derived address/length fields. `show_command()`, `show_busphase()`, and `show_autophase()` are the debug hooks used by `nsp32.c`. `nsp32_print_register()` dumps key register values only when `NSP32_SPECIAL_PRINT_REGISTER` is enabled in the debug mask.

Control flow: normal driver macros compile these hooks to no-ops unless debug is built. In debug builds, queueing and interrupt paths call the show helpers around command submission, phase changes, and AutoSCSI completion. Register dumping reads live I/O and indexed registers through `nsp32_read*()` and `nsp32_index_read*()`.

State and persistence: maintains only static string tables and uses no persistent runtime state. It observes current hardware and command state through its arguments and register reads.

Dependencies and integration: depends on SCSI command sizing, `printk`, bus-phase and AutoSCSI bit definitions from `nsp32.h`, and low-level I/O helpers from `nsp32_io.h`. It is included directly into `nsp32.c`, so symbols are intentionally `static`.

Risks: register dumps can perturb timing-sensitive hardware if used excessively, and debug printing inside interrupt/phase paths can change timing. Test signals are debug builds that compile cleanly, readable CDB and phase logs, and guarded register output that appears only when the special mask is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32_io.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/nsp32_io.h

Purpose: inline I/O helper layer for NinjaSCSI-32Bi/UDE register access. It wraps byte/word/dword port I/O, MMIO access with the chip's MMIO offset, indexed register access, and FIFO burst transfers.

Important APIs: `nsp32_write1/read1`, `nsp32_write2/read2`, and `nsp32_write4/read4` access normal I/O ports. `nsp32_mmio_write*/read*` access memory-mapped registers and convert 16/32-bit values to/from little-endian. `nsp32_index_read*/write*` and `nsp32_mmio_index_read*/write*` select `INDEX_REG` and transfer through `DATA_REG_LOW`/`DATA_REG_HI`. `nsp32_fifo_read()` and `nsp32_fifo_write()` use `insl`/`outsl` against `FIFO_DATA_LOW`.

Control flow: callers in initialization, queueing, interrupt handling, EEPROM reading, and debug code use these helpers directly. Indexed 32-bit operations split values into low/high words, matching the hardware register protocol.

State and persistence: no state is stored here. Correctness depends on the caller passing a valid I/O base or mapped base and respecting hardware access-width restrictions documented in `nsp32.h`.

Dependencies and integration: depends on Linux/architecture I/O primitives, endian conversion helpers, and register offset constants from `nsp32.h`. It is included into `nsp32.c` after the SCSI host template and before debug includes.

Risks: MMIO pointers cast from integer bases lack `__iomem` typing in several helpers, making sparse-style checking weak. Incorrect access width or endian conversion would corrupt hardware programming. Test signals include successful register initialization, FIFO transfer under bus-master mode, and big-endian build behavior, which the driver revision history explicitly called out.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/nsp32_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Kconfig

Purpose: declares configuration options for low-level PCMCIA SCSI adapter support and the individual PCMCIA SCSI client drivers in this directory.

Important options: `SCSI_LOWLEVEL_PCMCIA` gates the menu on SCSI and PCMCIA availability. The submenu intentionally requires `SCSI && PCMCIA && m`, matching the comment that these drivers have problems when built in. Driver symbols are `PCMCIA_AHA152X`, `PCMCIA_FDOMAIN`, `PCMCIA_NINJA_SCSI`, `PCMCIA_QLOGIC`, and `PCMCIA_SYM53C500`. Several depend on `HAS_IOPORT`; AHA152X selects `SCSI_SPI_ATTRS`, and Future Domain selects the shared `SCSI_FDOMAIN` core.

Control flow: this file controls whether Makefile objects are compiled as modules. `PCMCIA_NINJA_SCSI` additionally restricts 64-bit builds unless `COMPILE_TEST` is set, reflecting old 16-bit PCMCIA and pointer/I/O assumptions.

State and persistence: no runtime state. The Kconfig selections persist as kernel build configuration and module availability.

Dependencies and integration: integrates with `drivers/scsi/pcmcia/Makefile` and shared SCSI core Kconfig symbols. Help text documents supported NinjaSCSI product strings and points to `Documentation/scsi/NinjaSCSI.rst`.

Risks: module-only gating means built-in testing is intentionally unavailable. Incorrect dependencies can expose non-portable I/O code to unsupported architectures. Test signals include `allyesconfig`/`allmodconfig` with module builds, `COMPILE_TEST` coverage for restricted drivers, and verifying each selected symbol emits the expected module name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Makefile

Purpose: maps PCMCIA SCSI Kconfig symbols to module objects and adds the SCSI driver include path.

Important entries: `ccflags-y := -I $(srctree)/drivers/scsi` lets stubs include shared core headers such as `qlogicfas408.h`, `fdomain.h`, and `aha152x.h`. Module objects are `qlogic_cs.o`, `fdomain_cs.o`, `aha152x_cs.o`, `nsp_cs.o`, and `sym53c500_cs.o`. Composite modules are `aha152x_cs-objs := aha152x_stub.o aha152x_core.o` and `qlogic_cs-objs := qlogic_stub.o`.

Control flow: Kbuild includes objects only when their `CONFIG_PCMCIA_*` symbol is enabled. The AHA152X module links the PCMCIA stub plus the included core wrapper, while Qlogic is only the stub around the shared qlogicfas408 code.

State and persistence: no runtime state. The file determines build artifacts and module composition.

Dependencies and integration: tightly paired with `Kconfig`. The include flag reaches one directory up into shared SCSI driver sources.

Risks: object composition must match symbol names expected by module aliases and PCMCIA IDs. Test signals are module builds for each config, especially `aha152x_cs` linking both stub and core, and no missing header errors from shared include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_core.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_core.c

Purpose: tiny compile-unit wrapper that configures the shared AHA152X core for PCMCIA use. It defines `AHA152X_PCMCIA` and `AHA152X_STAT`, then includes `aha152x.c`.

Important APIs/types/functions: no local functions are defined. The file imports the shared AHA152X implementation with PCMCIA-specific preprocessor settings so `aha152x_stub.c` can call `aha152x_probe_one()`, `aha152x_release()`, and `aha152x_host_reset_host()`.

Control flow: Kbuild links this file into `aha152x_cs.o` alongside `aha152x_stub.o`. Runtime control flow is entirely in the included core and the stub.

State and persistence: no direct state here; the included core provides host state and SCSI command handling.

Dependencies and integration: depends on `drivers/scsi/aha152x.c` and its header. It is not standalone and must be compiled in the PCMCIA module context.

Risks: direct inclusion means macro settings affect the whole shared core and can diverge from non-PCMCIA builds. Test signals include successful `aha152x_cs` link, exported core entry points resolving, and probe/remove exercised through the PCMCIA stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_stub.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_stub.c

Purpose: PCMCIA binding layer for Adaptec AHA152X-compatible SCSI cards. It handles card matching, I/O/IRQ configuration, module parameters, setup handoff to the shared AHA152X core, resume reset, and resource teardown.

Important APIs and functions: module parameters `host_id`, `reconnect`, `parity`, `synchronous`, `reset_delay`, and `ext_trans` populate `struct aha152x_setup`. `aha152x_probe()` allocates `scsi_info_t`, sets PCMCIA config flags, and calls `aha152x_config_cs()`. `aha152x_config_check()` selects a valid I/O window, including the New Media T&J alternate resource behavior. `aha152x_config_cs()` loops configs, enables the card, builds the setup structure, and calls `aha152x_probe_one()`. `aha152x_release_cs()` calls `aha152x_release()` and disables the device. `aha152x_resume()` resets the host through the shared core.

Control flow: PCMCIA probe allocates private state and configures the socket. On success the shared AHA core creates and registers the SCSI host. Remove calls release and frees private state. Resume assumes an existing host and performs a host reset.

State and persistence: `scsi_info_t` stores the PCMCIA device and returned `Scsi_Host`. Module parameters persist for the module lifetime and affect every probed card.

Dependencies and integration: integrates PCMCIA Card Services, SCSI midlayer headers, and the AHA152X core built via `aha152x_core.c`.

Risks: `aha152x_release_cs()` calls `aha152x_release(info->host)` without a local NULL guard, so failed partial probes depend on core tolerance. Resource sizing is old PCMCIA-specific. Test signals include matching listed product IDs, successful I/O request/enable, SCSI scan through the core, resume reset, and failed-config cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/aha152x_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/fdomain_cs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/fdomain_cs.c

Purpose: compact PCMCIA wrapper for Future Domain-compatible SCSI cards. It reserves a PCMCIA I/O window, enables the device, claims the I/O region, creates the shared Future Domain SCSI host, and tears it down on removal.

Important APIs and functions: `fdomain_config_check()` requests an auto-width 10-line I/O resource sized to `FDOMAIN_REGION_SIZE`. `fdomain_probe()` configures/enables the PCMCIA device, requests the I/O region, calls `fdomain_create(base, irq, 7, &link->dev)`, and stores the host in `link->priv`. `fdomain_remove()` calls `fdomain_destroy()`, releases the region, and disables the device.

Control flow: unlike older stubs, probe directly creates the SCSI host after resource acquisition and does not use an intermediate private wrapper. Errors unwind through `fail_release` and `fail_disable`.

State and persistence: runtime state is just `link->priv` holding the `Scsi_Host`. Host ID is fixed at 7. No module parameters or persistent settings are defined.

Dependencies and integration: depends on PCMCIA APIs, SCSI host types, and the shared `fdomain.h` core selected by Kconfig.

Risks: assumes IRQ from PCMCIA config is valid for `fdomain_create()`. Requesting both PCMCIA I/O and `request_region()` must stay balanced. Test signals include product-ID match, I/O region conflict handling, successful shared-core initialization, remove cleanup, and probe failure without leaked regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/fdomain_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.c

Purpose: full 16-bit PCMCIA WorkBit NinjaSCSI-3/NinjaSCSI-32Bi SCSI host adapter driver. It manages PCMCIA card configuration, SCSI host registration, command queueing, arbitration/selection, phase-driven interrupt handling, PIO/MMIO FIFO transfers, SDTR negotiation, and reset/suspend/resume behavior.

Important APIs and functions: module parameters `nsp_burst_mode` and `free_ports` control FIFO transfer mode and optional I/O release after configuration. The SCSI template exposes `nsp_queuecommand()`, `nsp_show_info()`, `nsp_info()`, `nsp_eh_bus_reset()`, and `nsp_eh_host_reset()`. Hardware flow uses `nsphw_init()`, `nsphw_start_selection()`, `nsp_start_timer()`, `nsp_nexus()`, `nsp_pio_read()`, `nsp_pio_write()`, `nsp_fifo_count()`, `nsp_analyze_sdtr()`, `nsp_message_in()`, `nsp_message_out()`, `nspintr()`, and `nsp_scsi_done()`. PCMCIA lifecycle is handled by `nsp_cs_probe()`, `nsp_cs_config()`, `nsp_cs_release()`, `nsp_cs_detach()`, suspend, and resume.

Control flow: probe allocates `scsi_info_t`, loops PCMCIA configs, maps optional memory window, requests IRQ, enables the card, initializes hardware, allocates a SCSI host, adds and scans it. Queueing accepts only one command, initializes `struct scsi_pointer` scratch fields over the SG list, and starts arbitration/selection. The ISR disables chip IRQs, distinguishes timer/SCSI/FIFO events, handles selection timeout, reselection, bus reset, bus free, and SCSI phases, then drives command, data, status, and message transfers. Data movement uses polling loops around FIFO counters and bus phase changes.

State and persistence: `nsp_hw_data` stores base addresses, current command, FIFO count, transfer mode, timer/selection counters, SDTR table per target, message buffer, info string, lock, and PCMCIA glue pointer. Per-command `struct scsi_pointer` stores phase, status/message, SG cursor, residuals, and data direction. SDTR state persists per target until reset, suspend, or host init clears it.

Dependencies and integration: depends on PCMCIA, SCSI midlayer, low-level I/O helpers in `nsp_io.h`, protocol definitions in `nsp_cs.h`, and direct inclusion of `nsp_message.c` plus optional `nsp_debug.c`.

Risks: legacy single-command design, hand-rolled phase machine, polling timeouts in interrupt context, optional memory mapping with integer address casts, and quirks for skipped data phases. 32-bit burst modes require alignment and sufficiently large residuals. Test signals include card ID matching, host scan, command completion under IO8/IO32/MEM32, SDTR status display, selection timeout, reselection, suspend/resume reset, and error-handler bus reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.h

Purpose: hardware and driver-state header for the 16-bit NinjaSCSI PCMCIA driver. It declares register offsets, bit masks, bus-phase encodings, transfer mode constants, state structures, prototypes, and debug hooks for `nsp_cs.c`, `nsp_io.h`, `nsp_message.c`, and optional debug code.

Important APIs and types: register definitions cover base and indexed registers such as `IRQCONTROL`, `SCSIIRQMODE`, `SCSIBUSCTRL`, `SCSIBUSMON`, `ARBITSTATUS`, `TRANSFERMODE`, `SYNCREG`, FIFO and counter registers. `sync_data` stores per-target SDTR negotiation state. `nsp_hw_data` is the per-host object with I/O/MMIO addresses, current command, FIFO/timer counters, transfer mode, `Sync[]`, message buffer, info string, lock, and PCMCIA glue pointer. `scsi_info_t` binds a PCMCIA device to a SCSI host. Enums describe SCSI phases, data direction, and burst modes.

Control flow support: bus monitor masks and `BUSPHASE_*` constants drive the ISR switch. `BUFFER_ADDR()` maps the current SG element into a CPU address for PIO/MMIO FIFO transfer. Prototypes document the separation between PCMCIA lifecycle, SCSI template methods, hardware init/selection, data transfer, message handling, and reset handling.

State and persistence: this header defines all persistent runtime state for the driver but stores none itself. SDTR states persist per target, while command phase and SG cursor live per active SCSI command.

Dependencies and integration: depends on PCMCIA and SCSI data structures and on midlayer `struct scsi_pointer` private command storage. Included by `nsp_cs.c` before `nsp_io.h`.

Risks: the header encodes old assumptions such as initiator ID 7, 8 targets, and `struct scsi_pointer` use as driver private storage. Several prototypes are duplicated or commented. Test signals include compile coverage for all included C fragments, correct phase decoding in debug output, and stable PIO/MMIO modes across supported cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_cs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_debug.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_debug.c

Purpose: optional debug helpers for the 16-bit NinjaSCSI PCMCIA driver. It prints SCSI command names, command bytes, LBA/length summaries, current software phase, hardware bus phase, and accumulated message bytes.

Important APIs and functions: `print_opcodek()` and `print_commandk()` decode CDB opcodes using static group tables. `show_command()` prints a command. `show_phase()` translates `nsp_scsi_pointer(SCpnt)->phase` into the driver's phase names. `show_busphase()` decodes bus phase masks. `show_message()` dumps `nsp_hw_data::MsgBuffer`.

Control flow: included only under `NSP_DEBUG` from `nsp_cs.c`. Queueing, ISR, and message paths call the show helpers through macros that become no-ops in normal builds.

State and persistence: no mutable state beyond static string tables. It observes current command and driver state supplied by callers.

Dependencies and integration: depends on `COMMAND_SIZE()`, `printk`, `nsp_hw_data`, phase constants, bus-phase constants, and the command-private accessor used by the driver.

Risks: debug output inside timing-sensitive PIO/interrupt paths may change behavior. `show_phase()` must stay synchronized with enum values. Test signals include debug build compile, meaningful opcode and phase logs, and no output in non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_io.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_io.h

Purpose: low-level inline I/O helpers for the 16-bit NinjaSCSI PCMCIA driver. It wraps base register I/O, indexed register selection, 8/16/32-bit FIFO port bursts, and memory-mapped 32-bit FIFO access.

Important APIs: `nsp_write()`/`nsp_read()` access byte I/O registers. `nsp_index_write()`/`nsp_index_read()` select `INDEXREG` and transfer via `DATAREG`. FIFO helpers include `nsp_fifo8_read/write`, `nsp_fifo16_read/write`, and `nsp_fifo32_read/write`. MMIO helpers include `nsp_mmio_write/read`, `nsp_mmio_index_write/read`, and `nsp_mmio_fifo32_read/write`.

Control flow: data-phase code in `nsp_cs.c` chooses IO8, IO32, or MEM32 and calls the corresponding FIFO helper. Hardware init and phase handling use indexed register helpers for control/status registers.

State and persistence: stateless. Correct operation depends on valid PCMCIA I/O base or mapped memory address and caller-managed transfer alignment/counts.

Dependencies and integration: depends on architecture I/O primitives, `NSP_MMIO_OFFSET`, and register constants from `nsp_cs.h`.

Risks: MMIO helpers use raw pointer casts and integer base types rather than strongly typed `__iomem`. `nsp_mmio_fifo32_read/write()` signatures take `unsigned int base` but call helpers expecting `unsigned long`, which is one reason Kconfig restricts normal 64-bit builds. Test signals include IO8 baseline transfer, 32-bit burst transfer only for aligned buffers, MEM32 transfer on mapped-window cards, and compile-test coverage on restricted architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_message.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_message.c

Purpose: message phase helper included directly into `nsp_cs.c`. It implements manual SCSI message-in and message-out transfers for the NinjaSCSI chip, including a documented quirk where the chip interrupts only on phase changes and therefore requires polling for additional REQ assertions in the same phase.

Important APIs and functions: `nsp_message_in()` loops reading `SCSIDATAIN`, asserts/deasserts ACK through `SCSIBUSCTRL`, waits for REQ negation, and stores bytes in `data->MsgBuffer`. `nsp_message_out()` sends bytes from `data->MsgBuffer` via `nsp_xfer()` and polls for further message-out REQ signals.

Control flow: `nspintr()` calls these helpers in `BUSPHASE_MESSAGE_IN` and `BUSPHASE_MESSAGE_OUT`. Message-in results are later parsed for SDTR and command-complete/disconnect messages; message-out typically sends IDENTIFY and optional SDTR.

State and persistence: mutates `nsp_hw_data::MsgBuffer` and `MsgLen`. No external persistence; message state belongs to the active command.

Dependencies and integration: depends on `nsp_cs.c` local helpers `nsp_negate_signal()`, `nsp_expect_signal()`, and `nsp_xfer()`, plus indexed I/O and message constants. Direct inclusion makes functions static to the driver translation unit.

Risks: bounded by `MSGBUF_SIZE`, but unusual target message sequences can still trigger rejection or incomplete handling in the caller. Polling timeouts and ACK sequencing are timing-sensitive. Test signals include multi-byte SDTR message receipt, IDENTIFY/SDTR message-out, disconnect/command-complete messages, and no buffer overflow with maximum message length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/qlogic_stub.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/qlogic_stub.c

Purpose: PCMCIA wrapper for Qlogic FAS SCSI controllers using the shared `qlogicfas408` core. It configures PCMCIA resources, initializes chip-specific quirks, allocates/registers a SCSI host, wires interrupts, and handles removal/resume.

Important APIs and functions: `qlogicfas_driver_template` delegates SCSI operations to `qlogicfas408_*`. `qlogic_detect()` probes chip type, sets initiator ID, calls `qlogicfas408_setup()`, allocates the host, populates `qlogicfas408_priv`, requests IRQ, adds/scans the host, and returns it. `qlogic_probe()`, `qlogic_config_check()`, `qlogic_config()`, `qlogic_release()`, and `qlogic_resume()` implement the PCMCIA lifecycle.

Control flow: probe allocates `scsi_info_t`, sets config flags, and calls config. Config loops resources, enables the card, applies manufacturer-specific ATA command writes for selected cards, chooses base+16 for 32-byte windows, and calls `qlogic_detect()`. Remove removes the host, frees IRQ, disables the card, and puts the host. Resume re-enables the card, reapplies quirks, and calls the shared reset helper.

State and persistence: `scsi_info_t` stores PCMCIA device, host, and manufacturer ID, although this file never assigns `manf_id` from `link->manf_id`. Shared core private state stores base, IRQ, initiator ID, and info string.

Dependencies and integration: depends on PCMCIA, SCSI midlayer, `qlogicfas408.h`, and active-low open-drain PCMCIA interrupt mode via `INT_TYPE 0`.

Risks: missing `info->manf_id` assignment likely prevents manufacturer quirk paths from running. `qlogic_resume()` calls `qlogicfas408_host_reset(NULL)`, noted as ugly, relying on core behavior. Test signals include listed PCMCIA IDs, IRQ handling, base offset behavior for 32-byte windows, shared-core command completion, remove cleanup, and resume reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/qlogic_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/sym53c500_cs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/sym53c500_cs.c

Purpose: standalone PCMCIA SCSI driver for Symbios Logic 53C500-based cards. It implements chip initialization, PIO data transfer, interrupt-driven SCSI phase handling, queueing, reset, BIOS geometry, a `fast_pio` sysfs attribute, and PCMCIA resource lifecycle.

Important APIs and functions: hardware helpers `chip_init()` and `SYM53C500_int_host_reset()` program register sets and reset the SCSI bus. `SYM53C500_pio_read()` and `SYM53C500_pio_write()` move SG data through the PIO FIFO, optionally using 32-bit string I/O. `SYM53C500_intr()` handles reset, PIO/parity/gross errors, disconnect, and SCSI phases. SCSI template methods include `SYM53C500_queue()`, `SYM53C500_host_reset()`, `SYM53C500_biosparm()`, and `SYM53C500_info()`. Sysfs methods `SYM53C500_show_pio()` and `SYM53C500_store_pio()` expose `fast_pio`. PCMCIA lifecycle uses `SYM53C500_probe()`, `SYM53C500_config()`, `SYM53C500_release()`, `SYM53C500_detach()`, and `sym53c500_resume()`.

Control flow: PCMCIA probe allocates `scsi_info_t`, configures I/O/IRQ, applies manufacturer quirks, initializes the chip, allocates a SCSI host, requests IRQ, sets host fields, adds/scans the host, and stores it. Queueing writes destination ID and CDB into the chip FIFO, then starts selection. Interrupts read PIO and SCSI status, perform SG PIO transfers for data phases, initiate command completion on status, capture status/message in message-in, reject unsupported message-out/save-pointer/disconnect cases, and call `scsi_done()` on disconnect or error.

State and persistence: `sym53c500_data` stores the current command and `fast_pio`; `sym53c500_cmd_priv` stores status, message, and phase per command. `fast_pio` persists for the host lifetime and can be changed via sysfs.

Dependencies and integration: depends on PCMCIA, SCSI midlayer, I/O port primitives, shared IRQ registration, and class-to-SCSI-host sysfs helpers. It registers as `sym53c500_cs`.

Risks: single-current-command state has no explicit busy rejection in queueing. The ISR dereferences `current_SC` before checking for NULL, making unexpected interrupts hazardous. SAVE_POINTERS and DISCONNECT are rejected, limiting disconnect/reconnect support. Error paths call `SYM53C500_release(link)` in some failed states where `link->priv->host` may not be initialized. Test signals include card probe/scan, fast and slow PIO reads/writes, sysfs `fast_pio` validation, host reset, BIOS geometry, command completion, parity/PIO error handling, and card removal during idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/sym53c500_cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/Makefile

Purpose: Kbuild file for the PM8001/PM80xx SAS/SATA HBA driver. It builds the `pm80xx` module when `CONFIG_SCSI_PM8001` is enabled and defines its component objects.

Important entries: `obj-$(CONFIG_SCSI_PM8001) += pm80xx.o` creates the module. `CFLAGS_pm80xx_tracepoints.o := -I$(src)` ensures tracepoint compilation can find local headers. `pm80xx-y` aggregates `pm8001_init.o`, `pm8001_sas.o`, `pm8001_ctl.o`, `pm8001_hwi.o`, `pm80xx_hwi.o`, and `pm80xx_tracepoints.o`.

Control flow: no runtime code. Kbuild composes the low-level init, SAS transport, control, hardware-interface, PM80xx hardware-interface, and tracepoint units into one driver object.

State and persistence: none directly; build configuration persists as the selected module layout.

Dependencies and integration: tied to the PM8001 source directory and SCSI/SAS driver Kconfig symbol outside this file.

Risks: missing objects or tracepoint include flags would break module builds. Test signals include `CONFIG_SCSI_PM8001=m/y` builds, tracepoint object compilation, and module link with all listed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_chips.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_chips.h

Purpose: low-level register access helper header for PMC-Sierra SPC 8001/PM8001 SAS/SATA HBAs. It provides small inline helpers for memory and BAR-based 32-bit reads/writes plus a PCI BAR-number to internal index mapper.

Important APIs: `pm8001_read_32()` and `pm8001_write_32()` dereference host memory/register windows directly. `pm8001_cr32()` and `pm8001_cw32()` perform BAR-indexed `readl`/`writel` through `pm8001_hba_info::io_mem[bar].memvirtaddr`. `pm8001_mr32()` and `pm8001_mw32()` operate on an arbitrary `void __iomem *` plus offset. `get_pci_bar_index()` maps PCI BAR addresses `0x18/0x1c` to index 1, `0x20` to 2, `0x24` to 3, and all others to 0.

Control flow: other PM8001 driver units include this header to abstract register access. There is no branching beyond BAR-index mapping.

State and persistence: stateless. Correctness depends on `pm8001_hba_info` having valid ioremapped BARs and callers using offsets for 32-bit registers.

Dependencies and integration: depends on Linux MMIO primitives and the PM8001 host structure declaration from surrounding driver headers. The license block allows BSD-style redistribution or GPLv2.

Risks: `pm8001_write_32()` uses `void *` pointer arithmetic and direct `__le32 *` dereference rather than `writel`, so it is appropriate only for memory that is safe for CPU stores, not arbitrary MMIO. Endianness differs between direct helpers and `readl`/`writel` helpers. Test signals include register read/write smoke tests during adapter initialization, BAR mapping validation, sparse/endian build checks, and exercising all BAR index cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_chips.h -->
