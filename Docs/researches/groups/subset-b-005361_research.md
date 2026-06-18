# subset-b-005361 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw2.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw2.h

## Purpose
This header embeds the second-generation NCR/Symbios/LSI 53C8xx SCSI SCRIPTS firmware used by the `sym53c8xx_2` driver. It is not a conventional declaration-only header: it defines the exact microprogram fragments that the host driver copies into DMA memory or on-chip SRAM, patches with bus addresses, and starts on the SCRIPTS processor. The firmware drives initiator selection, reselection, message handling, data movement, completion queueing, phase-mismatch recovery, negotiation message hand-offs, abort/reset message sequences, and the small startup snoop test.

## Important APIs, Types, and Functions
The important exported data contracts are `struct SYM_FWA_SCR`, `struct SYM_FWB_SCR`, and `struct SYM_FWZ_SCR`, plus the matching static instances `SYM_FWA_SCR`, `SYM_FWB_SCR`, and `SYM_FWZ_SCR`. The struct fields are label-sized arrays, and their array lengths are the ABI for all `SCRIPTA_BA()`, `SCRIPTB_BA()`, `SCRIPTZ_BA()`, and `PADDR_*()` patch references in the rest of the driver. The comments explicitly require length updates when SCRIPTS instructions are changed.

`SYM_FWA_SCR` is the main fast path, usually suitable for 4 KiB on-chip RAM: `start`, `getjob_*`, `select`, `dispatch`, command/data/status/message phases, `done`, `complete_error`, save/restore data pointers, disconnect handling, reselection lookup, data-in/data-out tables, and phase-mismatch mini-scripts. `SYM_FWB_SCR` holds secondary paths that may remain in host memory except on 8 KiB RAM chips: 64-bit startup, abort selection, extended message parsing, WDTR/SDTR/PPR responses, data overrun drain, bad reselection handlers, bad-status callback, and SCRIPTS-side phase-mismatch contexts. `SYM_FWZ_SCR` is a short initialization/snoop-test script used by `sym_snooptest()`.

## Control Flow
The SCRIPTS scheduler reads `startpos` from the circular start queue, loads a CCB DSA, selects a target, sends IDENTIFY/tag/negotiation messages, transfers the CDB, and dispatches by current SCSI phase. Normal completions store the completed DSA into the done queue, perform a dummy read to flush posted DMA writes, raise `INTFLY`, and return to `start`. Error or policy situations use programmed interrupts such as `SIR_COMPLETE_ERROR`, `SIR_BAD_SCSI_STATUS`, `SIR_MSG_RECEIVED`, `SIR_DATA_OVERRUN`, and task-recovery SIRs; `sym_hipd.c` interprets those interrupts.

Reselection flow resolves target, LUN, and optional tag through the target table, LUN table, and ITLQ table populated by the C code. Bad reselections branch to dedicated labels that request `M_ABORT`, `M_ABORT_TAG`, or reset handling. Data phase flow jumps through `lastp`; `data_in` and `data_out` arrays are filled at runtime according to `SYM_CONF_MAX_SG`. Phase mismatch is handled either by SCRIPTS mini-contexts (`pm0`, `pm1`) on capable chips or by C recovery.

## State and Persistence Behavior
The file itself has no persistent runtime storage outside static firmware templates, but it defines the hardware-visible state machine layout. The firmware reads and writes CCB fields such as `phys.head.status`, `lastp`, `savep`, selection registers, scatter-gather entries, message buffers, and phase-mismatch contexts. It also depends on HCB data words such as `done_pos`, `startpos`, `targtbl`, `pm*_data_addr`, and `scratch`. Runtime persistence is in DMA memory owned by `struct sym_hcb`, `struct sym_ccb`, `struct sym_tcb`, and `struct sym_lcb`.

## Dependencies and Integration Points
This file depends on the SCRIPTS opcode macros and address macros from the surrounding driver headers. It is consumed through the firmware descriptor machinery included by `sym_glue.h` and initialized by `sym_hcb_attach()`. `sym_start_up()` patches/downloads the scripts, starts the DSP at `init` or `start64`, and uses labels from this file for reset, start, done, abort, and phase-mismatch operations. The C interrupt handler in `sym_hipd.c` is tightly coupled to this file's SIR codes, critical sections, and label boundaries.

