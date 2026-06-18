# `sources/distributed-fs/ceph/src/osd/recovery_types.h`

## Purpose

`recovery_types.h` defines backfill interval containers used by OSD recovery. A backfill interval represents objects in `[begin, end)` observed at a specific scan version. The header separates primary and replica representations because primaries may track multiple shard/version pairs per object for optimized erasure-coded pools, while replicas track a single version per object.

## Important APIs And Types

- `template <typename T> class BackfillInterval` stores `eversion_t version`, `hobject_t begin`, `hobject_t end`, and `T objects`.
- Common helpers include `clear_objects()`, `reset(start)`, `empty()`, `extends_to_end()`, `trim_to(soid)`, `trim()`, abstract `clear()`, abstract `pop_front()`, and abstract `dump()`.
- `PrimaryBackfillInterval` uses `std::multimap<hobject_t, std::pair<shard_id_t, eversion_t>>`.
- `ReplicaBackfillInterval` uses `std::map<hobject_t, eversion_t>`.
- `operator<<` prints the interval bounds and object count/map.
- For fmt >= 9, both concrete interval types use `fmt::ostream_formatter`.

## Control Flow And State Behavior

`BackfillInterval::reset()` clears the interval and sets both bounds to the requested start. `trim()` advances `begin` to the first object key or to `end` when empty. `trim_to()` first normalizes `begin`, then repeatedly drops entries whose object key is `<= soid`. The concrete `pop_front()` behavior differs: primary intervals erase all entries for the first object key because multiple shards may be represented for the same object, while replica intervals erase only the first map entry.

Primary intervals model optimized EC partial-write behavior: an object may have a `NO_SHARD` baseline version plus shard-specific overrides. Replica intervals model one shard's object versions. Both `dump()` methods emit formatter objects containing begin/end and per-object entries.

## Persistence Behavior

This header does not define `WRITE_CLASS_ENCODER` encoders for the interval classes; they are transient recovery/backfill scan containers. The object and version element types are persistent elsewhere, but these classes are used as in-memory progress/state during recovery work.

## Dependencies And Integration Points

The file includes `<map>` and `osd_types.h`, relying on `hobject_t`, `eversion_t`, `shard_id_t`, `ceph_assert`, `Formatter`, and stream support. It is integrated with OSD backfill/recovery code that scans object ranges, trims already-processed entries, and ships or compares interval contents between primary and replicas.

## Risks And Edge Cases

- `pop_front()` asserts that the interval is non-empty; callers must guard empty intervals.
- Primary `pop_front()` erases all entries for the first object key. This is correct for per-object advancement but would be wrong for code expecting shard-by-shard advancement.
- `trim_to()` removes `<= soid`, not just `< soid`; callers must pass the last completed object, not the next object to retain.
- `extends_to_end()` relies on `end.is_max()`, so scan code must set `end` consistently for terminal intervals.
- Since the containers are maps, ordering follows `hobject_t` comparison and must match objectstore scan ordering.

## Test Signals

Backfill tests should cover empty/unpopulated intervals, terminal intervals, `trim_to()` boundary behavior, primary intervals with multiple entries for one object, replica single-entry trimming, and dump/stream formatting. EC optimized-pool tests are important because shard-specific primary interval entries are the unusual case.
