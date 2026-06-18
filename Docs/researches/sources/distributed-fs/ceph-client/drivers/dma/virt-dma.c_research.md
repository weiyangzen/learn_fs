# sources/distributed-fs/ceph-client/drivers/dma/virt-dma.c

## Purpose
`virt-dma.c` implements the exported non-inline parts of the dmaengine virtual channel helper. It centralizes cookie submission, descriptor lookup, callback/tasklet completion, descriptor freeing, and channel initialization for DMA drivers that want common list and callback handling while programming their own hardware.

## Important APIs, Types, and Functions
The file operates on `struct virt_dma_chan` and `struct virt_dma_desc` from `virt-dma.h`. Exported functions are `vchan_tx_submit`, `vchan_tx_desc_free`, `vchan_find_desc`, `vchan_dma_desc_free_list`, and `vchan_init`. The internal `vchan_complete` tasklet drains completed descriptors and cyclic callbacks.

## Control Flow
Drivers allocate a descriptor embedding `struct virt_dma_desc`, call `vchan_tx_prep` from the header, and later the dmaengine core invokes `vchan_tx_submit`. `vchan_tx_submit` locks the virtual channel, assigns a cookie, and moves the descriptor from `desc_allocated` to `desc_submitted`. Driver `issue_pending` hooks call `vchan_issue_pending` to move submitted work to `desc_issued`, then program hardware from `vchan_next_desc`.

When hardware completes a descriptor, the driver calls `vchan_cookie_complete`, which completes the cookie, moves the descriptor to `desc_completed`, and schedules `vc->task`. `vchan_complete` splices completed descriptors locally, snapshots a pending cyclic callback if present, releases the lock, invokes callbacks, and finalizes each completed descriptor with `vchan_vdesc_fini`. Descriptor finalization either returns reusable descriptors to `desc_allocated` or calls the driver's `desc_free` hook. `vchan_tx_desc_free` supports explicit freeing of reusable descriptors by removing the descriptor from whatever list it is on and invoking `desc_free`.

## State and Persistence
All state is per-channel and volatile: five descriptor lists, one cyclic callback pointer, a spinlock, and a tasklet. The helper does not store hardware state. `vchan_init` initializes cookies, lock, lists, tasklet, connects the channel to the dma_device, and appends it to the device channel list.

## Dependencies and Integration Points
This file exports GPL-only symbols and is used by many dmaengine drivers. It depends on dmaengine callback helpers, tasklets, spinlocks, list APIs, and the local `dmaengine.h` wrapper. Its contract requires most list operations to be performed under `vc->lock`, with callbacks invoked outside the lock by the helper tasklet.

## Risks and Review Signals
Drivers must remove an issued descriptor from `desc_issued` before or as part of completion when their hardware model requires it; the helper does not infer hardware progress. `vchan_find_desc` only searches `desc_issued`, so residue/status support for active descriptors must be compatible with that list model. `vchan_synchronize` kills the tasklet and frees terminated cyclic descriptors, so callers must prevent new callbacks before invoking it. Tests should cover descriptor reuse, cyclic callback ordering, terminate followed by synchronize, explicit reusable descriptor free, and lockdep expectations around helper calls.
