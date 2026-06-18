# sources/distributed-fs/ceph-client/drivers/dma/virt-dma.h

## Purpose
`virt-dma.h` is the shared helper interface for virtual dmaengine channels. It defines the channel and descriptor data structures and provides inline operations for descriptor preparation, queue promotion, completion, cyclic callbacks, termination, resource cleanup, and synchronization.

## Important APIs, Types, and Functions
`struct virt_dma_desc` wraps a dmaengine transaction descriptor, a `dmaengine_result`, and a list node protected by the channel lock. `struct virt_dma_chan` embeds `struct dma_chan`, a completion tasklet, a driver-supplied `desc_free` hook, a spinlock, descriptor lists for allocated/submitted/issued/completed/terminated states, and a cyclic descriptor pointer.

The header declares the exported functions implemented in `virt-dma.c` and defines inline helpers: `to_virt_chan`, `vchan_tx_prep`, `vchan_issue_pending`, `vchan_cookie_complete`, `vchan_vdesc_fini`, `vchan_cyclic_callback`, `vchan_terminate_vdesc`, `vchan_next_desc`, `vchan_get_all_descriptors`, `vchan_free_chan_resources`, and `vchan_synchronize`.

## Control Flow and State Model
The state machine is explicit. Prepared descriptors enter `desc_allocated`; submit moves them to `desc_submitted`; `vchan_issue_pending` moves them to `desc_issued`; drivers pull from `desc_issued` with `vchan_next_desc`; completion moves them to `desc_completed`; the tasklet invokes callbacks and either frees or recycles descriptors. Terminated descriptors move to `desc_terminated` and are released during synchronization or resource cleanup.

`vchan_tx_prep` initializes dmaengine descriptor fields, sets the common submit and reusable-free callbacks, initializes result state to `DMA_TRANS_NOERROR`, and appends to the allocated list. `vchan_cookie_complete` must be called with the lock held and schedules callback processing. `vchan_get_all_descriptors` drains all lists into a caller-provided list, which is why terminate and free-resource paths can gather state under lock and free after unlocking.

## Dependencies and Integration Points
The header depends on dmaengine, interrupts/tasklets, and the local dmaengine helper header. It is used across many DMA drivers, including the UniPhier and Xilinx XDMA drivers in this work item.

## Risks and Review Signals
The helper is small but central, so misuse is more likely than internal complexity. Drivers must honor lock requirements, must set `vc->desc_free` before descriptors can be freed, and must not schedule new callbacks while synchronizing. Because `vchan_free_chan_resources` clears reuse on every drained descriptor before freeing, reusable descriptor clients need tests around final release. Review signals include lockdep warnings, list corruption after termination, double completion of cyclic descriptors, and drivers that forget to remove active descriptors from issued state.
