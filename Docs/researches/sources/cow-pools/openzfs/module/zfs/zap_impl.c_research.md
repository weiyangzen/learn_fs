# File Research: sources/cow-pools/openzfs/module/zfs/zap_impl.c

## Purpose
Provides shared ZAP infrastructure: slab caches for names/attributes, string and uint64 key initialization, Unicode normalization and matching, hash computation, ZAP locking/unlocking and lock upgrades, byteswap dispatch, and attribute allocation helpers.

## Main Responsibilities
- Creates and destroys kmem caches for `zap_name_t` and `zap_attribute_t`, including long-name variants.
- Normalizes string keys according to ZAP normalization flags and match type.
- Initializes string and uint64-array `zap_name_t` objects.
- Computes salted CRC64-based ZAP hashes or accepts pre-hashed uint64 keys.
- Opens/locks ZAP objects from dnodes/dbufs and handles microzap growth or fatzap upgrade.
- Provides reader/writer lock upgrade helpers used by fatzap split/shrink.
- Tears down `zap_t` dbuf users on eviction.
- Dispatches byteswap between microzap and fatzap formats.

## Key Data And State
- Static caches:
  - `zap_name_cache`, `zap_attr_cache` for normal names/attributes.
  - `zap_name_long_cache`, `zap_attr_long_cache` for longer directory names.
- `zap_name_t` captures original key, normalized key, integer width, integer count, match flags, norm flags, computed hash, owning `zap_t`, and normalization buffer size.
- `zap_t` lock state and micro/fat identity are maintained as dbuf user data.

## Important Functions
- `zap_init()` / `zap_fini()`: lifecycle for ZAP object caches.
- `zap_name_alloc_str()` / `zap_name_alloc_uint64()` / `zap_name_init_str()` / `zap_name_free()`: key wrapper allocation and initialization.
- `zap_normalize()` / `zap_match()`: Unicode textprep normalization and match-type-aware comparison.
- `zap_hash()`: CRC64 hash over normalized string or uint64 key material, masked to either 28 or 48 significant bits depending on flags.
- `zap_lock_impl()`: validates object type, opens microzap if needed, chooses lock mode, dirties dbuf for writers, grows microzap block size, activates large-microzap feature when needed, and upgrades to fatzap if microzap max size is exceeded.
- `zap_lock_by_dnode()` / `zap_lock()` / `zap_unlock()`: public lock/hold wrappers.
- `zap_lock_try_upgrade()` / `zap_lock_upgrade()`: convert a read lock to writer lock while dirtying the header dbuf.
- `zap_evict_sync()`: destroys locks and micro/fat auxiliary state on dbuf eviction.
- `zap_getflags()`, `zap_hashbits()`, `zap_maxcd()`: format/flag helpers.
- `zap_byteswap()`: DMU byteswap callback for microzap/fatzap blocks.
- `zap_attribute_alloc()`, `zap_attribute_long_alloc()`, `zap_attribute_free()`: cursor attribute allocation.

## Control Flow Notes
- Match-type `MT_MATCH_CASE` removes case-folding for that lookup while preserving the original hash normalization rules.
- Hashing omits the terminating NUL for string keys for historical on-disk compatibility.
- Microzap growth can increase block size until the pool/dataset feature limits require conversion to fatzap.
- `zap_lock_impl()` may initially take a writer lock for a microzap operation, then downgrade if another thread already upgraded the object to fatzap.

## Error Handling And Invariants
- Non-ZAP DMU object types are rejected with `EINVAL`.
- Invalid microzap/fatzap on-disk state returns `EIO`.
- Unsupported normalization or match requests return `ENOTSUP`.
- Long key allocation must use the long-name cache when the key exceeds old ZAP maximum name length.
- `zap_maxcd()` reserves collision differentiator bits according to hash-width mode.

## Dependencies
Depends on DMU/dbuf/dnode lifecycle, DSL dataset feature activation, Unicode textprep, CRC64 tables, microzap/fatzap open and byteswap functions, and ZAP physical format flags.

## Research Notes
This file is the shared correctness boundary between public ZAP APIs and the micro/fat implementations. Normalization, hash masking, and lock-upgrade behavior must remain consistent with on-disk compatibility.
