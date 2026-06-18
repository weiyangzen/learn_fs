# sources/distributed-fs/ceph-client/drivers/dma/ti/cppi41.c

## Purpose
This driver provides DMAengine support for TI CPPI 4.1 DMA, primarily used by USB on AM335x and DA8xx platforms. It configures the CPPI DMA scheduler, queue manager, packet descriptors, completion queues, and teardown flow.

## Important APIs, Types, and Functions
Core types are `struct cppi41_dd`, `struct cppi41_channel`, `struct cppi41_desc`, `struct chan_queues`, and `struct cppi_glue_infos`. DMAengine entry points are `cppi41_dma_alloc_chan_resources()`, `cppi41_dma_free_chan_resources()`, `cppi41_dma_prep_slave_sg()`, `cppi41_dma_issue_pending()`, `cppi41_dma_tx_status()`, and `cppi41_stop_chan()`. Hardware setup and teardown are handled by `init_cppi41()`, `init_descs()`, `init_sched()`, `deinit_cppi41()`, and `cppi41_tear_down_chan()`. OF translation uses `cppi41_dma_xlate()` plus `cpp41_dma_filter_fn()`.

## Control Flow
Probe reads platform glue data from the compatible string, maps controller/scheduler/queue-manager resources, enables runtime PM, initializes queue-manager scratch and coherent descriptors, builds RX/TX channel objects, registers the shared IRQ, registers DMAengine, and registers OF DMA translation. A client requests a channel with a two-cell specifier: USB port and RX/TX direction. Preparation fills a host packet descriptor from the first SG entry. `issue_pending()` adds the channel to a controller pending list, and `cppi41_run_queue()` pushes descriptors into hardware queues if not runtime-suspended. The IRQ scans pending completion queues, pops descriptors, maps them back through `chan_busy[]`, computes residue, completes the cookie, and invokes callbacks.

## State and Persistence
Persistent runtime state includes coherent descriptor memory, queue-manager scratch memory, pending software queue, per-channel queue numbers, busy descriptor map, teardown flags, saved `DMA_TDFDQ`, and runtime suspend flag. Runtime PM references are deliberately held while descriptors are in `chan_busy[]` to prevent autosuspend during long USB transfers. System suspend saves teardown queue configuration and disables the scheduler; resume restores queue-manager memory base, scheduler, RX completion queue routing, scratch, and teardown queue.

## Dependencies and Integration Points
The driver depends on DMAengine, OF DMA, platform resources, IRQs, coherent DMA memory, runtime PM, raw MMIO, and USB/MUSB-style clients. Platform glue supplies queue numbering differences between AM335x and DA8xx. Device tree must provide `reg-names`, `dma-channels` or deprecated `#dma-channels`, and an interrupt.

## Risks
The implementation supports only one descriptor per channel despite iterating SG entries; true SG requires client/controller support beyond current use. The queue-manager and teardown paths are timing-sensitive and contain retry logic. Raw MMIO requires explicit barriers before pushing descriptors. Runtime-suspend interactions are subtle: pending transfers are held while suspended and completion IRQs warn if observed during suspend. Queue table bounds currently use AM335x array size in the filter, so platform-specific queue array size assumptions matter.

## Test Signals
Test with USB RX/TX traffic on AM335x and DA8xx, runtime autosuspend during long mass-storage transfers, channel terminate while active and while pending, shared IRQ completion, zero-length packet descriptors, residue reporting, DT xlate/filter selection, and system suspend/resume. Fault injection should cover allocation failure for coherent descriptors/scratch and invalid `dma-channels` or `reg-names`.
