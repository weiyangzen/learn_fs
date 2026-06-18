# sources/cloud-native/nydus/storage/src/cache/state/persist_map.rs

Purpose: provides `PersistMap`, the low-level memory-mapped bitmap file used by `IndexedChunkMap` and `BlobRangeMap`. It manages file creation/opening, header validation, bit-level atomic readiness updates, all-ready accounting, and optional removal for non-persistent users.

Important APIs and control flow: `PersistMap::open` rejects zero counts, opens the file with create/truncate rules based on `create` and `persist`, computes expected header plus bitmap size, writes a header for empty files, rejects size mismatches, maps the file with `FileMapState`, repairs all-zero race-window files, validates v1 magic fields, counts ready bits unless the header says all-ready, calls `readahead`, and removes the file if `persist` is false. `set_chunk_ready` validates the index, loops with atomic compare-exchange on the containing byte, decrements `not_ready_count`, and calls `mark_all_ready` when the final bit is set. `is_chunk_ready` reads one bit using a high-bit-first mask.

State and persistence behavior: file format starts with a 4096-byte `Header` containing magic/version/all-ready fields, followed by one bit per managed item. `not_ready_count` is in-memory, derived at open. `mark_all_ready` currently syncs data but leaves header mutation commented, so all-ready persistence may require bit recount on reopen unless an existing header was already marked.

Dependencies and integration points: depends on Unix fd cloning, `FileMapState`, `AtomicU8` bitmap operations, `div_round_up`, and local `readahead`.

Risks and test signals: corrupt size/header is intentionally fatal. Atomic byte updates protect concurrent setters, but sync/header behavior is conservative. Tests in `indexed_chunk_map.rs` exercise file-size validation, new and existing headers, all-ready headers, v0 compatibility, and bit setting.
