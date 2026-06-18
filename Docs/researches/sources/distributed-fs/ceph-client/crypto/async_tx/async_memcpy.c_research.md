# sources/distributed-fs/ceph-client/crypto/async_tx/async_memcpy.c

Purpose: implements `async_memcpy()`, an async_tx memory copy helper that uses DMA engine offload when possible and falls back to synchronous CPU copy.

Important APIs/types/functions: `async_memcpy()` finds a `DMA_MEMCPY` channel with `async_tx_find_channel()`, allocates `dmaengine_unmap_data`, maps source and destination pages, prepares `device_prep_dma_memcpy()`, submits with `async_tx_submit()`, or performs a `kmap_atomic()`/`memcpy()` fallback. It exports the symbol for RAID and other async_tx users.

Control flow: if a DMA channel exists, unmap data allocates, and offsets/length are DMA-aligned, it prepares and submits an async descriptor with interrupt/fence flags as requested. Otherwise it waits for `submit->depend_tx`, maps pages atomically, copies bytes, unmaps, and runs `async_tx_sync_epilog()`.

State and persistence: DMA descriptors and unmap data live until descriptor completion; synchronous state is temporary. Page contents are modified at the destination.

Dependencies and integration points: depends on DMA engine, page mapping, highmem helpers, and async_tx core dependency/callback handling.

Risks: DMA mappings must use the correct directions and be paired with descriptor unmap ownership. Atomic mappings require short, non-sleeping copy sections. Fallback must honor dependencies and callbacks to preserve async_tx semantics.

Test signals: aligned DMA path, unaligned fallback, missing channel fallback, dependency ordering, callback execution, highmem pages, and DMA mapping error instrumentation.
