# sources/distributed-fs/ceph-client/drivers/scsi/ipr.h

## Purpose

`ipr.h` is the private protocol, hardware, and state-definition header for the IBM Power Linux RAID adapter SCSI driver. It defines the adapter command opcodes, IOASC status values, PCI/subsystem IDs, interrupt bits, reset and dump timing constants, packed firmware-facing request/response layouts, asynchronous notification buffers, resource tables, host response queues, and the per-adapter `struct ipr_ioa_cfg` state used by `ipr.c`.

The file is not a generic Ceph or distributed filesystem interface despite its repository path. It is Linux kernel SCSI/PCI driver infrastructure for IBM IPR storage controllers, with SIS32 and SIS64 adapter variants handled by parallel structure families and conditionals.

## Important APIs, Types, and Definitions

The protocol constants define adapter commands such as `IPR_QUERY_IOA_CONFIG`, `IPR_HOST_CONTROLLED_ASYNC`, `IPR_CANCEL_REQUEST`, `IPR_CANCEL_ALL_REQUESTS`, `IPR_RESET_DEVICE`, `IPR_IOA_SHUTDOWN`, `IPR_WR_BUF_DOWNLOAD_AND_SAVE`, and `IPR_IOA_SERVICE_ACTION`. IOASC constants such as `IPR_IOASC_NR_IOA_RESET_REQUIRED`, `IPR_IOASC_SYNC_REQUIRED`, `IPR_IOASC_BUS_WAS_RESET`, `IPR_IOASC_HW_CMD_FAILED`, `IPR_IOASC_ABORTED_CMD_TERM_BY_HOST`, and driver-private `IPR_IOASC_IOA_WAS_RESET` encode completion and recovery outcomes. Request classes are selected with `IPR_RQTYPE_SCSICDB`, `IPR_RQTYPE_IOACMD`, `IPR_RQTYPE_HCAM`, and `IPR_RQTYPE_PIPE`.

Firmware wire formats are represented by packed, endian-annotated structures. `struct ipr_ioarcb` is the adapter request control block and embeds `struct ipr_cmd_pkt`, IOASA DMA addresses, data transfer lengths, IOADL addresses, and SIS64-specific extended address data. `struct ipr_ioadl_desc` and `struct ipr_ioadl64_desc` are the 32-bit and 64-bit DMA scatter/gather descriptors. `struct ipr_ioasa`, `struct ipr_ioasa64`, and `struct ipr_ioasa_hdr` describe adapter status, residual length, autosense validity, failing device identifiers, and auto-sense buffers.

Configuration discovery is described by `struct ipr_config_table`, `struct ipr_config_table64`, `struct ipr_config_table_entry`, `struct ipr_config_table_entry64`, and `struct ipr_config_table_entry_wrapper`. These records carry resource handles, resource addresses or SIS64 resource paths, LUN identifiers, WWNs, queueing model bits, protocol IDs, and standard inquiry data. `struct ipr_resource_entry` is the driver's live representation of one adapter resource and caches bus/target/lun, virtual bus assignment, type, queueing model, resource handle, device ID, LUN WWN, SCSI LUN, resource path, `struct scsi_device *`, and add/delete/reset flags.

Asynchronous event handling is modeled by `struct ipr_hcam`, `struct ipr_hostrcb`, and many overlay-specific `ipr_hostrcb_*` structures. These define configuration-change notifications, error logs, cache/config/array/fabric/service-required overlays, and both classic resource-address and SIS64 resource-path variants. The overlay IDs and notification type constants decide how `ipr.c` interprets the union.

Runtime controller state is centralized in `struct ipr_ioa_cfg`. It owns adapter flags, generated SIS64 target bitmaps, trace buffer, DMA configuration table, resource lists, HCAM queues, host response queues, bus attributes, MMIO register mappings, reset state, wait queues, dump state, VPD command buffers, command DMA pool, command list, MSI-X vector metadata, and SCSI/PCI object pointers. `struct ipr_cmnd` is the per-command object containing the IOARCB, IOADL array, IOASA, list linkage, SCSI command pointer, completion/timer/work objects, callback function pointers, DMA addresses, sibling/error-handler state, HRRQ pointer, and parent `ipr_ioa_cfg`.

Small inline classifiers form the main header-level API: `ipr_is_ioa_resource()`, `ipr_is_af_dasd_device()`, `ipr_is_vset_device()`, `ipr_is_gscsi()`, `ipr_is_scsi_disk()`, `ipr_is_gata()`, `ipr_is_naca_model()`, `ipr_is_device()`, and `ipr_sdt_is_fmt2()`. Logging and tracing macros include `ipr_err`, `ipr_info`, `ipr_dbg`, resource-aware printk wrappers, `ipr_hcam_err`, and conditional sysfs creation wrappers for trace and dump binary files.

