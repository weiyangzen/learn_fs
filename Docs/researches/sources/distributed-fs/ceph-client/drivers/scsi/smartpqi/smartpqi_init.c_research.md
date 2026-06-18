# Research: sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_init.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005356`: lines 1-9280, `Docs/researches/chunks/subset-b-005356_research.md`
- `subset-b-005357`: lines 9281-11224, `Docs/researches/chunks/subset-b-005357_research.md`

## Chunk Research

### subset-b-005356: lines 1-9280

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

### subset-b-005357: lines 9281-11224

# sources/distributed-fs/ceph-client/drivers/scsi/smartpqi/smartpqi_init.c lines 9281-11224

Chunk ID: `subset-b-005357`

## Purpose

This chunk is the driver lifecycle tail of `smartpqi_init.c`. It covers controller reporting, PCI probe/remove, shutdown and power-management callbacks, supported PCI device matching, module registration, and the compile-time structure layout checks that protect the SmartPQI/SIS/BMIC hardware command ABI. The opening line is the end of `pqi_take_ctrl_devices_offline()`, which marks attached SCSI devices offline under `scsi_device_list_lock` before releasing the lock.

The core responsibility in this range is to bridge Linux PCI/PM/module entry points to the driver's controller initialization and teardown machinery while preserving cache flush ordering, request quiescing, interrupt ownership, controller online flags, and exact wire-format layouts.

## Important APIs, Types, and Functions

- `pqi_print_ctrl_info()` chooses either `pci_device_id.driver_data` or the generic `"Microchip Smart Family Controller"` description and logs the detected controller.
- `pqi_pci_probe()` is the PCI `.probe` entry point. It rejects wildcard-only matches when `pqi_disable_device_id_wildcards` is set, assigns a NUMA node, allocates `struct pqi_ctrl_info`, stores `pci_dev`, then calls `pqi_pci_init()` followed by `pqi_ctrl_init()`.
- `pqi_pci_remove()` is the PCI `.remove` path. It distinguishes surprise removal from graceful removal by reading `PCI_SUBSYSTEM_VENDOR_ID`; `0xffff` means the PCI function has disappeared. Graceful removal attempts `pqi_flush_cache(..., RESTART)` before `pqi_remove_ctrl()`.
- `pqi_shutdown()` is the PCI `.shutdown` hook. It waits for OFA completion, blocks SCSI requests, device resets, and controller requests, waits for quiescence, flushes cache using `RESTART` or `SHUTDOWN`, checks for pending commands, resets the controller, and unblocks device reset.
- `pqi_crash_if_pending_command()` scans `ctrl_info->io_request_pool` and emits `WARN_ON()` for any request with a nonzero refcount, deliberately warning whether `io_request->scmd` is present or absent. It is a shutdown/suspend invariant check that expects no outstanding driver or SCSI-midlayer commands after quiescing.
- `pqi_process_lockup_action_param()`, `pqi_process_ctrl_ready_timeout_param()`, and `pqi_process_module_params()` normalize module parameters. The controller-ready timeout is clamped to 30 seconds through 30 minutes and copied to `sis_ctrl_ready_timeout_secs`.
- `pqi_suspend_or_freeze()`, `pqi_suspend()`, `pqi_freeze()`, `pqi_resume_or_restore()`, `pqi_thaw()`, and `pqi_poweroff()` implement `CONFIG_PM` callbacks through `struct dev_pm_ops pqi_pm_ops`.
- `pqi_get_flush_cache_shutdown_event()` special-cases subsystem `PCI_VENDOR_ID_ADAPTEC2:0x1304` to use `RESTART` during suspend/poweroff; otherwise suspend uses `SUSPEND`.
- `pqi_pci_id_table[]` enumerates supported SmartPQI-compatible PCI subsystem IDs, ending with a wildcard `PCI_ANY_ID` entry for Adaptec2 device `0x028f`.
- `pqi_pci_driver` wires `.probe`, `.remove`, `.shutdown`, and optional `.driver.pm` into the PCI core.
- `pqi_init()` and `pqi_cleanup()` are the module init/exit hooks. Init verifies structures, attaches the SAS transport template, processes module parameters, and registers the PCI driver; cleanup unregisters the PCI driver and releases the SAS transport.
- `pqi_verify_structures()` uses `BUILD_BUG_ON()` and `offsetof()` checks to assert packed hardware-visible layouts for PQI registers, admin queues, RAID/AIO requests and responses, event IUs, task-management IUs, BMIC identify/feature structures, and queue sizing constants.

