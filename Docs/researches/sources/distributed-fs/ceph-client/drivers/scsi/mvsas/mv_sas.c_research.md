# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_sas.c

## Purpose

`mv_sas.c` is the core libsas low-level driver implementation for Marvell 88SE64xx/88SE94xx SAS/SATA HBAs. It translates libsas `sas_task` work into hardware command slots, manages PHY and port notifications, owns device-private allocation and teardown, handles task management and error recovery, and drains RX completion/attention events from the controller. It is intentionally chip-family-neutral: hardware differences are routed through the `mvs_dispatch` table defined in `mv_sas.h` and implemented by the 64xx/94xx backend files.

## Important APIs, Types, and Functions

- `mvs_queue_command()` is the libsas queue entry. It locates the per-controller `struct mvs_info`, prepares a hardware slot with `mvs_task_prep()`, and starts delivery through `MVS_CHIP_DISP->start_delivery()`.
- `mvs_task_prep()`, `mvs_task_prep_smp()`, `mvs_task_prep_ssp()`, and `mvs_task_prep_ata()` build command headers, open address frames, PRD tables, DMA mappings, response buffers, and TX ring descriptors for SMP, SSP, SATA, and STP tasks.
- `mvs_slot_complete()` is the main completion path. It interprets RX descriptors, fills libsas task status, copies SMP responses, handles ATA D2H FIS responses, frees DMA/slot state, drops device running counts, and invokes `task_done`.
- `mvs_int_rx()` drains the RX ring and dispatches completions, errors, slot resets, and attention interrupts.
- `mvs_int_port()`, `mvs_update_phyinfo()`, `mvs_bytes_dmaed()`, `mvs_work_queue()`, and `mvs_sig_time_out()` implement hotplug, OOB completion, SATA signature waits, broadcast-change notifications, and PHY loss/recovery.
- `mvs_dev_found()`, `mvs_dev_gone()`, `mvs_port_formed()`, and `mvs_port_deformed()` are the libsas discovery callbacks that bind/unbind `domain_device` and `asd_sas_port` objects to driver-private `mvs_device` and `mvs_port` records.
- `mvs_abort_task()`, `mvs_query_task()`, `mvs_lu_reset()`, and `mvs_I_T_nexus_reset()` provide SAM task management and error-handler reset behavior.
- Tag helpers `mvs_tag_alloc()`, `mvs_tag_free()`, `mvs_find_tag()`, and slot helpers `mvs_slot_task_free()` coordinate reserved internal tags, blk-mq request tags, DMA pool buffers, and `task->lldd_task`.

## Control Flow

Normal I/O starts in libsas, enters `mvs_queue_command()`, and runs under `mvi->lock`. `mvs_task_prep()` validates port/device presence, maps SGLs for non-ATA tasks, chooses either a request tag plus `MVS_RSVD_SLOTS` or a reserved bitmap tag, allocates a DMA slot buffer, then calls the protocol-specific builder. The builders write one TX ring entry and one command header; the shared caller links the slot onto the port list, attaches `task->lldd_task`, increments `mvi_dev->running_req`, advances `tx_prod`, and the queue entry kicks the hardware.

Completion runs from interrupt context through `mvs_int_rx()`. The first RX dword mirrors the hardware producer; if it does not change the driver falls back to `rx_update()`. Each descriptor triggers `mvs_slot_complete()` for DONE or ERR cases. Completion marks the task done under `task_state_lock`, handles aborted tasks specially, maps RX flags/protocol-specific status into libsas status, decrements `running_req`, frees SATA register sets when the last ATA request drains, releases DMA resources, drops the HBA lock around the upper-layer callback, and then reacquires it.

Hotplug enters through per-PHY interrupts in `mvs_int_port()`. POOF/loss events release outstanding tasks, clear SRS interrupts, and schedule delayed work. COMWAKE starts a SATA signature timer. SIG_FIS or ID_DONE causes port type detection, PHY info repair, optional SAS PHY tuning, byte-DMA notification to libsas, and port-formed notification if the event followed a plug-out. Broadcast changes are converted to libsas port events through delayed work.

