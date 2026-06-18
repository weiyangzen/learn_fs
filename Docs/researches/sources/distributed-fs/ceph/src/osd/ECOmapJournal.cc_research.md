# sources/distributed-fs/ceph/src/osd/ECOmapJournal.cc

Purpose: `ECOmapJournal.cc` implements the in-memory journal that makes deferred OMAP updates visible for optimized EC pools while those updates live only in the PG log and have not yet been applied to the ObjectStore.

Important APIs and functions: `add_entry`, `remove_entry`, `remove_entry_by_version`, `clear`, `clear_all`, `has_omap_updates`, `get_value_updates`, `get_updated_header`, `append_delete`, `append_create`, `append_whiteout`, `trim_delete`, and `get_generation` are the main surface. Helper value types update versioned key values, merged removed ranges, and headers.

Control flow: writes append `ECOmapJournalEntry` objects to `entries`. Read-side calls process entries lazily through `process_entries`, folding insert/remove/range/header/clear operations into `key_map`, `removed_ranges_map`, and `header_map`, then erasing unprocessed entries. Removal APIs delete either queued entries or already-folded updates by matching versions. Range removal logic merges overlapping or open-ended intervals.

State and persistence: the journal is process-local memory, not durable storage. Durability comes from the PG log entry that also records the EC OMAP modification. `object_state_map` tracks outstanding delete generations and whiteout/lost-delete state used by PG backend OMAP generation handling.

Dependencies and integration: depends on `ECOmapJournal.h`, `bufferlist`, `hobject_t`, `eversion_t`, `OmapUpdateType`, Ceph decode helpers, and `DoutPrefixProvider`. `ECTransaction` adds entries; `ECBackend` merges journal state into ObjectStore OMAP reads; `PGBackend` trims/removes entries through backend hooks.

Risks: `process_entries` copies the entry list for logging but then iterates the live list; concurrent access is not protected here and relies on backend serialization. Removal of processed entries by version can erase only last-writer state, so overlapping versions require careful ordering. Open-ended range representation using `nullopt` must match ObjectStore iteration semantics.

Test signals: tests should cover lazy folding, clear-plus-header behavior, inserts after range deletes, deletes/whiteouts, clone visibility, remove-by-version before and after processing, and OMAP reads observing log-only updates.
