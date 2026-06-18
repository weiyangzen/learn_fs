# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_dedup_table.h

## Purpose
`rgw_dedup_table.h` declares the compact dedup table key and value layout plus operations for duplicate detection and representative-record tracking.

## Important APIs, Types, And Functions
`key_t` is a 24-byte packed key made from object data MD5 high and low words, object size in 4 KiB units, multipart part count, and storage-class index. It uses raw `memcmp()` equality and `md5_low` as the hash.

`dedup_table_t::value_t` is an 8-byte packed value containing the representative `disk_block_id_t`, duplicate count, record id, and flags. Flags track valid strong hash, shared manifest, and occupied state. Public accessors expose duplicate count, source block id, source record id, shared-manifest state, and valid-hash state.

The table API includes `add_entry()`, `update_entry()`, `get_val()`, `inc_count()`, `set_shared_manifest_src_mode()` declaration, `set_src_mode()`, `count_duplicates()`, and `remove_singletons_and_redistribute_keys()`.

## Control Flow
Keys are generated from disk records during MD5-shard processing. The table first estimates duplicates, then after singleton removal and redistribution acts as an index from target records to source records for actual dedup or deeper verification.

## State And Persistence Behavior
The table layout is packed and size-asserted, but it is not persisted as a stable RADOS object by this header. It is a memory view over caller-owned raw memory. Values reference persistent slab records, not object data directly.

## Dependencies And Integration Points
It depends on disk-store identifiers and dedup stats. It is used by the background dedup pipeline and full-dedup paths that set source flags after strong hash or shared manifest checks.

## Risks And Edge Cases
`key_t` equality compares all bytes, so padding must be initialized; the constructor sets `pad8 = 0`, but default-constructed or manually filled keys require care. `md5_low` as the only hash is fast but can be collision-heavy for adversarial inputs. The declared `set_shared_manifest_src_mode()` is not defined in the visible implementation, so users should confirm link coverage or remove stale API.

## Test Signals
Tests should assert packed sizes, key equality with initialized padding, hash consistency, value flag transitions, duplicate group source selection, and public API link coverage.
