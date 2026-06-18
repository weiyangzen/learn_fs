# sources/distributed-fs/ceph-client/drivers/scsi/vmw_pvscsi.c

## Purpose

`vmw_pvscsi.c` implements the Linux PCI driver for VMware's paravirtualized SCSI host adapter. It maps VMware PVSCSI MMIO registers and DMA rings, translates SCSI commands into request descriptors, processes completion and message rings, supports SCSI error handling, and registers a `Scsi_Host` behind the PCI device.

## Important APIs, Types, And Functions

Driver-private state is `struct pvscsi_adapter`, containing MMIO base, revision/features, hardware lock, optional message workqueue, request/completion/message rings and DMA addresses, shared ring state page, PCI and SCSI host pointers, a free context list, and a context map. Each `struct pvscsi_ctx` tracks the SCSI command, per-context SG list page, DMA addresses for data/sense/SG list, and optional abort completion.

Register and command helpers are `pvscsi_reg_read()`, `pvscsi_reg_write()`, `pvscsi_write_cmd_desc()`, `ll_adapter_reset()`, `ll_bus_reset()`, `ll_device_reset()`, `pvscsi_abort_cmd()`, `pvscsi_kick_rw_io()`, and `pvscsi_process_request_ring()`.

I/O helpers include `pvscsi_acquire_context()`, `pvscsi_release_context()`, `pvscsi_map_context()`, `pvscsi_get_context()`, `pvscsi_create_sg()`, `pvscsi_map_buffers()`, `pvscsi_unmap_buffers()`, `pvscsi_queue_ring()`, and `pvscsi_queue_lck()`. Completion and EH paths are `pvscsi_process_completion_ring()`, `pvscsi_complete_request()`, `pvscsi_abort()`, `pvscsi_host_reset()`, `pvscsi_bus_reset()`, `pvscsi_device_reset()`, and `pvscsi_reset_all()`.

Lifecycle and resources are handled by `pvscsi_probe()`, `pvscsi_remove()`, `pvscsi_shutdown()`, `pvscsi_allocate_rings()`, `pvscsi_setup_all_rings()`, `pvscsi_allocate_sg()`, `pvscsi_release_resources()`, and IRQ setup/shutdown. Hotplug messages flow through `pvscsi_process_msg_ring()`, `pvscsi_process_msg()`, and `pvscsi_msg_workqueue_handler()`.

## Control Flow And State

Probe enables PCI, sets a 64-bit or 32-bit coherent DMA mask, requests BARs, locates an MMIO BAR large enough for the PVSCSI register layout, maps it, and uses a temporary adapter to query controller configuration for max targets. It chooses ring pages, allocates a SCSI host, resets the adapter, detects optional message-ring and request-threshold support, allocates coherent ring memory, sets up rings with page frame numbers, allocates the context map and per-context SG pages, obtains one IRQ vector, registers an ISR, adds the SCSI host, unmasks interrupts, and scans.

Queueing takes `hw_lock`, obtains a context from `cmd_pool`, fills a request ring slot selected by `reqProdIdx`, maps the sense buffer, sets CDB/LUN/tag/direction fields, maps data either as direct DMA or as a one-page PVSCSI SG list, writes a non-zero context ID, uses a compiler barrier, advances `reqProdIdx`, releases the lock, and kicks either the RW or non-RW path. RW kicks can be coalesced by the device-supplied request threshold.

Completions are consumed while `cmpConsIdx != cmpProdIdx`. Barriers prevent the compiler from reading a descriptor before the emulated device has published it or advancing the consumer before descriptor fields are consumed. Completion maps `hostStatus` and `scsiStatus` to Linux SCSI result bytes, sets residuals where appropriate, unmaps buffers, releases the context, and calls `scsi_done()`. If an abort is pending for that context, the normal completion is swallowed and the abort waiter is completed.

Error handling serializes with the hardware lock. Abort first drains completions, locates the context, sets `abort_cmp`, sends `PVSCSI_CMD_ABORT_CMD`, waits up to two seconds, then either reports `DID_ABORT` or fails. Host reset disables message work, drains request/completion rings around adapter reset, completes all outstanding commands as reset, rebuilds rings, and unmasks interrupts. Bus/device reset flushes requests, sends the reset command, and drains completions.

Message-ring interrupts schedule an ordered workqueue. Device-added messages add a missing SCSI device, while device-removed messages look up and remove the device.

## Dependencies And Integration Points

The driver depends on PCI, DMA coherent allocation, Linux SCSI midlayer, IRQ vector allocation, workqueues, and the ABI structures in `vmw_pvscsi.h`. It exposes module parameters for ring pages, message-ring pages, commands per LUN, MSI/MSI-X disable switches, message-ring enablement, and request-threshold coalescing.

## Risks And Test Signals

Resource cleanup has sharp edges: several error labels call `pvscsi_shutdown_intr()` even on paths where IRQ vectors may not have been allocated, so probe-failure paths should be audited in the exact kernel context. Ring memory and context mappings are tightly coupled; `pvscsi_reset_all()` is only safe after reset or when the completion ring will not be walked again. The code relies on x86 strong ordering and uses compiler barriers rather than full memory barriers because PVSCSI is VMware/x86-focused.

Other risks are SG count overflow beyond a single PVSCSI SG page, residual underflow if a completion reports larger `dataLen` in underrun cases, hotplug message races with host removal, and abort races with normal completion. Tests should cover 32/64-bit DMA masks, MSI-X/MSI/INTx, ring-page parameter extremes, heavy queue depth, abort/reset paths, hot-add/remove messages, direct and SG I/O, request coalescing, suspend/shutdown, and probe failure injection at each allocation/register step.
