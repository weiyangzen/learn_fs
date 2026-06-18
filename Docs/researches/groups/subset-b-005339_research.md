# subset-b-005339 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_os.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_os.c

## Purpose
`qla_os.c` is the Linux OS integration layer for the QLogic/Brocade `qla2xxx` Fibre Channel HBA driver. It binds the qla2xxx hardware-specific core to the PCI bus, SCSI midlayer, FC transport, optional target mode, optional FC-NVMe support, firmware loading, timers, workqueues, kernel threads, PCI error recovery, sysfs/debug setup, and module lifecycle.

The file is intentionally broad. It owns module parameters, global caches, the `scsi_host_template`, the `pci_driver`, chip-family `isp_operations` dispatch tables, probe/remove/shutdown, queue-pair allocation, SCSI command submission, SCSI error handling, adapter memory allocation, background DPC processing, FC-port loss/relogin scheduling, PUREX/RDP ELS response handling, 83xx IDC reset coordination, heartbeat/watchdog timer behavior, firmware request/release, and PCI AER/FLR callbacks.

## Important APIs, Types, and Functions
The public/module-facing globals and entry points include `qla2x00_version_str`, `srb_cachep`, many `ql2x*` module parameters, `qla2xxx_transport_vport_template`, `qla2x00_sp_free_dma()`, `qla2x00_sp_compl()`, `qla2xxx_qpair_sp_free_dma()`, `qla2xxx_qpair_sp_compl()`, `qla2x00_wait_for_hba_online()`, `qla2x00_wait_for_sess_deletion()`, `qla2x00_wait_for_chip_reset()`, `qla2x00_eh_wait_for_pending_commands()`, `qla2x00_loop_reset()`, `qla2x00_abort_all_cmds()`, `qla2x00_free_fcports()`, `qla2x00_mark_device_lost()`, `qla2x00_mark_all_devices_lost()`, `qla2x00_set_exlogins_buffer()`, `qla2x00_free_exlogin_buffer()`, `qla2x00_set_exchoffld_buffer()`, `qla2x00_free_exchoffld_buffer()`, `qla2x00_create_host()`, `qla2x00_alloc_work()`, `qla2x00_post_work()`, several `qla2x00_post_*_work()` helpers, `qla24xx_sched_upd_fcport()`, `qla24xx_create_new_sess()`, `qla2x00_do_work()`, `qla24xx_post_relogin_work()`, `qla2x00_relogin()`, `qla83xx_schedule_work()`, `qla83xx_*` IDC helpers, `qla24xx_process_purex_rdp()`, `qla24xx_process_purex_list()`, `qla2xxx_wake_dpc()`, `qla2x00_timer()`, `qla2x00_request_firmware()`, `qla_pci_set_eeh_busy()`, and `qla_schedule_eeh_work()`.

Core static integration functions are `qla2x00_probe_one()`, `qla2x00_remove_one()`, `qla2x00_shutdown()`, `qla2x00_mem_alloc()`, `qla2x00_mem_free()`, `qla2xxx_queuecommand()`, `qla2xxx_mqueuecommand()`, the SCSI error handlers `qla2xxx_eh_abort()`, `qla2xxx_eh_device_reset()`, `qla2xxx_eh_target_reset()`, `qla2xxx_eh_bus_reset()`, and `qla2xxx_eh_host_reset()`, the DPC kernel thread `qla2x00_do_dpc()`, PCI error callbacks `qla2xxx_pci_error_detected()`, `qla2xxx_pci_mmio_enabled()`, `qla2xxx_pci_slot_reset()`, `qla2xxx_pci_resume()`, `qla_pci_reset_prepare()`, and `qla_pci_reset_done()`, plus module init/exit.

Important data structures are mostly defined in the qla headers, but this file instantiates and wires `struct qla_hw_data`, `scsi_qla_host_t`, `struct req_que`, `struct rsp_que`, `struct qla_qpair`, `srb_t`, `fc_port_t`, `struct qla_work_evt`, `struct fw_blob`, `struct isp_operations`, `struct scsi_host_template`, `struct pci_error_handlers`, and `struct pci_driver`. It also creates global kmem caches for SRBs and CT6 contexts, a firmware blob table for `ql2100_fw.bin` through `ql2800_fw.bin`, and build-time ABI checks for hardware IOCB/register/NVRAM/dump structure sizes.

