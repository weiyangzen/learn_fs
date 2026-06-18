# sources/distributed-fs/ceph-client/drivers/md/dm-pcache/cache_writeback.c

## Purpose
Implements asynchronous writeback for dirty `dm-pcache` key sets. It walks the persisted dirty-tail stream, decodes each key set, issues writes from cache pmem into the backing device, and advances the persisted dirty tail only after all writes for that key set complete and the backing device is flushed.

## Important APIs, Types, And Functions
`cache_writeback_init()` initializes a one-subtree `writeback_key_tree`, clears the pending count, and queues `writeback_work`. `cache_writeback_exit()` cancels work, flushes the backing device, and destroys the tree. `cache_writeback_fn()` is the delayed-work state machine. `cache_key_writeback()` converts a dirty cache key into one or more `pcache_backing_dev_req` writes. `cache_wb_tree_writeback()` submits all decoded keys and tracks completion through `writeback_ctx`.

Helper `is_cache_clean()` reads the current dirty tail into `wb_kset_onmedia_buf`, checks `PCACHE_KSET_MAGIC` and CRC, and treats unreadable or invalid data as clean/no-work. `last_kset_writeback()` handles a terminal key set by moving `dirty_tail` to the next cache segment.

## Control Flow
The worker exits early if a previous writeback batch is still pending or the pcache target is stopping. Otherwise it snapshots `cache->dirty_tail`, reads a key set, and either backs off for `PCACHE_CACHE_WRITEBACK_INTERVAL` if the cache appears clean, advances to the next segment if the key set is marked `PCACHE_KSET_FLAGS_LAST`, or decodes all keys into the writeback RB tree.

For a normal key set, each non-clean key is written back in chunks no larger than `backing_dev_req_coalesced_max_len()`, which avoids crossing incompatible devmap pages in vmalloc-backed pmem mappings. `writeback_ctx.pending` starts at one sentinel reference, each backing request increments it, and each completion calls `writeback_ctx_end()`. The final completion flushes the backing device, advances and persists `dirty_tail`, and immediately requeues the worker.

## State And Persistence
Persistent state is the dirty-tail cache position encoded by `cache_encode_dirty_tail()` after successful writeback. Cached key sets and data remain in the pmem segment log until GC/segment reuse. Volatile state includes `writeback_ctx.pending`, `writeback_ctx.ret`, `writeback_ctx.advance`, `writeback_key_tree`, and the reusable key-set buffer.

Writeback is conservative: any request error is latched, dirty-tail advancement is skipped, and the worker retries later from the same persistent dirty tail. The backing device is flushed before the dirty tail is persisted, maintaining writeback ordering across crashes.

## Dependencies And Integration Points
The file depends on `cache.h` for key decoding, cache positions, CRC helpers, and workqueue access; `backing_dev.h` for request creation/submission and flush; `cache_dev.h` for pmem address helpers; and `dm_pcache.h` for stop-state/logging. It is paired with the dirty-key append path and cache GC: writeback makes key sets safe to clean, while GC can reclaim after dirty-tail progress.

## Risks
Treating unreadable or invalid key-set metadata as clean avoids an infinite loop but can hide metadata loss; with dirty data this can become data loss. Pending-count ordering is critical because dirty-tail advancement must happen exactly once and only after all writes finish. The code assumes a key fits within the remaining segment (`BUG_ON(seg_remain < key->len)`), so corrupt metadata can crash the kernel. Retry behavior can spin forever on persistent backing errors unless higher layers surface and manage the fault.

## Test Signals
Test writeback with multiple keys per key set, key sets spanning different pmem page mappings, backing write failures, backing flush failures, and target teardown while work is pending. Crash tests should verify that data written but not dirty-tail-advanced is replayed, and data whose dirty tail advanced is present on the backing device. Status output should show dirty-tail progress over sustained writeback.
