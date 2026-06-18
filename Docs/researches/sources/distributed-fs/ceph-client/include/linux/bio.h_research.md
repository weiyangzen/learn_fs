# sources/distributed-fs/ceph-client/include/linux/bio.h

## Purpose
Provides the main block I/O bio helper API: segment iteration, allocation, splitting, chaining, completion, page/vector attachment, iov handling, cgroup association, bio lists, biosets, polling flags, and discard/zone helpers.

## Important APIs, types, and functions
- Iteration helpers include `bio_iter_*`, `bio_for_each_segment`, `bio_for_each_bvec`, all-segment variants, and `bio_for_each_folio_all()`.
- State helpers include `bio_flagged()`, `bio_set_flag()`, `bio_clear_flag()`, `bio_has_data()`, `bio_data()`, `bio_segments()`, `bio_get()`, `bio_cnt_set()`, and `bio_inc_remaining()`.
- Advancement/splitting: `bio_advance_iter()`, `bio_advance()`, `bio_trim()`, `bio_split()`, `bio_split_io_at()`, and `bio_next_split()`.
- Allocation/lifecycle: `bioset_init()`, `bioset_exit()`, `bio_alloc_bioset()`, `bio_alloc()`, `bio_kmalloc()`, `bio_put()`, `bio_init()`, `bio_reset()`, `bio_reuse()`, `bio_chain()`, and `bio_await()`.
- I/O submission and completion: `submit_bio()`, `bio_endio()`, `bio_io_error()`, `bio_wouldblock_error()`, and `submit_bio_wait()`.
- Data attachment/copying: `bio_add_page()`, `bio_add_folio()`, vmalloc helpers, iov page helpers, bounce helpers, copy helpers, dirty/release helpers, zero fill, and end-of-device guard.
- `struct bio_list` and helpers implement singly-linked bio queues.
- `struct bio_set` owns bio/bvec pools, optional per-CPU cache, rescue list/workqueue, and CPU hotplug node.

## Control flow and state
Callers allocate/init a bio, set device/op/sector, attach pages or iterator-backed vectors, optionally associate cgroups, submit it, and later receive completion. Splitting advances or clones iterators so lower layers process only their slice. Chaining uses remaining counters so parent completion waits for child bios. List helpers queue bios in remapping drivers. Biosets provide preallocated pools and rescue work to avoid stacking deadlocks.

## State and persistence behavior
Bio state is transient per I/O. It references pages, folios, block devices, cgroup associations, operation flags, iterator position, status, and completion counters. Data may persist to block devices when the op writes. Page pin/dirty state must be released correctly after completion.

## Dependencies and integration points
Depends on mempool, block types, UIO, request queues, block devices, cgroups, folios, and queue limits. Integrated by filesystems, direct I/O, block drivers, device mapper, md, loop, discard/zone code, and integrity support.

## Risks
Drivers must not use `bio_for_each_segment_all()` or all-bvec variants on bios they do not fully own because bios may have been split. Iterator advancement differs for discard/secure erase/write zeroes. Reference count barriers around `BIO_REFFED` and `BIO_CHAIN` are required. Polled I/O must not block waiting for unavailable resources. `bio_set_dev()` clears throttle/remap flags and re-associates blkcg state, which matters for remappers.

## Test signals
Run block tests covering split/merge, discard/write-zeroes, zone append emulation, chained completions, bio list ordering, cgroup association, page pin release, iov/vmalloc attachment, bounce/unbounce, polled NOWAIT failures, and bioset rescuer behavior.
