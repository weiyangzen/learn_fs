# sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.cc

## Purpose

`scrub_backend.cc` implements `ScrubBackend`, the comparison and repair backend used by `PgScrubber` once scrub maps have been built. It decodes replica maps, merges primary and replica object listings into a per-chunk authoritative object set, chooses an authoritative copy for each object, compares object metadata/data digests/snapsets/hinfo/attributes across shards, records inconsistencies, schedules digest and snap mapper fixes, and marks bad peers missing during repair.

## Important APIs, types, and functions

- `scrub_chunk_t::scrub_chunk_t()` initializes per-chunk state and installs an empty local `ScrubMap` under the current `pg_shard_t`.
- Primary and replica `ScrubBackend` constructors bind the scrubber listener, PG backend listener, pool metadata, local shard, scrub level, repair mode, and EC optimization flags. The primary constructor also records acting shards excluding itself and sizes the EC CRC digest map for deep EC scrub when supported.
- `new_chunk()`, `get_primary_scrubmap()`, and `decode_received_map()` manage the current chunk's map collection.
- `scrub_compare_maps()` is the primary comparison entry point. It inserts the local map into cleaned metadata, merges all received maps, calls `update_authoritative()`, creates a metadata-safe map via `clean_meta_map()`, validates snapshot metadata, and returns inconsistent-object wrappers plus snap mapper fixes.
- `scrub_process_inconsistent()` and `repair_object()` are the repair path. They cluster-log a summary, require `m_repair`, then call `PgScrubBeListener::force_object_missing()` for shards in `m_missing` or `m_inconsistent`.
- `select_auth_object()` and `possible_auth_shard()` choose an authoritative shard. They prefer primary first, then highest object version, then richer digest information, while rejecting shards with read/stat/OI/snapset/hinfo/size errors or non-primary EC status.
- `compare_obj_in_maps()`, `match_in_shards()`, and `compare_obj_details()` classify per-object discrepancies and fill `inconsistent_obj_wrapper`/`shard_info_wrapper`.
- `setup_ec_digest_map()` performs EC-specific CRC reconstruction/verification for deep scrub with EC plugins that support CRC encode/decode.
- `scrub_snapshot_metadata()`, `process_clones_to()`, `scan_snaps()`, `scan_object_snaps()`, and `clean_meta_map()` validate head/clone ordering, snapset contents, clone sizes/overlap, SnapMapper consistency, and partial chunk metadata boundaries.

## Control flow

The active scrub FSM builds a local map and receives replica maps, then calls `scrub_compare_maps()`. That function constructs `all_chunk_objects` from every map, then `update_authoritative()` either just accumulates omap stats for a single-shard acting set or invokes `compare_smaps()` for multi-shard comparison. `compare_smaps()` iterates all object ids and calls `compare_obj_in_maps()`.

For each object, the backend clears `m_current_obj`, selects an auth object, optionally validates EC CRC relationships, compares every shard against the auth object, records missing shards, object-level discrepancies, digest mismatches, snapset/hinfo/object-info inconsistencies, and possible digest repair requests. If there are missing or inconsistent shards, `inconsistents()` stores authoritative peers in the current chunk and records `m_missing`/`m_inconsistent`; if replicas agree but object info digests are stale, it may queue digest fixes instead. After object comparison, `update_authoritative()` writes selected authoritative object entries into `m_cleaned_meta_map` so snapshot metadata is validated against the selected good copy.

Snapshot validation walks the cleaned map in reverse object order, treating head objects as snapset anchors and clone entries as expected reverse-ordered snap ids. It logs missing or unexpected clones, validates clone sizes and overlap accounting, updates scrub stats, submits digest fixes, and leaves incomplete clone groups in `m_cleaned_meta_map` when the chunk ended before the full clone set.

## State and persistence behavior

Most state is per scrub session or per chunk. `this_chunk` owns received maps, union object ids, per-chunk authoritative peer lists, inconsistency wrappers, error counters, EC digest data, and queued digest fixes. Session-wide state includes `m_auth_peer`, `m_missing`, `m_inconsistent`, `m_cleaned_meta_map`, and accumulated `m_omap_stats`.

The backend does not directly persist scrub state. Persistence effects are delegated: `submit_digest_fixes()` asks the scrubber to update data/omap digest metadata, SnapMapper fix lists are returned to the caller, `force_object_missing()` causes PG recovery/repair machinery to rebuild bad shards, and `add_to_stats()` updates PG object stats from scrubbed metadata.

## Dependencies and integration points

This file is tightly coupled to `ScrubMap`, `object_info_t`, `SnapSet`, `MOSDRepScrubMap`, `PGPool`, `PG`/`PrimaryLogPG` services exposed through `PgScrubBeListener`, `SnapMapReaderI`, Ceph logging, EC utility APIs, and inconsistency wrapper types from `osd_types`. It is called from the active scrub workflow after `build_primary_map_chunk()`/replica map delivery and before `PgScrubber` finalizes a chunk.

## Risks

Auth selection is correctness-critical: choosing a corrupt, stale, or non-primary EC shard as auth can drive false repair. EC CRC handling is complex and depends on plugin behavior, padding, legacy hinfo rules, and available shard sets. Snapshot metadata validation relies on object ordering and careful partial-chunk handling; mistakes can emit false clone errors or skip real ones. Repair calls mark objects missing rather than copying data directly, so wrong `m_missing`/`m_inconsistent` classification can trigger unnecessary recovery. Some error paths abort the OSD on unexpected decode/backend failures, which is intentional but high impact.

## Test signals

Comments call out tests that depend on log text, including scrub map auth-selection formatting and `qa/standalone/scrub/osd-scrub-snaps.sh` grepping `scan_snaps()` messages. Useful tests would cover replicated digest mismatch repair, stale digest age limits, missing/corrupt OI/SS/hinfo attributes, optimized and legacy EC sizes, EC CRC encode/decode mismatch cases, partial clone sets at chunk boundaries, SnapMapper add/update/overwrite fixes, and repair-mode `force_object_missing()` behavior.
