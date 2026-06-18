# Research group: subset-b-005228

This grouped report covers the requested legacy SCSI host adapter files under `sources/distributed-fs/ceph-client/drivers/scsi/`. Each section preserves its source path and is wrapped with the reconciliation markers required for splitting into one source-tree-aligned research document per file.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha152x.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aha152x.c

## Purpose
`aha152x.c` is the Linux SCSI host driver for Adaptec AHA-152x and related AIC-6260/AIC-6360/AIC-6370 style ISA or PCMCIA controllers, with additional support for TC1550 register layout quirks and optional ISA PnP/autodetection. It implements host discovery, controller reset, SCSI command queuing, interrupt-driven phase handling, error recovery hooks, BIOS geometry reporting, and proc-style diagnostics for the `aha152x` host template.

The driver is low-level and mostly state-machine oriented. It does not delegate bus phases to firmware. Instead, it directly drives SCSI signals, transfer counters, FIFO/DMA controls, and interrupt masks through the register macros from `aha152x.h`.

## Important APIs, Types, And Functions
The key exported or externally used entry points are `aha152x_probe_one()`, `aha152x_release()`, and `aha152x_host_reset_host()`, which are also declared for the PCMCIA stub in `aha152x.h`. The module entry and exit paths are `aha152x_init()` and `aha152x_exit()`, with `aha152x_setup()` parsing built-in kernel command-line configuration when not built as a module.

`struct aha152x_hostdata` is the central per-host state. It stores the issue, current, disconnected, and done command queues; the host spinlock; current and previous bus state; negotiation state per target; transfer/message buffers; reset delay and configuration flags; selected port windows; and the list node used by the global `aha152x_host_list`. `struct aha152x_cmd_priv`, allocated via the SCSI command private area, tracks per-command data pointer, scatterlist cursor, residual count, status byte, message byte, command-sent flag, and phase flags. `struct aha152x_scdata`, stored in `host_scribble`, links commands in internal queues and holds completion/error-handler save state.

The `states[]` table maps `enum aha152x_state` values to optional phase init/run/end callbacks and whether the phase uses SPIO mode. Important callbacks include `busfree_run()`, `seldo_run()`, `seldi_run()`, `selto_run()`, `msgi_run()`, `msgo_run()`, `cmd_run()`, `status_run()`, `datai_run()`, `datao_run()`, `parerr_run()`, and `rsti_run()`.

The SCSI mid-layer integration is through `aha152x_driver_template`: `queuecommand`, abort, device reset, bus reset, BIOS geometry, proc show/write callbacks, `cmd_size`, queue depth, SG limits, and DMA boundary. The queue front door is `aha152x_queue_lck()` via `DEF_SCSI_QCMD()`, which calls `aha152x_internal_queue()`.

## Control Flow
Initialization collects setup from command-line/module parameters, optional compile-time `SETUP0/SETUP1`, ISA PnP devices, and BIOS/port probing. `checksetup()` validates accepted ports, IRQ range, SCSI ID, and boolean feature fields. `aha152x_probe_one()` allocates the SCSI host, initializes hostdata, programs IDs and options, resets the SCSI bus, resets controller ports, tests the IRQ path using a temporary software interrupt handler, installs the real IRQ handler, adds the host, and scans the bus.

Runtime command flow starts in `aha152x_internal_queue()`. It initializes command phase flags, allocates `host_scribble` for normal commands, prepares the scatterlist cursor and residual, appends the command to `ISSUE_SC`, turns on the activity LED for the first outstanding command, and arms expected interrupts. When the bus is free, `busfree_run()` promotes the first issue command to `CURRENT_SC` and starts selection. `seldo_run()` sends IDENTIFY and optionally ABORT, BUS DEVICE RESET, or SDTR negotiation messages. `cmd_run()` emits the CDB, data phases move payload through the FIFO/data port, `status_run()` captures target status, `msgi_run()` handles completion/disconnect/reselection/SDTR messages, and final completion is consolidated by `busfree_run()`.

The IRQ path is split. `intr()` verifies the register block is present, checks `INTSTAT`, disables controller interrupts, marks service pending, and schedules a global work item. `run()` walks `aha152x_host_list` and calls `is_complete()` per host. `is_complete()` loops while expected interrupt conditions are already pending: it calls `update_state()`, ends the previous state, switches SPIO/DMA setup as needed, acknowledges phases, initializes the new state, runs the current state handler, and re-arms expected interrupts.

Error handling is partially integrated with the mid-layer. `aha152x_abort()` can remove not-yet-issued commands but explicitly cannot abort running or disconnected commands. `aha152x_device_reset()` reuses a command to issue a BUS DEVICE RESET and waits for completion. `aha152x_bus_reset_host()` flushes eligible queued/disconnected commands and asserts `SCSIRSTO`. Check condition handling reuses the failed command with `scsi_eh_prep_cmnd()` to fetch sense data, then restores the original command with `scsi_eh_restore_cmnd()`.

