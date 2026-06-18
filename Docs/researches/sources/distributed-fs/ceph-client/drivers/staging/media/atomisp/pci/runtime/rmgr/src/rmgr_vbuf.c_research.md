# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/src/rmgr_vbuf.c

## Purpose

`rmgr_vbuf.c` implements the AtomISP CSS runtime resource manager for virtual-buffer handles backed by HMM allocations. It centralizes reference counting for small handle objects, provides copy-on-write acquisition semantics for shared buffers, and optionally recycles released HMM buffers through a fixed-size pool to reduce allocation churn in buffer enqueue paths.

## Important APIs, Types, and Functions

The file owns a static `handle_table[1000]` of `struct ia_css_rmgr_vbuf_handle`, plus three exported pool pointers: `vbuf_ref`, `vbuf_write`, and `hmm_buffer_pool`. `vbuf_ref` is a plain retaining pool, `vbuf_write` enables copy-on-write, and `hmm_buffer_pool` enables copy-on-write plus recycling with 32 cached handles.

`ia_css_rmgr_init_vbuf()` zeroes the global handle table and allocates the optional recycle handle array with `kvmalloc()`. `ia_css_rmgr_uninit_vbuf()` frees any cached HMM buffers, releases their handles, and frees the recycle array. `ia_css_rmgr_refcount_retain_vbuf()` converts an external zero-count handle descriptor into an internally managed slot and increments its `u8` count. `ia_css_rmgr_refcount_release_vbuf()` decrements a managed handle and clears `vptr`/`size` when the count reaches zero.

The private `rmgr_push_handle()` retains a handle and stores it in the first free recycle slot; `rmgr_pop_handle()` finds a cached buffer of the requested size and returns that handle to the caller. `ia_css_rmgr_acq_vbuf()` is the public acquire path, including copy-on-write buffer allocation via `hmm_alloc()`. `ia_css_rmgr_rel_vbuf()` releases a caller reference, freeing the HMM allocation for non-recycle pools or pushing single-reference buffers back to the recycle pool.

## Control Flow

Callers create a temporary zero-count handle with a desired `size` and call `ia_css_rmgr_acq_vbuf()`. For non-copy-on-write pools, the acquire path simply retains the descriptor, which replaces the caller's pointer with a slot from `handle_table`. For copy-on-write pools, an already unique handle is reused directly. A shared handle is released, a new same-sized descriptor is prepared, and the function then tries to pop a matching recycled HMM buffer before allocating a new one. New allocations are retained into the global table before being returned.

Release first checks whether the caller owns the last reference. If so, non-recycling pools free the underlying `vptr` immediately, while recycling pools retain the handle into the pool cache and then release the caller's reference. The final release clears the caller's pointer. Uninitialization walks cached recycle entries, frees each HMM buffer, releases the associated refcount slot, and frees the cache array.

## State and Persistence Behavior

There is no filesystem persistence. The durable runtime state is process-global within the AtomISP driver: the fixed handle table, pool metadata, optional recycle arrays, handle refcounts, and HMM virtual pointers. Recycle-pool contents survive across individual buffer enqueue/release operations until pool uninitialization. The global handle table is reset every time `ia_css_rmgr_init_vbuf()` is called for any pool, which makes initialization ordering significant.

## Dependencies and Integration Points

The resource manager depends on HMM allocation primitives (`hmm_alloc()`, `hmm_free()`), kernel allocation helpers (`kvmalloc()`, `kvfree()`), CSS debug logging, and the public declarations in `runtime/rmgr/interface/ia_css_rmgr_vbuf.h`. In the local tree, `sh_css.c` uses `hmm_buffer_pool` while enqueueing CSS buffers: it allocates a `struct sh_css_hmm_buffer`, stores it to HMM memory, and passes the HMM pointer into SP buffer queues. The design is tightly integrated with AtomISP firmware-visible DDR/HMM addresses rather than normal kernel virtual memory.

## Risks and Edge Cases

There is no locking around `handle_table`, pool arrays, or refcounts, so concurrent acquire/release from multiple contexts can race unless higher layers serialize all use. The `count` field is `u8`; repeated retains can wrap. If the 1000-entry handle table is exhausted, retain logs an error and leaves the caller with `NULL` after having detached the original zero-count descriptor. `ia_css_rmgr_acq_vbuf()` does not check `hmm_alloc()` failure before retaining the handle, so callers must inspect `h_vbuf->vptr` as `sh_css.c` does. `rmgr_push_handle()` asserts on a full recycle pool instead of gracefully freeing the buffer. The global refcount table reset in each pool init can invalidate existing handles if init is called while any pool is live.

## Test Signals

Useful tests include zero-count acquisition and release for all three exported pools, copy-on-write from shared handles, allocation failure from `hmm_alloc()`, recycle hit and miss by size, recycle-pool-full behavior, uninit with populated recycle slots, invalid argument handling, handle-table exhaustion, and repeated retains near the `u8` overflow boundary. Integration tests should enqueue and release frame/statistics/metadata buffers through `ia_css_pipe_enqueue_buffer()` and verify that HMM pointers are freed or recycled exactly once.
