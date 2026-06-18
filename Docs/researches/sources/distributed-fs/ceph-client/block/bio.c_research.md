# sources/distributed-fs/ceph-client/block/bio.c

## Purpose

`bio.c` implements core bio allocation, initialization, lifetime, vector management, cloning, splitting, iterator/page mapping, bounce buffers, synchronous wait helpers, dirty-page completion handling, and final bio completion.

## Important APIs, Types, And Functions

Important allocation state includes `struct bio_alloc_cache`, `bvec_slabs`, `struct bio_set fs_bio_set`, and the shared `bio_slabs` xarray. Major APIs include `bio_init()`, `bio_reset()`, `bio_reuse()`, `bio_chain()`, `bio_alloc_bioset()`, `bio_kmalloc()`, `bio_put()`, `bio_alloc_clone()`, `bio_init_clone()`, `bio_add_page()`, `bio_add_folio()`, `bio_add_vmalloc()`, `bio_iov_iter_get_pages()`, `bio_iov_iter_bounce()`, `bio_iov_iter_unbounce()`, `bio_await()`, `submit_bio_wait()`, `bdev_rw_virt()`, `__bio_advance()`, `bio_copy_data()`, `bio_set_pages_dirty()`, `bio_check_pages_dirty()`, `bio_endio()`, `bio_split()`, `bio_trim()`, `bioset_init()`, and `bioset_exit()`.

## Control Flow, State, And Persistence

`bio_alloc_bioset()` tries slab/per-CPU-cache allocation for small bios and falls back to mempools for blocking allocations. If recursive submit paths could deadlock on the same bioset, `punt_bios_to_rescuer()` moves current-task queued bios to a rescuer workqueue before sleeping.

`bio_init()` and `bio_reset()` initialize visible state, counters, cgroup association, integrity, crypto, and vector ownership. `bio_uninit()` releases blkcg, integrity, and crypto state. `bio_put()` either returns a small bio to the per-CPU cache or calls `bio_free()`.

Vector helpers add pages, folios, vmalloc chunks, or iov_iter pages, merge contiguous segments where legal, enforce `BIO_MAX_SIZE`, mark P2PDMA bios `REQ_NOMERGE`, and reject cloned mutation. Bounce helpers allocate folios, copy write data into bounce buffers, or retain original read bvecs for completion copy-back.

`bio_endio()` handles chained remaining counts, integrity-delayed completion, zone/rq-qos hooks, trace completion, iterative parent completion for chained bios, blkcg reference cleanup, and final `bi_end_io`. `bio_split()` and `bio_trim()` adjust iterators and integrity metadata while rejecting invalid, zone append, and atomic write split cases.

## Dependencies And Integration Points

The file integrates with MM folios and page pinning, vmalloc cache maintenance, mempools, workqueues, cgroups, blk-crypto, bio integrity, rq-qos, block tracing, zone handling, blk-mq submit paths, and `bio_associate_blkg()` from blkcg.

## Risks And Test Signals

Risk areas are mempool deadlock avoidance, cloned vector lifetimes, pinned-page release and dirtying outside interrupt context, per-CPU cache pruning, chained completion recursion, and integrity/crypto cleanup. Test memory pressure, stacking-driver recursion, CPU hotplug, direct I/O pin/unpin, bounce reads/writes, vmalloc I/O, clone/split/trim lifetime, chained completion ordering, and synchronous wait paths.
