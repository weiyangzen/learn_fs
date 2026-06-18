# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_init.c (lines 1-9280)

## Scope

This chunk covers the main initialization, discovery, queueing, interrupt, SCSI mid-layer, sysfs/ioctl, firmware-feature, reset/OFA, PCI resource, and controller-offline logic for the Microchip SmartPQI Linux SCSI driver through line 9280. The requested range stops inside `pqi_take_ctrl_devices_offline()`, so later probe/remove/module boilerplate and structure checks are out of scope except where referenced by declarations or callbacks in this range.

## Purpose

`smartpqi_init.c` is the core SmartPQI controller driver implementation. It transitions a supported PCI storage controller from SIS mode into PQI mode, allocates DMA-backed admin/operational queues, registers with the SCSI and SAS transport layers, discovers logical and physical devices, submits RAID-path and AIO-path I/O, handles completions/events, exposes management knobs via sysfs and CCISS-compatible ioctls, and tears the controller down or takes it offline on firmware/queue/heartbeat faults.

The driver uses PQI as the high-performance command transport while still relying on SIS helper operations for bootstrapping, resets, and legacy mode transitions. It tracks logical volumes, physical devices, RAID maps, queue groups, request slots, controller health, OFA state, heartbeat state, and host memory buffers in `struct pqi_ctrl_info` and per-device `struct pqi_scsi_dev` objects.

## Important APIs, Types, and Entry Points

- Module identity and tunables: `DRIVER_VERSION`, `DRIVER_NAME_SHORT`, module params `disable_device_id_wildcards`, `disable_heartbeat`, `disable_ctrl_shutdown`, `lockup_action`, `expose_ld_first`, `hide_vsep`, `disable_managed_interrupts`, and `ctrl_ready_timeout`.
- Request/private state: `struct pqi_cmd_priv` stores per-SCSI-command residual retry state; `pqi_cmd_priv()` returns `scsi_cmd_priv(cmd)`.
- Controller health and blocking helpers: `pqi_ctrl_offline()`, `pqi_check_ctrl_health()`, `pqi_ctrl_block_requests()`, `pqi_wait_if_ctrl_blocked()`, `pqi_ctrl_wait_until_quiesced()`, scan/reset/OFA locking helpers, and `pqi_take_ctrl_offline()`.
- Synchronous RAID/admin path: `pqi_build_raid_path_request()`, `pqi_send_scsi_raid_request()`, `pqi_submit_raid_request_synchronous()`, `pqi_submit_admin_request_synchronous()`.
- Discovery path: `pqi_report_phys_luns()`, `pqi_report_logical_luns()`, `pqi_get_device_lists()`, `pqi_get_device_info()`, `pqi_update_scsi_devices()`, `pqi_update_device_list()`, and `pqi_scan_scsi_devices()`.
- RAID bypass/AIO mapping: `pqi_get_raid_map()`, `pqi_validate_raid_map()`, `pqi_raid_bypass_submit_scsi_cmd()`, `pqi_calc_aio_r5_or_r6()`, `pqi_aio_submit_io()`, `pqi_aio_submit_r1_write_io()`, and `pqi_aio_submit_r56_write_io()`.
- SCSI host hooks: `pqi_driver_template` wires `queuecommand`, `scan_start`, `scan_finished`, `eh_device_reset_handler`, `eh_abort_handler`, `ioctl`, `sdev_init`, `sdev_configure`, `sdev_destroy`, and `map_queues`.
- Interrupts/events: `pqi_irq_handler()`, `pqi_process_io_intr()`, `pqi_process_event_intr()`, `pqi_event_worker()`, `pqi_acknowledge_event()`.
- Initialization/resume/removal: `pqi_pci_init()`, `pqi_ctrl_init()`, `pqi_ctrl_init_resume()`, `pqi_register_scsi()`, `pqi_remove_ctrl()`, `pqi_free_ctrl_resources()`.
- Firmware/config feature handling: `pqi_process_config_table()`, `pqi_process_firmware_features_section()`, `pqi_enable_firmware_features()`, `pqi_ctrl_update_feature_flags()`.
- OFA and host buffers: `pqi_ofa_ctrl_quiesce()`, `pqi_ofa_ctrl_unquiesce()`, `pqi_process_soft_reset()`, `pqi_host_setup_buffer()`, `pqi_host_free_buffer()`, `pqi_host_memory_update()`.

## Control Flow

