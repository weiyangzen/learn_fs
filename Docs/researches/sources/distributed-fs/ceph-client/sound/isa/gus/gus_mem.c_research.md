<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem.c

Purpose: bottom-layer allocator for onboard GF1/InterWave sample memory. It tracks used blocks across 8-bit and 16-bit banks and supports shared block IDs for synth/sample reuse.

Important APIs/types/functions: exported `snd_gf1_mem_alloc()`, `snd_gf1_mem_xfree()`, and `snd_gf1_mem_free()`. Init/teardown helpers are `snd_gf1_mem_init()` and `snd_gf1_mem_done()`. Internals include ordered insertion, address lookup, share lookup, and first-fit allocation across bank descriptors.

Control flow: init creates reserved driver blocks for InterWave LFO memory and the default silent voice address. Allocation locks `memory_mutex`, optionally finds an existing shared block, computes a free aligned range in the requested 8/16-bit banks, copies share IDs, inserts the block sorted by address, and returns it. Free looks up by address and decrements share count or unlinks/frees the block. Debug builds expose a `gusmem` proc summary.

State and persistence: allocator state is a linked list plus `banks_8`/`banks_16` arrays in `gus->gf1.mem_alloc`. The actual DRAM content is separate; this file only reserves address ranges.

Dependencies and integration: PCM playback allocates `"GF1 PCM"` blocks; reset initializes default voice memory; InterWave/plain detection populates bank sizes before init. Depends on ALSA proc debug support and Linux slab/string helpers.

Risks: `snd_gf1_mem_alloc()` returns `NULL` both for allocation failure and for successful share hit after incrementing `share`, which is a legacy ambiguous contract. Bank iteration assumes valid nonzero bank arrays. Test signals include allocating/freeing 8/16-bit aligned blocks, sharing IDs, debug proc output, PCM buffer resize freeing old memory, and no leaks after `snd_gf1_mem_done()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_mem.c -->
