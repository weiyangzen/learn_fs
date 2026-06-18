# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/tdma.c Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/tdma.c

### Purpose
`tdma.c` provides CESA TDMA descriptor-chain helpers shared by cipher and hash implementations. It builds DMA descriptor lists, prepares SRAM-relative addresses for a selected engine, launches hardware TDMA execution, processes completed request boundaries, and frees descriptor resources.

### Important APIs, Types, And Functions
Key entry points are `mv_cesa_req_dma_iter_next_transfer()`, `mv_cesa_dma_step()`, `mv_cesa_dma_cleanup()`, `mv_cesa_dma_prepare()`, `mv_cesa_tdma_chain()`, `mv_cesa_tdma_process()`, `mv_cesa_dma_add_result_op()`, `mv_cesa_dma_add_op()`, `mv_cesa_dma_add_data_transfer()`, `mv_cesa_dma_add_dummy_launch()`, `mv_cesa_dma_add_dummy_end()`, `mv_cesa_dma_add_op_transfers()`, and `mv_cesa_sg_copy()`. It manipulates `struct mv_cesa_tdma_chain`, `struct mv_cesa_tdma_desc`, engine software/hardware chain pointers, TDMA flags such as `CESA_TDMA_OP`, `CESA_TDMA_DATA`, `CESA_TDMA_RESULT`, `CESA_TDMA_END_OF_REQ`, `CESA_TDMA_BREAK_CHAIN`, and SRAM source/destination markers.

### Control Flow, State, And Persistence
Descriptor builders append zeroed descriptors from the TDMA pool, link `next` and `next_dma`, and attach op contexts or data moves. `mv_cesa_dma_prepare()` converts SRAM-relative offsets to engine-specific DMA addresses and adjusts op contexts for the engine. `mv_cesa_tdma_chain()` appends a request to the engine software chain unless the next request must reload state or the previous request breaks the chain. `mv_cesa_dma_step()` promotes the prepared request to the hardware chain, programs TDMA control and next address registers, and starts CESA. `mv_cesa_tdma_process()` walks hardware descriptors until the current hardware pointer or an incomplete request, dequeues logical crypto requests at `END_OF_REQ`, invokes request-specific `process` and `complete`, queues completed requests, and preserves a failed request in `engine->req`.

### Dependencies, Integration Points, Risks, And Test Signals
The file depends on CESA DMA pools, engine locks, request queues, crypto async request completion, SG mapping iterators, and low-level CESA TDMA/SA registers. Risks include chain pointer races under `engine->lock`, freeing op DMA pools only for `CESA_TDMA_OP`, correctly re-chaining after each logical request, not missing the hardware current descriptor, and SG iterator offset math across scatterlist boundaries. Test signals include chained cipher/hash requests, state-reload chain breaks, result-copy descriptors, SG lists with more than one segment, forced descriptor allocation failure, TDMA interrupt processing with backlog completion, and noncoherent SRAM copy paths.
