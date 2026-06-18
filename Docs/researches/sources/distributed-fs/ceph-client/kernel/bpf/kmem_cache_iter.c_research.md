# sources/distributed-fs/ceph-client/kernel/bpf/kmem_cache_iter.c

## Purpose

`kmem_cache_iter.c` implements a BPF iterator target and open-coded iterator kfuncs for walking kernel slab `struct kmem_cache` objects. It exposes slab cache metadata to BPF iterator programs while coordinating with slab lifetime rules through `slab_mutex` and explicit refcount handling.

## Important APIs, Types, And Functions

`struct bpf_iter_kmem_cache` is the public opaque iterator state. `struct bpf_iter_kmem_cache_kern` stores the current `struct kmem_cache *`. `KMEM_CACHE_POS_START` is a sentinel for the not-yet-started state.

Open-coded iterator kfuncs are `bpf_iter_kmem_cache_new()`, `bpf_iter_kmem_cache_next()`, and `bpf_iter_kmem_cache_destroy()`. They initialize the cursor, return successive slab caches, and release the current cache reference.

Seq-file integration uses `struct bpf_iter__kmem_cache`, `union kmem_cache_iter_priv`, `kmem_cache_iter_seq_start()`, `kmem_cache_iter_seq_next()`, `kmem_cache_iter_seq_stop()`, and `kmem_cache_iter_seq_show()`.

Registration uses `BTF_ID_LIST_GLOBAL_SINGLE(bpf_kmem_cache_btf_id, struct, kmem_cache)`, `DEFINE_BPF_ITER_FUNC(kmem_cache, ...)`, `bpf_kmem_cache_reg_info`, and `bpf_kmem_cache_iter_init()`.

## Control Flow

The open-coded iterator starts with `kit->pos = KMEM_CACHE_POS_START`. `bpf_iter_kmem_cache_next()` locks `slab_mutex`, handles empty lists, translates the sentinel to the first entry, advances from the previous entry otherwise, increments `next->refcount` for active caches, and drops/destroys the previous cache after releasing the mutex if its refcount reaches zero.

The seq-file iterator starts by scanning `slab_caches` to the requested position while holding `slab_mutex`. It takes a reference to the selected active cache, stores it in private iterator state, calls the attached BPF iterator program in `show`, and invokes the program one final time with `s == NULL` from `stop` for end-of-iteration semantics.

Registration happens at `late_initcall`, fills the BTF ID for `struct kmem_cache`, and registers the target name `kmem_cache` with `BPF_ITER_RESCHED` and a trusted nullable BTF pointer context argument.

## State And Persistence Behavior

Iterator state is per-open or per open-coded iterator invocation and stores only the current cache pointer. It does not own the global slab list; it temporarily bumps `kmem_cache->refcount` for active entries and releases that reference on next/destroy/stop.

Boot caches have negative refcounts and are deliberately not touched. Cache destruction may be deferred until after dropping `slab_mutex` when the iterator releases the last active reference.

## Dependencies And Integration Points

The file reaches into `../../mm/slab.h` for `kmem_cache`, `slab_caches`, and `slab_mutex`. It integrates with BPF iterator registration, BTF ID resolution, seq_file, and slab allocator lifetime rules.

## Risks And Edge Cases

The seq start path scans by position instead of keeping a reference across all mutations, so concurrent deletion can skip or miss entries. Comments call this rare and acceptable. Refcount handling is delicate: destroying under `slab_mutex` would be unsafe, while failing to destroy after refcount reaches one would leak caches awaiting destruction.

The iterator is sleepable because it takes `slab_mutex`. BTF flags and registration must continue to reflect that or verifier assumptions will be wrong.

## Test Signals

Tests should cover open-coded iterator use, seq iterator use through BPF iter links, empty slab lists, early destroy without next, full iteration with final NULL callback, and concurrent cache create/destroy stress under slab debug or KASAN.