## State And Persistence Behavior
Persistent state is in memory only: hostdata queues, per-target synchronous negotiation arrays, current state/previous state, current message buffers, command counters, and optional statistics. Hardware state is held in controller registers, FIFO state, interrupt masks, transfer counters, and SCSI bus signals. No on-disk persistence exists.

Queue state is protected by `QLOCK`, but parts of phase processing deliberately drop the lock while touching hardware. Command ownership moves among `ISSUE_SC`, `CURRENT_SC`, `DISCONNECTED_SC`, and `DONE_SC`. Completion frees `host_scribble` for non-reset commands before calling `scsi_done()`. Reset command completions use a stack completion rather than normal mid-layer completion.

## Dependencies And Integration Points
The driver depends on Linux SCSI mid-layer APIs, SPI transport helper `spi_populate_sync_msg()`, ISA/ISAPnP resource APIs, IRQ/workqueue APIs, `scsicam_bios_param()`, and low-level port I/O. It directly includes `aha152x.h` for register layout and bit definitions. It integrates with PCMCIA via non-static probe/release/reset helpers and with module/kernel boot configuration via module parameters and `__setup`.

## Risks
The phase engine is timing-sensitive and depends on correct hardware interrupt, FIFO, and SCSI phase behavior. Several paths call `panic()` through `aha152x_error()` for internal state corruption, so unexpected concurrent bottom-half state can crash the system. `aha152x_abort()` only handles not-yet-issued commands, leaving active or disconnected aborts to fail. Data in/out loops poll with long timeouts and use manual residual repair, so FIFO count mismatches can stall or produce noisy diagnostics. The global `aha152x_tq` work item and global host list require careful lifetime handling when multiple hosts and removal interact. The reselection path assumes IDENTIFY is delivered and that the disconnected command can be found by target/lun.

## Test Signals
Meaningful test signals include successful module load with valid parameters, IRQ software-interrupt self-test success, `scsi_add_host()` and `scsi_scan_host()` success, successful selection and command completion for simple INQUIRY/READ/WRITE, correct disconnect/reconnect under tagged or queue depth pressure, SDTR negotiation accept/reject behavior, check-condition/request-sense recovery, abort/reset return codes, and proc output from `aha152x_show_info()` showing queues, ports, and negotiated targets. Hardware or emulation tests should exercise both AHA152x and TC1550 port layouts plus shared IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha152x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha152x.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aha152x.h

## Purpose
`aha152x.h` defines the register map, bit fields, helper macros, autoconfiguration layout, and externally visible setup/probe interfaces for the AHA-152x driver. The C driver uses this header as its complete symbolic interface to the AIC-6260/6360 style port registers.

## Important APIs, Types, And Functions
The header declares the maximum queue depth `AHA152X_MAXQUEUE`, the revision string `AHA152X_REVID`, port offset macros such as `SCSISEQ`, `SXFRCTL0`, `SCSISIG`, `SCSIRATE`, `SSTAT0`, `SSTAT1`, `SIMODE0`, `DMACNTRL0`, `DMASTAT`, and `DATAPORT`, and constants for SCSI phases, interrupt sources, FIFO/DMA controls, and test registers.

It defines `aha152x_config`, a packed-ish bitfield union over the board's PORTA/PORTB configuration word. Field aliases such as `cf_irq`, `cf_id`, `cf_tardisc`, `cf_syncneg`, and `cf_parity` are used by autodetection in `aha152x.c`.

The low-level access macros are `SETPORT()`, `GETPORT()`, `SETBITS()`, `CLRBITS()`, `TESTHI()`, `TESTLO()`, and `SETRATE()`. `struct aha152x_setup` carries user or autodetected configuration into `aha152x_probe_one()`. The declared functions are `aha152x_probe_one()`, `aha152x_release()`, and `aha152x_host_reset_host()`.

## Control Flow
This header has no runtime control flow, but it encodes the control vocabulary used by the driver. The state machine tests `SSTAT0`, `SSTAT1`, `DMASTAT`, and `SCSISIG` bits, acknowledges interrupt conditions through write-to-clear bits, selects SCSI phases via `P_*` masks, enables interrupt sources through `SIMODE0/1`, and changes FIFO/DMA behavior through `SXFRCTL0` and `DMACNTRL0`.

## State And Persistence Behavior
All state described here is volatile hardware state: register bits, transfer counters, FIFO status, message/data phase signals, and configuration latch fields. `aha152x_config` captures firmware/jumper-like configuration exposed through controller ports, but the header itself persists nothing.

## Dependencies And Integration Points
The macros assume `HOSTIOPORT0` and `HOSTIOPORT1` are defined in the including C file and depend on Linux `inb()`/`outb()`. The public setup structure depends on `struct Scsi_Host` from the SCSI mid-layer through declarations only. The header is tightly coupled to `aha152x.c`; most macros are not general-purpose.

