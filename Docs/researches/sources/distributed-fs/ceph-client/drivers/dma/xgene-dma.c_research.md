# sources/distributed-fs/ceph-client/drivers/dma/xgene-dma.c

## Purpose
`xgene-dma.c` is the Applied Micro X-Gene SoC DMA engine driver. Its exposed dmaengine functionality is focused on async_tx RAID offload, specifically XOR and PQ generation, rather than generic memcpy or slave DMA.

## Important APIs, Types, and Functions
Important hardware/software types are `struct xgene_dma_desc_hw`, `struct xgene_dma_desc_sw`, `struct xgene_dma_ring`, `struct xgene_dma_chan`, and `struct xgene_dma`. Descriptor helpers include `xgene_dma_init_desc`, `xgene_dma_set_src_buffer`, `xgene_dma_lookup_ext8`, `xgene_dma_prep_xor_desc`, `xgene_dma_prep_xor`, and `xgene_dma_prep_pq`. Queue and completion paths include `xgene_dma_tx_submit`, `xgene_chan_xfer_request`, `xgene_chan_xfer_ld_pending`, `xgene_dma_cleanup_descriptors`, `xgene_dma_run_tx_complete_actions`, and `xgene_dma_clean_running_descriptor`. Hardware setup functions include ring creation/deletion, interrupt setup, memory bring-up, and async registration.

## Control Flow
Probe maps four MMIO regions: DMA CSR, ring CSR, ring command CSR, and efuse CSR. It optionally enables a clock, brings ring-manager and DMA RAM out of shutdown, sets a 42-bit coherent DMA mask, initializes channel software state, allocates per-channel TX/RX hardware rings, requests one error IRQ and one RX-ring IRQ per channel, enables the DMA engine, and registers one dmaengine device per hardware channel.

Capabilities are selected per channel. Channel 1 exposes PQ and XOR if PQ is enabled by efuse. Channel 0 exposes XOR only when PQ is disabled, avoiding a documented hardware hang when channel 0 and channel 1 run XOR/PQ simultaneously. Prep functions allocate software descriptors from a DMA pool, build one or two hardware descriptors per request chunk, and chain all chunk descriptors through the returned descriptor's `tx_list`. XOR/PQ transfers are split into chunks no larger than the hardware buffer length.

Submit assigns a cookie only to the client-visible descriptor and splices the descriptor group into `ld_pending`. `issue_pending` pushes pending descriptors to the TX hardware ring until `max_outstanding` is reached. The hardware reports completions through RX rings initialized with an empty signature. The channel ISR disables the RX IRQ and schedules a tasklet. The tasklet cleans completed RX descriptors, reports descriptor-level errors, notifies hardware that completions were consumed, decrements pending counts, starts more pending work, invokes callbacks, completes cookies, runs dependencies, and frees or parks descriptors depending on async ACK state.

## State and Persistence
Runtime state lives in ring head pointers, ring descriptors, `pending`, `max_outstanding`, and three descriptor lists: `ld_pending`, `ld_running`, and `ld_completed`. There is no persistent state. Remove unregisters dmaengine devices, masks interrupts, disables hardware, frees IRQs, kills tasklets, deletes rings, and disables the clock.

## Dependencies and Integration Points
The driver supports OF compatible `apm,xgene-storm-dma` and ACPI id `APMC0D43`. It depends on dmaengine async_tx XOR/PQ APIs, DMA pools, coherent ring allocation, platform resources, IRQ APIs, optional clocks, and efuse state.

## Risks and Review Signals
The descriptor error status indexes into sparse error string arrays; unexpected status values could produce invalid lookup if not constrained by hardware. IRQ cleanup has a suspicious loop in the request-error path that assigns `chan = &pdma->chan[i]` inside a `for (j = 0; j < i; j++)`, likely freeing the wrong channel repeatedly. Descriptor grouping relies on only the last descriptor having the client cookie. Tests should cover PQ efuse-enabled and disabled systems, max outstanding ring pressure, 64-byte descriptor paths, completion error descriptors, IRQ request failure unwinding, async ACK delayed freeing, and probe/remove after partial setup failure.
