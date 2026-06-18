# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-core.c

## Purpose

This file provides static delta core operations: checksum-array parsing, delta listing, index listing, offline execution, part opening and decompression, human-readable dumping, signature verification, deletion, existence checks, superblock digest calculation, and delta index regeneration.

## Important APIs, Types, and Functions

- `_ostree_static_delta_parse_checksum_array()` validates packed object type/checksum arrays.
- `ostree_repo_list_static_delta_names()` and `ostree_repo_list_static_delta_indexes()` enumerate repository delta and index layouts.
- `_ostree_repo_static_delta_part_have_all_objects()` checks whether a part can be skipped.
- `_ostree_repo_static_delta_is_signed()` and `_ostree_repo_static_delta_verify_signature()` parse and verify signed superblocks.
- `ostree_repo_static_delta_execute_offline_with_signature()` applies an already-downloaded delta directory or superblock file.
- `_ostree_static_delta_part_open()` verifies, decompresses, and parses a part payload.
- `_ostree_delta_get_endianness()` and `_ostree_delta_needs_byteswap()` interpret delta endianness metadata or historical heuristics.
- `_ostree_repo_static_delta_dump()`, `_ostree_repo_static_delta_delete()`, `_ostree_repo_static_delta_query_exists()`, `ostree_repo_static_delta_verify_signature()`, and `ostree_repo_static_delta_reindex()` expose maintenance behavior.

## Control Flow

Offline execution opens either a delta directory or a direct superblock file. It detects signed containers, optionally enforces `core.sign-verify-deltas`, verifies with the supplied `OstreeSign`, and extracts the raw superblock. It validates from/to checksum fields, ensures the source commit exists when specified, writes detached target commit metadata if present, and writes the target commit object if missing. It rejects offline execution when fallback entries are present. For each part header, it checks the part version, skips execution if every object already exists, opens inline or external part data, validates external checksums unless skipped, and invokes `_ostree_static_delta_part_execute()`.

Part opening reads the first byte as a compression type. Uncompressed parts can be memory-mapped or sliced from inline bytes. LZMA parts are decompressed into anonymous tmpfile-backed bytes and parsed as `OSTREE_STATIC_DELTA_PART_PAYLOAD_FORMAT_V0`. If checksum validation is enabled, the checksum input stream covers the bytes consumed and is compared with the expected part checksum.

Reindexing takes a shared repo lock, ensures `core.indexed-deltas` is true in config, enumerates deltas and old indexes, groups deltas by target commit, computes each superblock digest, writes reproducible sorted index variants, and removes stale indexes. Existing identical index content is left untouched to reduce write and sync load.

## State and Persistence Behavior

Core operations read and write repository files under `deltas/` and `delta-indexes/`. Offline execution writes metadata, content, and detached metadata objects into object storage through normal repo write APIs. Delete removes an entire delta directory. Reindex writes or unlinks index files under their content-addressed paths and may update repo config to enable indexed deltas.

## Dependencies and Integration Points

This file sits between generated delta artifacts and the low-level part executor. It depends on static delta private formats, checksum input streams, LZMA decompression, GLib variants, fd-relative filesystem helpers, repo object storage APIs, and the signing abstraction. Pull/summary logic can consume the delta indexes generated here through the `ostree.static-deltas` metadata key.

## Risks and Edge Cases

Signed and unsigned superblocks share entry points, so mis-detecting signatures can produce confusing errors. Inline parts intentionally skip part checksum validation, relying on metadata integrity and outer signatures where applicable. Historical deltas may lack endianness metadata, so heuristic byteswap detection remains a compatibility risk. Offline deltas with fallback entries are rejected because they require network object fetching. Reindex must handle stale indexes and deltas disappearing under prune, hence the shared lock.

## Test Signals

Tests should cover signed and unsigned offline execution, mandatory signature verification, missing source commit failure, fallback rejection, already-have-all-objects part skipping, compressed and uncompressed part opening, checksum mismatch detection, inline part handling, dump output across endian variants, delta deletion and existence checks, stale index removal, reproducible sorted indexes, and no-op index rewrite when content is unchanged.
