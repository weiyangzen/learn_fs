# sources/distributed-fs/ceph-client/include/linux/shdma-base.h

## Purpose

`shdma-base.h` defines the common dmaengine base library contract for SH-based DMA controllers. Controller-specific drivers embed these base structs and implement `struct shdma_ops` so generic queueing, channel management, IRQ request, init, cleanup, and filtering can be shared.

## Important APIs, Types, And Functions

Types include `enum shdma_pm_state`, `struct shdma_slave`, `struct shdma_desc`, `struct shdma_chan`, `struct shdma_ops`, and `struct shdma_dev`. `struct shdma_desc` embeds `dma_async_tx_descriptor`, transfer direction, partial byte count, cookie, chunk count, mark, and cyclic flag. `struct shdma_chan` keeps channel lock, queued and free descriptor lists, embedded `dma_chan`, device pointer, descriptor storage, max transfer length, raw channel ID, IRQ, slave IDs, hardware request line, and PM state.

`struct shdma_ops` supplies controller-specific callbacks for descriptor completion, halting, busy checks, slave address, descriptor setup, slave binding, transfer setup, start, embedded descriptor lookup, IRQ handling, and partial progress. APIs include `shdma_request_irq()`, `shdma_reset()`, `shdma_chan_probe()`, `shdma_chan_remove()`, `shdma_init()`, `shdma_cleanup()`, and conditional `shdma_chan_filter()`. The `shdma_for_each_chan()` macro iterates channels.

## Control Flow

A controller driver allocates and embeds `shdma_dev`/`shdma_chan`, fills `shdma_ops`, initializes channels with `shdma_init()` and `shdma_chan_probe()`, requests IRQs, and services transfers through dmaengine callbacks. Transfer preparation may move PM state through busy and pending phases. IRQ handlers call the controller `chan_irq()` hook and mark descriptors complete. Cleanup removes channels and frees shared state.

## State And Persistence

Persistent runtime state includes descriptor queues, descriptor pools, channel locks, DMA cookies, cyclic flags, partial progress, PM state, and controller operation pointers. Hardware state is controlled by implementation callbacks.

## Dependencies And Integration Points

Dependencies include dmaengine, interrupt handling, list management, and fixed-width types. Integration points are controller-specific SH DMA drivers, platform-specific `sh_dma.h` data, dmaengine clients, IRQ core, and DMA channel filtering for slave requests.

## Risks And Test Signals

Risks include descriptor queue corruption, incorrect PM state transitions when locks are dropped, partial progress misreporting, channel filter mismatches, and IRQ completion races. Test signals include dmaengine async memcpy/slave transfers, cyclic transfers, terminate/reset paths, interrupt storms, descriptor reuse, residue reporting, and disabled `CONFIG_SH_DMAE_BASE` builds where filtering returns false.
