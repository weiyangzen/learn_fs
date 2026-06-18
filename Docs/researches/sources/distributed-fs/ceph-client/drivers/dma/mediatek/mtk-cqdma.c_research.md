<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-cqdma.c -->
# sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-cqdma.c

## Purpose
DMAEngine driver for MediaTek Command-Queue DMA controllers used for memory-to-memory copies. It exposes many virtual DMA channels over a smaller set of physical command-queue engines.

## Important APIs, Types, And Functions
Core state is split into `struct mtk_cqdma_device`, `struct mtk_cqdma_vchan`, `struct mtk_cqdma_pchan`, and `struct mtk_cqdma_vdesc`. Register helpers `mtk_dma_read/write/rmw/set/clr` isolate MMIO access. `mtk_cqdma_prep_dma_memcpy` splits large copies into parent/child descriptors capped by `MTK_CQDMA_MAX_LEN`. `mtk_cqdma_issue_pending`, `mtk_cqdma_start`, `mtk_cqdma_irq`, and `mtk_cqdma_tasklet_cb` move work from vchan lists to physical queues and complete it. Resource hooks allocate/free physical channels by reference count, and probe/remove register the DMAEngine and OF DMA controller.

## Control Flow
Probe allocates the device, reads `dma-requests` and `dma-channels` with defaults, maps one resource and IRQ per physical channel, initializes virtual channels, registers the DMA device and OF xlate, enables clocks/runtime PM, resets physical channels, and creates per-PC tasklets. A memcpy request becomes one or more CVDs linked by `tx->next`; issue-pending moves issued vdesc entries onto the chosen physical channel queue. If the queue was empty, `mtk_cqdma_start` programs source/destination low and high registers, length registers, interrupt enable, and engine enable. IRQ clears the per-PC interrupt flag, disables that IRQ, and schedules a tasklet. The tasklet consumes one queued child descriptor, subtracts parent residue, completes the parent only after all children finish, starts the next queued child, runs dependencies, frees child descriptors, and reenables the IRQ.

## State And Persistence
Persistent runtime state includes each VC's current PC assignment, completion object, synchronization flag, each PC's queue/refcount/tasklet/lock, descriptor residues, and hardware registers. Clocks and runtime PM are enabled for the driver lifetime. No filesystem persistence exists.

## Dependencies And Integration Points
Depends on DMAEngine, `virt-dma`, platform resources, device tree `dma-requests`/`dma-channels`, `of_dma_xlate_by_chan_id`, clocks, IRQs, and runtime PM. It advertises `DMA_MEMCPY`, 4-byte widths, memory-to-memory direction, and segment residue granularity. CQDMA Kconfig also selects async_tx channel switching for dependencies.

## Risks And Edge Cases
`kzalloc_objs(*cvd, nr_vd, GFP_NOWAIT)` allocates an array of pointers; any allocation failure after `cvd` itself leaks that pointer array, and the function does not free the array after successful descriptor creation. Parent/child lifetime is subtle because only children are explicitly freed in the tasklet and the parent is freed by `desc_free`. Termination cannot abort a hardware-active transfer immediately; it waits for active VC completion. IRQ disabling/enabling per PC must stay paired with tasklet cleanup. Device-tree `dma-channels` controls both resource count and IRQ count, so binding/resource mismatches fail probe.

## Test Signals
Use dmatest memcpy on supported MediaTek CQDMA hardware for short and >`MTK_CQDMA_MAX_LEN` transfers, verify residues during active transfers, test multiple VCs sharing PCs, terminate while active, and remove with pending IRQs. Fault-injection around allocation and missing `dma-requests`/`dma-channels` properties should exercise defaults and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/dma/mediatek/mtk-cqdma.c -->
