# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index.c

## Purpose
Implements the core UDS index engine. It dispatches requests to per-zone workers, coordinates sparse-cache barrier messages, manages open chapter rollover, writes closed chapters through a writer thread, loads or rebuilds indexes, and exposes save/free/stats/enqueue operations to the session layer.

## Important APIs, Types, And Functions
Public functions are `uds_make_index()`, `uds_free_index()`, `uds_wait_for_idle_index()`, `uds_save_index()`, `uds_replace_index_storage()`, `uds_get_index_stats()`, and `uds_enqueue_request()`. Private `struct chapter_writer` owns the writer thread, condition variable, per-zone completed chapter pointers, an open-chapter index, and collated record buffer. `struct index_zone` and `struct uds_index` are declared in `index.h`.

Core helpers include `triage_request()`, `dispatch_index_request()`, `execute_zone_request()`, `search_index_zone()`, `remove_from_index_zone()`, `open_next_chapter()`, `close_chapters()`, `load_index()`, `rebuild_index()`, `replay_volume()`, `replay_chapter()`, and `replay_record()`.

## Control Flow
Requests enter at `uds_enqueue_request()`. Sparse multi-zone indexes use a triage queue to detect when a sampled record points to a sparse chapter that needs caching; triage enqueues one barrier message per zone before forwarding the original request. Zone workers handle control messages or normal requests. Normal search/update/delete first uses the volume index to locate a likely chapter, resolves the record in the open chapter, writing chapter, dense volume pages, or sparse cache, then updates/removes volume-index entries and the open chapter as request type requires.

When an open chapter zone fills or receives a chapter-closed announcement, `open_next_chapter()` swaps active and writing chapters, advances per-zone chapter counters, announces closure to other zones, and hands the old chapter to the writer. The writer waits until all zones have submitted the same chapter, optionally discards a saved open chapter, collates and writes the chapter to the volume, advances global chapter counters, and wakes waiting zones.

Opening creates layout, volume, zones, volume index, queues, and writer thread. Loading restores saved state; failed loads under `UDS_LOAD` trigger rebuild by scanning volume chapter boundaries, replaying record pages, and rebuilding the page map.

## State And Persistence
The index tracks global and per-zone oldest/newest virtual chapters, `need_to_save`, `has_saved_open_chapter`, `last_save`, and `prev_save`. Clean saves are delegated to `index-layout.c`; dirty state begins on request execution. Rebuild reconstructs volatile volume-index/page-map state from persistent volume chapters. The saved open chapter is invalidated after the first post-load chapter write so future unclean shutdowns require recovery.

## Dependencies And Integration Points
Depends on `index-layout`, `volume`, `volume-index`, `open-chapter`, `sparse-cache`, request queues, hash utilities, allocation, and logging. It is called by `index-session.c` and calls into storage-facing volume APIs for cached index/record pages, chapter writes, rebuild boundaries, prefetching, and storage replacement.

## Risks
The most delicate area is coordination across zone workers and the writer thread: zones may not get more than one chapter ahead, and all zones must participate in sparse-cache barriers. Requeued requests cache location state that may become stale and must be invalidated when chapter advice changes. Volume-index collisions and chapter-index overflow are intentionally lossy in some cases, so false misses or dropped dedupe opportunities are expected but must not corrupt metadata. Save requires requests to be drained; calling it with active mutation would persist inconsistent open-chapter and volume-index state.

## Test Signals
Exercise all request types, open-chapter hits, writing-chapter hits, dense lookups, sparse lookups, collision and overflow handling, chapter rollover with multiple zones, sparse barrier ordering, rebuild from unclean shutdown, no-rebuild failure on dirty state, save/load round trips, stats memory accounting, and storage replacement.
