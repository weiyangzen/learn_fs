# File Research: sources/cow-pools/openzfs/module/zfs/ddt_zap.c

## Scope

ZAP-backed DDT storage backend. It implements the `ddt_ops_t` interface for creating, destroying, looking up, updating, removing, prefetching, walking, and counting DDT entries stored as uint64-keyed ZAP objects with compressed phys payloads.

## Main Interfaces

- Backend operations exposed through `ddt_zap_ops`.
- Compression helpers: `ddt_zap_compress()`, `ddt_zap_decompress()`.
- Object lifecycle: `ddt_zap_create()`, `ddt_zap_destroy()`.
- Entry operations: `ddt_zap_lookup()`, `ddt_zap_contains()`, `ddt_zap_update()`, `ddt_zap_remove()`.
- Scan/prefetch: `ddt_zap_prefetch()`, `ddt_zap_prefetch_all()`, `ddt_zap_walk()`, `ddt_zap_count()`.
- Tunables: `ddt_zap_default_bs`, `ddt_zap_default_ibs`.

## State And Control Flow

Entries use `ddt_key_t` as a multi-word uint64 ZAP key. `ddt_zap_create()` creates `DMU_OT_DDT_ZAP` objects with `ZAP_FLAG_HASH64` and `ZAP_FLAG_UINT64_KEY`; it adds `ZAP_FLAG_PRE_HASHED_KEY` when the checksum function supports dedup prehashing.

Phys payloads are compressed before storage. `ddt_zap_compress()` reserves one version byte, tries ZLE compression directly through ABD wrappers, stores uncompressed data when compression does not reduce size, and records host byte order in the high bit. `ddt_zap_decompress()` reverses that operation and byteswaps when imported on the opposite endian host.

Lookup asks ZAP for the stored value length, reads up to `psize + 1`, and decompresses to the caller’s phys buffer. Update compresses to a temporary buffer and writes it with `zap_update_uint64_by_dnode()`. Walk uses a serialized ZAP cursor for stable scan bookmarks, avoids full-object prefetch on first cursor initialization, retrieves compressed values, decompresses them, copies the key out of `za_name`, advances the cursor, and returns the serialized cursor.

## Dependencies

Uses ZAP uint64-key APIs, dnode/object APIs, ABD wrappers, ZIO compression/decompression tables, byte-swap helpers from DMU, and DDT key/phys sizes from `ddt_impl.h`.

## Correctness Notes

The version byte carries both compression function and byte order, allowing payloads to remain portable. Walk intentionally avoids prefetching enormous DDT ZAPs because scrub traversal usually spends more time issuing block reads than reading the ZAP itself. The compressed size is asserted not to exceed `psize + 1`.