## Risks
The port macros directly evaluate their arguments and perform raw I/O, so misuse can touch incorrect hardware ports. The `aha152x_config` bitfield layout is compiler- and endian-sensitive in principle, although it reflects legacy driver assumptions. Several definitions encode write-to-clear status bits; confusing read status with clear values can lose interrupts. `SETRATE()` masks with `0x7f`, which is correct for this hardware but can hide invalid negotiation values if callers do not validate first.

## Test Signals
Compile coverage is the primary test for this header. Runtime signals include successful port tests using `O_STACK`/`O_DMACNTRL1`, correct phase decoding in proc diagnostics, expected interrupt enable strings, valid autodetected IRQ/SCSI ID fields from `aha152x_config`, and correct data transfer behavior when `ENDMA`, `_8BIT`, `WRITE_READ`, `DFIFOEMP`, and `DFIFOFULL` paths are exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha152x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1542.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aha1542.c

## Purpose
`aha1542.c` implements the Linux SCSI host driver for Adaptec AHA-1542 compatible ISA and ISA PnP adapters. It uses the adapter mailbox/CCB interface, ISA DMA, IRQ handling, coherent DMA memory for mailboxes and command blocks, and a per-command bounce buffer limited to 16 sectors.

## Important APIs, Types, And Functions
`struct aha1542_hostdata` stores BIOS translation mode, round-robin mailbox indices, command pointers by mailbox, and coherent DMA-backed mailbox/CCB arrays. `struct aha1542_cmd` stores the per-command coherent bounce buffer and DMA handle.

Hardware command helpers include `wait_mask()`, `aha1542_outb()`, `aha1542_out()`, `aha1542_in()`, `aha1542_intr_reset()`, and status mapping `makecode()`. Detection and setup are handled by `aha1542_test_port()`, `aha1542_getconfig()`, `aha1542_mbenable()`, `aha1542_query()`, `aha1542_set_bus_times()`, and `aha1542_hw_init()`. Runtime entry points are `aha1542_queuecommand()`, `aha1542_interrupt()`, `aha1542_dev_reset()`, `aha1542_bus_reset()`, `aha1542_host_reset()`, and `aha1542_biosparam()`.

The `driver_template` integrates with the SCSI mid-layer and supplies `init_cmd_priv`/`exit_cmd_priv`, queue depth, max sectors, SG settings, and error handlers. Bus integration is through an `isa_driver` plus optional `pnp_driver`.

## Control Flow
Module init registers the PnP driver when enabled, then registers an ISA driver across `MAXBOARDS` slots. `aha1542_isa_match()` and `aha1542_pnp_probe()` call `aha1542_hw_init()`. Hardware init requests the I/O region, allocates a SCSI host, tests the adapter, applies bus timing options, rejects AHA-1740 emulation mode, queries DMA/IRQ/SCSI ID, sets a 24-bit coherent DMA mask, allocates mailboxes and CCBs, initializes the mailbox interface with `CMD_MBINIT`, requests IRQ/DMA, adds the host, and scans.

For each command, `aha1542_queuecommand()` short-circuits REQUEST SENSE because auto-sense data is already copied at completion time. For write commands it copies request segments into the coherent bounce buffer. It selects a free outgoing mailbox round-robin under the host lock, fills the CCB with target/lun, direction, CDB, data length, and data pointer, sets mailbox status to start, and sends `CMD_START_SCSI`.

`aha1542_interrupt()` clears adapter interrupts, scans incoming mailboxes for completed CCBs, maps mailbox CCB pointers back to CCB indices, frees DMA mappings/bounce state, copies auto sense data if target status is CHECK CONDITION, converts host/target status into `cmd->result`, clears `int_cmds[mbo]`, and calls `scsi_done()`.

Reset flow either sends a device-reset CCB (`op = 0x81`) or writes bus/host reset bits to the control port, waits for idle, reinitializes mailboxes after hard reset, and clears pending commands that are not protected by `soft_reset`.

## State And Persistence Behavior
Driver state is volatile host private memory plus coherent DMA objects shared with the adapter. The mailbox arrays form the persistent runtime contract with firmware until driver removal. BIOS translation mode is cached after adapter query and used by `bios_param()`. Per-command bounce buffers are allocated once at command-private init and reused for command submissions. There is no file or disk persistence.

## Dependencies And Integration Points
The driver depends on ISA, PnP, legacy DMA channel APIs, coherent DMA mapping, SCSI mid-layer command/request helpers, and the mailbox/CCB definitions in `aha1542.h`. It uses module parameters `isapnp`, `io[]`, `bus_on[]`, `bus_off[]`, and `dma_speed[]`.

