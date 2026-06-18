# File Research: sources/block-storage/stratisd/src/engine/strat_engine/dm.rs

This file owns shared devicemapper context initialization and Stratis devicemapper-name cleanup helpers.

Key responsibilities:
- Lazily initializes the global `DM_CONTEXT`.
- Provides `get_dm_init()` for fallible initialization and `get_dm()` for post-initialization use.
- Defines `/dev/mapper` as `DEVICEMAPPER_PATH`.
- Removes optional devicemapper devices if present.
- Builds lists of expected thin-pool, metadata-volume, backstore, cache, crypt, and partial-pool devices.
- Detects leftover devices from partial construction for both legacy and newer naming schemes.

Important behavior:
- Legacy cleanup includes per-device crypt mappings via device UUIDs.
- Newer cleanup includes pool-level crypt backstore naming.
- `has_leftover_devices*()` first queries devicemapper and falls back to `/dev/mapper/<name>` path existence if listing fails.

Tests:
- No local tests in this file.
