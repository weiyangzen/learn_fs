# sources/distributed-fs/ceph/src/osd/ECOmapJournal.h

Purpose: `ECOmapJournal.h` declares the optimized EC OMAP journal and its versioned helper records. The header documents why EC OMAP updates are initially recorded in PG log state and applied later, and why reads must merge ObjectStore state with in-flight journaled updates.

Important APIs and types: `ECOmapJournalEntry` stores one versioned OMAP mutation batch: clear flag, optional header, and encoded update operations. `ECOmapValue` stores a versioned optional value, with `nullopt` representing removal. `ECOmapRemovedRanges` stores versioned key ranges, including open-ended ranges. `ECOmapHeader` stores the latest versioned header. `ECOmapJournal` exposes entry addition/removal, read-side value/header extraction, delete generation tracking, and iterators over unprocessed entries.

Control flow: write generation builds entries from PG transaction OMAP changes. Read paths call `get_value_updates` and `get_updated_header`, which cause lazy processing. PG cleanup paths call remove/trim methods as log entries become safe or deletes are resolved.

State and persistence: all maps are in-memory indexes keyed by `hobject_t`. Persistent authority remains the PG log and eventual ObjectStore application; the journal is a visibility bridge during the deferred-apply window.

Dependencies and integration: uses Ceph `bufferlist`, `hobject_t`, `eversion_t`, `version_t`, `gen_t`, and `OmapUpdateType`. `ECTransaction`, `ECBackend`, `ECSwitch`, and `PGBackend` are the main integration points.

Risks: callers must understand the distinction between unprocessed and processed entries. The public `begin_entries`/`end_entries` call `entries.at`, so callers must guard with `has_unprocessed_entries` or know entries exist. No locking is declared in the type.

Test signals: header-level API coverage should include construction of entries/values/ranges/headers, `entries_size`, `has_unprocessed_entries`, iterator preconditions, and delete generation return behavior.
