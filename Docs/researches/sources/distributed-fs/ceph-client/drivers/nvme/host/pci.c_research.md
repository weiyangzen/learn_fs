# sources/distributed-fs/ceph-client/drivers/nvme/host/pci.c

## Purpose

`pci.c` is the Linux NVMe PCIe host transport driver. It binds PCI devices in the NVMe class or explicit quirk table, maps the controller BAR, creates admin and I/O queues, translates blk-mq requests into NVMe submission queue entries, maps request data and metadata through DMA, handles completions through interrupts or polling, and coordinates controller reset, shutdown, suspend/resume, and PCI error recovery. It is the hardware-facing transport implementation behind the generic `nvme_ctrl` core for local PCIe NVMe devices.

## Important APIs, types, and functions

- Module parameters shape runtime behavior: `use_threaded_interrupts`, `use_cmb_sqes`, `max_host_mem_size_mb`, `sgl_threshold`, `io_queue_depth`, `write_queues`, `poll_queues`, `noacpi`, and `quirks`.
- `struct nvme_dev` is the per-PCI-function transport object. It embeds `struct nvme_ctrl`, blk-mq tag sets, MMIO BAR pointers, doorbell stride, queue counts, CMB/HMB state, shadow doorbell buffers, descriptor pools, and shutdown serialization.
- `struct nvme_queue` represents an admin or I/O queue pair with SQ/CQ DMA memory, doorbell pointers, phase/head/tail indices, IRQ vector, poll lock, and queue flags such as `NVMEQ_ENABLED`, `NVMEQ_SQ_CMB`, and `NVMEQ_POLLED`.
- `struct nvme_iod` is blk-mq request private data. It stores the prepared NVMe command, descriptor pointers, DMA iterator state, metadata mapping state, and flags that tell completion paths how to unmap resources.
- Request mapping is split across `nvme_prep_rq`, `nvme_map_data`, `nvme_pci_setup_data_simple`, `nvme_pci_setup_data_prp`, `nvme_pci_setup_data_sgl`, `nvme_map_metadata`, `nvme_pci_setup_meta_mptr`, and `nvme_pci_setup_meta_iter`.
- Submission and batching are handled by `nvme_queue_rq`, `nvme_queue_rqs`, `nvme_submit_cmds`, `nvme_sq_copy_cmd`, `nvme_write_sq_db`, and `nvme_commit_rqs`.
- Completion handling is centered on `nvme_irq`, `nvme_poll`, `nvme_poll_cq`, `nvme_handle_cqe`, `nvme_pci_complete_rq`, and `nvme_pci_complete_batch`.
- Queue lifecycle is implemented by `nvme_alloc_queue`, `nvme_create_queue`, `nvme_setup_io_queues`, `nvme_create_io_queues`, `nvme_delete_io_queues`, `nvme_suspend_queue`, and `nvme_free_queues`.
- Controller lifecycle is implemented by `nvme_probe`, `nvme_pci_enable`, `nvme_pci_configure_admin_queue`, `nvme_reset_work`, `nvme_dev_disable`, `nvme_remove`, `nvme_shutdown`, and the PM and PCI error handler callbacks.
- The `nvme_pci_ctrl_ops` vtable connects this transport to the NVMe core through register access, async event submission, subsystem reset, address reporting, P2PDMA support, and virtual boundary reporting.

## Control flow

Probe starts in `nvme_probe`. The driver allocates `nvme_dev`, applies static, DMI, ACPI, and user-specified quirks, initializes the generic controller, maps PCI BAR0, allocates the I/O descriptor mempool, enables the PCI device, configures the admin queue, allocates the admin blk-mq tag set, marks the controller `CONNECTING`, finishes generic controller initialization, allocates optional doorbell buffers and host memory buffer, sets up I/O queues, optionally creates the I/O tag set, marks the controller `LIVE`, starts scans/events, and returns with the controller registered.

For I/O, blk-mq calls `nvme_queue_rq` or `nvme_queue_rqs`. The transport first checks queue enabled state and controller readiness, then `nvme_prep_rq` calls the core `nvme_setup_cmd`, maps data and integrity metadata, and starts the request. The SQE is copied into the submission ring under `sq_lock`; the driver writes a real or shadow doorbell when the batch requires it or the next command would wrap. Batched submission groups requests by hardware queue before ringing the doorbell.

Data mapping chooses between PRP and SGL. Single-segment requests try a fast path using `dma_map_bvec`. Multi-segment requests use blk DMA iterators. SGL is forced for controller page gaps, user commands, and multiple integrity segments; otherwise SGL is selected only when supported and the average segment size exceeds `sgl_threshold`. PRP setup builds one or more PRP list pages from DMA pool descriptors. SGL setup builds a data or segment descriptor list. Metadata uses MPTR for trusted single-segment kernel integrity data where possible, and metadata SGLs for user commands, P2P cases, or multi-segment integrity.