## Control Flow
Module load starts in `qla2x00_module_init()`. It verifies packed hardware ABI sizes with `BUILD_BUG_ON()`, creates the qla2xxx trace instance, allocates the SRB slab cache, initializes target-mode support through `qlt_init()`, derives the driver version string, attaches FC transport templates, registers a minimal character device, then registers the PCI driver. Module unload reverses this by unregistering PCI, releasing cached firmware, destroying caches, releasing transports, exiting target mode, and dropping trace state.

PCI probe is the largest path. `qla2x00_probe_one()` selects IO/MEM BAR policy from the PCI device id, enables the PCI function, disables MQ and firmware dump allocation for kdump kernels, allocates and initializes `struct qla_hw_data`, configures EDIF security state, sets chip flags with `qla2x00_set_isp_flags()`, selects the per-family `isp_operations` table, maps MMIO/MQIO via `iospace_config`, configures DMA addressing, allocates adapter memory and base request/response rings, allocates the SCSI host with `qla2x00_create_host()`, fills SCSI host capabilities, requests interrupts, allocates queue maps and optional qpairs, initializes target mode, initializes firmware/adapter state, creates the DPC thread and workqueues, starts the one-second timer, registers DIF/DIX capabilities, enables interrupts, adds the SCSI host, scans if in initiator/dual mode, creates sysfs/debugfs attributes, logs adapter identity, and adds target-mode support. Each failure label unwinds the subset already allocated.

SCSI IO enters through `qla2xxx_queuecommand()`. The path rejects commands during unload, EEH permanent failure, missing/blocked FC rports, unsupported DIF/DIX commands, deleted/offline ports, dead loop state, and active retry-delay windows. If blk/scsi-mq is enabled, the blk-mq hardware queue index selects a `qla_qpair` and delegates to `qla2xxx_mqueuecommand()`. Otherwise it initializes an SRB on the base qpair, sets SCSI command type and completion/free callbacks, and calls the selected chip family's `start_scsi()` operation. MQ submission is analogous but requires an online qpair and uses `start_scsi_mq()`.

SCSI error handling follows the FC transport contract. Abort uses `fc_block_scsi_eh()`, links a stack completion into the SRB, issues `abort_command()`, then waits up to `4 * R_A_TOV` for the original completion. Device and target reset wait for rport readiness, issue `lun_reset()` or `target_reset()`, and poll outstanding command slots by host/target/LUN with `qla2x00_eh_wait_for_pending_commands()`. Bus reset issues loop reset and waits for all pending commands. Host reset either aborts a virtual port ISP, handles special 82xx FCoE context reset, or calls `abort_isp()` on the base adapter, then drains outstanding commands.

The DPC thread is the adapter background state machine. `qla2x00_timer()`, interrupt paths, and work helpers set bits in `vha->dpc_flags`; `qla2xxx_wake_dpc()` wakes `qla2x00_do_dpc()`. The DPC loop handles EEH scheduling, ISP unrecoverable states, FCoE context reset, FX00 recovery, SFP-change events, ISP aborts, PUREX IOCBs, quiesce requests, reset markers, relogin scheduling, loop resync, NPIV flash configuration, interrupt re-enable, beacon blinking, qpair online changes, ZIO threshold changes, vport DPC work, and N2N link reset. It intentionally skips work during unload, mailbox busy periods, and EEH-busy windows.

The one-second timer is the periodic coordinator. It detects EEH disconnects, runs P3P/FX00 watchdogs, increments link-down counters, decrements loop-down timers, schedules early queue aborts for FCP2 devices, schedules ISP aborts when loop-down expires, queues beacon blinking, invokes EDIF timers, kicks deferred IOCB work, adjusts NVMe/ZIO thresholds, adjusts buffer pools, wakes DPC when any relevant flag is set, schedules heartbeat work for stalled outstanding IO, and rearms itself.

