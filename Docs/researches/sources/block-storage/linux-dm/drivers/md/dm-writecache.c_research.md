# File Research: sources/block-storage/linux-dm/drivers/md/dm-writecache.c

## Scope

This file implements the Device Mapper `writecache` target. It accelerates an origin block device with either a persistent-memory/DAX cache device (`p` mode) or an SSD cache device (`s` mode), maintains persistent cache metadata, services reads/writes/flushes/discards, performs asynchronous writeback to the origin, and exposes status/messages for administrative control.

## Public And Internal APIs Covered

- DM target entry points: `writecache_ctr()`, `writecache_dtr()`, `writecache_map()`, `writecache_end_io()`, `writecache_suspend()`, `writecache_resume()`, `writecache_status()`, `writecache_message()`, `writecache_iterate_devices()`, `writecache_io_hints()`.
- Module lifecycle: `dm_writecache_init()` registers `writecache_target`; `dm_writecache_exit()` unregisters it.
- Persistent-memory helpers: `persistent_memory_claim()`, `persistent_memory_release()`, page/offset/cache flush helpers, and `pmem_assign()`.
- Persistent metadata helpers: superblock/entry accessors, `read_original_sector()`, `read_seq_count()`, `clear_seq_count()`, `write_original_sector_seq_count()`, `writecache_flush_region()`, `writecache_flush_all_metadata()`, `writecache_commit_flushed()`, `ssd_commit_flushed()`, `ssd_commit_superblock()`.
- Cache lookup/list management: `writecache_find_entry()`, `writecache_insert_entry()`, `writecache_unlink()`, `writecache_add_to_freelist()`, `writecache_pop_from_freelist()`, `writecache_free_entry()`, `writecache_discard()`.
- I/O mapping helpers: `writecache_map_read()`, `writecache_map_write()`, `writecache_map_flush()`, `writecache_map_discard()`, `writecache_map_remap_origin()`, `writecache_bio_copy_ssd()`, `bio_copy_block()`.
- Background workers: `writecache_flush_thread()`, `writecache_endio_thread()`, `writecache_writeback()`, `writecache_flush_work()`, timers for autocommit and max age.
- Writeback helpers: `__writecache_writeback_pmem()`, `__writecache_writeback_ssd()`, completion callbacks, and throttling.
- Control messages: `flush`, `flush_on_suspend`, `cleaner`, and `clear_stats`.

## Control Flow And Behavior

- Construction parses mode, origin device, cache device, block size, and optional arguments such as `start_sector`, watermarks, writeback job limit, autocommit thresholds, `max_age`, `cleaner`, `fua`/`nofua`, `metadata_only`, and `pause_writeback`.
- PMEM mode requires synchronous DAX, maps the cache device using `dax_direct_access()`, optionally vmaps discontiguous pages, and flushes/invalidate cache ranges directly. SSD mode allocates a volatile metadata map in kernel memory, reads/writes cache metadata through `dm-io`, uses a dirty bitmap to persist changed metadata sectors, creates a flush thread, and uses `dm_kcopyd` for writeback copies.
- The on-cache metadata contains a small superblock and one `wc_memory_entry` per cache block. `seq_count` distinguishes committed entries from current uncommitted writes. `original_sector == -1` and `seq_count == -1` mark free entries.
- `writecache_resume()` reloads cache metadata, rebuilds the RB tree of valid entries and the freelist, drops duplicate or uncommitted entries, repairs metadata if needed, starts max-age writeback, and validates against hardware memory errors with `copy_mc_to_kernel()` where available.
- `writecache_map()` serializes state changes with `wc->lock`, handles preflush before sector remapping, enforces cache-block alignment, and dispatches reads, writes, discards, and flushes to specialized helpers.
- Reads hit the cache by original sector. PMEM hits are copied directly into the bio with machine-check-safe reads; SSD hits are remapped to cache sectors and counted as in-progress reads. Misses are partially remapped to the origin up to the next cached sector.
- Writes update an existing uncommitted entry, overwrite a committed SSD entry when safe, allocate a free entry, or bypass to the origin in cleaner/metadata-only/no-free-entry cases. PMEM writes copy data immediately into persistent memory; SSD writes remap contiguous cache blocks to the cache device. Autocommit is triggered by block count, timer, or FUA.
- Flushes commit metadata and, for SSD mode, are offloaded to the flush thread so the target can handle the two flush-bio pattern. Discards invalidate matching cached entries and then pass the discard to the origin.
- `writecache_flush()` persists dirty data/metadata for all uncommitted LRU entries up to the next committed boundary, increments the superblock sequence count, writes the superblock, and frees older duplicate entries for the same original sector.
- Writeback is queued when free entries fall below watermarks, cleaner/writeback-all is active, max age expires, or messages request it. It selects committed LRU entries, skips entries shadowed by in-progress newer duplicates, batches adjacent sectors, marks entries `write_in_progress`, and submits PMEM bios or SSD `dm_kcopyd` copies.
- Completion callbacks add finished work to `endio_list`; `writecache_endio_thread()` performs required origin flushes, frees entries, commits metadata again, and wakes freelist waiters. SSD endio waits for reads before final metadata commit.
- Suspend stops timers, flushes metadata, optionally forces writeback-all, drains the workqueue, waits for in-flight writeback, flushes PMEM mappings, and poisons lists to catch access while suspended.

