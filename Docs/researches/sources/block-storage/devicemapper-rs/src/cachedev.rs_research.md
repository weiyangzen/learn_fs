# File Research: sources/block-storage/devicemapper-rs/src/cachedev.rs

## Purpose
Implements the `dm-cache` high-level wrapper: target parameters, single-line target table, status parsing, construction/setup, resizing of meta/cache/origin backing linear devices, and teardown.

## Key Types
`CacheTargetParams` serializes/deserializes `cache <meta> <cache> <origin> <block_size> <features> <policy> <policy_args>`. `CacheDevTargetTable` enforces exactly one target line. `CacheDevUsage`, `CacheDevPerformance`, `CacheDevMetadataMode`, `CacheDevWorkingStatus`, and `CacheDevStatus` model kernel status output.

## Behavior
`CacheDev::new` rejects existing names, generates a default writethrough/default-policy table, and creates a private DM device. `setup` is idempotent when the kernel table and uuid match. `set_origin_table`, `set_cache_table`, and `set_meta_table` reload relevant subdevices and then reload the cache table; cache/meta reloads deliberately reload unchanged cache table to avoid a documented smq issue. `equivalent_tables` ignores policy name but compares core identity fields and policy args.

## Dependencies
Builds on `LinearDev`, `DM`, `DmOptions`, `DmDevice`, `TargetTable`, shared parsing helpers, and sector/block unit wrappers. Uses `status!`, `to_raw_table_unique!`, and device/name/uuid/devnode macros from `shared_macros.rs`.

## Tests/Notes
Loopback tests create a minimal cache from two or three loop devices, verify parsed status, kernel table, metadata/cache/origin size changes, and suspend/resume. Parsing assumes enough fields after declared feature/policy counts; malformed count/length mismatches may panic by slice indexing rather than always returning `DmError`.