## Risks
The highest risk is ABI drift between label array sizes, generated instruction offsets, and C-side patching. A one-word insertion without updating the struct field length can redirect jumps to the wrong instruction. SCSI phase handling is timing-sensitive; critical sections such as `getjob`, `ungetjob`, `done`, and `sel_for_abort` are explicitly unsafe to interrupt and force host reset if interrupted. DMA ordering is also subtle: the script relies on dummy reads and host memory barriers to make done-queue writes visible before interrupts. Wide-residue, overrun, and phase-mismatch paths are hardware-specific and easy to regress on older or errata-affected chips.

## Test Signals
Useful signals are successful module probe with SCRIPTS copied or downloaded to SRAM, CCB start-queue scheduling, done-queue completions under load, reselection with tagged and untagged commands, CHECK CONDITION auto-sense, WDTR/SDTR/PPR negotiation, parity-error recovery, MODIFY DATA POINTER and IGNORE WIDE RESIDUE handling, data overrun/underrun reporting, abort and target-reset paths, SCSI bus reset recovery, and `sym_snooptest()` passing on each supported MMIO/DMA platform.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_fw2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.c

## Purpose
This file is the Linux-facing glue for the `sym53c8xx_2` PCI SCSI host driver. It translates Linux SCSI midlayer, SPI transport, PCI probe/remove, module parameters, DMA mapping, IRQ/timer handling, proc controls, and PCI error recovery into calls into the OS-independent HIPD core in `sym_hipd.c`.

## Important APIs, Types, and Functions
Global setup is held in `sym_driver_setup` and exposed through module parameters such as `cmd_per_lun`, `burst`, `led`, `diff`, `irqm`, `buschk`, `hostid`, `verb`, `debug`, `settle`, `nvram`, `excl`, and `safe`. `sym2_setup_params()` parses `excl` and applies the legacy safe-mode profile.

The SCSI host template `sym2_template` wires Linux callbacks to this driver: `sym53c8xx_queue_command`, `sym53c8xx_sdev_init`, `sym53c8xx_sdev_configure`, `sym53c8xx_sdev_destroy`, error handlers for abort/target reset/bus reset/host reset, and optional proc read/write handlers. `struct sym_ucmd` stores the per-command error-handler completion pointer in `scsi_cmd_priv()`. `sym_xpt_done()`, `sym_xpt_async_bus_reset()`, `sym_set_cam_result_error()`, `sym_setup_data_and_start()`, `sym_scatter()`, and `sym_log_bus_error()` are the main glue functions called from the core.

PCI lifecycle is implemented by `sym2_probe()`, `sym_attach()`, `sym2_remove()`, `sym_detach()`, `sym_iomap_device()`, `sym_check_supported()`, `sym_check_raid()`, `sym_set_workarounds()`, and `sym_config_pqs()`. PCI error recovery is implemented by `sym2_io_error_detected()`, `sym2_io_slot_dump()`, `sym2_io_slot_reset()`, and `sym2_io_resume()`. SPI transport integration is via `sym2_transport_functions`, including setters for offset, period, width, and DT mode.

## Control Flow
Module init attaches the SPI transport and registers the PCI driver. Probe enables the PCI device, requests BAR regions, identifies the chip, maps register/SRAM resources, skips RAID-owned chips, applies hardware workarounds, reads NVRAM when enabled, and calls `sym_attach()`. Attach allocates `Scsi_Host`, allocates the HCB, selects DMA mask, calls `sym_hcb_attach()` to initialize the core and SCRIPTS state, requests IRQ, resets the SCSI bus, starts SCRIPTS, starts the timer, and fills host limits before `scsi_add_host()` and `scsi_scan_host()`.

Command submission enters `sym53c8xx_queue_command_lck()` with the host lock held. It respects bus-settle suspension after resets, allocates a CCB through `sym_queue_command()`, maps DMA/scatterlist entries in `sym_scatter()`, builds the CDB and data pointers in `sym_setup_data_and_start()`, and starts the core via `sym_put_start_queue()`. IRQ handling calls `sym_interrupt()` under the host lock. The timer keeps the settle interval and can reap missed completions on affected bridges.

Error handlers synchronize with the core using completions and SEM/SIGP-driven SCRIPTS stops. Abort marks a CCB and may wait up to five seconds for completion. Target reset asks the core to send a target reset and waits for affected CCBs. Bus reset calls `sym_reset_scsi_bus()`. Host reset also cooperates with PCI error recovery via `sym_data->io_reset`.