## Risks
The driver panics if no free mailbox is found, which converts queue accounting bugs into system crashes. The bounce buffer size is fixed by `AHA1542_MAX_SECTORS`; correctness relies on the host template `max_sectors` matching that allocation. `aha1542_pnp_probe()` scans for an empty `io[]` slot but uses the loop index afterward; if all slots are occupied, the index can be out of range. `aha1542_dev_reset()` reserves `int_cmds[mbo]` for the reset command, but completion/error semantics are minimal. Interrupt paths print unusual adapter interrupts but do not deeply recover from SCRD/HACC/MBOA beyond clearing the interrupt.

## Test Signals
Relevant signals include successful detection at configured I/O ports, correct inquiry/config responses, mailbox init success, correct DMA channel setup or no-DMA behavior for compatible boards, read/write completion through all mailboxes, auto-sense delivery without issuing REQUEST SENSE to hardware, bus/host reset recovery, and BIOS geometry results for both 64/32 and 255/63 translation modes. PnP probing should be tested with free and fully occupied `io[]` slot arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1542.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1542.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aha1542.h

## Purpose
`aha1542.h` defines the AHA-1542 I/O register interface, adapter command opcodes, mailbox format, scatter/gather chain format, CCB layout, byte packing helpers, and driver sizing constants used by `aha1542.c`.

## Important APIs, Types, And Functions
Register macros include `STATUS(base)`, `INTRFLAGS(base)`, `CONTROL(base)`, and `DATA(base)`. Status and interrupt bits include `STST`, `DIAGF`, `INIT`, `IDLE`, `CDF`, `DF`, `ANYINTR`, `SCRD`, `HACC`, `MBOA`, and `MBIF`. Control bits include `HRST`, `SRST`, `IRST`, and `SCRST`.

Adapter command constants include mailbox initialization, start SCSI command, inquiry, bus timing, DMA speed, configuration query, setup query, echo, extended BIOS query, and mailbox enable. `struct mailbox` stores a status byte and 24-bit CCB pointer. `struct chain` is the hardware scatter/gather entry. `struct ccb` is the command control block with operation, target/lun/direction byte, CDB length, request sense allocation length, 24-bit data pointer/length, link pointer, host and target status, and combined CDB/sense storage.

`any2scsi()` writes a 24-bit big-endian adapter address/length field. `scsi2int()` and `xscsi2int()` decode 24-bit and 32-bit SCSI-style values. Constants `MAX_CDB`, `MAX_SENSE`, `AHA1542_REGION_SIZE`, and `AHA1542_MAILBOXES` size the driver structures.

## Control Flow
The header has no executable control flow except `any2scsi()`. Its structures are consumed by `setup_mailboxes()`, `aha1542_queuecommand()`, and `aha1542_interrupt()`: outgoing mailboxes point at CCBs, CCBs describe work to firmware, and incoming mailboxes report completion status and the CCB pointer.

## State And Persistence Behavior
Mailboxes and CCBs are persistent runtime DMA state shared between host and adapter until release. The status bytes in `struct mailbox` are both ownership and completion indicators. The `ccb` status fields preserve firmware completion details until the interrupt handler converts them into SCSI result codes.

## Dependencies And Integration Points
The header includes Linux integer types and expects Linux `BIT()` definitions. It is tightly integrated with `aha1542.c` and the AHA-1542 firmware mailbox specification. It uses 24-bit pointer representations, so callers must enforce DMA addressability; the C file does this with a 24-bit DMA mask.

## Risks
The 24-bit pointer helpers silently truncate higher address bits if used without an appropriate DMA mask. `MAX_SENSE` is 14 while the C driver copies up to `SCSI_SENSE_BUFFERSIZE` from the CCB sense area, relying on the larger `cdb[MAX_CDB + MAX_SENSE]` layout and padding behavior. The CCB format is hardware ABI, so structure packing, field widths, and allocation in coherent memory are critical.

## Test Signals
Tests should validate that mailbox CCB pointers round-trip through `any2scsi()` and `scsi2int()`, that reset/inquiry/config commands observe expected status bits, that CCB target/lun/direction fields match READ/WRITE commands, and that auto-sense bytes are placed where `aha1542_interrupt()` expects them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1542.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1740.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aha1740.c

## Purpose
`aha1740.c` is the Linux EISA enhanced-mode driver for Adaptec AHA-1740/174x SCSI host adapters. Unlike AHA-1542 emulation mode, it uses the 1740 enhanced control block and mailbox registers, EISA device matching, DMA-mapped ECB arrays, and firmware-supported command execution.

## Important APIs, Types, And Functions
`struct aha1740_hostdata` stores the matched EISA device, BIOS translation flag, last ECB index, DMA address for the in-host ECB array, and `AHA1740_ECBS` ECBs. `struct aha1740_sg` stores a per-command coherent scatter/gather chain plus DMA bookkeeping. ECB and register definitions are from `aha1740.h`.