Completion flow starts from an IRQ, threaded IRQ check, or blk-mq poll. `nvme_poll_cq` checks the CQE phase bit, uses `dma_rmb`, handles each CQE, advances head/phase, and rings the CQ doorbell. AEN command IDs bypass normal request lookup and go to the core async-event completion path. Normal completions locate the request in the relevant tag set, try the core completion fast path, batch if possible, and finally unmap metadata/data before `nvme_complete_rq`.

Reset and error flow is explicit. Timeouts first poll for a missed interrupt. If a request is still in flight, the driver may submit an admin abort; a repeated abort or admin timeout transitions to controller reset. `nvme_reset_work` disables a previously enabled controller if needed, re-enables PCI/admin queues, repeats core initialization, recreates HMB/doorbell resources and I/O queues, updates queue counts, and either returns to `LIVE` or marks namespaces dead and the controller `DEAD`. PCI AER callbacks quiesce and disable queues on frozen channels and schedule reset after slot reset.

## State and persistence behavior

Persistent state is mostly kernel-resident controller and queue state. `nvme_dev` persists for the lifetime of the PCI binding, while controller-visible state includes admin/I/O queue registers, doorbell memory, optional controller memory buffer mappings, and optional host memory buffer descriptors. The driver stores HMB allocations across resets when reusable and tells the controller with `NVME_HOST_MEM_RETURN`; it frees them on teardown or explicit sysfs disable.

Queue state is volatile and recreated during reset. `online_queues`, `queue_count`, `max_qid`, queue flags, CQ phase, SQ/CQ indices, and IRQ vector allocations are reinitialized when queues are created. Shadow doorbell buffers are DMA coherent memory tied to the number of allocated queues; they are zeroed before reuse so stale values are not exposed to a new controller instance.

The module-level dynamic quirk list is persistent until module unload and is freed in `nvme_exit`. Suspend state records `last_ps` to restore a host-managed power state on resume when the driver chooses protocol-level suspend rather than full controller shutdown.

## Dependencies and integration points

This file depends on the NVMe core interfaces in `nvme.h`, tracepoints, blk-mq, blk-integrity, DMA mapping helpers, PCI core, IRQ affinity, P2PDMA, ACPI/DMI quirk detection, kernel PM, and PCI error recovery. It exports no direct application API; it registers a `pci_driver` named `nvme` and uses `nvme_ctrl_ops` plus blk-mq ops as integration surfaces.

The sysfs groups are a composition of generic NVMe attributes from `sysfs.c` and PCI-specific CMB/HMB attributes declared here. Core functions such as `nvme_init_ctrl`, `nvme_init_ctrl_finish`, `nvme_start_ctrl`, `nvme_remove_namespaces`, `nvme_alloc_admin_tag_set`, `nvme_alloc_io_tag_set`, `nvme_complete_rq`, and `nvme_check_ready` define much of the contract.

## Risks and edge cases

- DMA mapping/unmapping is complex. Incorrect `iod` flags, descriptor counts, or failure cleanup can leak DMA mappings, double-free descriptor pool entries, or corrupt device-visible PRP/SGL chains.
- PRP list construction depends on NVMe controller page alignment and bounded descriptor counts. Bad assumptions around segment gaps or maximum transfer size can produce invalid commands.
- Reset paths must coordinate blk-mq freezing, queue quiescing, IRQ freeing, BAR remapping, and PCI disable. Races between timeout, remove, reset, and error recovery are high-risk.
- Doorbell buffer ordering relies on `wmb`/`mb` and controller-side ordering. Relaxing barriers can lose queue notifications.
- CMB and P2PDMA paths depend on BAR alignment, resource sizing, and peer memory support. CMB queue allocation must safely fall back to host memory.
- HMB setup tolerates allocation failure, but reuse and sysfs toggling must keep descriptor memory and controller feature state synchronized.
- Quirk handling is essential for real devices. Changes to quirk masks, queue sizes, MSI behavior, or suspend choices can regress specific SSD and platform combinations.

## Test signals

Useful validation signals include successful module probe and namespace discovery; admin and I/O queue creation counts in logs; blk-mq read/write, discard, write-zeroes, passthrough, and integrity workloads; IRQ and polled I/O completion coverage; suspend/resume across APST and simple-suspend quirked systems; hot remove and PCI AER recovery; reset during active I/O; HMB sysfs enable/disable; CMB presence and fallback; P2PDMA-capable DMA paths; and fault injection around DMA allocation, queue creation, interrupts, and admin command failures.