## State and Persistence Behavior
Runtime state is split between Linux objects and the core HCB. `struct sym_data` binds a `Scsi_Host` to `struct sym_hcb`, `struct pci_dev`, and the optional PCI reset completion. `struct sym_shcb` in the HCB tracks MMIO/SRAM mappings, timer, instance names, settle timing, and the `Scsi_Host`. Per-LUN Linux state in `struct sym_slcb` records requested tags and configured queue depth. Module parameters persist only as module/global runtime configuration; device transfer settings are negotiated dynamically and may be seeded from NVRAM.

## Dependencies and Integration Points
This file depends on the Linux SCSI midlayer, SPI transport class, PCI core, DMA mapping API, interrupt and timer APIs, proc info support when configured, and `sym_nvram.c`. It is the only layer that calls `scsi_done()`, `scsi_dma_map()`, `scsi_dma_unmap()`, `scsi_add_host()`, `scsi_scan_host()`, `spi_attach_transport()`, and PCI error-recovery callbacks. It integrates with `sym_hipd.c` through exported core functions such as `sym_hcb_attach()`, `sym_interrupt()`, `sym_queue_scsiio()`, `sym_abort_scsiio()`, `sym_reset_scsi_target()`, and `sym_hcb_free()`.

## Risks
Resource unwind is complex because BAR mappings are owned by `sym_iomap_device()` until `sym_attach()` succeeds, then by the HCB teardown path. Error handlers mix host-lock sections with waits and must clear `eh_done` on timeout without racing a late completion. `sym53c8xx_eh_target_reset_handler()` currently returns `SCSI_SUCCESS` even after some timeout/failure paths set `sts`, which is a behavior worth reviewing. DMA scatter setup adjusts odd-byte wide transfers by increasing mapped lengths, so residual and unmap behavior depend on the core's accounting. PCI recovery disables IRQ and device access, so all paths must respect `pci_channel_offline()`.

## Test Signals
Primary validation is build coverage across MMIO/proc/NVRAM options, module parameter parsing, probe and remove on supported PCI IDs, failure injection at each probe step, SCSI scan with NVRAM scan restrictions, queue-depth configuration and tagged-command enablement, DMA mapping with max-SG and odd-wide transfers, IRQ-driven completions, timer fallback where configured, all SCSI EH callbacks, PCI AER or slot-reset recovery, SPI transport sysfs setters, proc read/write controls when enabled, and clean module unload after active I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.h

## Purpose
This header defines the Linux adaptation contract for the `sym53c8xx_2` driver. It pulls in the required kernel, SCSI, PCI, and transport headers; defines Linux-specific configuration hooks and barriers; maps endian-sensitive SCRIPTS patching helpers; and declares the OS-facing state embedded in the core driver structures.

## Important APIs, Types, and Functions
Key macros include `SYM_CONF_TIMER_INTERVAL`, `SYM_OPT_LIMIT_COMMAND_REORDERING`, printk compatibility wrappers, `MEMORY_READ_BARRIER()`, `MEMORY_WRITE_BARRIER()`, `cpu_to_scr()`, `scr_to_cpu()`, `SCSI_SUCCESS`, `SCSI_FAILED`, `sym_name()`, and `sym_print_addr()`. The header explicitly rejects `SYM_CONF_CHIP_BIG_ENDIAN`; chips are supported only in little-endian addressing mode.

`struct sym_slcb` is the Linux-specific LUN extension and stores `reqtags` plus `scdev_depth`. `struct sym_shcb` is the Linux-specific host extension embedded in the HCB: unit number, instance/chip names, `Scsi_Host *`, MMIO/SRAM ioremaps, timer, last timer tick, and settle-time state. `struct sym_device` is a probe-time wrapper used before full HCB allocation, carrying `pci_dev`, bus addresses, mapped addresses, chip descriptor, NVRAM pointer, and selected host ID. `struct sym_data` is the `Scsi_Host` private data tying Linux to `struct sym_hcb`.

Inline helpers include `sym_get_hcb()` for hostdata lookup, `sym_set_cam_status()`, `sym_get_cam_status()`, and `sym_set_cam_result_ok()`. Cross-file declarations include `sym_set_cam_result_error()`, `sym_xpt_done()`, `sym_xpt_async_bus_reset()`, `sym_setup_data_and_start()`, `sym_log_bus_error()`, and `sym_dump_registers()`.

