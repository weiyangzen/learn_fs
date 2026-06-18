# sources/distributed-fs/ceph-client/crypto/async_tx/async_pq.c

Purpose: implements asynchronous RAID6 P/Q syndrome generation and validation with DMA PQ offload and synchronous software fallback.

Important APIs/types/functions: global `pq_scribble_page` provides temporary P/Q storage for sync generation when one destination is omitted. `do_async_gen_syndrome()` chunks source lists according to DMA engine `dma_maxpq()` and chains descriptors. `do_sync_gen_syndrome()` calls RAID6 software syndrome routines. `async_gen_syndrome()` generates P and/or Q. `async_syndrome_val()` validates existing P/Q against recomputed values. `pq_val_chan()` optionally disables validation DMA.

Control flow: generation collapses NULL data sources, maps sources and P/Q destinations, sets `DMA_PREP_PQ_DISABLE_P/Q` when one destination is absent, and chains PQ operations if the engine cannot handle all sources at once. Sync fallback waits dependencies, substitutes zero pages and scribble destinations, then calls RAID6 software. Validation either submits `device_prep_dma_pq_val()` or recomputes P and Q into a spare page and compares.

State and persistence: `pq_scribble_page` is allocated at module init and freed at exit. Operations modify P/Q destination pages and `pqres` validation flags. DMA descriptor state is transient.

Dependencies and integration points: depends on DMA engine PQ/PQ_VAL capabilities, RAID6 tables and calls, async_tx core, async_xor helpers, and page-addressable buffers.

Risks: NULL P/Q handling is subtle; callers may omit either but not both. DMA engines differ in max source and continue support, so descriptor chaining must preserve flags and callbacks. Sync validation requires caller-provided spare and scribble buffers. `BUG_ON()` input checks can panic on invalid RAID callers.

Test signals: generation with P only, Q only, both, NULL data sources, engines with limited `dma_maxpq`, sync fallback, validation success/failure flags, disabled PQ_VAL DMA, and module init failure to allocate scribble page.
