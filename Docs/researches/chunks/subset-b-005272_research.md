# sources/distributed-fs/ceph-client/drivers/scsi/ipr.c lines 9237-10096

## Scope

This chunk is the tail of the IBM Power RAID SCSI (`ipr`) driver. It starts inside `ipr_wait_for_pci_err_recovery()` and covers interrupt-vector naming and MSI probing, first-stage PCI/SCSI host probe, adapter bringdown and hot-remove, second-stage PCI probe registration with sysfs artifacts and SCSI scanning, shutdown/reboot handling, the supported PCI ID table, PCI error-handler and PCI driver registration, the reboot notifier, and module init/exit.

The chunk depends on earlier definitions in the same file for chip tables, module parameters, interrupt handlers, reset state machines, memory allocation/free helpers, SCSI worker threads, sysfs binary attributes, command allocation, and PCI error recovery callbacks. It also depends on `ipr.h` for the core `struct ipr_ioa_cfg`, `struct ipr_hrr_queue`, `struct ipr_chip_t`, `struct ipr_chip_cfg_t`, and `enum ipr_shutdown_type` shapes. The preceding chunk contains most implementation details for the reset path and memory/resource helpers that this tail orchestrates.

## Purpose

The visible code turns a matched PCI function into a live SCSI host and tears it down again. Its responsibilities are:

- recover from probe-time EEH/PCI-channel-offline states before continuing PCI configuration;
- select MSI/MSI-X/INTx interrupt mode, verify MSI delivery, register one interrupt per hardware response queue when vectors are available, and fall back to legacy shared interrupts when needed;
- allocate and initialize the per-adapter `struct ipr_ioa_cfg` hosted in `Scsi_Host->hostdata`;
- map adapter MMIO BARs, configure DMA masks and cache-line size, save PCI state, detect card reset/error state, allocate DMA resources, and place the adapter on the global driver list;
- expose trace, dump, and async error-log sysfs files only after the SCSI host is added, then enable scanning and initialize optional `irq_poll` for multi-HRRQ SIS64 adapters;
- remove or shut down an adapter by stopping scans, flushing reset/work queues, initiating an IOA shutdown/reset sequence, freeing IRQs/resources, and unregistering from the global adapter list;
- register the PCI driver and reboot notifier at module load and unregister them at module unload.

This chunk is therefore the driver lifecycle boundary between the kernel PCI core, SCSI midlayer, low-level adapter reset logic, and system reboot/shutdown paths.

## Important APIs, Types, and Functions

