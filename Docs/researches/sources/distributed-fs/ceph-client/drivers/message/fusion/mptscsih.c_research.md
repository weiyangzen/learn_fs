# sources/distributed-fs/ceph-client/drivers/message/fusion/mptscsih.c

## Purpose
`mptscsih.c` is the generic SCSI host service layer for Fusion MPT protocol drivers. It builds MPT SCSI I/O request frames from Linux `scsi_cmnd` objects, maps scatter-gather DMA including MPT chain buffers, completes SCSI commands from firmware replies, issues task-management requests, flushes commands across resets/removal, provides internal scan/domain-validation commands, adjusts queue depth, exposes host sysfs attributes, and exports these services for SAS/SPI/FC-specific drivers.

In this source set, `mptsas.c` consumes this file heavily: SAS queuecommand delegates to `mptscsih_qcmd()`, completion contexts use `mptscsih_io_done()`, reset handlers use `mptscsih_*reset()`, and SAS host attributes/lifecycle callbacks reuse this implementation.

## Important APIs, types, and functions
- I/O construction and completion: `mptscsih_qcmd()`, `mptscsih_AddSGE()`, `mptscsih_getFreeChainBuffer()`, `mptscsih_freeChainBuffers()`, and `mptscsih_io_done()`.
- Command lookup: `mptscsih_get_scsi_lookup()`, `mptscsih_getclear_scsi_lookup()`, `mptscsih_set_scsi_lookup()`, and `SCPNT_TO_LOOKUP_IDX()` manage the `ioc->ScsiLookup[]` table indexed by MPT request frame number.
- Reset/error handling: `mptscsih_IssueTaskMgmt()`, `mptscsih_abort()`, `mptscsih_dev_reset()`, `mptscsih_bus_reset()`, `mptscsih_host_reset()`, `mptscsih_taskmgmt_complete()`, `mptscsih_taskmgmt_reply()`, `mptscsih_taskmgmt_response_code()`, and `mptscsih_get_tm_timeout()`.
- Reset cleanup: `mptscsih_flush_running_cmds()`, `mptscsih_search_running_cmds()`, and `mptscsih_ioc_reset()`.
- Internal commands: `mptscsih_scandv_complete()`, `mptscsih_get_completion_code()`, `mptscsih_do_cmd()`, and `mptscsih_synchronize_cache()`.
- Device configuration: `mptscsih_sdev_configure()`, `mptscsih_sdev_destroy()`, `mptscsih_change_queue_depth()`, and `mptscsih_bios_param()`.
- RAID helpers: `mptscsih_is_phys_disk()` and `mptscsih_raid_id_to_num()` translate firmware RAID physical disk state, including SAS dual-path and inactive-list cases.
- Lifecycle and observability: `mptscsih_remove()`, `mptscsih_shutdown()`, optional `mptscsih_suspend()/resume()`, `mptscsih_info()`, `mptscsih_show_info()`, and sysfs host attributes for firmware, BIOS, MPI, product, NVDATA, board, delays, and debug level.

## Control flow
For normal I/O, the SCSI midlayer calls `mptscsih_qcmd()`. The function checks task-management quiesce state, obtains a message frame, chooses data direction and tag control, maps the Linux CDB and LUN into `SCSIIORequest_t`, selects normal SCSI I/O or RAID physical-disk passthrough, writes sense-buffer DMA address, builds either a null SGE or a full SGL with optional chain buffers, stores the command in `ScsiLookup[]`, records the frame in `host_scribble`, and posts the frame to firmware.

Firmware completion calls `mptscsih_io_done()`. The function validates request indices, retrieves and clears the lookup entry, rejects already-freed or mismatched frames, handles deleted SAS targets, translates IOC/SCSI status into Linux `sc->result`, copies sense data, logs selected errors, adjusts residual bytes, reports queue-full events, unmaps DMA, calls `scsi_done()`, and releases chain buffers.

