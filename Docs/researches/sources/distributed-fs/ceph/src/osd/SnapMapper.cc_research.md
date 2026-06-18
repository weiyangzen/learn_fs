# sources/distributed-fs/ceph/src/osd/SnapMapper.cc

## Purpose
`SnapMapper.cc` implements Ceph OSD snap clone indexing. It maintains a bidirectional omap-backed mapping from object to snap set (`OBJ_...`) and from snap/object to object (`SNA_...`) so snap trim can enumerate objects by snap and scrub can verify mapper consistency.

## Important APIs, Types, And Functions
`OSDriver` adapts `ObjectStore` or Crimson store access to `MapCacher::StoreDriver`, providing `get_keys()`, `get_next()`, and `get_next_or_current()`. `SnapMapper` implements key formatting (`get_prefix()`, `to_raw_key()`, `to_object_key()`), encoding/decoding (`object_snaps`, `Mapping`, `from_raw()`), reads (`get_snaps_common()`, legacy and `tl::expected` `get_snaps()`), consistency checking (`get_snaps_check_consistency()`), writes (`set_snaps()`, `clear_snaps()`, `add_oid()`, `update_snaps()`, `remove_oid()`), trim enumeration (`get_next_objects_to_trim()`, `get_objects_by_prefixes()`), PG-log application (`update_snap_map()`), and purged snap tracking (`record_purged_snaps()` plus lookup/key helpers).

## Control Flow
Object updates enter through `update_snap_map()` from PG log handling. Deletes remove both `OBJ_` and all corresponding `SNA_` keys. Clone/promote entries call `add_oid()`, while modify/replace entries call `update_snaps()`. `update_snaps()` removes obsolete `SNA_` keys and tolerates a missing object entry by rebuilding from scratch to avoid creating one-sided state. Snap trim calls `get_next_objects_to_trim()` repeatedly for a snap; the mapper walks hash prefixes, returns up to `max` objects, preserves prefix iterator progress, and performs a second pass when it appears empty.

## State And Persistence Behavior
Durable state is stored as omap keys. `OBJ_` keys encode `object_snaps { oid, snaps }`; `SNA_` keys encode `Mapping { snap, hoid }` and sort by pool/snap/shard/object string. Purged snap intervals are stored under `PSN_` keys, with adjacent intervals merged. `MapCacher` buffers changes into caller-provided transactions; `flush_and_reset_backend()` persists pending state on interval changes. In-memory state includes `mask_bits`, `match`, pool/shard info, generated hash prefixes, `prefix_itr`, and `last_key_checked`.

## Dependencies And Integration Points
The mapper integrates `ObjectStore`, `MapCacher`, `hobject_t`, PG log entries, scrub reader interface, OSD map snap intervals, and optional Crimson store APIs. `PrimaryLogPG` updates it while logging operations, snap trim reads it to find clones, and scrub uses the reader interface for consistency checks and repair planning.

## Risks And Test Signals
Risks include key-format compatibility, shard-prefix parsing, one-sided `OBJ_`/`SNA_` corruption, iterator state across snap changes, split/merge `mask_bits` updates, purged interval merging, and backend iteration errors. Tests should cover encode/decode compatibility, add/update/remove idempotence, trim enumeration across prefixes, scrub consistency mismatch detection, recovery of missing mapper entries, purged snap interval joins, and Crimson/non-Crimson driver behavior.