- `ipr_wait_for_pci_err_recovery(struct ipr_ioa_cfg *ioa_cfg)` waits on `ioa_cfg->eeh_wait_q` while `pci_channel_offline(pdev)` is true, bounded by `IPR_PCI_ERROR_RECOVERY_TIMEOUT`, then restores PCI config state. It is called during probe error/retry points.
- `name_msi_vectors(struct ipr_ioa_cfg *ioa_cfg)` writes per-vector IRQ names into `ioa_cfg->vectors_info[]` as `host<host_no>-<vec_idx>`.
- `ipr_request_other_msi_irqs(struct ipr_ioa_cfg *ioa_cfg, struct pci_dev *pdev)` registers MSI/MSI-X vectors 1 through `nvectors - 1` with `ipr_isr_mhrrq` and each corresponding `struct ipr_hrr_queue`; vector 0 is registered separately with `ipr_isr`.
- `ipr_test_intr(int irq, void *devp)` is the temporary interrupt handler used only by the MSI self-test. Under `host_lock`, it sets `ioa_cfg->msi_received` and wakes `msi_wait_q`.
- `ipr_test_msi(struct ipr_ioa_cfg *ioa_cfg, struct pci_dev *pdev)` clears/masks adapter interrupts, installs `ipr_test_intr` on vector 0, triggers `IPR_PCII_IO_DEBUG_ACKNOWLEDGE`, waits one second for delivery, then frees the temporary IRQ. It returns `-EOPNOTSUPP` when the interrupt is not observed so probe can fall back to INTx.
- `ipr_probe_ioa(struct pci_dev *pdev, const struct pci_device_id *dev_id)` performs first-stage adapter allocation and hardware setup. It allocates a `Scsi_Host`, initializes `struct ipr_ioa_cfg`, requests PCI regions, enables the device, maps BAR 0, initializes register offsets, configures DMA masks, allocates IRQ vectors, saves/sets PCI-X command registers, allocates driver memory, saves PCI config state, checks interrupt/reset indicators, registers permanent IRQ handlers, configures the reset method, and adds the adapter to `ipr_ioa_head`.
- `ipr_initiate_ioa_bringdown(struct ipr_ioa_cfg *ioa_cfg, enum ipr_shutdown_type shutdown_type)` marks dump collection as aborting when needed, resets retry counters, marks `in_ioa_bringdown`, and starts the reset/shutdown state machine.
- `__ipr_remove(struct pci_dev *pdev)` is the internal resource-removal path used by hot-remove and probe-failure unwind after `scsi_add_host()`. It waits for active reset reloads, marks HRRQs as removing, initiates normal shutdown, flushes work, removes the adapter from the global list, restores dump state, and calls `ipr_free_all_resources()`.
- `ipr_remove(struct pci_dev *pdev)` is the PCI remove callback. It removes trace/dump/async-error sysfs files, removes the SCSI host, and then delegates to `__ipr_remove()`.
- `ipr_probe(struct pci_dev *pdev, const struct pci_device_id *dev_id)` is the PCI probe callback. It wraps `ipr_probe_ioa()`, starts adapter enable/reset through `ipr_probe_ioa_part2()`, adds the SCSI host, creates sysfs binary files, enables scan work, initializes secondary-HRRQ `irq_poll` where applicable, and calls `scsi_scan_host()`.
- `ipr_shutdown(struct pci_dev *pdev)` is the PCI shutdown callback. It disables secondary `irq_poll`, waits for reset reloads, selects `IPR_SHUTDOWN_QUIESCE` for SIS64 fast reboot, initiates bringdown, waits for completion, and in fast-reboot mode frees IRQs and disables the PCI device.
- `ipr_pci_table[]` lists supported IBM/Mylex/Adaptec PCI vendor/device/subsystem combinations and flags entries needing long transition-to-operational timeouts or PCI warm reset.
- `ipr_err_handler` wires the PCI EEH/error-recovery callbacks defined earlier: `ipr_pci_error_detected`, `ipr_pci_mmio_enabled`, and `ipr_pci_slot_reset`.
- `ipr_driver` is the Linux `struct pci_driver` binding name, ID table, probe/remove/shutdown callbacks, and PCI error handler.
- `ipr_halt_done(struct ipr_cmnd *ipr_cmd)` returns the shutdown-prepare command to its HRRQ free list.
- `ipr_halt(struct notifier_block *nb, ulong event, void *buf)` is a reboot notifier that sends `IPR_IOA_SHUTDOWN` with `IPR_SHUTDOWN_PREPARE_FOR_NORMAL` to all adapters that are accepting commands, except SIS64 fast-reboot restart cases.
- `ipr_init()` registers the reboot notifier and PCI driver; `ipr_exit()` unregisters both.

Key data carried through these paths includes `struct ipr_ioa_cfg` fields such as `host`, `pdev`, `ipr_chip`, `chip_cfg`, `sis64`, `clear_isr`, `max_cmds`, `transop_timeout`, `nvectors`, `hrrq_num`, `vectors_info`, `regs`, `reset`, `reset_work_q`, `needs_hard_reset`, `needs_warm_reset`, `ioa_unit_checked`, `in_reset_reload`, `in_ioa_bringdown`, `sdt_state`, `iopoll_weight`, and per-HRRQ `removing_ioa`/`allow_cmds` state.

## Control Flow

Probe starts in `ipr_probe()`, which calls `ipr_probe_ioa()` for resource acquisition. `ipr_probe_ioa()` first allocates the SCSI host and zeroes `hostdata`, looks up chip metadata from the PCI ID, derives SIS32/SIS64 mode and transition timeout, and initializes software queues and wait queues via `ipr_init_ioa_cfg()` from the previous chunk. It then requests PCI BAR ownership, enables the function, waits and retries if the channel is offline, maps BAR 0, calculates register addresses, and selects a 64-bit DMA mask for SIS64 adapters with 32-bit fallback.

After basic PCI setup, probe writes the PCI cache-line size and performs an MMIO read to surface EEH state. It clamps the global `ipr_number_of_msix` module parameter to `IPR_MAX_MSIX_VECTORS`, requests IRQ vectors with INTx always allowed and MSI/MSI-X allowed only when the chip advertises `has_msi`, and records `ioa_cfg->nvectors`. Legacy interrupt mode forces `clear_isr = 1`.