## Control Flow
The header has no runtime control flow by itself, but it determines how control flows between Linux glue and the core. `sym_glue.c` allocates `struct sym_data` as `Scsi_Host` private data and uses `sym_get_hcb()` from every callback. `sym_hipd.c` calls the declared glue functions when it completes commands, reports reset events, needs Linux result mapping, or dumps PCI/register diagnostics. Including `sym_fw.h` and `sym_hipd.h` after the Linux definitions lets the OS-neutral code compile with Linux-specific HCB/LCB extensions available.

## State and Persistence Behavior
State declared here is runtime-only. `struct sym_shcb` persists for the life of one host adapter and stores mappings and timer state. `struct sym_slcb` persists per allocated LUN while the SCSI device exists. `struct sym_data` persists for the `Scsi_Host` lifetime and is also used during PCI error recovery. No settings are written back to firmware or NVRAM by this header.

## Dependencies and Integration Points
This file is the include pivot for Linux kernel APIs, SCSI core APIs, SPI transport, local driver headers (`sym53c8xx.h`, `sym_defs.h`, `sym_misc.h`, `sym_fw.h`, and `sym_hipd.h`), and architecture I/O functions. Its barrier and endian macros are used by the SCRIPTS/core paths for DMA-visible queue ordering and script instruction patching. Its type extensions are referenced throughout `sym_glue.c`, `sym_hipd.c`, and NVRAM helpers.

## Risks
Because this header defines structure extensions that are embedded into core types, small layout or macro changes can break many source files at once. `sym_get_cam_status()` returns `host_byte(cmd->result)` while `sym_set_cam_status()` writes the host byte field directly; callers must preserve SCSI status bits correctly. The SCRIPTS endian macros assume little-endian chip addressing; adding big-endian chip mode would require a larger audit than changing the macro. Barrier macros are minimal wrappers and rely on explicit PCI dummy reads elsewhere for posted-write ordering.

## Test Signals
Useful signals include allmodconfig/build testing for the driver, sparse/endian checking around `cpu_to_scr()` and `scr_to_cpu()`, command result mapping tests through success and error completions, host reset/bus reset settle-time behavior, timer initialization and deletion, PCI error-recovery use of `struct sym_data`, and compile coverage with optional proc/NVRAM/MMIO configuration combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.c

## Purpose
This file implements the hardware-independent protocol driver core for Symbios/LSI 53C8xx and 53C1010 PCI SCSI I/O processors. It owns chip reset/startup, clock and transfer-parameter calculation, SCRIPTS setup and patching, CCB/LCB/TCB allocation, start and done queues, interrupt recovery, SCSI message negotiation, data pointer/residual handling, task abort/reset recovery, and command completion. Linux-specific calls are kept behind `sym_glue.h` hooks.

## Important APIs, Types, and Functions
Externally important entry points include `sym_print_xerr()`, `sym_reset_scsi_bus()`, `sym_lookup_chip_table()`, `sym_put_start_queue()`, `sym_start_up()`, `sym_interrupt()`, `sym_clear_tasks()`, `sym_get_ccb()`, `sym_free_ccb()`, `sym_alloc_lcb()`, `sym_free_lcb()`, `sym_queue_scsiio()`, `sym_reset_scsi_target()`, `sym_abort_scsiio()`, `sym_complete_error()`, `sym_complete_ok()`, `sym_hcb_attach()`, and `sym_hcb_free()`.

Important internal functions are `sym_chip_reset()`, `sym_soft_reset()`, `sym_getclock()`, `sym_getpciclock()`, `sym_getsync()`, `sym_prepare_setting()`, `sym_snooptest()`, `sym_log_hard_error()`, `sym_prepare_nego()`, `sym_wakeup_done()`, `sym_recover_scsi_int()`, `sym_int_par()`, `sym_int_ma()`, `sym_int_sir()`, `sym_sir_bad_scsi_status()`, `sym_sir_task_recovery()`, `sym_evaluate_dp()`, `sym_modify_dp()`, and `sym_compute_residual()`. The `sym_dev_table` maps PCI IDs/revisions to chip names, capabilities, offsets, burst limits, and clock-divisor counts.

## Control Flow
Attach flow starts in `sym_hcb_attach()`: it records the selected firmware descriptor, saves BIOS/firmware register settings, resets the chip, derives clock/bus/transfer settings, allocates start/done queues, target tables, SCRIPTS buffers, CCB hash buckets, bad-LUN tables, and an initial CCB, copies firmware templates, runs firmware setup/binding, and verifies cache snooping. `sym_start_up()` clears queues, patches scripts, resets active jobs with `DID_RESET`, programs chip registers and interrupts, initializes target negotiation state, downloads SCRIPTS to SRAM when available, starts the DSP, and notifies the upper layer on reset reasons.

