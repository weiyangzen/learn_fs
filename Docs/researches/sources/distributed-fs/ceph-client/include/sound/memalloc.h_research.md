# sources/distributed-fs/ceph-client/include/sound/memalloc.h

Source read summary: 120 lines, ALSA DMA buffer allocation abstraction.

Purpose: defines common DMA buffer descriptors, allocation types, synchronization helpers, mmap support, scatter-gather accessors, and devm allocation wrappers for ALSA PCM and control paths.

Important APIs, types, and functions: `struct snd_dma_device` stores DMA type, direction, sync requirement, and device. `struct snd_dma_buffer` stores device info, CPU area, DMA address, byte size, and allocator-private data. DMA type macros cover continuous, device, write-combined, IRAM, vmalloc, noncontiguous, noncoherent, and optional SG buffers. APIs include `snd_dma_alloc_dir_pages()`, `snd_dma_alloc_pages()`, fallback allocation, `snd_dma_free_pages()`, `snd_dma_buffer_mmap()`, `snd_dma_buffer_sync()`, `snd_sgbuf_get_addr/page/chunk_size()`, `snd_devm_alloc_dir_pages()`, and `snd_dma_noncontig_sg_table()`.

Control flow: PCM drivers request or preallocate buffers, set them into runtime state, map them to userspace if supported, sync for CPU/device access when needed, and free or devm-release at teardown.

State and persistence behavior: state is volatile DMA allocation metadata and memory. Audio samples persist only while buffers are allocated; allocator-private SG/noncontig data lives in `private_data`.

Dependencies and integration points: depends on Linux DMA mapping, pages, devices, vm_area, SG tables, and optional DMA/SG configs. It is used heavily by `pcm.h` and sound drivers.

Risks and edge cases: DMA direction and sync mode must match hardware, fallback allocations may reduce size, SG chunk math must not cross pages incorrectly, and mmap attributes must match cacheability.

Test signals: allocate/free each enabled DMA type, mmap and userspace access, noncoherent sync, SG address/page/chunk helpers, fallback paths under memory pressure, and devm cleanup.
