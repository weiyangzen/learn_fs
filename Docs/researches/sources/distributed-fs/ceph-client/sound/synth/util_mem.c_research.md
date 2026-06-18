# sources/distributed-fs/ceph-client/sound/synth/util_mem.c

## Purpose
Provides a small generic allocator for soundcard/device memory represented as a linear address space. It tracks allocated blocks in offset order and supports both locked public APIs and unlocked internal helpers for callers that already hold `block_mutex`.

## Important APIs, Types, and Functions
Exports `snd_util_memhdr_new()`, `snd_util_memhdr_free()`, `snd_util_mem_alloc()`, `snd_util_mem_free()`, `snd_util_mem_avail()`, plus internal exported helpers `__snd_util_mem_alloc()`, `__snd_util_mem_free()`, and `__snd_util_memblk_new()`. It operates on `struct snd_util_memhdr` and `struct snd_util_memblk` from `<sound/util_mem.h>`.

## Control Flow
`snd_util_memhdr_new()` allocates the header, initializes size, mutex, and list head. `__snd_util_mem_alloc()` aligns requested sizes to even units, scans the sorted block list for the first gap, and inserts a new block after the previous block. `snd_util_mem_alloc()` wraps this in `block_mutex`. `snd_util_mem_free()` validates inputs, locks, removes the block from the list, decrements counters, and frees it. Header free drains every block without callbacks.

## State and Persistence
The header persists allocator-wide `size`, `used`, `nblocks`, `block_extra_size`, mutex, and ordered block list. Each block persists `offset` and `size`; optional extra bytes after the block structure allow device-specific metadata.

## Dependencies and Integration Points
Used by ALSA synth/sample loaders that need to reserve hardware sample RAM or similar linear resources. SoundFont sample callbacks receive an `snd_util_memhdr` and can use this allocator to back `snd_sf_sample` storage.

## Risks
The allocator is first-fit and non-compacting, so fragmentation can deny large allocations even when total available space is enough. Public allocation assumes `hdr` is non-null before taking `&hdr->block_mutex`; callers must not pass null. Size arithmetic uses ints/unsigned ints and should be reviewed for very large virtual regions. Header free does not coordinate with live users.

## Test Signals
Test odd-size alignment, exact-fit head/middle/tail gaps, fragmentation, free counter underflow prevention, extra metadata sizing, concurrent public allocate/free, and null/invalid argument handling through `snd_BUG_ON()` paths.