## Control Flow Supported by the Header

Normal SCSI I/O starts in `ipr_queuecommand()` in `ipr.c`: the SCSI mid-layer command is mapped to a `struct ipr_resource_entry`, a `struct ipr_cmnd` is taken from an HRRQ free queue, the CDB is copied into `ipr_ioarcb.cmd_pkt.cdb`, request type and flags are selected from resource type and command attributes, 32-bit or 64-bit IOADLs are built, the command is moved to an HRRQ pending queue, and the IOARCB DMA address is written to the adapter IOARRIN register. The layout and flag definitions for every one of those fields come from this header.

Completion flow is centered on `struct ipr_hrr_queue`. Each queue stores the coherent host response queue, DMA address, current/toggle pointers, free and pending command lists, lock, interrupt/command gating flags, command-ID range, and optional `irq_poll` object. ISR and polling code consume HRRQ entries using the response handle masks and toggle bits from the header, locate the `struct ipr_cmnd`, and dispatch its `fast_done`/`done` callbacks.

Configuration change flow uses HCAM buffers. `ipr_send_hcam()` sends an `IPR_HOST_CONTROLLED_ASYNC` command against `IPR_IOA_RES_HANDLE` with either config-change or log-data type, DMA-mapping the embedded `struct ipr_hcam` inside `struct ipr_hostrcb`. `ipr_process_ccn()` and `ipr_handle_config_change()` interpret `struct ipr_hostrcb_cfg_ch_not`, update or allocate `struct ipr_resource_entry` records, and schedule SCSI add/remove work. SIS64 config entries allocate synthetic targets from `target_ids`, `array_ids`, and `vset_ids`; SIS32 entries use physical bus/target/lun values directly.

Reset flow is a state machine using `struct ipr_cmnd` callback fields `job_step` and `job_step_failed`, shutdown types from `enum ipr_shutdown_type`, IOA flags in `struct ipr_ioa_cfg`, timeout constants, and adapter interrupt/register bit definitions. `_ipr_initiate_ioa_reset()` blocks requests, disables command submission on HRRQs, stores the reset command, and repeatedly advances through shutdown, HCAM cancellation, reset alert, BIST/PCI reset, config-space restore, dump collection, and IOA enable stages until a step returns `IPR_RC_JOB_RETURN`.

Dump and diagnostics flow uses `struct ipr_sdt`, `struct ipr_dump`, `struct ipr_driver_dump`, `struct ipr_ioa_dump`, and associated eye-catcher/status constants. The driver can expose trace and dump binary sysfs files when `CONFIG_SCSI_IPR_TRACE` or `CONFIG_SCSI_IPR_DUMP` is enabled, and records command lifecycle entries in the circular trace buffer defined by `IPR_NUM_TRACE_ENTRIES`.

## State and Persistence Behavior

All state in this header is runtime driver state. Command blocks, IOASAs, IOADLs, HRRQs, config tables, hostrcbs, VPD buffers, and dumps are allocated in kernel memory or coherent DMA memory during probe and freed on remove/error cleanup. `struct ipr_ioa_cfg` persists only for the lifetime of one probed PCI adapter and is attached to both `Scsi_Host.hostdata` and `pci_set_drvdata()`.

The adapter firmware and hardware maintain persistent facts such as resource handles, VPD, microcode level, array membership, and error logs; this header defines the transport structures used to fetch or update those facts. The driver caches some values, including bus attributes, generated SIS64 target IDs, firmware capability pages, resource tables, and trace/error counters, but those caches are rebuilt on probe, reset reload, and configuration-change handling.

Queue and reset flags are concurrency-sensitive. `allow_cmds`, `allow_interrupts`, `ioa_is_dead`, `removing_ioa`, `in_reset_reload`, `scsi_blocked`, and `scsi_unblock` coordinate SCSI mid-layer submission, ISR completion, polling, PCI error recovery, and teardown. Resource flags such as `add_to_ml`, `del_from_ml`, `needs_sync_complete`, `in_erp`, `resetting_device`, and `reset_occurred` persist across short control-flow windows and drive later workqueue or command flag behavior.

## Dependencies and Integration Points

The header depends on Linux kernel list, completion, kref, irq_poll, endian, unaligned-access, SCSI, PCI, DMA, MMIO, workqueue, timer, waitqueue, and sysfs concepts. It includes `linux/unaligned.h`, `linux/types.h`, `linux/completion.h`, `linux/list.h`, `linux/kref.h`, `linux/irq_poll.h`, `scsi/scsi.h`, and `scsi/scsi_cmnd.h`, while relying on additional types supplied by the including C file and kernel headers such as `struct pci_dev`, `struct Scsi_Host`, `struct scsi_device`, `struct scatterlist`, `dma_addr_t`, `spinlock_t`, and `void __iomem`.