If MSI/MSI-X is enabled, `ipr_test_msi()` installs a temporary handler on vector 0, unmasks/debug-acknowledges the adapter interrupt, waits for `msi_received`, then removes the test handler. A successful test keeps the allocated vectors. A missing interrupt returns `-EOPNOTSUPP`, causing probe to wait for PCI recovery, free the vectors, reset `nvectors` to 1, set `clear_isr`, and continue with legacy interrupt setup. Other test errors abort probe through the vector-cleanup path.

`hrrq_num` is the minimum of allocated vectors, online CPUs, and `IPR_MAX_HRRQ_NUM`. The function then saves/sets PCI-X command state, allocates coherent resources and command blocks, saves PCI config state for reset recovery, checks adapter interrupt/microprocessor registers for unknown/error/reset-alert state, masks and clears interrupts under `host_lock`, and registers permanent IRQ handlers. With MSI/MSI-X, vector 0 uses `ipr_isr` and remaining vectors use `ipr_isr_mhrrq`; with INTx, `ipr_isr` is registered shared on `pdev->irq`.

Warm-reset-capable hardware is selected from PCI ID flags or an early Obsidian-E revision. Those adapters set `needs_warm_reset`, use `ipr_reset_slot_reset`, and allocate an ordered reset workqueue named by host number. Other adapters use `ipr_reset_start_bist`. Once the reset method is established, the adapter is added to `ipr_ioa_head` under `ipr_driver_lock` and first-stage probe succeeds. Every failure label unwinds only the resources acquired up to that point: IRQs, driver memory, IRQ vectors, MMIO map, PCI enablement, regions, and SCSI host reference.

Second-stage probe continues in `ipr_probe()`. It starts the adapter enable/reset path with `ipr_probe_ioa_part2()`, then registers the host with the SCSI midlayer. Sysfs trace, async error-log, and dump files are created in sequence; each failure path removes previously created files, removes the SCSI host when needed, and calls `__ipr_remove()`. Once sysfs setup succeeds, `scan_enabled` is set under `host_lock`, `work_q` is scheduled to populate devices, optional secondary-HRRQ `irq_poll` instances are initialized for SIS64 multi-vector adapters, and `scsi_scan_host()` starts discovery.

Removal reverses the lifecycle. `ipr_remove()` first removes sysfs files and detaches the SCSI host so no new midlayer operations enter. `__ipr_remove()` waits out active reset reloads, marks every active HRRQ as `removing_ioa`, issues a normal IOA bringdown, waits for reset completion, flushes normal and reset work, clears `used_res_q`, removes the adapter from `ipr_ioa_head`, repairs `sdt_state` from `ABORT_DUMP` back to `WAIT_FOR_DUMP` when appropriate, and frees all hardware/software resources.

Shutdown is similar but optimized for system poweroff/restart. It disables active secondary `irq_poll`, waits for reset reloads, chooses quiesce shutdown for SIS64 fast reboot on `SYSTEM_RESTART`, initiates bringdown, waits for completion, and for that fast-reboot path frees IRQs and disables PCI without freeing the whole host object because normal module/device teardown is not necessarily running.

The reboot notifier runs earlier in reboot/halt/poweroff notification. Under the global adapter lock it iterates `ipr_ioa_head`, locks each host, skips adapters that cannot accept commands or SIS64 fast-reboot restart cases, obtains a free internal command, fills an IOA shutdown-prepare CDB, submits it with `ipr_do_req()`, and relies on `ipr_halt_done()` to return the command to the free queue on completion.

## State and Persistence

Most state in this chunk is volatile kernel and adapter runtime state:

- `pci_set_drvdata()` from earlier initialization makes `struct ipr_ioa_cfg` the persistent per-device handle for all PCI callbacks.
- PCI regions, PCI enablement, BAR mappings, DMA masks, saved PCI state, IRQ-vector allocations, and registered IRQ handlers are acquired during `ipr_probe_ioa()` and released by failure labels, `__ipr_remove()`, or fast reboot shutdown.
- `ioa_cfg->nvectors`, `hrrq_num`, `vectors_info[]`, and each `hrrq[]` determine interrupt distribution and command-completion queue ownership for the lifetime of the adapter instance.
- `ioa_cfg->needs_hard_reset`, `needs_warm_reset`, `ioa_unit_checked`, `reset`, and `reset_work_q` capture detected adapter condition and select the later reset/reload behavior.
- `ioa_cfg->sdt_state` is temporarily changed from `WAIT_FOR_DUMP` to `ABORT_DUMP` during bringdown to stop dump collection and restored during remove if no longer tearing down.
- `scan_enabled` gates asynchronous resource discovery, while `scsi_add_host()`/`scsi_scan_host()` publish the host to the SCSI midlayer.
- `ipr_ioa_head` is the global list used by reboot notification; membership begins after first-stage probe succeeds and ends during internal removal.
- Module parameters from earlier in the file influence persistent runtime policy: `ipr_transop_timeout`, `ipr_number_of_msix`, `ipr_fast_reboot`, `ipr_debug`, and kernel `reset_devices`.

