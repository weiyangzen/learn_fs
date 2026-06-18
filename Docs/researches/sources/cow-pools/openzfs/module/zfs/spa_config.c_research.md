# File Research: sources/cow-pools/openzfs/module/zfs/spa_config.c

## Summary
Manages SPA pool configuration generation and cachefile synchronization. It writes imported writable pool configs to cache files and generates nvlists used in MOS configs and vdev labels.

## Main Responsibilities
- Writes or removes pool cache files.
- Synchronizes cachefile contents for all imported pools sharing a cache path.
- Tracks a global config generation for zone-visible config queries.
- Stores and replaces `spa->spa_config`.
- Generates pool and vdev configuration nvlists.
- Updates labels, expands newly added vdevs, waits for config sync, and refreshes cachefiles.

## Key APIs
- `spa_write_cachefile()`.
- `spa_all_configs()`.
- `spa_config_set()`.
- `spa_config_generate()`.
- `spa_config_update()`.

## Important Behavior
Cachefile writes pack an nvlist and overwrite the target path in place; if writing fails, the file is removed and an async config update is requested for retry. Read-only pools are excluded from cachefiles because they may not be importable on reboot.

`spa_config_generate()` includes pool identity, txg, host info, errata, allocation limits, comments, compatibility, top-level config, vdev tree, read-required features, and optional DDT stats. Temporary import names preserve the previous pool name in generated config.

## Risks
The cachefile can lag behind MOS config if a crash occurs between MOS sync and cachefile write, requiring explicit import. Config generation assumes SPA config/state locks are held. Cachefile path changes leave old dirents on `spa_config_list` until the next successful write removes stale entries.
