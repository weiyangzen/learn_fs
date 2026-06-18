# sources/distributed-fs/ceph-client/sound/pci/trident/trident_memory.c

## Purpose
This file implements virtual memory page allocation for Trident 4DWave-NX TLB-backed PCM buffers. The chip can address only a limited DMA window at one time, so the driver maps ALSA DMA buffer pages into a hardware TLB and hands voice programming a virtual offset.

## Important APIs, types, and functions
The exported functions are `snd_trident_alloc_pages()` and `snd_trident_free_pages()`. Internal allocation paths are `snd_trident_alloc_sg_pages()` for ALSA scatter-gather buffers and `snd_trident_alloc_cont_pages()` for contiguous device DMA buffers. `search_empty()` allocates aligned regions from the ALSA util memory block list. `is_valid_page()` verifies that DMA addresses fit the hardware mask and are 4 KiB aligned.

Macros adapt the hardware 4 KiB Trident page model to the kernel `PAGE_SIZE`. For 4 KiB pages, one aligned page maps one TLB entry. For 8 KiB pages, one aligned page maps two TLB entries. For larger page sizes, `UNIT_PAGES` maps each kernel page to multiple hardware TLB entries. `set_tlb_bus()` writes bus addresses into the TLB table; `set_silent_tlb()` resets entries to the driver's silent page.

## Control flow
PCM hw_params in `trident_main.c` calls `snd_trident_alloc_pages()` when TLB entries exist and the buffer changed. The allocator selects SG or contiguous mode from `substream->dma_buffer.dev.type`, locks the util memory header, finds a free virtual page range, validates every physical page, and writes corresponding TLB entries. On validation failure it frees the just-created memory block and returns NULL. Hardware voice setup later uses `voice->memblk->offset` as the loop begin address.

On hw_free or buffer replacement, `snd_trident_free_pages()` locks the same memory header, rewrites the block's TLB entries to the silent page, frees the util memory block, and returns.

## State and persistence behavior
The allocator mutates `trident->tlb.entries`, the DMA-visible TLB table allocated in `trident_main.c`, and `trident->tlb.memhdr`, the software allocation map. `struct snd_trident_memblk_arg` stores first and last aligned page numbers in each util memory block. Freed TLB slots intentionally remain mapped to the silent page rather than stale user buffer pages.

## Dependencies and integration points
The file depends on `struct snd_trident_tlb` from `trident.h`, ALSA util memory internals, ALSA PCM SG helpers, DMA addresses from PCM runtime buffers, and Linux I/O/endian helpers. It is meaningful only for devices where `trident->tlb.entries` was allocated, currently NX initialization.

## Risks and test signals
Risks include page-size-specific mapping errors, off-by-one range handling in `search_empty()`, physical address validation failures, concurrency around the util memory block list, and stale TLB mappings if free paths are skipped. Test signals include NX playback using SG buffers, repeated hw_params with changing buffer sizes, allocation failure cleanup, freeing resetting entries to the silent page, validation rejection of unaligned or too-large DMA addresses, and no memory leaks reported by ALSA util memory diagnostics in `/proc`.