Initialization starts in the PCI/probe lane outside this chunk, but this range contains the important setup pipeline. `pqi_pci_init()` enables the PCI function, sets a 64-bit or 32-bit coherent DMA mask, requests BAR regions, maps controller registers, lengthens the PCIe completion timeout, enables bus mastering, stores register pointers, and attaches `ctrl_info` to the PCI device.

`pqi_ctrl_init()` then handles kdump/reset-specific preparation, forces SIS mode if needed, waits for controller readiness, reads controller properties/capabilities, clamps outstanding request limits, sizes I/O resources, allocates the error buffer, asks SIS to enter PQI mode, waits for PQI signature/idle/all-registers-ready, creates admin queues, reports and validates PQI capabilities, sizes queue groups, enables MSI-X, allocates request/queue memory, creates event/operational queues, requests IRQs, enables MSIX in hardware, marks the controller online, processes the PQI config table, starts heartbeat monitoring, enables advanced RAID bypass config if write bypass features are available, enables events, registers SCSI/SAS hosts, registers optional controller-log memory, reads product/serial metadata, enables diagnostic rescan, writes host wellness metadata, schedules time updates, and performs the first SCSI device scan.

The resume/OFA restart path in `pqi_ctrl_init_resume()` is a reduced reinitialization. It forces SIS mode, waits for resume readiness, reenters PQI mode, reinitializes queue indices, recreates queues, reenables interrupts, unblocks requests, resets config-derived flags, reprocesses config, restarts heartbeat/events, restores OFA/controller-log memory handling, and rescans devices.

Normal SCSI I/O enters through `pqi_scsi_queue_command()`. The driver increments per-device outstanding command counters, rejects commands for offline/removing/resetting/blocked devices, maps blk-mq hardware queue to a `pqi_queue_group`, then chooses a path:

- Logical devices may use RAID bypass if enabled, request type is eligible, and stream-detection does not force parity writes down the controller path.
- Non-bypassed logical commands use the RAID path.
- Physical devices use AIO if `aio_enabled`, otherwise RAID path.

Submission allocates a `pqi_io_request` from a blk-mq tag-backed slot for SCSI requests, builds an IU in the per-request buffer, DMA maps the SCSI SG list, queues the request to the selected inbound queue list, and rings the producer index in `pqi_start_io()` when space is available.

Completions arrive in `pqi_irq_handler()`. `pqi_process_io_intr()` drains outbound responses, validates producer indices and request IDs, decodes success/error/vendor/TMF/AIO-disabled response IUs, fills `io_request->status` or SCSI result/sense data, and invokes the request completion callback. The callback releases DMA mappings, decrements request references, and calls `pqi_scsi_done()`, which funnels through `pqi_prep_for_scsi_done()` to decrement outstanding counters and complete any error-handler waiters.

Event interrupts are drained by `pqi_process_event_intr()`, which records pending supported events and schedules `pqi_event_worker()`. The worker acknowledges non-OFA events, marks rescans for hotplug/logical/AIO changes, disables RAID bypass on AIO state changes, and schedules a delayed rescan. OFA events may allocate firmware-usable host memory, quiesce the controller, acknowledge quiesce only after blocking I/O/reset/scan activity, and then process soft reset/restart or abort handling.

## Device Discovery and Reconciliation

Discovery uses CISS/BMIC RAID path commands. `pqi_report_phys_logical_luns()` first fetches a header-sized report, reallocates to the returned list length, retries if the device list grows, and returns physical or logical LUN data. `pqi_report_phys_luns()` normalizes older 8-byte WWID physical report formats into the 16-byte WWID format expected by the rest of the driver.

`pqi_get_device_lists()` appends the controller itself as an all-zero logical LUN entry. `pqi_update_scsi_devices()` allocates candidate `pqi_scsi_dev` objects, optionally hides the virtual SEP, honors the `expose_ld_first` ordering policy, skips masked devices, classifies physical/logical/external RAID/SMP devices, gathers BMIC physical info or INQUIRY/VPD logical info, suppresses drives undergoing erase, assigns bus/target/lun for controller/logical devices, captures WWIDs/volume IDs/AIO handles, and passes valid candidates to `pqi_update_device_list()`.

`pqi_update_device_list()` performs a lock-minimized reconciliation between existing and newly discovered devices. It marks existing devices gone, matches by SCSI-3 address and stable identity (`wwid` for physical, `volume_id` for logical), updates same devices in place, builds separate add/delete lists, removes disappeared/offline devices outside the spinlock, updates queue depths and rescans changed volumes, and exposes new devices through `scsi_add_device()` or SAS transport helpers. Device structures own `raid_map`, optional per-CPU `raid_io_stats`, SAS/SCSI attachment pointers, reset work items, and flags such as `device_gone`, `new_device`, `keep_device`, `device_offline`, `in_remove`, and per-LUN reset state.