Workqueue control flows use `qla2x00_alloc_work()` and `qla2x00_post_work()` to append `qla_work_evt` nodes to a per-vha list and schedule `qla2x00_iocb_work_fn()`. `qla2x00_do_work()` handles FC host events, IDC ACKs, async login/logout/ADISC/PRLO, uevents, FX AENs, SRB unmap, relogin, new session creation, GPDB/PRLI/GPSC/GNL/GFPNID, NACK, fabric scan, SP retry, IIDMA, ELS PLOGI, and EDIF security association replacement.

## State and Persistence Behavior
Driver configuration persists primarily in module parameters. These parameters affect security enablement, Class 2 support, login timeout/retries, PLOGI behavior for absent devices, firmware dump allocation, debug logging masks, FDMI/SmartSAN/RDP registration, queue depth, DIF/DIX policy, NVMe enablement and queue count, HBA error isolation, multi-queue enablement, firmware-load source, doorbell mode, GFF_ID usage, async TMF mode, reset behavior, max LUN, minidump mask and enablement, extended login/exchange counts, SFP autodetect, MSI/MSI-X mode, DIX protection mask/guard, DIF bundling, ABTS behavior, PCI error handling delay, and FC2 target enablement.

Adapter runtime state is long-lived in `struct qla_hw_data`: PCI device, BAR mappings, chip type and capability flags, firmware attributes, locks, request/response/qpair maps, DMA pools, firmware dump buffers, NVRAM/NPIV/cache buffers, target-mode state, EDIF SADB state, vport list, heartbeat and DPC workqueues, mailbox completions, MQ topology, EEH state, and firmware blob references. Per-host state persists in `scsi_qla_host_t`: SCSI host pointer, host/vport identity, FC port list, discovery scan data, work lists, timers, DPC flags, loop state, online/init flags, port names, counters, and per-vport queues.

DMA and firmware-facing memory allocation is centralized in `qla2x00_mem_alloc()`: init control blocks, host map, target memory, GID list, SRB mempool, optional CT6 mempool, cached NVRAM, common DMA pool, DSD/FCP command/DIF bundling pools, SNS/MS IOCB/CT SNS buffers, request and response rings, NPIV info, extended init and special-feature control blocks, async port database, loop-id bitmap, SFP and FLT buffers, PUREX DMA pool, and ELS/NVMe reject payload buffers. `qla2x00_mem_free()` and `qla2x00_free_device()` reverse those allocations, abort outstanding commands, stop timers, delete queues, disable interrupts, free FC ports/IRQs, destroy workqueues, release target and EDIF state, and free queue maps.

Firmware images are cached globally in `qla_fw_blobs` under `qla_fw_lock`. `qla2x00_request_firmware()` selects a blob by adapter family, calls `request_firmware()` once per blob, and returns the cached pointer. `qla2x00_release_firmware()` releases all cached firmware at module exit.

## Dependencies and Integration Points
This file depends heavily on Linux PCI, DMA, SCSI, blk-mq, FC transport, firmware loader, workqueue, kthread, timer, trace, irq, module parameter, kobject uevent, slab/mempool, btree, and vmalloc APIs. It integrates with the rest of the qla2xxx driver through `qla_def.h`, `qla_target.h`, firmware mailbox/IOCB helpers, interrupt handlers, hardware family helpers (`qla82xx`, `qla83xx`, `qla27xx`, `qlafx00`), discovery/fabric routines, EDIF security, NVMe-FC, target-mode `qlt_*`, sysfs/debugfs helpers, and FC transport templates.

Externally visible integration points are the PCI ID table, the SCSI host template, the FC transport templates, SCSI EH callbacks, blk-mq queue mapping, module firmware declarations, module parameters, the character device registration for `QLA2XXX_APIDEV`, kobject uevents for firmware dumps, and kernel trace instance `qla2xxx`.

## Risks
The main risk is lifecycle ordering. Probe and remove touch PCI resources, MMIO mappings, DMA pools, IRQs, DPC threads, workqueues, timers, target mode, FC transport, SCSI host registration, and firmware state. A missing unwind step or reordered cleanup can leave DMA active after unmap, free memory while interrupts still complete commands, or race vport/session deletion.