Error handling combines hardware slot errors and libsas TMFs. `mvs_slot_err()` inspects the error dwords in the slot response buffer, issues stop/active commands through dispatch hooks, fabricates SSP sense for no-destination cases, and maps SATA/STP failures to protocol responses. Abort/query/LU/I_T reset paths invoke libsas helpers with driver tags and then release local slot state.

## State and Persistence Behavior

Runtime state is in `struct mvs_info`: TX/RX rings, RX FIS area, command headers, slot array, reserved-tag bitmap, per-PHY/port/device tables, workqueue list, and chip dispatch pointer. This file does not persist configuration to disk or firmware; it only reads/writes device MMIO through dispatch hooks and consumes HBA info that other code initializes. Device state persists for the lifetime of libsas discovery objects via `dev->lldd_dev`, `sas_port->lldd_port`, `sas_phy->lldd_phy`, and `task->lldd_task`.

SATA register-set assignment is persistent per attached `mvs_device` while ATA requests are outstanding. `mvs_assign_reg_set()` lazily assigns taskfile sets; `mvs_slot_complete()` frees them only after `running_req` reaches zero, and device removal frees them unconditionally. Timers and delayed work hold transient PHY-event state and must be canceled or made harmless by state checks.

## Dependencies and Integration Points

The file depends heavily on libsas (`sas_task`, `domain_device`, `sas_notify_*`, `sas_abort_task`, `sas_lu_reset`, `sas_phy_reset`, `sas_drain_work`), libata for NCQ tags, the SCSI midlayer through libsas, PCI/DMA APIs, kernel timers/workqueues, and Marvell register definitions from `mv_defs.h`. Hardware-specific operations are abstracted through `MVS_CHIP_DISP`, including PRD layout, register-set allocation, interrupt clearing, PHY operations, RX producer reads, DMA workarounds, and GPIO writes.

Chip backends, probe code, and headers must initialize `mvi->chip`, DMA pools, rings, PHY tables, locks, and libsas callback registration correctly before these paths run. `mvs_scan_start()` and `mvs_scan_finished()` integrate with the SCSI scan lifecycle by synthesizing byte-DMA events on all PHYs and draining libsas work before reporting completion.

## Risks and Edge Cases

- Locking is subtle: `mvs_slot_complete()` intentionally drops `mvi->lock` around `task_done()`. Any caller must tolerate slot/task state changing around that callback.
- `task->lldd_task`, port lists, and device removal can race with abort/completion/hotplug paths. The code uses locks and task state flags, but stale slot pointers remain a high-risk area.
- `mvs_find_dev_mvi()` and related PHY lookup loops assume libsas arrays are populated and terminated as expected; invalid topology state could lead to wrong HBA selection.
- SMP response copying uses `kmap_atomic()` and copies `sg_dma_len()` bytes from the slot response; response length mismatches or malformed hardware data are important test cases.
- ATA/STP NCQ handling mutates the FIS sector count and uses libata `ata_queued_cmd` tags. Incorrect tag mapping can corrupt NCQ completion association.
- Delayed hotplug work allocates with `GFP_ATOMIC`; allocation failure silently drops event handling except for returning `-ENOMEM`.
- Timer function presence is used as an active flag for SATA signature timeout. That pattern is fragile if timer lifecycle rules change.

## Test Signals

Useful validation signals include successful SAS and SATA discovery, wide-port formation/deformation, SMP expander management, SSP read/write, SATA NCQ read/write, ATAPI command paths, broadcast-change rescans, link flap while I/O is outstanding, abort and LU/I_T reset recovery, RX descriptor error injection, DMA mapping failure handling, and controller removal while delayed PHY work or signature timers are pending. Kernel logs should show expected PHY attach/remove messages without leaked tasks, repeated "reuse same slot" reports, DMA API warnings, or libsas task timeouts.
