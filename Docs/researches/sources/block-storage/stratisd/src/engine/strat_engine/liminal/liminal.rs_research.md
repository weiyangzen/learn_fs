# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/liminal.rs

This file manages liminal Stratis devices: devices discovered by stratisd that are stopped, locked, incomplete, or not yet promoted into active pools.

Key state:
- `uuid_lookup`: maps device paths to `(pool_uuid, dev_uuid)` for remove/change handling.
- `stopped_pools`: complete or potentially startable stopped pools.
- `partially_constructed_pools`: pools with leftover devicemapper state from failed start/stop.
- `name_to_uuid`: pool-name lookup, including conflict representation when stopped pools share names.

Major operations:
- Unlocks encrypted stopped pools by setting up LUKS devices with `CryptHandle::setup()`.
- Starts legacy V1 pools by unlocking, rescanning opened devices, loading metadata, optionally removing cache metadata, and calling V1 setup.
- Starts V2 pools by loading metadata and passing unlock/passphrase information into V2 setup.
- Routes `start_pool()` by detected `StratSigblockVersion`.
- Stops active pools and records them as stopped or partially constructed.
- Cleans up partially constructed pools using version-specific devicemapper cleanup helpers.
- Reports locked and stopped pool summaries for API/reporting.
- Handles udev block add/change/remove events and promotes newly complete started pools.
- Checks block-device size changes on udev add/change events and returns `StratBlockDevDiff`.

Important behavior:
- Startup discovery merges LUKS and Stratis observations by pool UUID, records path lookup entries, tracks pool-name conflicts, and attempts to set up pools whose metadata says they were started.
- Pools whose metadata says `started = false` are retained in stopped state.
- If devices remain unopened, setup is deferred and the pool stays liminal.
- `handle_stopped_pool()` decides stopped versus partially constructed based on leftover devicemapper devices and metadata version.
- `remove_cache_from_metadata()` strips cache-tier metadata and returns paths for cache devices to wipe.
- `load_stratis_metadata()` validates BDA identifiers against expected pool/device UUIDs before reading MDA metadata.

Setup helpers:
- `setup_pool_legacy()` handles V1 name conflicts, blockdev reconstruction, encryption consistency, optional cache wipe paths, and LUKS pool-name consistency repair.
- `setup_pool()` handles V2 name conflicts, blockdev reconstruction, data-device presence, optional cache removal, unlock method, and passphrase propagation.

Tests:
- No local tests in this file, but it is heavily exercised through `engine.rs` start/stop/setup/rollback tests and `identify.rs` discovery tests.