Concurrency is also high risk. IO submission, completions, SCSI EH, timer, DPC thread, workqueues, PCI AER callbacks, target-mode callbacks, and vport deletion share `dpc_flags`, qpair state, outstanding command arrays, FC port lists, and adapter flags. Correct lock ownership around `hardware_lock`, `qp_lock_ptr`, `work_lock`, `vport_slock`, `mq_lock`, and `tgt.sess_lock` is critical.

Hardware ABI and chip-family dispatch are fragile. The `BUILD_BUG_ON()` block documents the fixed layout expectations for IOCBs, registers, NVRAM, dump structures, and FC payloads. The `isp_operations` tables must match each hardware generation; a wrong function pointer can break reset, interrupt, firmware, NVRAM, or SCSI start behavior.

Error recovery is delicate. EEH/AER paths mark qpairs offline, clear async states, mark devices lost, abort commands, perform reset and firmware restart, and then restore qpair online state. Returning the wrong `pci_ers_result_t`, missing `eeh_busy`, or allowing normal IO while PCI is frozen can cause command hangs or MMIO faults.

DIF/DIX, EDIF, FC-NVMe, target mode, NPIV, FX00, P3P/82xx/83xx, and RDP/PUREX features all add conditional allocations and alternate control paths. Changes must test both enabled and disabled configurations, including kdump mode where MQ and firmware dumps are deliberately disabled.

## Test Signals
Strong test signals include successful module load/unload; probe/remove on each supported PCI ID family; firmware loading from request_firmware and flash/default modes; SCSI host registration and scan; basic FCP read/write IO; blk-mq queue mapping and per-qpair submission; FC-NVMe enablement; target mode initialization/removal; NPIV vport create/delete; sysfs/debugfs creation/removal; timer and DPC wake behavior; FC port login, loss, relogin, and rport deletion; SCSI EH abort/device reset/target reset/bus reset/host reset; loop-down timeout recovery; ISP abort recovery; PCI AER frozen/permanent failure/slot reset/resume; FLR reset_prepare/reset_done; DIF/DIX IO with protection enabled and disabled; EDIF enabled boot; PUREX/RDP response generation; firmware dump/minidump paths; and clean removal with outstanding IO and sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_os.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_settings.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_settings.h

## Purpose
`qla_settings.h` is a small settings/version header for the qla2xxx driver. It provides driver-wide timeout/retry constants used by OS integration and includes `qla_version.h` so version definitions are available to code that consumes this settings layer.

## Important APIs, Types, and Functions
The file defines `MAX_RETRIES_OF_ISP_ABORT` as `5`, which bounds adapter online/reset retry logic, and `MAX_LOOP_TIMEOUT` as `60 * 5`, a five-minute loop-ready timeout. It has no functions or types. Its only include is `qla_version.h`.

## Control Flow
The header has no runtime control flow. It participates through preprocessing: constants are compiled into code such as `qla2x00_wait_for_hba_online()` and `qla2x00_wait_for_chip_reset()` in `qla_os.c`, where the timeout value limits waits for DPC/reset activity to settle and for the adapter to become online or chip reset to complete.

## State and Persistence Behavior
There is no mutable state. The constants are compile-time policy, so changing them changes driver behavior for every build that includes this header. The `qla_version.h` include propagates version metadata into the driver build.

## Dependencies and Integration Points
The direct dependency is `qla_version.h`. The important integration point is with qla2xxx initialization, reset, and loop-recovery code that uses the retry and timeout constants to decide when an adapter is considered failed or still recoverable.

## Risks
Increasing the timeout can make unload, error handling, or reset recovery wait much longer in fault scenarios. Decreasing it can produce false failures during slow fabric recovery, firmware reset, or PCI recovery. Because the constants are not runtime-tunable here, any change requires a rebuild and affects all supported qla2xxx hardware families.

## Test Signals
Relevant signals are adapter probe and link-up timing, ISP abort retry behavior, SCSI EH reset latency, loop-down/loop-ready recovery, module unload during recovery, and failure logs from `qla2x00_wait_for_hba_online()` or `qla2x00_wait_for_chip_reset()` when the timeout boundary is reached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_settings.h -->
