# sources/distributed-fs/ceph-client/drivers/scsi/hptiop.c

## Purpose

`hptiop.c` is the Linux SCSI low-level driver for HighPoint RocketRAID 3xxx/4xxx PCI controllers. It binds PCI IDs to one of three IOP adapter families, maps their MMIO/mailbox interfaces, negotiates firmware configuration, allocates DMA request blocks, implements the SCSI queue/completion path, handles interrupts and messages, exposes version attributes, performs host reset/shutdown, and registers the module's PCI and SCSI driver interfaces.

## Important APIs, Types, and Functions

- Adapter-family operations are collected in `hptiop_itl_ops`, `hptiop_mv_ops`, and `hptiop_mvfrey_ops`, each supplying `iop_wait_ready`, internal memory allocation/free, BAR mapping, interrupt control, config get/set, interrupt processing, message posting, request posting, DMA address width, reset-communication behavior, and host physical-address flags.
- Ready/config paths include `iop_wait_ready_itl()`, `iop_wait_ready_mv()`, `iop_wait_ready_mvfrey()`, `iop_get_config_*()`, `iop_set_config_*()`, `iop_send_sync_request_*()`, and `iop_send_sync_msg()`.
- Interrupt paths include `iop_intr_itl()`, `iop_intr_mv()`, `iop_intr_mvfrey()`, `hptiop_intr()`, outbound queue drain helpers, family-specific request callbacks, and `hptiop_message_callback()`.
- Request management functions include `get_req()`, `free_req()`, `hptiop_buildsgl()`, `hptiop_post_req_itl()`, `hptiop_post_req_mv()`, `hptiop_post_req_mvfrey()`, and `hptiop_finish_scsi_req()`.
- SCSI mid-layer entry points are exposed through `driver_template`: `hptiop_queuecommand`, `hptiop_reset`, `hptiop_info`, `hptiop_adjust_disk_queue_depth`, and `hptiop_sdev_configure`.
- PCI/module lifecycle is implemented by `hptiop_probe()`, `hptiop_remove()`, `hptiop_shutdown()`, `hptiop_module_init()`, and `hptiop_module_exit()`.
- Sysfs host attributes `driver-version` and `firmware-version` are provided through `hptiop_show_version()` and `hptiop_show_fw_version()`.

## Control Flow and State

Module initialization registers `hptiop_pci_driver`. Probe enables the PCI device, sets bus mastering and a DMA mask based on the matched adapter ops, requests PCI regions, allocates a `Scsi_Host` with `struct hptiop_hba` hostdata, maps family-specific BARs, waits for firmware readiness, allocates family-internal memory where needed, gets firmware configuration, records max request/device/S/G and version limits, optionally resets MVFREY communication rings, configures the firmware with host ID and max request size, requests the shared IRQ, allocates one DMA-coherent request buffer per firmware request slot, initializes the free-list, starts IOP background tasks, adds the SCSI host, and scans.

The normal I/O path starts at `hptiop_queuecommand_lck()`. It pops a request from `hba->req_list`, rejects out-of-range channel/target/LUN combinations with `DID_BAD_TARGET`, maps the Linux S/G list with `scsi_dma_map()`, fills an `IOP_REQUEST_TYPE_SCSI_COMMAND` request with CDB, target address, data length, S/G entries, pending result, and size, then posts it through the selected adapter ops. Completion arrives via IRQ polling of family-specific outbound queues or doorbells. The request callback decodes the tag/index, normalizes success bits for newer queue formats, and calls `hptiop_finish_scsi_req()`, which unmaps DMA, converts firmware result codes to Linux `DID_*` or check-condition status, copies sense data from the request payload for `IOP_RESULT_CHECK_CONDITION`, calls `scsi_done()`, and returns the request to the free-list.

Synchronous messages and config requests disable interrupts or poll the family interrupt handler while waiting for `hba->msg_done`. Reset posts `IOPMU_INBOUND_MSG0_RESET`, waits up to 60 seconds for `reset_wq`, then restarts background tasks. Shutdown sends `IOPMU_INBOUND_MSG0_SHUTDOWN` and disables outbound interrupts. Remove calls `scsi_remove_host()`, shutdown, IRQ free, request DMA free, internal memory free, BAR unmap, PCI region release, PCI disable, and `scsi_host_put()`.

## State and Persistence Behavior

All state is volatile kernel/device state. `struct hptiop_hba` persists while the PCI device is bound and stores adapter ops, mapped register pointers, firmware limits and versions, request size, free-list head, request array, DMA allocations, reset counters, flags (`initialized`, `iopintf_v2`, `msg_done`), and wait queues. Per-command private state lives in `struct hpt_cmd_priv` attached to each `scsi_cmnd`, tracking DMA mapping and S/G count. Firmware configuration is read at probe and written through `SET_CONFIG`, but the driver does not persist settings to filesystem storage.

## Dependencies and Integration Points

The driver integrates with Linux PCI APIs, DMA coherent allocation and streaming S/G mapping, interrupt registration, SCSI mid-layer host templates, queue limits, sysfs host attribute groups, wait queues, atomics, MMIO helpers, and module registration. It depends on `hptiop.h` for firmware request/register layouts and adapter state definitions. Hardware integration is split by adapter family: Intel-style queue registers, Marvell memory queues, and MVFREY inbound/outbound list rings.

## Risks

- `get_req()` and `free_req()` manipulate `hba->req_list` without internal locking and rely on the SCSI host lock held by queue and interrupt paths. Any future call outside that lock could corrupt the free-list.
- Several error paths in probe jump to `unmap_pci_bar` after family-internal memory allocation failures, relying on `internal_memfree()` to tolerate unallocated state. The MV and MVFREY implementations return `-1` for missing memory but are otherwise benign.
- `hptiop_buildsgl()` uses `BUG_ON()` for DMA mapping failures and S/G overflow, turning recoverable resource pressure into a kernel crash.
- Sense data for check condition is copied from `req->sg_list`, so the firmware ABI must place sense data there for that result. Any ABI change would corrupt sense reporting.
- MVFREY ring pointer toggling and tag encoding are hand-coded and sensitive to list count, shifted physical address width, and ordering of writes/readbacks.
- `hptiop_intr()` returns an integer `handled` as `irqreturn_t`; the values align with `IRQ_NONE`/`IRQ_HANDLED`, but changes should preserve that convention.

## Test Signals

- Build with `CONFIG_SCSI_HPTIOP` should validate SCSI template, PCI ID, queue-limit, and DMA APIs.
- Probe tests on each family should confirm BAR mapping, DMA mask selection, config read/write, IRQ registration, background-task start, and SCSI scan.
- I/O tests should cover reads/writes with no data, single S/G, and many S/G segments up to `max_sg_descriptors`, verifying residuals and DMA unmap.
- Fault tests should induce busy, bad target, reset, invalid request, fail, and check-condition firmware results and confirm Linux result mapping and sense propagation.
- Reset/remove/shutdown tests should verify wait-queue wakeup, interrupt disable, request-memory cleanup, and no completions after `scsi_remove_host()`.