Important functions include `ecb_dma_to_cpu()`, `ecb_cpu_to_dma()`, `aha1740_show_info()`, `aha1740_makecode()`, `aha1740_test_port()`, `aha1740_intr_handle()`, `aha1740_queuecommand_lck()`, `aha1740_getconfig()`, `aha1740_biosparam()`, `aha1740_eh_abort_handler()`, `aha1740_probe()`, and `aha1740_remove()`. `aha1740_template` supplies the SCSI host template, while `aha1740_driver` supplies the EISA probe/remove hooks.

## Control Flow
Module init registers the EISA driver. EISA matching uses IDs `ADP0000`, `ADP0001`, `ADP0002`, and `ADP0400`. Probe requests the slot I/O region, verifies enhanced mode, reads IRQ trigger and translation configuration, resets the adapter if mailbox output/busy state is not ready, allocates a SCSI host, maps the embedded ECB array for bidirectional DMA, requests the IRQ as shared for level-triggered interrupts, adds the host, and scans.

Queueing skips REQUEST SENSE because firmware auto-sense is enabled. `aha1740_queuecommand_lck()` finds a free ECB, reserves it by setting `cmdw`, fills CDB, target/lun, direction, suppress-underrun, auto-request-sense, sense/status pointers, and completion context. It allocates one coherent `aha1740_sg` block per command, maps the SCSI command, writes SG entries when present, waits for mailbox-out readiness and adapter-not-busy, writes the ECB DMA address to MBOXOUT, and sends `ATTN_START | target`.

The interrupt handler loops while `G2STAT_INTPEND` is set, reads adapter status and the inbound ECB pointer, clears the EISA interrupt, marks host ready for mailbox completions, unmaps SCSI DMA, frees the per-command SG block, copies sense data and maps status for CCB errors, clears the ECB, and calls the saved done callback. Hardware failure interrupts panic; async events are logged and acknowledged.

## State And Persistence Behavior
Runtime state is volatile. The ECB array is embedded in hostdata but DMA-mapped for the adapter, and an ECB's nonzero `cmdw` acts as the driver's in-use marker. Each queued command allocates a short-lived coherent SG block stored in `SCpnt->host_scribble` until interrupt completion. The BIOS translation flag is cached from EISA configuration and used for disk geometry.

## Dependencies And Integration Points
The file depends on the Linux EISA bus layer, SCSI mid-layer, DMA mapping APIs, IRQ APIs, and the enhanced-mode hardware definitions in `aha1740.h`. It integrates as a normal EISA driver and explicitly avoids 1542 emulation mode by using enhanced-mode port checks.

## Risks
Queue allocation sets `cmdw` before allocating the SG block; if SG allocation fails, the ECB is not cleared before returning busy, which can permanently reduce queue capacity. `BUG_ON(nseg < 0)` converts DMA map failure into a crash. The mailbox wait loops can panic on adapter busy deadlock. `aha1740_biosparam()` checks `ip[2] > 1024` before initializing `ip[2]`, so the extended translation branch depends on an incoming value rather than calculated geometry. Interrupt handling trusts inbound DMA addresses to index into the mapped ECB array.

## Test Signals
Useful signals include EISA ID match and enhanced-mode detection, successful IRQ trigger handling for both edge and shared level modes, queueing across all ECB slots, SG mapping and completion, auto-sense on CCB errors, async event logging, remove-time DMA unmap and region release, and geometry output with extended translation enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1740.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1740.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aha1740.h

## Purpose
`aha1740.h` defines the EISA configuration register map, enhanced-mode mailbox registers, status/control bits, scatter/gather chain format, ECB hardware layout, command opcodes, and sizing constants for the AHA-1740 driver.

## Important APIs, Types, And Functions
The EISA config macros cover HID, EBCNTRL, PORTADR, BIOSADR, INTDEF, SCSIDEF, BUSDEF, and reserved/config bytes. Runtime register macros cover `G2INTST`, `G2STAT`, inbound and outbound mailboxes, `ATTN`, and `G2CNTRL`. Status constants identify CCB completion, retry, error, hard failure, immediate command success/error, and async events. Control constants include hard reset, interrupt reset, host ready, and attention operations.

`struct aha1740_chain` is the SG entry. `struct ecb` is the enhanced control block with command word, bitfield flags, data pointer/length, status and link pointers, sense pointer/length, CDB, embedded sense/status buffers, and driver-private `SCpnt` and `done` fields. Command opcodes include initiator SCSI command, diagnostics, initialize SCSI, read sense, firmware download, inquiry, and target command. Constants define `AHA1740_ECBS` and `AHA1740_SCATTER`.

## Control Flow
The header has no independent control flow. `aha1740.c` uses these definitions to probe enhanced mode, detect pending interrupts, acknowledge mailbox completions, start ECBs by writing mailbox and attention registers, and translate ECB status/sense data into SCSI result codes.

