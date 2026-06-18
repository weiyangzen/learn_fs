# sources/distributed-fs/ceph/src/osd/scrubber/ScrubStore.cc

## Purpose
Implements persistent storage for scrub inconsistencies as shallow and deep OMAP databases on special PG temp objects, with cached reads through `MapCacher`.

## APIs and Control Flow
The constructor touches `scrub_<pgid>` and `deep_scrub_<pgid>` objects and initializes `OSDriver`/`MapCacher` backends. `add_object_error()` stores deep errors only during deep scrub and shallow-masked errors in the shallow DB. `add_snap_error()` stores snapset errors in shallow DB only. `flush()` writes staged results. `reinit()` clears shallow every scrub and deep only for deep scrubs. `get_errors()` merge-walks shallow and deep sorted keys, combining equal-object wrappers with `merge_encoded_error_wrappers()`.

## State, Dependencies, and Integration
Persistent state is OMAP entries on two hobjects. Runtime state includes `current_level`, DB optionals, caches, and staged results. It depends on `ObjectStore`, `OSDriver`, `MapCacher`, hobject string ordering, librados inconsistency wrappers, and `PgScrubber` logging. `PgScrubber::persist_scrub_results()` writes; `PrimaryLogScrub::get_store_errors()` reads.

## Risks and Test Signals
Pagination depends on `hobject_t::to_str()` ordering and virtual boundary keys. Merge policy for newer shallow versus deep read-failure versions has an unresolved note. Tests should cover level-specific clearing, flush/cleanup transactions, snap/object key ranges, pagination, and same-key wrapper merging.
