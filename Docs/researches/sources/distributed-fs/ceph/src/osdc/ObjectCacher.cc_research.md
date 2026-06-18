<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.cc -->
# sources/distributed-fs/ceph/src/osdc/ObjectCacher.cc

## Purpose

`ObjectCacher.cc` implements Ceph's in-memory object buffer cache with asynchronous read filling, dirty writeback, flush/release/purge/discard operations, dirty throttling, LRU trimming, and perf counters. It sits between higher file/object clients and a `WritebackHandler`, using `ObjectExtent` mappings from callers to cache and write back object byte ranges.

The implementation is a state machine around `BufferHead` regions. Each object has a sorted map of non-overlapping buffer heads, and every buffer head is in one of missing, clean, zero, dirty, RX, TX, or error state.

## Important APIs and Functions

`Object::split`, `merge_left`, `can_merge_bh`, `try_merge_bh`, and `maybe_rebuild_buffer` maintain the per-object interval map and buffer memory layout. Splitting preserves state, error, snap context, write/read tids, journal tid, flags, data, and read waiters. Merging requires adjacency, same state, compatible journal tid, and matching write tid for TX buffers.

`Object::map_read` maps an `ObjectExtent` into existing or newly allocated buffer heads, returning maps of hits, missing buffers, in-flight RX buffers, and error buffers. If the object is marked complete, gaps become clean zero hits. `Object::map_write` maps a write extent into one contiguous buffer head, splitting surrounding buffers and replacing journal tids when overwrites supersede earlier journal writeback expectations.

`bh_read` marks a buffer RX, assigns `last_read_tid`, submits `WritebackHandler::read`, and tracks outstanding reads through `C_ReadFinish`. `bh_read_finish` handles successful data, short reads padded with zeroes, trusted or distrusted `-ENOENT`, stale read tids, error state, waiter wakeups, merge attempts, retry of blocked reads, and outstanding-read accounting.

`readx` and `_readx` are the public and internal read paths. `_readx` maps every requested extent, submits missing reads, installs retry contexts on missing/RX buffers, handles optional `return_enoent`, constructs result data from cached buffer heads through `stripe_map`, records hole ranges for zero data, updates perf counters, trims clean cache, and returns either bytes read, error, `-ENOENT`, or zero for async-in-progress.

`writex` maps each write extent into cache, copies caller buffer fragments into dirty buffer heads, wakes read waiters invalidated by overwrite, updates dirty/nocache/dontneed flags, merges where legal, records perf counters, then calls `_wait_for_write` for dirty throttling or write-through behavior.

Writeback is implemented by `bh_write`, `bh_write_scattered`, `bh_write_adjacencies`, and `bh_write_commit`. Dirty buffers become TX, commit callbacks mark matching tids clean or dirty again on error, clear journal tids, update object commit tid, complete waiters in `waitfor_commit`, and notify `flush_set_callback` when an object set becomes fully clean.

Flush and lifecycle APIs include `flush`, `trim`, `flush_set`, range `flush_set`, `flush_all`, `purge_set`, `release_set`, `release_all`, `clear_nonexistence`, `discard_set`, and `discard_writeback`. `flusher_entry` is the background loop that flushes over-target dirty bytes, over-target dirty buffer-head counts, and aged dirty buffers, then waits for outstanding reads before thread exit.

Statistics maintenance is centralized in `bh_stat_add`, `bh_stat_sub`, `bh_set_state`, `bh_add`, `bh_remove`, and `verify_stats`. State changes update global byte counters, per-object-set dirty/tx byte counts, LRU membership, dirty-or-tx set membership, and dirty-waiter condition variables.

## Control Flow

Reads start with extent mapping. If every byte is represented by clean, zero, dirty, or TX buffers, `_readx` assembles the return buffer immediately. Missing buffers are marked RX and submitted to the writeback handler; the caller's completion is represented by a `C_RetryRead` attached to the last missing/RX buffer so the entire read is retried after enough data arrives. Cache pressure from RX bytes can push whole reads into the global `waitfor_read` queue until earlier reads complete.