Task management serializes on `ioc->taskmgmt_cmds.mutex` and the MPT task-management-in-progress flag. `mptscsih_IssueTaskMgmt()` checks IOC operational and doorbell state, allocates a task frame, fills target/bus/LUN/type/context fields, posts through high-priority queue or handshake path, waits for completion, parses the reply, and triggers a hard or soft-hard reset on timeout. Abort, LUN reset, bus reset, and host reset wrappers adapt this generic operation to the SCSI error-handler API.

Reset callbacks flush outstanding commands before or after IOC reset phases. Internal scan/domain-validation commands use a separate `internal_cmds` completion object and callback so they can issue INQUIRY, TUR, REQUEST SENSE, READ/WRITE BUFFER, reserve/release, and SYNCHRONIZE CACHE without going through a normal `scsi_cmnd`.

## State and persistence behavior
The key runtime state is `ioc->ScsiLookup[]`, `scsi_cmnd::host_scribble`, `ioc->ReqToChain[]`, `ioc->ChainToChain[]`, `ioc->FreeChainQ`, sense buffer pool offsets, `ioc->taskmgmt_cmds`, `ioc->internal_cmds`, target/device hostdata, and adapter RAID data. Nothing is persisted to disk.

The lookup table and chain-buffer trackers form the ownership model for in-flight I/O. Successful or failed completion must clear the lookup entry, unmap DMA, return chain buffers, and complete the SCSI command exactly once. Internal and task-management commands use completion/status fields instead of `ScsiLookup[]`.

`mptscsih_sdev_destroy()` sends SYNCHRONIZE CACHE for configured disk LUNs during teardown, except hidden RAID components. SMART sense data can be copied into the adapter event log and may trigger SEP slot predicted-fault status for IBM vendor devices.

## Dependencies and integration points
The file depends on `mptbase.h` for adapter structs, request/reply frame layout, frame allocation/posting/freeing, SGE construction, reset helpers, RAID page helpers, debug macros, and MPT management status bits. It depends on Linux SCSI midlayer APIs for `scsi_cmnd`, DMA mapping, queue depth, command completion, device/target hostdata, error handlers, and sysfs host attributes.

It is intentionally exported with many `EXPORT_SYMBOL()` entries so protocol drivers can reuse one SCSI implementation while providing transport-specific probing and topology.

## Risks and edge cases
- The `ScsiLookup[]` and `host_scribble` checks are critical double-completion guards. Any mismatch can leak frames, lose completions, or complete stale commands.
- `mptscsih_AddSGE()` handles chained SGEs manually. Off-by-one errors in chain offsets, `RequestNB`, or zero-length SGE handling would corrupt firmware requests.
- Timeout handling in task management and internal commands may free message frames and reset the IOC while a late completion is possible.
- Result translation contains adapter- and bus-specific behavior, including SPI errata, FC retry semantics, SAS nexus loss, queue-full handling, and autosense precedence. Regression risk is high if simplifying status mapping.
- Several paths depend on `VirtDevice`/`VirtTarget` hostdata being valid. Device removal and SAS hotplug must coordinate with command search/flush logic.
- The RAID helpers assume cached IOC RAID pages are current enough for hidden physical disk detection; stale pages can misclassify devices.

## Test signals
- Compile tests should cover the exported symbols with all protocol drivers that include `mptscsih.h`.
- I/O tests should verify no-data, read, write, large SG lists requiring chain buffers, zero-length SG entries, and DMA unmap on all completion/error paths.
- Error injection should cover every major IOC status class, autosense valid/failed, queue-full, device-not-there, task terminated, data underrun/overrun, residual mismatch, SAS nexus loss, and FC/SPI-specific branches.
- Reset tests should cover abort, LUN reset, bus reset, host reset, IOC reset phases, internal command timeouts, and late completion behavior.
- Device teardown tests should cover in-flight command cleanup and SYNCHRONIZE CACHE behavior.
- Sysfs tests should read all host attributes and write valid/invalid debug levels.
