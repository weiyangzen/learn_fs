# sources/distributed-fs/ceph-client/sound/core/pcm_memory.c

## Purpose

`sources/distributed-fs/ceph-client/sound/core/pcm_memory.c` manages ALSA PCM DMA buffer preallocation, managed runtime buffer allocation, free paths, procfs tuning hooks, and per-card allocation accounting. It is the memory backend used by PCM drivers that ask the core to allocate hardware buffers before `hw_params` and release them after `hw_free`. The source was read as a complete 501-line file for this report.

## Important APIs, Types, and Functions

Module parameters include `preallocate_dma`, `maximum_substreams`, and writable `max_alloc_per_card`; `snd_minimum_buffer` sets the fallback floor. Exported APIs include `snd_pcm_lib_preallocate_free_for_all`, `snd_pcm_lib_preallocate_pages`, `snd_pcm_lib_preallocate_pages_for_all`, `snd_pcm_set_managed_buffer`, `snd_pcm_set_managed_buffer_all`, `snd_pcm_lib_malloc_pages`, and `snd_pcm_lib_free_pages`. Internal helpers include `do_alloc_pages`, `do_free_pages`, `preallocate_pcm_pages`, `preallocate_pages`, and optional verbose-procfs read/write callbacks for `prealloc` and `prealloc_max`.

## Control Flow

Preallocation starts with driver setup calling `snd_pcm_lib_preallocate_pages*()` or `snd_pcm_set_managed_buffer*()`. `preallocate_pages()` records the DMA type/device, optionally allocates an initial buffer, falls back by halving the requested size down to `snd_minimum_buffer` when allowed, stores `buffer_bytes_max` and `dma_max`, and creates procfs entries when verbose procfs is enabled. Managed mode sets `substream->managed_buffer_alloc`, causing `pcm_native.c` `snd_pcm_hw_params()` to call `snd_pcm_lib_malloc_pages()` and `snd_pcm_hw_free()` to call `snd_pcm_lib_free_pages()`.

Allocation uses `do_alloc_pages()` to reserve bytes against `card->total_pcm_alloc_bytes` under `card->memory_mutex`, choose DMA direction from playback/capture, call `snd_dma_alloc_dir_pages()`, then correct accounting if the allocator returned a larger actual buffer. Runtime allocation prefers an existing runtime buffer if large enough, then a preallocated substream buffer if sufficient, otherwise dynamically allocates a new `struct snd_dma_buffer` unless the preallocation was fixed-size. Freeing releases only dynamically allocated runtime buffers; preallocated buffers remain on the substream until explicit preallocate-free.

## State and Persistence Behavior

Persistent state is in kernel memory only: `substream->dma_buffer`, `substream->dma_max`, `substream->buffer_bytes_max`, `substream->managed_buffer_alloc`, `runtime->dma_buffer_p`, `runtime->dma_bytes`, and `card->total_pcm_alloc_bytes`. Procfs writes can change a substream's preallocated buffer while the PCM is closed, but there is no disk persistence. Allocation accounting is card-wide and protected by `card->memory_mutex`.

## Dependencies and Integration Points

The file depends on Linux DMA allocation helpers, module parameters, ALSA info/procfs support, and `pcm_local.h` for substream iteration and runtime checks. It integrates with `pcm_native.c` hw-param and hw-free paths, with `snd_pcm_mmap_data()` and transfer code through `runtime->dma_area` and `runtime->dma_bytes`, and with drivers that declare managed buffers rather than implementing their own allocation policy.

## Risks and Edge Cases

Accounting must remain balanced when allocation size differs from requested size or allocation fails. Procfs resize is blocked while `substream->runtime` exists, avoiding live buffer replacement, but changes to `buffer_bytes_max` still affect future hw-params negotiation. Fixed-size preallocation (`max == 0`) rejects dynamic larger allocations. Fallback allocation can silently provide smaller buffers than the requested preallocation, so callers must still honor `buffer_bytes_max`. Incorrect DMA direction or missing explicit sync metadata can cause coherency issues in transfer and mmap paths.

## Test Signals

Test with preallocation enabled/disabled, multiple substreams beyond `maximum_substreams`, per-card allocation caps, fixed-size managed buffers, fallback allocation under memory pressure, procfs resize while closed and busy rejection while open, and hw_params/hw_free cycles that reuse preallocated buffers then force dynamic allocation. Leak/accounting checks should verify `card->total_pcm_alloc_bytes` returns to baseline after frees.
