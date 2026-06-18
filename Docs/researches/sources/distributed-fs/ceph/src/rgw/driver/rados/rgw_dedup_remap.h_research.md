# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_remap.h

## Purpose
`rgw_dedup_remap.h` provides a compact string-to-`uint8_t` remapping helper. Dedup uses it where variable strings, especially storage class names, must fit into byte-sized record or table keys.

## Important APIs, Types, And Functions
`remapper_t` is constructed with a maximum number of entries. `remap()` returns the existing index for a key, assigns the next index when capacity remains, or returns `NULL_IDX` and increments an overflow counter when full. `NULL_IDX` is `0xFF`.

## Control Flow
On every key lookup, `remap()` first checks the unordered map. New keys are assigned monotonically from zero to `d_max_entries - 1`. Overflow is reported through the caller-provided counter and debug log.

## State And Persistence Behavior
The remap table is in-memory only. Persisted records store the remapped byte, so the same remapper instance and mapping scope must be used consistently while building or processing a table.

## Dependencies And Integration Points
The class depends on `DoutPrefixProvider` for debug logging and is used by dedup table and full-dedup paths that need compact storage-class or similar identifiers.

## Risks And Edge Cases
Capacity above 255 is unsafe because the return type is `uint8_t` and `0xFF` is reserved as null. The constructor accepts `uint32_t`, so callers are responsible for passing a bound compatible with byte storage. Overflow must be handled by the caller or table keys may become invalid.

## Test Signals
Tests should cover repeated key stability, assignment order, exact-capacity behavior, overflow counting, and the reserved `NULL_IDX` value.