Its primary implementation partner is `drivers/scsi/ipr.c`, which includes this file directly and uses the definitions for module parameters, PCI probe/remove, interrupt handlers, SCSI host template callbacks, sysfs attributes, microcode download, error logging, reset/error recovery, and dump collection. The SCSI mid-layer integration uses `ipr_queuecommand`, error-handler callbacks, `sdev` setup/destroy callbacks, queue-depth changes, scan completion, and host blocking/unblocking. PCI integration uses adapter PCI IDs, MSI/MSI-X vector metadata, register offset tables, EEH/error recovery waits, and warm/fundamental reset paths.

The hardware-facing integration is highly ABI-sensitive. Packed structure layouts, alignment attributes, big-endian fields, response handle bit layout, mailbox/register offsets, and IOADL formats must match adapter firmware exactly. SIS32 and SIS64 variants share high-level flow but use different config entries, resource identity, IOARCB address fields, IOADL descriptors, dump sizes, and response queue setup.

## Risks and Edge Cases

Most structures are packed firmware contracts. Reordering fields, changing alignment, replacing big-endian types, or altering flexible-array placement can break DMA commands, config parsing, dump retrieval, or error-log decoding without producing obvious compile errors. The fallback `writeq()` writes high 32 bits before low 32 bits, which is intentional for this adapter path but is not a generic substitute for all devices.

SIS32 and SIS64 divergence is a recurring risk. Code must choose the matching config table entry, resource identity, IOADL descriptor, IOASA variant, response queue behavior, dump size, and path formatting. Accidentally using resource-address logic for SIS64, or resource-path logic for SIS32, can misidentify devices or log misleading locations.

Queue ownership is fragile because command blocks move between free, pending, done, reset, and workqueue contexts under different locks. HRRQ 0 is also reserved for internal commands when multiple response queues are enabled, while other HRRQs handle normal SCSI I/O. Bugs in `min_cmd_id`/`max_cmd_id`, response handle masking, toggle-bit handling, or `allow_cmds` transitions can leak commands, double-complete requests, or leave the SCSI mid-layer permanently busy.

Asynchronous notification buffers are finite (`IPR_MAX_HCAMS`). The implementation can reclaim reported buffers when free buffers run out, so slow userspace/report processing or repeated firmware notifications can lose detail. The header includes explicit notification-lost and overlay-default paths; test and logging code should not assume every error arrives with a fully decoded overlay.

Reset and dump timing constants span short polling delays through multi-minute shutdown and microcode-download waits. `ipr_fastfail` changes several timeout macros, so recovery behavior differs between normal and fast-fail configurations. The reset state machine also nests and aborts stale reset commands, which makes callback state correctness critical.

## Test Signals

Build coverage should include configurations with and without `CONFIG_SCSI_IPR_TRACE` and `CONFIG_SCSI_IPR_DUMP`, plus sparse/endian checks for `__be16`, `__be32`, `__be64`, `dma_addr_t`, and MMIO access. Structure-size and alignment regressions are especially important for `struct ipr_cmnd`, `struct ipr_ioarcb`, IOADL descriptors, IOASA variants, config table entries, HCAM overlays, and dump records.

Runtime signals include successful PCI probe, correct SCSI host limits for SIS32 versus SIS64, allocation and cleanup of command blocks/HRRQs/hostrcbs/config tables, successful config-table query and resource discovery, SCSI command submission/completion under load, correct scatter/gather DMA for 32-bit and 64-bit descriptors, and stable behavior with multiple MSI-X HRRQs and optional `irq_poll`.

Recovery tests should exercise adapter reset, device reset, abort/cancel paths, bus reset notification, IOA unit check handling, microcode download, shutdown variants, PCI error recovery, and IOA dump collection. Hotplug and config-change tests should verify resources move between free/used lists, SCSI devices are added or removed once, resource handles are invalidated on removal, SIS64 synthetic target IDs are released, and HCAMs are reissued after processing.

Logging tests should inject or simulate representative IOASC and HCAM overlay IDs, including generic/default overlays, SIS64 fabric/device/array overlays, notification-loss cases, and reset-required error logs. User-visible sysfs and module-parameter signals include `fastfail`, `debug`, `fast_reboot`, trace/dump files when configured, and `iopoll_weight` behavior on SIS64 adapters with multiple vectors.
