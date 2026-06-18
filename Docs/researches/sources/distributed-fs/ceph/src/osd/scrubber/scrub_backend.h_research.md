# sources/distributed-fs/ceph/src/osd/scrubber/scrub_backend.h

## Purpose

`scrub_backend.h` declares the scrub comparison backend interface and the data structures used to carry object, chunk, auth-selection, digest-fix, and inconsistency state between the scrubber frontend and the backend implementation.

## Important APIs, types, and functions

- `ScrubBeListener` is the backend's view of `PgScrubber`: logging, primary check, PG id/map, stats updates, and digest-fix submission.
- `PgScrubBeListener` is referenced from `scrubber_common.h` and supplies PG/pool/backend services such as `force_object_missing()`, EC helpers, and PG info.
- `data_omap_digests_t`, `digests_fixes_t`, `shard_info_map_t`, `shard_to_scrubmap_t`, `auth_peer_t`, `wrapped_err_t`, and `inconsistent_objs_t` define the backend's core collection vocabulary.
- `omap_stat_t` and `error_counters_t` collect session/chunk statistics.
- `objs_fix_list_t` returns both inconsistent object/snapset wrappers and SnapMapper fix orders from `scrub_compare_maps()`.
- `shard_as_auth_t` carries possible-auth status, error text, decoded `object_info_t`, map iterator, and digest. It distinguishes not-found, not-usable, usable, and EC non-primary not-usable-without-error cases.
- `auth_selection_t` holds the selected auth iterator/shard/OI plus the per-shard error map and a `digest_match` flag.
- `object_scrub_data_t` stores per-object missing/inconsistent shard sets and whether digest repair is needed.
- `scrub_chunk_t` owns received maps, union object set, missing digest fixes, authoritative peers, inconsistency wrappers, counters, EC digest map, and large-omap warning state.
- `ScrubBackend` exposes chunk setup, map decode, metadata cleanup on replicas, map comparison, inconsistent-object repair, omap stats, and authoritative-peer count.

## Control flow

The header shows the intended lifecycle. A `ScrubBackend` is created for a scrub session. `new_chunk()` creates per-chunk state and a local `ScrubMap`. The scrubber fills the local map, decodes remote maps with `decode_received_map()`, then the primary calls `scrub_compare_maps()` to get object inconsistencies and snap fixes. When in repair mode, the caller can invoke `scrub_process_inconsistent()` to repair selected missing/inconsistent objects.

Private helpers divide the backend into phases: merge maps, clean metadata map, compare object maps, select auth, build EC digest maps, decide digest repair, process snapshots, scan SnapMapper, and translate logical to on-disk sizes.

## State and persistence behavior

The class stores configuration and pool identity for the session, per-chunk state in `std::optional<scrub_chunk_t>`, session-wide omap stats, authoritative peer mapping, missing/inconsistent mappings, cleaned metadata carry-over, and EC digest sizing. The header does not define durable state itself; durable changes are delegated through listener calls for digest fixes, stats, SnapMapper fixes returned to the caller, and forced missing objects.

## Dependencies and integration points

This header sits between `PgScrubber`/`PrimaryLogScrub`, `ScrubMap`, `PGPool`, `OSDMap`, `SnapMapReaderI`, `MOSDRepScrubMap`, EC utilities, and Ceph formatting/logging. `friend class PgScrubber` and `friend class TestScrubBackend` indicate tight integration with scrub orchestration and unit-style testing.

## Risks

The API assumes `this_chunk` is initialized before map access, primary-only methods are only called on primaries, and listeners outlive the backend. `shard_as_auth_t` embeds an iterator into `received_maps`, so it depends on map lifetime and no invalidating mutations. Formatter text is test-sensitive. EC behavior depends on correct `m_ec_digest_map_size`, pool type flags, hinfo requirements, and `logical_to_ondisk_size()` translation.

## Test signals

Tests should validate construction for primary versus replica, chunk reset semantics, auth-selection formatting, missing-digest list formatting, empty/single-acting-set behavior, EC digest map sizing only on deep EC scrub with CRC support, and that `scrub_compare_maps()` returns both object and snap fix lists.
