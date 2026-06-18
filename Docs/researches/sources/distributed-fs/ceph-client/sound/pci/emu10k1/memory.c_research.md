# Research: sources/distributed-fs/ceph-client/sound/pci/emu10k1/memory.c

## Purpose
`memory.c` manages EMU10K1 sample memory and page table mappings. It maps ALSA PCM SG buffers and synthesizer sample allocations into the chip page table (PTB), maintains page-address/pointer tables, supports LRU-style eviction of unlocked mappings, and provides synth memory memset/copy helpers.

## Important APIs, Types, and Functions
Key public functions are `snd_emu10k1_memblk_map()`, `snd_emu10k1_alloc_pages()`, `snd_emu10k1_free_pages()`, `snd_emu10k1_alloc_pages_maybe_wider()`, `snd_emu10k1_synth_alloc()`, `snd_emu10k1_synth_free()`, `snd_emu10k1_synth_memset()`, and `snd_emu10k1_synth_copy_from_user()`. Internal helpers include `emu10k1_memblk_init()`, `search_empty_map_area()`, `map_memblk()`, `unmap_memblk()`, `search_empty()`, `is_valid_page()`, `synth_alloc_pages()`, `synth_free_pages()`, and `xor_range()`.

## Control Flow
PCM allocation finds an aligned free util-mem block, fills `emu->page_addr_table[]` from ALSA SG DMA addresses or the silent page, locks the mapping, and maps it into PTB entries. Synth allocation uses `__snd_util_mem_alloc()`, allocates individual DMA pages only for newly covered page ranges, maps the block, and can later be evicted from PTB if unlocked. Mapping searches the ordered mapped list for an exact or largest suitable hole; on failure, it unmaps oldest unlocked blocks until space is sufficient. Freeing unmaps PTB entries back to the silent page, releases allocated DMA pages, and returns the util memory block.

## State and Persistence
State is in `emu->memhdr`, mapped linked lists, `mapped_page`, `map_locked`, `first_page`, `last_page`, `page_addr_table[]`, `page_ptr_table[]`, `ptb_pages.area`, and `silent_page`. This state is runtime-only and rebuilt on device initialization; hardware PTB contents persist until rewritten or reset.

## Dependencies and Integration Points
`emupcm.c` relies on this file for playback buffer addressability. Synth code uses the synth alloc/free/memset/copy APIs. It depends on ALSA util memory helpers, ALSA DMA allocation, `snd_pcm_sgbuf_get_addr()`, PCI DMA masks, and EMU page constants from `sound/emu10k1.h`.

## Risks
PTB mapping correctness is critical: page zero is reserved, page-size conversion differs when `PAGE_SIZE != EMUPAGESIZE`, and invalid DMA alignment or mask violations can make hardware fetch wrong memory. The IOMMU workaround deliberately widens allocations and must remain synchronized between allocation and free. Locked PCM mappings must not be evicted; synth mappings can be evicted and remapped. `snd_emu10k1_synth_copy_from_user()` must not trust user sizes beyond the block bounds and returns `-EFAULT` on copy failure.

## Test Signals
Exercise repeated PCM `hw_params`/`hw_free` with different buffer sizes and synth allocations that fragment PTB space. Validate silent-page remapping after free and no DMA mask/alignment warnings. Test `PAGE_SIZE` configurations larger than EMUPAGESIZE if possible. User-copy tests should cover page-boundary offsets and XOR mode. IOMMU workaround hardware should be checked for no out-of-bounds device fetches.
