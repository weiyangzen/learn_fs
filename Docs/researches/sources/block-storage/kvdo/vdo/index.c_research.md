# File Research: sources/block-storage/kvdo/vdo/index.c

Core UDS index engine: request dispatch, zone coordination, chapter closing/writing, clean-load handling, and rebuild replay.

Key responsibilities:
- Routes requests through optional sparse triage queue, per-zone index queues, and message queues.
- Implements sparse-cache barrier coordination for multi-zone sparse indexes.
- Maintains per-zone open and writing chapters, plus index-level oldest/newest virtual chapter counters.
- Handles zone messages for sparse-cache barriers and chapter-close announcements.
- Searches and updates the volume index, open chapters, writing chapters, dense page cache, and sparse cache for post/update/query/delete requests.
- Runs a chapter-writer thread that waits for all zones to close a chapter, writes the closed chapter to the volume, expires old chapters, and wakes zones.
- Creates/free index zones, queues, volume, volume index, layout, and chapter writer.
- Loads cleanly saved index state via `load_index_state()`, or rebuilds by replaying chapters from the volume if clean load fails and rebuild is allowed.
- Saves index state on demand with `save_index()`.
- Exposes queue enqueueing and stats aggregation.

Important behavior:
- For a request, the volume index gives a virtual chapter hint; the engine resolves it against open chapter, recently writing chapter, sparse cache, or dense volume page cache.
- Query-without-update stops after lookup; post/update may move found records into the current open chapter and update the volume index to the newest chapter.
- Delete removes the volume-index record and removes/marks the record in the open chapter if needed.
- When a zone fills or is told another zone closed the current chapter, it swaps open/writing chapters, announces closure to peers, advances per-zone chapter counters, and possibly expires old chapters.
- The chapter writer only writes once all zones submit a chapter. It discards the saved open chapter after the first post-load chapter close.
- Rebuild finds valid volume chapter boundaries, sets virtual chapter range, rebuilds the page map, and replays record pages into the volume index, skipping non-sample records for chapters that will be sparse.
- `make_index()` marks load context ready after successful create/load/rebuild and initializes all zones to the index chapter range.
- `save_index()` waits for idle, records `last_save`, writes layout state, and sets `has_saved_open_chapter`.

Dependencies:
- Depends on layout, volume, open chapter, volume-index operations, sparse cache, request queues, geometry/hash helpers, and logging.

Notable risks:
- The chapter-writer rendezvous is subtle: per-zone and global newest/oldest chapter counters must stay coherent.
- Sparse-cache barriers allocate synthetic requests and assert allocation success in one path.
- `try`/requeue semantics rely on request fields such as `location`, `virtual_chapter`, and `requeued` remaining coherent across queue passes.
- `replay_record()` may intentionally lose duplicate/overflow records during rebuild.
- `index->need_to_save` is set when executing zone requests before dispatch; failures can mark sessions disabled but still leave save state dirty.
