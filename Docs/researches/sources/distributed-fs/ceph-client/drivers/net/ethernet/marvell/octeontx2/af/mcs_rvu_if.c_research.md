# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/mcs_rvu_if.c

## Purpose

`mcs_rvu_if.c` is the RVU mailbox bridge for the MCS MACsec driver. It exposes MCS hardware operations to PF/VF clients through AF mailbox handlers, handles asynchronous MCS interrupt notification back to PF/VF drivers, configures PTP/custom-header parsing interactions with RPM/CGX ports, initializes MCS state during RVU bring-up, and releases MCS resources during FLR and RVU teardown.

## Important APIs, Types, And Functions

The `MBOX_UP_MCS_MESSAGES` macro expansion builds upward mailbox allocators such as `otx2_mbox_alloc_msg_mcs_intr_notify()`. `rvu_mcs_ptp_cfg()` toggles parser skip behavior when RPM adds an 8-byte PTP header.

Async notification is implemented by `mcs_add_intr_wq_entry()`, `mcs_notify_pfvf()`, and `mcs_intr_handler_task()`. Events are masked by each PF/VF `intr_mask`, queued under `rvu->mcs_intrq_lock`, and sent on `rvu->afpf_wq_info.mbox_up` under `rvu->mbox_lock`.

Mailbox handlers cover interrupt config, hardware info, LMAC mode, port reset, stats get/clear, active LMAC bitmap, port config get/set, custom tag config get, flow ID enable, PN table writes, PN threshold set, RX/TX SA map writes, SA policy writes, RX SC CAM writes, SecY policy writes, flow TCAM writes, resource allocation/free, control packet rule allocation/free/write, FLR cleanup, init, and exit.

## Control Flow

RVU initialization calls `rvu_mcs_init()`, which discovers MCS block count via `mcs_get_blkcnt()`. For single-block CN10KB it programs LMAC channel bases and derives the active LMAC bitmap from CGX/RPM validity. For every MCS block it installs the default bypass entry, sets every LMAC to operational mode, stores the RVU back pointer, allocates PF and VF interrupt-mask arrays, and creates the MCS interrupt workqueue.

Mailbox handlers follow a common pattern: validate `req->mcs_id < rvu->mcs_blk_cnt`, fetch the block with `mcs_get_pdata()`, optionally validate port/Lmac/resource ownership, lock `rvu->rsrc_lock` for resource allocation/free or `mcs->stats_lock` for stats reads/clears, then delegate to `mcs.c` or `mcs_ops` functions. CNF10KB stats handlers set force-clock before reads and clear it afterward.

Resource allocation can allocate one resource type repeatedly or a full bundle of flow, SecY, SC, and two SA resources. Freeing can release one resource or all resources owned by the requester's `pcifunc`. FLR cleanup iterates all MCS blocks on CNF10KB and both directions, freeing resources for the reset function.

Interrupt notification starts in the hardware IRQ handler in `mcs.c`, which calls `mcs_add_intr_wq_entry()`. This bridge identifies PF versus VF from `pcifunc`, masks the event, queues it, and the workqueue sends an upward mailbox message to the PF that owns the function.

## State And Persistence Behavior

This file mutates RVU-owned process state: `rvu->mcs_blk_cnt`, `rvu->mcs_intrq_head`, `rvu->mcs_intr_work`, `rvu->mcs_intr_wq`, and each MCS block's `rvu`, `pf`, and `vf` pointers. It also mutates per-PF/VF interrupt masks and active LMAC bitmaps.

Mailbox operations persist by programming MCS hardware state through `mcs.c`. FLR cleanup removes the software ownership state and disables associated hardware entries. `rvu_mcs_exit()` destroys the interrupt workqueue, but PCI remove is handled by the lower MCS driver.

## Dependencies And Integration Points

The file depends on RVU core structures and locks, AF/PF mailbox helpers, `rvu_get_pf()`, `rvu_get_hwvf()`, CGX/RPM LMAC discovery through `lmac_common.h`, MCS core helpers, and register macros for the PTP parser adjustments. It is the main integration point between PF/VF MACsec clients and the physical MCS blocks.

## Risks

Several write handlers validate only `mcs_id` and then program hardware resource IDs supplied by the caller. Ownership is enforced on free, but direct writes to flow ID, SecY, SC, SA, and PN state rely on higher-level request discipline. `rvu_mbox_handler_mcs_alloc_resources()` logs allocation failure but returns 0, so callers must inspect response counts/IDs rather than only the mailbox return code.

`rvu_mcs_set_lmac_bmap()` declares `lmac_bmap` without an explicit zero initializer before setting bits, which risks stale stack bits becoming active LMACs. `mcs_add_intr_wq_entry()` indexes PF/VF interrupt arrays based on `pcifunc`; invalid or stale mappings would corrupt notification routing. Workqueue destruction does not explicitly drain the queue in this file, so teardown ordering must ensure no MCS IRQs can enqueue after `rvu_mcs_exit()`.

## Test Signals

Useful signals include mailbox ABI tests for every handler, invalid MCS ID rejection, invalid/inactive port rejection, PF/VF-specific interrupt mask filtering, upward interrupt notification contents for SA ID and LMAC ID, allocation/free/allocation reuse under `rvu->rsrc_lock`, FLR releasing both RX and TX resources, stats reads on CNF10KB with force-clock toggling, PTP enable/disable changing the expected parser skip register, and no workqueue use-after-free during RVU shutdown.
