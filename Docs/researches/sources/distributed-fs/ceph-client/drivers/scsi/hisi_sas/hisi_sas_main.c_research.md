# sources/distributed-fs/ceph-client/drivers/scsi/hisi_sas/hisi_sas_main.c

## Purpose

`hisi_sas_main.c` is the common core for HiSilicon SAS HBAs. It implements libsas transport operations, task submission, DMA mapping, PHY/port events, device discovery/removal, error handling and task management, controller reset sequencing, common memory allocation, platform probe/remove, and module-level debugfs/transport registration.

## Important APIs, types, and functions

- ATA/SATA helpers: `hisi_sas_get_ata_protocol()`, `hisi_sas_sata_done()`, `hisi_sas_softreset_ata_disk()`, and ATA reset FIS construction.
- Slot/tag management: `hisi_sas_slot_index_alloc()`, `hisi_sas_slot_task_free()`, and hardware-specific slot-index override support.
- DMA setup: `hisi_sas_dma_map()`, `hisi_sas_dma_unmap()`, `hisi_sas_dif_dma_map()`, and `hisi_sas_dif_dma_unmap()`.
- Submission: `hisi_sas_queue_command()` validates device/port/reset state, chooses a delivery queue, maps data/protection SGs, allocates a slot, and calls `hisi_sas_task_deliver()`.
- Completion synchronization: `hisi_sas_sync_cq()`, `hisi_sas_sync_cqs()`, and poll-queue synchronization.
- Discovery: `hisi_sas_dev_found()`, `hisi_sas_dev_gone()`, `hisi_sas_sdev_init()`, `hisi_sas_sdev_configure()`, scan start/finished callbacks.
- PHY/port handling: `hisi_sas_phy_oob_ready()`, `hisi_sas_notify_phy_event()`, `hisi_sas_phy_enable()`, `hisi_sas_phy_down()`, `hisi_sas_phy_bcast()`, and `hisi_sas_control_phy()`.
- Error handling/TMF: `hisi_sas_abort_task()`, `hisi_sas_abort_task_set()`, `hisi_sas_I_T_nexus_reset()`, `hisi_sas_lu_reset()`, `hisi_sas_clear_nexus_ha()`, and `hisi_sas_query_task()`.
- Reset: `hisi_sas_controller_reset_prepare()`, `hisi_sas_controller_reset_done()`, `hisi_sas_controller_prereset()`, `hisi_sas_controller_reset()`, and reset work handlers.
- Allocation/probe: `hisi_sas_alloc()`, `hisi_sas_free()`, `hisi_sas_get_fw_info()`, `hisi_sas_probe()`, and `hisi_sas_remove()`.

## Control flow

Module initialization attaches a SAS domain transport with `hisi_sas_transport_ops` and optionally creates the top-level debugfs directory. Platform hardware drivers call `hisi_sas_probe()` with their callback table. Probe allocates a SCSI host and `hisi_hba`, reads firmware properties (`sas-addr`, `phy-count`, `queue-count`, and platform reset/syscon properties), maps registers, allocates coherent command/completion/ITCT/IOST/slot buffers, wires libsas phy/port arrays, preinitializes interrupts, registers the SCSI host and SAS HA, runs hardware initialization, and scans.

Task submission enters through libsas `lldd_execute_task`. The driver rejects or waits during reset, verifies device and port state, chooses a blk-mq hardware queue or fallback queue, maps data and protection SGs, allocates a command slot/tag, fills common slot state, links the slot onto delivery and device lists, clears command/status memory, dispatches to a protocol-specific hardware prep callback, marks the slot ready with a memory barrier, and starts hardware delivery.

PHY events are queued onto an ordered workqueue. PHY-up work validates port ID changes, notifies SSP link layer when needed, copies identify/FIS data to libsas, and sends `PORTE_BYTES_DMAED`. PHY-down notifies loss-of-signal, updates port attachment, and ignores transient down events while resetting. Timers handle OOB-ready without PHY-up by scheduling link resets with bounded retries.

Error handling first synchronizes completions to avoid freeing tasks being completed concurrently. SSP aborts issue libsas TMF and internal aborts; SATA aborts abort device state, deregister hardware device state, and often soft-reset the disk; SMP aborts use internal abort and may detach the slot. Controller reset blocks SCSI requests, waits for commands, rejects new commands, performs hardware soft reset, restarts PHYs, refreshes ITCT/port IDs, reinitializes devices, unblocks requests, and rescans topology.

## State and persistence behavior

Driver state persists in `struct hisi_hba`: queue pointers, slots, device table, phys, ports, DMA tables, flags, workqueue, timers, and debugfs configuration. Each in-flight task persists as a `struct hisi_sas_slot` until completion, abort, release, or reset. Slot indexes below `HISI_SAS_RESERVED_IPTT` are reserved for internal/non-request operations unless hardware supplies its own allocator; request-backed IO uses blk-mq tags offset by the reserved range. Hardware-visible state persists in coherent command headers, completion headers, ITCT, IOST, FIS, breakpoint, status, and SGE buffers.

## Dependencies and integration points

The file integrates deeply with libsas (`sas_domain_function_template`), libata, SCSI midlayer, blk-mq, DMA mapping, platform firmware properties, syscon/regmap, clocks, runtime PM, async domains, debugfs, and hardware-specific HiSilicon callback implementations. Exported symbols are used by `hisi_sas_v1_hw.c`, `hisi_sas_v2_hw.c`, and `hisi_sas_v3_hw.c`.

## Risks and edge cases

- Reset and device-gone paths coordinate through `sem`, flags, workqueue, timers, and completion synchronization; missed ordering can race command submission or task freeing.
- `hisi_sas_debug_I_T_nexus_reset()` calls `sas_put_local_phy(local_phy)` before later checking `scsi_is_sas_phy_local(local_phy)` and using `local_phy->number`, which is a use-after-put pattern worth review.
- `hisi_sas_slot_task_free()` returns early if `task->lldd_task` is already NULL, which can skip slot cleanup when callers pass a slot with a cleared task pointer.
- DMA mapping error labels note that direct `dma_unmap_sg()` would be better but messy; SG mapping/unmapping paths deserve stress testing.
- `hisi_sas_alloc_dev()` loop control mutates `i` both in the `for` expression and inside the loop, which is unusual and should be checked for full table coverage.
- Reset failure paths must clear reject/reset flags and unblock SCSI requests; the code handles the main soft-reset failure path, but hardware callback failures elsewhere need validation.

## Test signals

High-value tests include boot/probe/remove for platform and PCI hardware versions, libsas discovery with direct SAS, SATA, and expander devices, blk-mq multi-queue submission, DIF/DIX IO, SMP requests with 4-byte alignment checks, IO aborts, LU reset, I_T nexus reset, host reset, device removal during IO, PHY flap/link-reset timers, runtime PM PHY-up work, debugfs register snapshots on timeout, and fault injection for DMA mapping, queue full, hardware fault, and soft reset failure.
