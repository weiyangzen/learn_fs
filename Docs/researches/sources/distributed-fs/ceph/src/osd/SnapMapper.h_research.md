# sources/distributed-fs/ceph/src/osd/SnapMapper.h

## Purpose
`SnapMapper.h` declares the snap mapper and its object-store driver. The mapper owns the durable index that relates cloned objects to the snapshots that reference them, enabling snap trim, scrub verification, and PG-log-driven maintenance.

## Important APIs, Types, And Functions
`OSDriver` implements `MapCacher::StoreDriver<std::string, bufferlist>` and exposes `OSTransaction`, which translates cached key set/remove operations into omap operations on a fixed collection/object. `SnapMapper::object_snaps` encodes object-to-snaps records. `SnapMapper::Mapping` encodes snap-to-object records. `SnapMapper::Scrubber` scans mapping and purged-snap objects to identify stray mappings. Public `SnapMapper` APIs include constructor, `update_bits()`, `flush_and_reset_backend()`, `update_snaps()`, `add_oid()`, `get_next_objects_to_trim()`, `remove_oid()`, legacy `get_snaps()`, `update_snap_map()`, and `SnapMapReaderI` implementations.

## Control Flow
Callers create a mapper with PG hash match bits, pool, and shard. On PG split/merge, `update_bits()` regenerates prefixes. PG log application calls `update_snap_map()` to add, modify, replace, promote, or remove clone mappings. Snap trim calls `get_next_objects_to_trim()` for a specific snap until it returns `nullopt`. Scrub calls the reader methods and may use `Scrubber` support to compare mappings against purged snap intervals.

## State And Persistence Behavior
The header documents two persistent key spaces: `OBJECT_PREFIX + object` for object-to-snap sets and `MAPPING_PREFIX + pool + snap + object` for snap enumeration. Sharded EC objects include a shard prefix; replicated objects omit it. The `backend` cache is mutable so const reads can still fill cache state, while writes are flushed into caller-owned transactions. The prefix iterator is in-memory state that optimizes repeated trim scans.

## Dependencies And Integration Points
Dependencies include `MapCacher`, `ObjectStore`, `hobject_t`, `OSDMap`, `SnapMapReaderI`, Ceph encoding, and optional Crimson store types. Integration points are `PrimaryLogPG`/PG log updates, snap trimmer, scrubber, and OSD map purged snap tracking.

## Risks And Test Signals
Interface risks include stale cached writes if `flush_and_reset_backend()` is missed, incorrect prefix generation after split/merge, and legacy callers interpreting inconsistent data as `-ENOENT`. Tests should compile both Crimson and classic variants where applicable, verify key strings for replicated and EC shards, and exercise all public mutation/read methods.