The code does not itself write adapter NVRAM or disk data. It does save PCI config state for later reset recovery and sends shutdown commands intended to flush adapter write cache during remove/shutdown/reboot.

## Dependencies and Integration Points

Kernel subsystem dependencies are broad:

- PCI core: `pci_request_regions()`, `pci_enable_device()`, `pci_ioremap_bar()`, `pci_set_master()`, `pci_alloc_irq_vectors()`, `pci_irq_vector()`, `pci_free_irq_vectors()`, `pci_save_state()`, `pci_restore_state()`, `pci_channel_offline()`, `pci_register_driver()`, `pci_unregister_driver()`, and PCI EEH/error-handler callbacks.
- IRQ and polling layers: `request_irq()`, `free_irq()`, `IRQF_SHARED`, `irq_poll_init()`, `irq_poll_disable()`, and the earlier `ipr_isr`, `ipr_isr_mhrrq`, and `ipr_iopoll` implementations.
- DMA/MMIO: `dma_set_mask_and_coherent()`, coherent allocations from previous helpers, `readl()`, `writel()`, `iounmap()`, and register offsets in `struct ipr_interrupts`.
- SCSI midlayer: `scsi_host_alloc()`, `scsi_host_put()`, `scsi_add_host()`, `scsi_remove_host()`, `scsi_scan_host()`, and the global `driver_template`.
- Workqueues and wait queues: adapter work uses `work_q`, `scsi_add_work_q`, optional ordered `reset_work_q`, `wait_event()`, and `wait_event_timeout()`.
- Sysfs binary attributes: `ipr_trace_attr`, `ipr_dump_attr`, and `ipr_ioa_async_err_log` are created under `host->shost_dev.kobj`; trace/dump helpers compile to no-ops unless their config options are enabled.
- Reboot notifiers: `register_reboot_notifier()`, `unregister_reboot_notifier()`, `SYS_RESTART`, `SYS_HALT`, `SYS_POWER_OFF`, and global `system_state`.

Internal integration points include previous-chunk helpers `ipr_init_ioa_cfg()`, `ipr_init_regs()`, `ipr_save_pcix_cmd_reg()`, `ipr_set_pcix_cmd_reg()`, `ipr_alloc_mem()`, `ipr_free_mem()`, `ipr_free_irqs()`, `ipr_free_all_resources()`, `ipr_probe_ioa_part2()`, `ipr_initiate_ioa_reset()`, `ipr_get_free_ipr_cmnd()`, `ipr_do_req()`, `ipr_timeout()`, and the earlier reset/PCI-error callback implementations. The ID table uses many `IPR_SUBS_DEV_ID_*` and `PCI_DEVICE_ID_*` constants from headers and supplies driver-data flags consumed during probe.

## Risks and Edge Cases

