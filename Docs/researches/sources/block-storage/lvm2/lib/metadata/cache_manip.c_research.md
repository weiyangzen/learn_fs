# File Research: sources/block-storage/lvm2/lib/metadata/cache_manip.c

Purpose: implements LVM cache and cache-pool/cachevol manipulation: cache mode/policy/metadata-format selection, metadata and chunk-size sizing, cache creation/removal, dirty-cache flushing, and cache metadata wiping.

Read coverage: complete file read, 1,279 lines.

Key responsibilities:
- Converts cache modes between enum and strings, validates user-provided modes, and resolves defaults from config/profiles.
- Computes minimum cache metadata sizes from cache data size and chunk size using dm-cache metadata overhead assumptions.
- Selects and validates cache pool chunk sizes against target limits, configured max chunks, metadata LV size, and data LV size.
- Validates cache pool and origin LV suitability before building a cached LV.
- Implements `lv_cache_create()` by inserting an origin layer, changing the top segment to cache, attaching the pool/cachevol, renaming used cache pools with `_cpool`, and inheriting profiles.
- Implements `lv_cache_wait_for_clean()` by polling cache status, switching to cleaner policy when needed, and waiting for dirty blocks to drain.
- Implements `lv_cache_remove()` with special handling for inactive writethrough/passthrough caches, temporary activation for writeback flush, pending-delete cache layer teardown, pool/cachevol detachment, and reload/deactivation sequencing.
- Detects default cache policy and metadata format from kernel target features, preferring `smq` and metadata format 2 when available.
- Applies cache policy settings from explicit config trees or profile config, including flattening old and new policy settings and removing `"default"` placeholder values.
- Implements newer cachevol parameter setup by carving metadata/data regions from one LV and requiring metadata format 2.
- Wipes unused cache-pool metadata/data volumes before use, skipping volumes whose segment type should not be zeroed.

Important entry points:
- Mode/policy/format: `cache_mode_num_to_str()`, `set_cache_mode()`, `cache_set_cache_mode()`, `cache_set_policy()`, `cache_set_metadata_format()`, `cache_set_params()`.
- Sizing/validation: `update_cache_pool_params()`, `validate_cache_chunk_size()`, `validate_lv_cache_chunk_size()`, `validate_lv_cache_create_pool()`, `validate_lv_cache_create_origin()`.
- Lifecycle: `lv_cache_create()`, `lv_cache_wait_for_clean()`, `lv_cache_remove()`, `cache_vol_set_params()`, `wipe_cache_pool()`.

Dependencies:
- Uses metadata, locking, activation, config/defaults, display, segment types, LV allocation, signal handling, and device-mapper cache target status/features.
- Relies on LV relationship helpers such as `first_seg()`, `seg_lv()`, `attach_pool_lv()`, `detach_pool_lv()`, `insert_layer_for_lv()`, and `remove_layer_from_lv()`.

Risk and edge cases:
- Writeback caches must be flushed before detaching; inactive writeback caches are temporarily activated for cleaning.
- Dirty cache flushing can be interrupted, and the code attempts to restore the normal table if cleaner-policy flushing is aborted.
- Cache metadata format 2 is enforced for cachevol creation, while legacy cache pools maintain compatibility with format 1.
- Cache on RAID in writeback mode logs a redundancy-loss warning.
- Chunk size is constrained by dm-cache target min/max, alignment, data volume size, metadata capacity, and configured max chunk count.
- Failed cache removal can leave a temporary pending-delete/cache structure that later commands must be able to complete.
