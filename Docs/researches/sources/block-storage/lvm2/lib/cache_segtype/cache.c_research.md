# File Research: sources/block-storage/lvm2/lib/cache_segtype/cache.c

## Summary
Implements LVM2 segment type support for device-mapper cache pools and cache LVs. It imports and exports cache-related metadata, detects kernel target capabilities, builds DM target lines for cache pool and cachevol layouts, and registers the `cache_pool` and `cache` segment types.

## Main Responsibilities
- Display cache chunk size, metadata format, cache mode, policy name, and policy settings.
- Fill missing defaults for older metadata: policy `mq`, metadata format 1, and writethrough mode.
- Import/export cache settings from text metadata: `chunk_size`, `cache_mode`, `policy`, and `policy_settings`.
- Import/export cache pool segments with separate data and metadata LVs.
- Import/export cache segments that attach an origin LV to either a cache pool or a cachevol.
- Handle cachevol metadata/data ranges, optional metadata/data IDs, and metadata format 2.
- Detect the `cache` DM target and optional features such as metadata2, MQ policy, and SMQ policy.
- Apply `global/cache_disabled_features` as a runtime feature mask.
- Build activation target lines using `dm_tree_node_add_cache_target()` or `dm_tree_node_add_cachevol_target()`.
- Register `SEG_TYPE_NAME_CACHE_POOL` and `SEG_TYPE_NAME_CACHE`.

## Key Interfaces
- Segment handlers: `_cache_pool_ops` and `_cache_ops`.
- Text import/export: `_cache_pool_text_import()`, `_cache_pool_text_export()`, `_cache_text_import()`, `_cache_text_export()`.
- Activation support under `DEVMAPPER_SUPPORT`: `_target_present()`, `_modules_needed()`, `_cache_add_target_line()`.
- Registration entry point: `init_cache_segtypes()`.

## Important Control Flow
Cache pool import resolves `data` and `metadata` LV names, reads optional `metadata_format`, imports shared settings, attaches pool data and metadata LVs, and fixes defaults if the pool is already used.

Cache LV import resolves `cache_pool` and `origin`, attaches the origin as area 0, reads optional cleaner mode and cache settings, reads metadata format/ranges for cachevols, marks cachevol pools, fixes old pool defaults for non-cachevol pools, then attaches the pool LV.

Activation selects settings from the cache segment for cachevols or the pool segment for classic cache pools. Cleaner mode forces writethrough. Metadata format 2 requires kernel feature support. Policy settings are filtered for known MQ/SMQ accepted keys, with unsupported settings warned and removed from a cloned config node before target construction.

Classic cache pools use separate metadata and data UUIDs from the pool segment. Cachevols build synthetic `cmeta` and `cdata` UUIDs from either stored IDs or the cachevol LV ID and pass explicit metadata/data ranges to the cachevol target.

## Cross-File Interactions
This file depends on metadata segment helpers for attaching LVs, config parsing/export helpers for text metadata, activation code for DM target construction, module/target detection helpers, and `toolcontext.c` registration through `_init_segtypes()` when `CACHE_INTERNAL` is enabled.

## Risks
Activation behavior depends on kernel target version, optional policy modules, and config-disabled features. Metadata import must preserve backward compatibility with older cache metadata that lacks explicit policy/mode/format. Cachevol range and UUID handling is sensitive: invalid ranges or unstable IDs can build incorrect DM devices. Policy setting filtering must stay aligned with kernel policy support.