Writes update the cache first and return according to the dirty throttling policy. Normal cached writes dirty memory and may complete after a throttle wait; FUA or zero dirty-limit paths force `flush_set` and optionally block until writeback commits. Overwriting TX data increments the overwritten-in-flush perf counter and preserves correctness by comparing write tids in commit callbacks.

Writeback moves dirty buffers to TX and submits handler writes. Commit callbacks may arrive after buffers were overwritten, split, discarded, or removed; the code therefore checks object existence, buffer state, and `last_write_tid` before marking clean. Commit waiters are keyed by object write tid, not individual buffer pointer.

Flush/release/discard paths all operate under the cache lock. Range flush walks intersecting buffers and schedules dirty ones. Release drops only clean/zero/error buffers and reports unclean bytes left. Discard removes in-memory extents, but if a buffer is TX and the caller used `discard_writeback`, it waits for commit before final completion.

## State and Persistence Behavior

The cache's persistent effects are through `WritebackHandler` reads and writes. In-memory state includes `objects` indexed by pool id and `sobject_t`, object LRU, clean/rest and dirty LRUs, `dirty_or_tx_bh`, wait queues, stats counters, and a private finisher for async wait callbacks.

`ObjectSet` groups objects for a higher-level inode/pool and tracks truncate size/seq, dirty/tx bytes, and whether single-extent reads should return `-ENOENT`. `Object` tracks existence and completeness: `complete=false` means gaps are not known zero; `complete=true` with `exists=false` means trusted `-ENOENT` told the cache the object is all zero/missing.

`BufferHead` state is the core persistence-adjacent state. Dirty and TX buffers represent data not yet safely written or currently committing. Clean/zero/error buffers are cacheable read state. RX buffers represent in-flight reads and pin themselves through reference counting. Journal tid tracks external journal writeback coordination; replacing it calls `WritebackHandler::overwrite_extent`.

## Dependencies and Integration Points

The implementation depends on `WritebackHandler` for storage I/O, `ObjectExtent`/`Striper` for caller mappings, Ceph `Context` and `Finisher`, `LRUObject`/`LRU`, `xlist`, `SnapContext`, perf counters, `ZTracer`, config `osdc_blkin_trace_all`, and the caller-provided shared cache lock.

Higher layers use `prepare_read`, `prepare_write`, `readx`, `writex`, and file convenience wrappers in the header. The writeback handler abstracts whether writes can be scattered and whether copy-on-write hazards exist. `flush_set_callback` lets the owner release journal or capability resources when dirty data has fully committed.

## Risks and Edge Cases

Correctness depends on non-overlapping buffer maps and exact stat symmetry. Splits, merges, state transitions, and removals must keep `data`, LRUs, `dirty_or_tx_bh`, object refs, and byte counters consistent. `verify_stats` exists because drift here can break dirty throttling, trimming, and shutdown.

`-ENOENT` handling is deliberately conservative. A trusted missing-object result can mark an object complete and nonexistent, wake all waiters, and remove all-zero buffers; `clear_nonexistence` must distrust in-flight reads when later writes/copy-up can invalidate that assumption.

TX commit races are common: a newer write tid can supersede an older commit, discarded TX buffers can delay completion through gathers, and overwritten journal tids must notify the writeback handler. Tests should target stale tid callbacks and object removal during in-flight I/O.

The cache lock is held across much of the control flow, with careful use of condition variables and finishers. The flusher intentionally unlocks when it has flushed too many aged buffers under lock to avoid starving other threads.

## Test Signals

Strong tests include interval splitting/merging invariants; read hits, misses, RX retries, error retries, holes, short read zero padding, trusted and distrusted `-ENOENT`; write overwrites of missing/clean/dirty/TX buffers; dirty limit blocking and async freespace callbacks; scattered and non-scattered writeback; commit error redirtying; flush_set/flush_all gather completion; discard_writeback waiting on TX commits; release/purge behavior; flusher threshold and age behavior; shutdown waiting for outstanding reads; and `verify_stats` after randomized operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osdc/ObjectCacher.cc -->