Logical disk metadata includes RAID level, RAID bypass status/map, volume status, encryption transfer limits, and vendor/model strings. Physical metadata includes queue depth, path/bay/box/connector fields, active path, NCQ priority support, erase state, and AIO capability.

## RAID Bypass and I/O Mapping

RAID bypass uses controller-provided RAID maps to submit certain logical volume I/O directly to physical disk AIO handles. `pqi_get_aio_lba_and_block_count()` accepts READ/WRITE 6/10/12/16 only and extracts LBA/count/data length. `pci_get_aio_common_raid_map_values()` validates volume bounds, computes row/column/strip positions, and only permits requests confined to one row and column. `pqi_aio_raid_level_supported()` gates read/write bypass by RAID level and firmware-advertised write-bypass limits.

For RAID 1/triple, reads are balanced via `device->next_bypass_group[]`; writes build multi-nexus RAID1 IUs. For RAID 5/6 and 50/60, `pqi_calc_aio_r5_or_r6()` ensures the request is in one group/row/column and computes data/parity nexus handles and row/xor information for write bypass. Encryption-enabled maps populate tweak/key fields through `pqi_set_encryption_info()` and enforce per-drive-type transfer caps.

If bypass submission fails with `PQI_RAID_BYPASS_INELIGIBLE`, the normal RAID path is used. If an AIO/raid-bypass completion indicates a retryable path problem, `pqi_aio_io_complete()` sets `DID_IMM_RETRY` and increments `this_residual`; `pqi_is_bypass_eligible_request()` blocks repeated bypass attempts for that command.

## State and Persistence Behavior

Persistent controller mode and firmware-triage support are stored in the SIS driver scratch register via `pqi_save_ctrl_mode()` and `pqi_save_fw_triage_setting()`. This survives across mode transitions enough for reset/kdump logic to infer the prior state. Most other state is runtime-only in `pqi_ctrl_info`, queue memory, request pools, `pqi_scsi_dev` entries, timers, work items, and sysfs-visible flags.

Concurrency state is controlled by:

- `scan_mutex` and `scan_blocked` for discovery serialization and OFA scan exclusion.
- `lun_reset_mutex` plus per-device `in_reset[lun]` for reset exclusion.
- `ofa_mutex` to serialize Online Firmware Activation.
- `block_requests`, `block_requests_wait`, `num_busy_threads`, and `num_blocked_threads` to quiesce driver activity.
- Queue-group `submit_lock[path]` protecting pending IU lists and producer index copies.
- `scsi_device_list_lock` protecting device-list membership and hostdata lookups.
- `sync_request_sem` limiting reserved synchronous/internal request slots.
- Atomic outstanding counters per LUN and request-slot reference counts.

Host wellness state is written to firmware using BMIC `WRITE_HOST_WELLNESS`: driver version once during init/resume and current time immediately plus every 24 hours. Optional controller logging and OFA memory buffers are DMA-coherent scatter/gather host-memory descriptors registered with firmware via vendor general requests.

## Dependencies and Integration Points

This code depends heavily on Linux kernel PCI, DMA, SCSI, blk-mq, SAS transport, workqueue, timer, atomic, mutex/spinlock, completion, sysfs, capability, and user-copy APIs. It includes `smartpqi.h` and `smartpqi_sis.h`; many structures and constants, plus helpers like `sis_wait_for_ctrl_ready()`, `sis_get_pqi_capabilities()`, `sis_init_base_struct_addr()`, `sis_soft_reset()`, `sis_shutdown_ctrl()`, `pqi_add_sas_device()`, and `pqi_remove_sas_device()`, are external to this chunk.

SCSI mid-layer integration is through `scsi_host_template`, `scsi_host_alloc()`, `scsi_add_host()`, `scsi_add_device()`, `scsi_remove_device()`, `scsi_change_queue_depth()`, `scsi_rescan_device()`, `scsi_block_requests()`, and error-handler callbacks. Block layer integration uses blk-mq tags as request-slot indices and maps hardware queues to MSI-X queue groups.

Management integration includes CCISS-compatible ioctls (`GETPCIINFO`, `GETDRIVVER`, `PASSTHRU`, disk register/rescan commands), shost sysfs attributes for controller metadata and feature toggles, and sdev sysfs attributes for LUN IDs, unique IDs, path info, SAS address, RAID bypass status/counters, NCQ priority control, NUMA node, and write stream counts.

