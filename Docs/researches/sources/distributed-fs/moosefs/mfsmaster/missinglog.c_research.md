## sources/distributed-fs/moosefs/mfsmaster/missinglog.c

Purpose: keeps a bounded, deduplicated, two-window log of missing chunk references for reporting. It records `(chunkid, inode, index, type)` tuples, swaps the active set into a previous set, and serializes the previous set to status clients.

Important APIs and types: `mlogentry` stores one tuple. Static globals hold active and previous open-addressed hash tables, table sizes, element counts, capacity, and a `blocked` flag. `missing_log_insert` deduplicates and inserts into the active hash. `missing_log_swap` rotates active to previous and clears a new active table. `missing_log_getdata` either returns serialized size after pruning entries no longer missing, or writes tuples to a buffer. `missing_log_reload` reads `MISSING_LOG_CAPACITY`; `missing_log_init` initializes and registers reload.

Control flow: insertion returns early when blocked, full, or chunk id zero. The hash and displacement mix inode/index/chunk id and use odd displacement for probing. Reload reallocates the active table when capacity changes and blocks one cycle after a live resize to avoid mixing old/new windows. Size calculation also calls `chunk_remove_from_missing_log` to drop entries already resolved.

State and persistence behavior: state is memory-only and intentionally lossy/bounded. It is not serialized in metadata. Reload can clear active data when capacity changes.

Dependencies and integration points: depends on `cfg`, `main` reload registration, `datapack` serialization, `chunks` for pruning, and `mfslog`. Status/reporting code can call `missing_log_getdata`; chunk/filesystem paths insert missing references.

Risks: the table has no dynamic growth beyond configured capacity; once full, new events are dropped. `mloghashprev` is initially NULL/size zero, so consumers should tolerate empty previous windows until the first swap. The open addressing code assumes `mloghashsize` is a power of two and nonzero after reload.

Test signals: test deduplication, capacity bounds/clamping, resize blocking, swap behavior, size vs data modes, optional `type` byte mode, and pruning via a fake `chunk_remove_from_missing_log`.
