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