- `ipr_wait_for_pci_err_recovery()` calls `pci_restore_state()` after a bounded wait even if the channel remains offline. Callers often retry or check again, but the helper itself does not report timeout status.
- The MSI self-test temporarily requests vector 0 before permanent IRQ setup. Any mismatch between adapter debug interrupt generation and platform MSI delivery causes fallback to INTx, reducing queue parallelism.
- In the MSI fallback path, `pci_free_irq_vectors()` is called and `nvectors` is set to 1, but the code does not call `pci_alloc_irq_vectors()` again for INTx before the later legacy `request_irq(pdev->irq, ...)`. This relies on `pdev->irq` being valid for legacy INTx after vector cleanup on the target kernel.
- `ipr_request_other_msi_irqs()` frees only vectors already requested in its own loop on failure; vector 0 is freed later by the `cleanup_nolog` path through `ipr_free_mem()` only after jumping to cleanup. In this chunk, an error after vector 0 registration but before `ipr_request_other_msi_irqs()` success jumps to `cleanup_nolog`, which does not free vector 0 directly; later `out_msi_disable` frees IRQ vectors, but a registered IRQ handler still needs `free_irq()` first. The normal vector-registration failure path deserves careful review against the exact kernel IRQ-vector cleanup semantics.
- `name_msi_vectors()` uses `sizeof(desc) - 1` as the `snprintf()` size and then writes a NUL at `strlen(desc)`. This is redundant and leaves one byte unused, but appears bounded for the fixed descriptor buffer.
- `ipr_probe_ioa()` error labels are dense and order-sensitive. Small changes in resource acquisition order can introduce leaks or double frees if the unwind labels are not updated together.
- `ipr_free_irqs()` assumes `ioa_cfg->nvectors` corresponds to registered permanent IRQs. It is correct after successful permanent registration, but unsafe if reused in partially registered states without matching vector-handler accounting.
- `__ipr_remove()` waits for `in_reset_reload` before and after initiating bringdown. If reset completion never wakes `reset_wait_q`, hot-remove or shutdown can block indefinitely.
- `INIT_LIST_HEAD(&ioa_cfg->used_res_q)` in `__ipr_remove()` discards the active resource list before `ipr_free_all_resources()`. That is intentional after `scsi_remove_host()` and bringdown, but any later code expecting to walk used resources during free would observe an empty list.
- `ipr_shutdown()` frees IRQs and disables the PCI device only for the SIS64 fast-reboot path; other shutdowns depend on the adapter shutdown/reset sequence and platform reboot/poweroff, not full resource free.
- `ipr_halt()` obtains a free command without checking for `NULL`. The code assumes `allow_cmds` implies an internal command is available; if the free list is empty during reboot notification, this could dereference a bad pointer.
- `ipr_halt_done()` returns commands to the free list without taking the HRRQ lock in this local function. The surrounding request/completion path may already run under appropriate locking, but the function is fragile if reused outside that context.
- Reboot notifier ordering with PCI shutdown can matter. `ipr_halt()` may send shutdown-prepare commands while later `ipr_shutdown()` also initiates bringdown; fast reboot skips notifier commands for SIS64 restart cases to avoid conflicting with the quiesce path.
- The PCI ID table is large and manually maintained. Missing or incorrect `driver_data` flags can select wrong transition timeouts or reset methods for a hardware revision.

## Test and Validation Signals

Useful validation for this chunk should focus on lifecycle, hardware modes, and failure unwinding:

- Probe supported SIS32 and SIS64 adapters with INTx-only, MSI, and MSI-X-capable platforms. Confirm `scsi_add_host()`, sysfs trace/dump/async-log creation, `scan_enabled`, `scsi_scan_host()`, and command completion all work.
- Force `ipr_number_of_msix` above `IPR_MAX_MSIX_VECTORS` and verify it is clamped with an error message and no out-of-bounds vector naming or IRQ registration.
- Inject MSI test failure and confirm fallback to legacy interrupts, `clear_isr = 1`, `nvectors = 1`, successful permanent legacy `request_irq()`, and no leaked temporary IRQ/vector state.
- Fault-inject each `ipr_probe_ioa()` acquisition step: host allocation, PCI regions, PCI enable, BAR map, DMA mask, cache-line write, vector allocation, PCI-X setup, driver memory allocation, PCI state save, permanent IRQ request, and reset workqueue allocation. Check all acquired resources are released once.
- Exercise EEH/PCI-channel-offline recovery during probe and verify wait-queue wakeups, state restore, retry behavior, and eventual failure if the channel stays offline.
- Probe devices with interrupt registers indicating unmasked HRRQ updates, reset alerts, PCI error interrupts, unit check, and `reset_devices`; verify `needs_hard_reset` and `ioa_unit_checked` feed `ipr_probe_ioa_part2()` as expected.
- Remove an adapter under load and during reset reload. Confirm `removing_ioa` is set on all active HRRQs, outstanding reset waits complete, work queues flush, sysfs files are gone before resource free, and no SCSI commands enter after `scsi_remove_host()`.
- Test sysfs creation failures independently for trace, async error log, and dump paths; each should remove previous artifacts and invoke internal removal without leaking host or PCI resources.
- Validate `irq_poll` setup and teardown for SIS64 multi-vector adapters with nonzero `iopoll_weight`; secondary HRRQs should be initialized after probe and disabled during shutdown.
- Reboot, halt, poweroff, and fast-reboot restart paths should show shutdown-prepare commands for eligible adapters, normal bringdown on shutdown, quiesce mode for SIS64 fast reboot, and no duplicate command submission in the skipped fast-reboot notifier case.
- Module load/unload should verify notifier registration is undone if `pci_register_driver()` fails, and normal unload unregisters notifier before the PCI driver.