Key types visible in this chunk include `struct pqi_ctrl_info`, `struct pci_dev`, `struct pci_device_id`, `struct pci_driver`, `struct dev_pm_ops`, `enum bmic_flush_cache_shutdown_event`, `struct pqi_io_request`, and `struct scsi_cmnd`.

## Control Flow

PCI discovery flows through `pqi_pci_probe()`:

1. Log controller identity and enforce the wildcard-match module policy.
2. Pick a NUMA node from the PCI device or fall back to CPU 0, then persist it into the device with `set_dev_node()`.
3. Allocate controller state with `pqi_alloc_ctrl_info(node)`, attach `pci_dev`, and run PCI-level setup with `pqi_pci_init()`.
4. Run controller-level initialization with `pqi_ctrl_init()`.
5. On any failure after allocation, call `pqi_remove_ctrl()` so partially initialized PCI/controller resources are unwound through the common removal path.

Normal removal flows through `pqi_pci_remove()`. It obtains `ctrl_info` from PCI driver data, probes whether config space still responds, sets `ctrl_removal_state`, flushes battery-backed cache only for graceful removal, then delegates final teardown to `pqi_remove_ctrl()`.

System shutdown is stricter than normal remove. `pqi_shutdown()` blocks new work at multiple layers, waits for outstanding work to drain, chooses `RESTART` for reboot or `SHUTDOWN` otherwise, flushes cache, asserts that no request slots remain referenced, performs a controller reset, and only then unblocks device reset. The unblock after reset appears to restore internal gating even though the machine is shutting down, likely to leave controller state consistent for later paths or diagnostics.

Power management has two related paths:

- Suspend/freezer entry uses `pqi_suspend_or_freeze()`: wait for OFA, block scan/requests/resets, quiesce, optionally flush cache for real suspend, stop heartbeat, assert no pending commands, free IRQs, and mark `controller_online`/`pqi_mode_enabled` false.
- Resume/restore reacquires IRQs, unblocks reset/request/scan gates, waits `PQI_POST_RESET_DELAY_SECS`, then calls `pqi_ctrl_init_resume()` to reinitialize the controller. Thaw is lighter: reacquire IRQs, mark the controller online and PQI mode enabled, then unblock gates without full controller resume initialization.

Module load starts with structure verification and SAS transport registration before PCI registration, so the SCSI/SAS integration surface exists before devices are probed. If PCI registration fails, the SAS transport template is released immediately. Module exit reverses that order.

## State and Persistence Behavior

This chunk does not write persistent on-disk state. Its state changes are kernel-resident and hardware-visible:

- `ctrl_info->numa_node`, `ctrl_info->pci_dev`, and PCI driver data bind a controller instance to the PCI function.
- `ctrl_info->ctrl_removal_state` records graceful versus surprise removal for downstream teardown behavior.
- `ctrl_info->controller_online` and `ctrl_info->pqi_mode_enabled` are cleared during suspend/freeze and restored during thaw; resume relies on `pqi_ctrl_init_resume()` for full state restoration.
- Request, scan, and reset gates are changed via `pqi_ctrl_block_scan()`, `pqi_scsi_block_requests()`, `pqi_ctrl_block_device_reset()`, `pqi_ctrl_block_requests()`, and matching unblock calls.
- `sis_ctrl_ready_timeout_secs` is updated from the validated `pqi_ctrl_ready_timeout_secs` module parameter, affecting later SIS controller-ready waits.
- `pqi_lockup_action` is selected from the user-facing `pqi_lockup_action_param` string.
- Hardware cache persistence is protected by `pqi_flush_cache()` on graceful remove, shutdown, suspend, and poweroff. The shutdown event value controls firmware behavior for restart, shutdown, suspend, or device-specific restart-on-suspend semantics.

## Dependencies and Integration Points

This range integrates with several kernel subsystems:

- PCI core: `struct pci_driver`, `pci_register_driver()`, `pci_unregister_driver()`, `MODULE_DEVICE_TABLE()`, `pci_get_drvdata()`, `pci_read_config_word()`, and PCI subsystem/vendor matching macros.
- SCSI/SAS stack: request blocking/unblocking helpers, `struct scsi_cmnd`, `scsi_device_set_state()` in the preceding function, `sas_attach_transport()`, and `sas_release_transport()`.
- Power management: `struct dev_pm_ops`, suspend/resume/freeze/thaw/poweroff/restore callbacks, and `to_pci_dev()`.
- Kernel module framework: `module_init()`, `module_exit()`, module parameters consumed by the processing helpers, and build-time `BUILD_BUG_ON()` assertions.
- Controller internal layers: `pqi_pci_init()`, `pqi_ctrl_init()`, `pqi_ctrl_init_resume()`, `pqi_remove_ctrl()`, `pqi_flush_cache()`, `pqi_reset()`, IRQ allocation/free, heartbeat management, OFA wait, quiesce logic, SIS shutdown, and queue/request structures defined earlier in the file.

The PCI ID table is also a product-integration point. It controls which OEM and vendor-branded controllers bind automatically, while the final wildcard match permits broader Adaptec2 `0x028f` matching unless explicitly disabled by module parameter.

## Risks and Edge Cases

- The wildcard PCI entry intentionally broadens binding. The `pqi_disable_device_id_wildcards` guard mitigates deployments where unknown subsystem IDs should not attach to this driver, but default behavior still allows wildcard matches and logs only a warning.
- `pqi_pci_remove()` identifies surprise removal by reading `PCI_SUBSYSTEM_VENDOR_ID == 0xffff`. This is common PCI behavior but can misclassify if config-space access has unusual failure semantics.
- Cache flush failures during remove and shutdown are logged but do not stop teardown or shutdown. Data durability relies on firmware/hardware behavior after a failed flush.
- `pqi_crash_if_pending_command()` uses two mutually exclusive `WARN_ON()` checks so any referenced request slot warns. This is useful as an invariant signal but can be noisy if a preceding quiesce path fails during shutdown or PM.
- Suspend/freezer paths free IRQs and mark the controller offline. A failure in `pqi_request_irqs()` during resume/thaw returns an error before unblocking requests, leaving the controller gated as intended but requiring upper-layer recovery.
- Thaw sets `controller_online` and `pqi_mode_enabled` true without running `pqi_ctrl_init_resume()`, while resume/restore does run full resume initialization after a delay. Changes to freeze semantics must preserve that distinction.
- `pqi_verify_structures()` is a hard compile-time compatibility net. Any structure packing, field type, alignment, or constant change that affects hardware ABI will fail the build. This is intentional but means cross-compiler or architecture packing assumptions must remain stable.
- The large PCI ID table is easy to edit incorrectly. Duplicate, mistyped, or misplaced subsystem IDs can change hardware binding without affecting ordinary unit tests.

## Test and Validation Signals

- Build coverage is essential: `pqi_verify_structures()` produces compile-time failures for ABI drift in register maps, IU layouts, BMIC payloads, event/task-management formats, and queue element constraints.
- PCI probe testing should cover exact subsystem matches, wildcard matches with the default policy, and wildcard matches with `pqi_disable_device_id_wildcards` enabled.
- Lifecycle testing should exercise successful probe, failure after `pqi_pci_init()`, failure after partial controller initialization, graceful remove, surprise remove, reboot shutdown, poweroff shutdown, suspend/resume, freeze/thaw, and poweroff.
- Fault injection around `pqi_flush_cache()`, `pqi_request_irqs()`, and `pqi_ctrl_init_resume()` would verify teardown ordering, request gates, and user-visible logs.
- Runtime warning signals from `pqi_crash_if_pending_command()` indicate quiesce violations and should be treated as high-value evidence in shutdown/PM tests.
- Device binding validation should confirm representative IDs from the table and the final wildcard entry resolve to `pqi_pci_driver`, and that `MODULE_DEVICE_TABLE(pci, ...)` exports the expected aliases.

## Cross-Chunk References

This chunk calls many helpers defined earlier in `smartpqi_init.c` or adjacent SmartPQI files: controller allocation/removal, PCI setup, controller init/resume, request gating, OFA wait, heartbeat, IRQ setup/free, cache flush, reset, SIS shutdown, SAS transport functions, and the hardware-visible structures verified here. The later merge lane should connect this lifecycle tail to earlier chunks that define those helpers and the `struct pqi_ctrl_info` fields mutated here.