Command flow starts with a CCB from `sym_get_ccb()`, which assigns tagged or untagged nexus resources and populates reselect tables. `sym_queue_scsiio()` builds IDENTIFY/tag and optional negotiation messages, initializes selection/register fields and status fields, then calls Linux glue to build CDB/data descriptors. `sym_put_start_queue()` publishes the CCB bus address into the circular start queue with ordering barriers and signals the SCRIPTS processor.

Completion flow is split. Normal SCRIPTS completions place DSAs into the done queue and raise `INTFLY`; `sym_interrupt()` clears that flag and `sym_wakeup_done()` calls `sym_complete_ok()`. Error completions stop SCRIPTS and call into `sym_complete_error()`, which computes residuals, removes not-yet-started jobs for the device from the start queue, restarts SCRIPTS, maps result status, and flushes the completion queue. CHECK CONDITION and COMMAND TERMINATED trigger an internal REQUEST SENSE command before completing the original command.

Interrupt flow prioritizes fast recoverable conditions: parity plus phase mismatch, plain phase mismatch, and SIR callbacks. SCSI reset restarts all hardware and target state. Selection timeout, unexpected disconnect, and bus-mode change have targeted recovery. Fatal DMA, PCI, SGE, HTH, ABRT, IID, and unknown hard conditions are logged and reset. The code explicitly avoids trusting script state when interrupted inside queue-critical firmware regions.

## State and Persistence Behavior
Persistent per-adapter runtime state lives in `struct sym_hcb`: feature bits, saved/restored register values, clock and transfer limits, SCRIPTS addresses, start/done queues, CCB hash table, target table, bad-LUN/task actions, DMA maps, message buffers, and interrupt synchronization flags. `struct sym_tcb` stores per-target transfer registers, negotiation goals, user flags, LUN tables, reset flags, and printed transfer agreement state. `struct sym_lcb` tracks per-LUN tag resources, reselect entries, queue depth, and clear flags. `struct sym_ccb` persists each active command's CDB, messages, data descriptors, phase-mismatch contexts, status, tag, residual/extreme pointer state, and abort flags.

No driver state is persisted across unload except external effects such as SCSI device mode changes or reset side effects. NVRAM influences initial host/target policy but is read by other code. Negotiated SPI parameters persist until reset, target reset, bus mode change, or renegotiation.

## Dependencies and Integration Points
The core depends on chip register definitions, SCRIPTS firmware descriptors and patch helpers, queue primitives, DMA allocation helpers, Linux glue callbacks, SPI message helpers, SCSI status/message constants, and optional NVRAM setup. It integrates upward through `sym_glue.c` for DMA mapping, command completion, reset notification, PCI logging, and register dumps. It integrates downward with the SCRIPTS processor through DMA-visible HCB/CCB/TCB/LCB structures and hard-coded script labels.

## Risks
This is high-risk low-level driver code. Recovery depends on exact DSP/DSA interpretation, hardware FIFO accounting, SCSI phase semantics, and the assumption that DMA-visible structures remain coherent. The phase-mismatch and residual code handles many edge cases but can still return conservative or negative residuals. Negotiation falls back from PPR to legacy modes for compatibility, but target-specific bugs can still cause resets or degraded transfer modes. CCB/tag accounting must stay consistent with reselect tables or stale DSAs can complete the wrong command. Many paths run under host lock/IRQ context and allocate with atomic constraints. Chip errata workarounds are tied to PCI IDs and revisions.

## Test Signals
Strong signals include successful probe across representative chip families, cache snoop test pass, SCRIPTS startup from host memory and SRAM, async/wide/sync/PPR negotiation, DT/LVD and SE fallback behavior, tagged and untagged I/O with reselection, max-SG I/O, odd-byte wide transfers, CHECK CONDITION auto-sense, queue-full depth reduction when enabled, MODIFY DATA POINTER and IGNORE WIDE RESIDUE, parity error recovery, selection timeout, unexpected disconnect, bus reset, target reset, command abort and timeout abort, PCI/DMA hard-error logging, PCI channel-offline behavior through glue, and teardown without leaked CCB/LCB/SCRIPTS allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_hipd.c -->