## State And Persistence Behavior
The ECB is the main state carrier. Fields before the "driver defined" comment are hardware ABI and are shared with the adapter through DMA. Fields after that comment are host-only completion context and cached auto-sense/status storage. Register status bits are transient hardware state.

## Dependencies And Integration Points
The header depends on Linux integer types and is bound to the EISA enhanced-mode programming model. It duplicates SCSI byte-conversion helpers (`any2scsi`, `xany2scsi`, `scsi2int`, `xscsi2int`) for older 24-bit and 32-bit fields.

## Risks
The `struct ecb` bitfield layout is compiler ABI sensitive and must match the adapter's expected little-endian layout. The pointer conversion macros are multi-statement macros without `do { } while (0)`, so they are unsafe in conditional single-statement contexts. `MAX_SENSE` and `MAX_STATUS` must match both firmware behavior and driver copy sizes. DMA address width and alignment are implicit in the enhanced-mode interface.

## Test Signals
Signals include correct EISA config decoding, enhanced-mode bit detection through `PORTADDR_ENH`, valid interrupt status classification, ECB DMA address round-trips, SG chain transfer success, firmware auto-sense into the embedded sense buffer, and command start via `ATTN_START`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aha1740.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/Makefile

## Purpose
This Makefile defines how the Linux kernel builds the Adaptec `aic7xxx` Fast through Ultra160 driver and `aic79xx` Ultra320 driver families, including platform glue, optional EISA/PCI front ends, optional pretty register printers, and generated sequencer/register headers from `aicasm`.

## Important APIs, Types, And Functions
Kbuild targets are `obj-$(CONFIG_SCSI_AIC7XXX) += aic7xxx.o` and `obj-$(CONFIG_SCSI_AIC79XX) += aic79xx.o`. `aic7xxx-y` includes core files `aic7xxx_core.o` and `aic7xxx_93cx6.o`, platform files `aic7xxx_osm.o` and `aic7xxx_proc.o`, plus conditional EISA (`aic7770.o`, `aic7770_osm.o`), PCI (`aic7xxx_pci.o`, `aic7xxx_osm_pci.o`), and pretty-print objects. `aic79xx-y` similarly includes core, PCI, OSM, proc, OSM PCI, and optional pretty-print objects.

The Makefile declares generated files `aic7xxx_seq.h`, `aic7xxx_reg.h`, `aic7xxx_reg_print.c`, `aic79xx_seq.h`, `aic79xx_reg.h`, and `aic79xx_reg_print.c` as clean targets. It defines dependencies from all driver objects to generated sequence/register headers.

## Control Flow
When firmware build configs are enabled, `aicasm` is built from `aicasm/*.[chyl]` and invoked with include, register, optional pretty-print, output, and sequence inputs. When firmware build configs are disabled, shipped generated register print C files are used for pretty printing. `subdir += aicasm` ensures clean descends into the assembler directory.

## State And Persistence Behavior
The Makefile persists no runtime state. Build artifacts are generated in the object tree and removed by `make clean`. Conditional generated-file variables act as build graph state based on kernel config.

## Dependencies And Integration Points
This file integrates with Kbuild, `CONFIG_SCSI_AIC7XXX`, `CONFIG_SCSI_AIC79XX`, EISA/PCI config symbols, register pretty-print configs, firmware build configs, and the local `aicasm` tool. It is the integration point that makes `aic7770.c` and `aic7770_osm.c` part of `aic7xxx.o` only when `CONFIG_EISA` is enabled.

## Risks
Generated headers are prerequisites for many objects; stale or missing `aicasm` outputs can break broad builds. Pretty-print generation depends on OSM header names. `WARNINGS_BECOME_ERRORS` can turn compiler warning drift into build failures. The shipped generated paths are only wired for register print C files, so sequence/register header availability depends on repository contents or firmware build settings.

## Test Signals
Useful signals include successful `make M=drivers/scsi/aic7xxx` under AIC7XXX and AIC79XX configs, with and without EISA/PCI and pretty-print options; clean removal of generated files; correct `aicasm` rebuild when sequence/register inputs change; and no missing generated header errors in incremental builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770.c

## Purpose
`aic7770.c` contains product-specific probe and attach logic for AIC7770-based EISA/VL Adaptec 274x/284x controllers in the aic7xxx driver family. It identifies boards, maps registers, reads EISA or VL/SEEPROM configuration, initializes core `ahc_softc` state, applies bus timing/autoflush settings, maps interrupts, and enables the board.