Firmware integration uses PQI admin functions for capability and queue creation, PQI operational queues for SCSI/TMF/vendor/event traffic, BMIC/CISS commands for discovery and metadata, config-table feature negotiation, heartbeat and soft-reset config sections, and vendor general host-memory/config-table update functions.

## Risks and Edge Cases

- Queue corruption detection is strict. Out-of-range producer indices, invalid request IDs, unmatched request IDs, or unexpected IU types call `pqi_take_ctrl_offline()`, disable the PCI device, optionally shut down the controller, and complete outstanding I/O with errors.
- The requested line range ends before `pqi_take_ctrl_devices_offline()` finishes. Within the included portion, it iterates devices under `scsi_device_list_lock` and sets attached SCSI devices offline, but subsequent unlock/loop details are outside scope.
- Synchronous RAID requests rely on reserved slots and a semaphore. A controller going offline while waiting converts completion waits to `-ENXIO`; callers must handle partially filled error buffers.
- RAID bypass correctness depends on controller RAID maps, endian-safe field extraction, row/column arithmetic, and bounds checks. Mistakes can redirect logical I/O to the wrong physical LBA, especially for RAID 50/60, encrypted volumes, or differing logical/physical block sizes.
- `pqi_aio_submit_io()` sets SOP direction flags in an inverted-looking way for DMA directions (`DMA_TO_DEVICE` maps to `SOP_READ_FLAG`, `DMA_FROM_DEVICE` to `SOP_WRITE_FLAG`), likely matching controller terminology but worth preserving carefully.
- Device reconciliation intentionally defers SCSI/SAS add/remove outside the list spinlock. Bugs in `keep_device`, `device_gone`, or botched-add handling can leak devices, double free RAID maps/stats, or desynchronize the SCSI mid-layer view.
- OFA quiesce blocks scans, SCSI requests, resets, and driver activity before soft reset. Missing an unblock path on abort/failure would deadlock I/O; the code has explicit unquiesce paths for abort/noreponse and resume unblocks.
- Heartbeat monitoring treats no interrupts plus unchanged heartbeat counter as controller lockup. `disable_heartbeat` suppresses this by not wiring `heartbeat_counter`.
- Error handling maps controller sense/data-out results to SCSI host bytes. Some AIO path failures offline devices and schedule rescans; retry behavior is sensitive to `raid_bypass`, `this_residual`, and `DID_NO_CONNECT`.
- User passthrough ioctl requires `CAP_SYS_RAWIO` and validates CDB length/type/direction, but it still exposes firmware command execution and DMA-backed user buffers, so copy/mapping/unmap paths are security-critical.
- Removal/surprise-removal paths must not wait forever for hardware. `pqi_remove_ctrl()` fails outstanding requests immediately for surprise removal and marks `pqi_mode_enabled = false`.

## Test Signals

Useful validation signals for this chunk include:

- Probe/init logs showing SIS ready, PQI mode transition, admin/operational queue creation, MSI-X allocation, firmware feature enablement, event enablement, SCSI host registration, firmware/product/serial metadata, host wellness update, and first device scan.
- Device discovery with physical/logical LUN changes: hotplug events should produce event ACKs, delayed rescans, correct add/remove/offline logs, stable unique IDs, queue-depth changes, and volume rescans.
- RAID bypass coverage: sysfs `ssd_smart_path_enabled`, `raid_bypass_cnt`, and `write_stream_cnt` should change under eligible logical disk I/O; ineligible, parity-stream, too-large encrypted, multi-row/column, and retry cases should fall back to RAID path without data errors.
- Error recovery: injected LUN reset, task abort, AIO path disabled, invalid/no-path device, and controller offline events should produce expected SCSI host bytes, completions, outstanding counter decrements, and no stuck `host_scribble` waiters.
- Interrupt/queue robustness: invalid producer index/request ID/IU type tests should take the controller offline and complete outstanding requests.
- OFA path: memory allocation events should register OFA memory; quiesce should block I/O and scans; soft-reset initiate/abort/timeout/noreponse should restart, unquiesce, or offline the controller as appropriate.
- Sysfs/ioctl behavior: controller metadata attributes must match firmware, toggles should parse and clamp to 0/1, NCQ priority writes should fail when unsupported, and CCISS passthrough should require `CAP_SYS_RAWIO` and return CISS-style error info.
- Cleanup/removal: graceful and surprise removal should stop heartbeat/update/rescan work, unregister SCSI/SAS hosts, free DMA resources, and avoid new I/O submission.
