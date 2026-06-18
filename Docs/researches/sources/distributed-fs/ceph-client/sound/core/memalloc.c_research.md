# sources/distributed-fs/ceph-client/sound/core/memalloc.c

## Purpose
`memalloc.c` implements ALSA's generic DMA/audio buffer allocation layer. It abstracts different memory backends behind `snd_malloc_ops` so PCM and other audio paths can allocate, free, mmap, sync, and query buffer pages regardless of whether memory is contiguous, vmalloc-backed, coherent DMA, noncontiguous DMA, noncoherent DMA, IRAM, write-combined, or fallback SG.

## Important APIs, Types, and Functions
The central dispatch type is `struct snd_malloc_ops`. Public APIs include `snd_dma_alloc_dir_pages()`, `snd_dma_alloc_pages_fallback()`, `snd_dma_free_pages()`, `snd_devm_alloc_dir_pages()`, `snd_dma_buffer_mmap()`, `snd_dma_buffer_sync()`, `snd_sgbuf_get_addr()`, `snd_sgbuf_get_page()`, and `snd_sgbuf_get_chunk_size()`. Backend functions implement continuous pages, vmalloc, IRAM, coherent device memory, write-combined device memory, DMA noncontiguous memory, noncoherent memory, and optional x86 SG fallback.

## Control Flow and State
Allocation aligns sizes to pages, records device/type/direction, dispatches through `snd_dma_get_ops()`, stores area/address/private data, and records byte size on success. Fallback allocation halves requested size down to a page on `-ENOMEM`. Continuous allocation uses `alloc_pages_exact()` with DMA mask fallback to DMA32 or DMA zones and optional x86 WC attributes. Vmalloc backends translate pages on demand and compute physically contiguous chunks by walking page addresses. DMA noncontiguous allocation stores `sg_table`, vmaps it, records sync need, and implements explicit CPU/device sync. SG fallback tries standard DMA first, then allocates progressively smaller contiguous chunks, maps an sg table, vmaps pages, and exposes mmap/chunk helpers. Noncoherent allocation tracks `need_sync` and uses dma sync APIs.

## Dependencies and Integration Points
The file depends on Linux DMA mapping APIs, genalloc, vmalloc/vmap, scatter-gather iterators, architecture write-combining helpers, and ALSA `snd_dma_buffer` contracts. Consumers rely on these helpers for PCM ring buffers and mmap into user space.

## Risks and Test Signals
Risks include DMA mask fallback leaks, wrong cache synchronization for noncoherent/noncontiguous memory, incorrect chunk calculations across page boundaries, SG fallback partial-allocation cleanup, and write-combine attribute restoration. Tests should allocate/free every enabled type, mmap buffers, validate physical address/page lookup at offsets, exercise fallback under pressure, run DMA sync in both directions, and check no leaks on injected failures in SG/vmap/dma-map stages.