## Important APIs, Types, And Functions
`aic7770_ident_table` maps hardware IDs to names and setup callbacks. `aic7770_config()` is the main attach routine used by the OS-specific EISA glue. Static setup helpers are `ahc_aic7770_VL_setup()`, `ahc_aic7770_EISA_setup()`, and `ahc_aic7770_setup()`. `aic7770_chip_init()` restores bus timing/autoflush/enable state during chip init. `aha2840_load_seeprom()` reads 284x SEEPROM through `aic7xxx_93cx6` helpers and seeds target rate, disconnect, SCSI ID, parity, reset, extended translation, and termination flags.

## Control Flow
`aic7770_config()` first applies the product setup callback, maps I/O registers through the OSM function, disables interrupts, initializes the common softc, installs `aic7770_chip_init`, resets the chip, validates IRQ vector from `INTDEF`, and records edge-triggered interrupts. For EISA boards it reads BIOS and SCSI configuration registers to derive channel, host ID, termination, and extended translation. For VL AHA-2840 boards it attempts SEEPROM loading. It then enables autoflush, programs FIFO threshold and bus-off timing from `HOSTCONF`, calls common `ahc_init()`, maps the interrupt, increments init level, and enables bus drivers through `BCTL`.

## State And Persistence Behavior
State is stored in `struct ahc_softc`: chip type, feature/bug flags, board description, `our_id`, termination flags, extended translation flags, SEEPROM config pointer, bus timing cache, init level, and interrupt trigger flags. Hardware state includes `SBLKCTL`, `BUSSPD`, `BUSTIME`, `BCTL`, target rate registers, disconnect disable registers, and SCSI config registers. SEEPROM contents are persistent on hardware but only read and applied here.

## Dependencies And Integration Points
The file depends on `aic7xxx_osm.h` for OS glue, `aic7xxx_inline.h` for register access, `aic7xxx_93cx6.h` for SEEPROM access, and common aic7xxx core functions such as `ahc_softc_init()`, `ahc_reset()`, `ahc_init()`, `ahc_chip_init()`, and `ahc_intr_enable()`. It calls OSM-provided `aic7770_map_registers()` and `aic7770_map_int()` implemented in `aic7770_osm.c`.

## Risks
Failure after register mapping or partial softc init relies on caller/core cleanup paths; errors must preserve resource ownership. IRQ validation is strict and rejects unexpected firmware settings. If SEEPROM checksum fails, defaults are used, which may alter negotiation, termination, or host ID behavior. EISA channel and termination handling differs for wide and non-wide features and can be wrong if feature flags are misdetected. The code writes hardware target rate and disconnect masks directly from SEEPROM data.

## Test Signals
Signals include successful EISA/VL product match, valid IRQ vector acceptance, SEEPROM read/checksum success and fallback paths, correct host ID and termination flags, common `ahc_init()` success, interrupt mapping, and bus enable. Regression tests should cover BIOS-disabled defaults, Olivetti differential IDs, AHA-2840 SEEPROM settings, and reset-time `aic7770_chip_init()` restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770_osm.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770_osm.c

## Purpose
`aic7770_osm.c` is the Linux OS-specific EISA attachment glue for AIC7770-based aic7xxx controllers. It maps I/O regions and IRQs, binds EISA IDs to the generic `aic7770_config()` path, registers the resulting SCSI host, and tears resources down on removal.

## Important APIs, Types, And Functions
The core exported glue functions are `aic7770_map_registers()` and `aic7770_map_int()`, which are called from `aic7770.c`. EISA bus callbacks are `aic7770_probe()` and `aic7770_remove()`. Module-level EISA registration helpers are `ahc_linux_eisa_init()` and `ahc_linux_eisa_exit()`. `aic7770_ids` maps EISA IDs such as `ADP7771`, `ADP7756`, and `ADP7783` to offsets in `aic7770_ident_table`.

## Control Flow
`aic7770_probe()` computes the slot I/O base, creates a name like `ahc_eisa:<slot>`, allocates an `ahc_softc`, stores the Linux device pointer, calls `aic7770_config()` with the identity selected by EISA driver data, stores the softc in driver data, and registers the SCSI host through `ahc_linux_register_host()`. `aic7770_map_registers()` requests the I/O region and records PIO bus-space fields. `aic7770_map_int()` chooses shared IRQ mode unless the core marked the interrupt edge-triggered, then requests `ahc_linux_isr`.

Removal unregisters the SCSI host when present, disables interrupts under the aic7xxx lock, and frees the softc. Driver init and exit simply register/unregister the `eisa_driver`.

## State And Persistence Behavior
Persistent runtime state is in `struct ahc_softc` and its platform data: requested I/O port, IRQ number, Linux device pointer, registered SCSI host, and driver data pointer. No disk persistence exists. Resource ownership is transferred to the softc cleanup path after successful config.

## Dependencies And Integration Points
The file depends on Linux device/EISA APIs, resource APIs, IRQ APIs, and aic7xxx Linux OSM helpers from `aic7xxx_osm.h`. It is conditionally included in the `aic7xxx` build by the Makefile when `CONFIG_EISA` is enabled.

