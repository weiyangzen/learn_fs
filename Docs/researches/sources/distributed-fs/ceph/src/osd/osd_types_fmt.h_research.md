# `sources/distributed-fs/ceph/src/osd/osd_types_fmt.h`

## Purpose

`osd_types_fmt.h` supplies fmtlib formatters for selected OSD types declared in `osd_types.h`. It centralizes compact, allocation-conscious diagnostic formatting for request IDs, PG IDs, versions, object info/manifests, PG history/info, snap sets, scrub maps, and object stat summaries. It also bridges a few ostream-only types into fmt for fmt version 9 and newer.

## Important APIs And Types

- `fmt::formatter<osd_reqid_t>` renders `entity.inc:tid`.
- `fmt::formatter<pg_shard_t>` renders undefined shards as `?`, no-shard entries as the OSD id, and sharded entries as `osd(shard)`.
- `fmt::formatter<eversion_t>` renders `epoch'version`.
- `fmt::formatter<chunk_info_t>`, `object_manifest_t`, and `object_info_t` expose manifest, chunk, digest, allocation-hint, and per-shard-version details.
- `fmt::formatter<pg_t>` and `spg_t` render pool/seed and optional shard suffix.
- `fmt::formatter<pg_history_t>` and `pg_info_t` mirror the ostream summaries in `osd_types.h`.
- `fmt::formatter<SnapSet>` supports a `D` parse flag for verbose clone/overlap/snap detail.
- `fmt::formatter<ScrubMap::object>` recognizes `OI_ATTR` and `SS_ATTR`, hiding raw object-info bytes and decoding snapset bytes for readable output.
- `fmt::formatter<ScrubMap>` supports a `D` parse flag to include all objects.
- `fmt::formatter<object_stat_sum_t>` prints every stat field as a labeled tuple and backs an inline `operator<<`.
- For fmt >= 9, `pg_missing_set<TrackChanges>`, `pool_opts_t`, and `store_statfs_t` use `fmt::ostream_formatter`.

## Control Flow And State Behavior

The file has no persistent state beyond formatter booleans parsed from format specs. `SnapSet` and `ScrubMap` formatters implement small parse methods that consume a single `D` debug flag and switch between compact and verbose rendering. `ScrubMap::object` iterates attributes and treats object-info and snapset attributes specially, which prevents unreadable binary object-info dumps while still exposing decoded snapset state.

## Persistence Behavior

This header does not encode or persist data. Its behavior affects logs, asserts, debug messages, and operator output only. Because output text is often used in tests and operational debugging, format stability still matters, but it is not a wire/on-disk compatibility contract.

## Dependencies And Integration Points

It includes `common/hobject.h`, `include/types_fmt.h`, `osd/osd_types.h`, and fmt headers for chrono/ranges/std/ostream support. It is consumed by scheduler item formatting, PG/OSD logs, scrub diagnostics, and any code using `fmt::format()` with OSD types. The dependency on `OI_ATTR` and `SS_ATTR` couples scrub-map formatting to object-info/snapset attribute names from `osd_types.h`.

## Risks And Edge Cases

- Verbose scrub-map formatting can emit one line per object and each object's attributes; this is useful for debugging but risky in hot paths or large PGs.
- `ScrubMap::object` converts attribute buffers to strings; binary or very large attributes can be expensive or unreadable, although `OI_ATTR` is explicitly suppressed.
- `object_stat_sum_t` formatter must be kept in sync with fields in `object_stat_sum_t`; omitted fields reduce diagnostics and can break expectations in tests.
- `SnapSet` verbose formatting assumes maps contain clone metadata and prints `??` when related entries are missing, which is useful but may hide structural corruption unless tests assert it.
- The fmt version guards mean formatting support can differ across dependency versions.

## Test Signals

Compile coverage is the primary signal because these are template specializations. Unit tests or log-format tests that call `fmt::format()` on each specialized type, including `{:D}` for `SnapSet` and `ScrubMap`, are useful. Runtime scrub logs, PG-info logs, and scheduler-item logs provide integration signals that formatting compiles and does not recurse or dump raw binary unexpectedly.