## State And Data Structures

- `struct dm_writecache` is the target state: origin/cache devices, mapped metadata/data area, RB tree by original sector, LRU list, freelist/freetree, watermarks, sequence count, timers, workqueue, kthreads, dm-io/kcopyd clients, dirty bitmap, bioset/mempool, in-flight bio counters, and statistics.
- `struct wc_entry` represents one cache block and stores RB/LRU linkage, cache index, age, writeback state, contiguous-writeback hint, and optional shadow copies of persistent metadata for hardware-error handling.
- `struct wc_memory_superblock` and `struct wc_memory_entry` are the persistent metadata format.
- `struct writeback_struct` wraps a bio plus the cache entries it writes back in PMEM mode; `struct copy_struct` tracks SSD kcopyd writeback completion.
- `bio->bi_private` is used as a small tag: cache-device remaps decrement `bio_in_progress`, and origin write bypasses are tracked by `dm_io_tracker` for pause-writeback idleness.

## Dependencies

- Device Mapper target APIs, `dm-io`, `dm-kcopyd`, `dm-io-tracker`, target messages/status, and dm device lookup.
- Linux block layer bio cloning/remapping/submission, flush/FUA/discard flags, queue limits, biosets, mempools, kthreads, timers, workqueues, wait queues, RB trees, lists, vmalloc/vmap.
- DAX/libnvdimm/PMEM APIs when persistent-memory mode is compiled in.
- Architecture copy/flush helpers including `copy_mc_to_kernel()`, `memcpy_flushcache()`, `clflushopt`, and cache maintenance helpers.

## Risks And Invariants

- Metadata commit ordering is central: data and per-entry metadata must be durable before the superblock `seq_count` is advanced.
- Duplicate entries for the same original sector are legal only across sequence generations; stale duplicates must be freed only after newer committed data is safe.
- PMEM and SSD modes have different durability models. PMEM relies on cacheline writeback and memory barriers; SSD mode relies on explicit metadata writes, cache flushes, and a dirty bitmap.
- The freelist and writeback-size accounting gate forward progress; missed wakeups or unbalanced `write_in_progress` flags would block writes indefinitely.
- SSD overwrite of committed entries and discard handling wait for in-flight I/O where necessary so cached data is not freed while a remapped bio still references it.
- `copy_mc_to_kernel()` error handling is a reliability boundary for persistent-memory media errors.
- `writecache_map()` requires all I/O to be aligned to the configured cache block size; misaligned bios are failed.
- The target must not access normal list/tree structures while suspended after list poisoning.