## Risks
If `ahc_alloc()` fails after `kstrdup()` succeeds, the allocated name is not explicitly freed in this file, relying on allocation conventions or leaking it. After `aic7770_config()` succeeds but `ahc_linux_register_host()` fails, cleanup responsibility depends on the caller and returned error path. IRQ sharing depends on the core correctly setting `AHC_EDGE_INTERRUPT`. Probe returns negative or negated errors depending on core return conventions.

## Test Signals
Signals include EISA ID table matching, successful I/O region request, correct shared versus edge IRQ flags, `aic7770_config()` success, `ahc_linux_register_host()` success, SCSI host removal on device removal, interrupt disable before free, and unregister behavior on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7770_osm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx.h

## Purpose
`aic79xx.h` is the core OS-neutral definition header for Adaptec AIC79xx Ultra320 SCSI controllers. It defines register-facing macros, chip/features/bugs/flags enums, hardware and software SCB layouts, queue and target-mode structures, transfer negotiation state, SEEPROM/VPD formats, flexport constants, the main `ahd_softc`, and public function declarations used by the aic79xx core and OS modules.

## Important APIs, Types, And Functions
Important constants include target/lun limits, max transfer size, SCB queue sizes, target-mode command counts, and bus reset delay. Macros such as `SCSIID_TARGET()`, `SCB_GET_TARGET()`, `BUILD_TCL()`, `AHD_BUILD_COL_IDX()`, and `AHD_SET_SCB_COL_IDX()` encode target/lun/channel addressing.

Core enums describe chip identity (`ahd_chip`), hardware features (`ahd_feature`), silicon workarounds (`ahd_bug`), software/runtime flags (`ahd_flag`), SCB state (`scb_flag`), message flags/types, register window modes, device role, search actions, negotiation modes, and queue algorithm.

Major structures include `struct hardware_scb`, `struct ahd_dma_seg`, `struct ahd_dma64_seg`, `struct scb`, `struct scb_data`, `struct target_cmd`, `struct ahd_tmode_tstate`, `struct ahd_transinfo`, `struct seeprom_config`, `struct vpd_config`, `struct ahd_suspend_state`, `struct ahd_completion`, `struct ahd_softc`, `struct ahd_devinfo`, and `struct ahd_pci_identity`. The header also declares public core APIs for PCI config, SCB management, initialization, reset, flexport access, error recovery, device info compilation, negotiation updates, target mode, and debug dumping.

## Control Flow
As a header, it defines no direct execution path. Its declarations shape the aic79xx core control flow: allocate/init `ahd_softc`, configure PCI or other bus front end, allocate SCBs and DMA maps, queue SCBs through QINFIFO, complete through QOUTFIFO, manage pending/disconnected queues, negotiate SPI width/sync/PPR settings, apply hardware bug workarounds, handle target-mode events, and suspend/resume register state.

## State And Persistence Behavior
`struct ahd_softc` is the central persistent runtime state for a controller. It holds bus handles, SCB data, pending SCBs, register mode state, platform data, target-mode state, timer/statistics fields, chip/features/bugs/flags, SEEPROM config, QIN/QOUT FIFO cursors, qfreeze count, critical sections, overrun buffer, channel and ID information, target command FIFO, message buffers, DMA shared data maps, suspend snapshots, interrupt coalescing parameters, and user negotiation bitmasks.

`struct hardware_scb` is the controller-visible command state, while `struct scb` wraps it with OS and DMA metadata. SEEPROM and VPD structures model persistent adapter configuration read from hardware, but this header only defines their layout.

## Dependencies And Integration Points
The header includes generated `aic79xx_reg.h`, so it depends on the Makefile/aicasm generation path. It also depends on platform typedefs supplied by OS-specific headers before inclusion, such as bus-space, DMA, device, and queue/list types. It is consumed by aic79xx core, PCI front end, OSM layer, proc/debug code, and generated register pretty printers.

## Risks
This header is a dense hardware ABI. Layout changes in `struct hardware_scb`, SG entries, completion entries, or SEEPROM/VPD structs can break firmware communication. Many flags represent silicon errata; failing to set the right bug bits can cause subtle data corruption or failed recovery. Queue constants assume power-of-two FIFO sizes and tag ranges. Target-mode sections are conditionally compiled and rely on platform CAM-like types when enabled. The generated register dependency means stale `aic79xx_reg.h` can desynchronize macros from sequencer firmware.

## Test Signals
Signals include successful builds with generated register headers, SCB allocation and tag-index mapping up to queue limits, correct 32-bit and 64-bit SG programming, negotiation transitions for async, sync, DT, packetized, and paced modes, reset and qfreeze behavior, interrupt coalescing thresholds, suspend/resume state restoration, SEEPROM checksum and parse behavior, and debug dumps that decode register state consistently with generated tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx.h -->
