# Group Research: group_1781_stratisd_sources_block_storage_stratisd_src_engine_strat_engine_cry_a3c7098c85be

Scope verified against `Docs/research_subset_a.md`: `sources/block-storage/stratisd` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/shared.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/shared.rs

This file is the shared cryptsetup/LUKS2 support layer for the Stratis engine. It wraps `libcryptsetup-rs`, Clevis command helpers, kernel keyring helpers, and Stratis encryption metadata conventions.

Key responsibilities:
- Configures cryptsetup logging and safely acquires/loads LUKS2 `CryptDevice` handles.
- Adds and validates Stratis keyring-backed LUKS2 keyslots and tokens.
- Parses LUKS2 JSON tokens into Stratis `EncryptionInfo`, including key-description tokens and Clevis tokens.
- Interprets Clevis Tang/SSS/TPM2 metadata, including nested SSS recursion limits and Tang trust requirements.
- Activates encrypted devices by passphrase, token, or keyring-backed volume key, with V2 process-keyring volume key handling.
- Deactivates and wipes crypt devices, including fallback manual zeroing when libcryptsetup handle acquisition fails.
- Backs up/restores LUKS2 headers.
- Registers a Clevis token callback with cryptsetup and bridges callback errors through global `CLEVIS_ERROR`.
- Supports online reencryption setup and execution by duplicating keyslots/tokens onto a new volume key, then invoking the external reencryption command.

Important behavior:
- `activate()` enforces the metadata-version precondition: V1 has no pool UUID for volume-key keyring loading, V2 does.
- `get_keyslot_number()` expects each Stratis token to map to exactly one keyslot and errors on multiple keyslots.
- `encryption_info_from_metadata()` ignores unrelated token types but errors if no valid unlock mechanism remains.
- `interpret_clevis_config()` requires each Tang config to include trust material unless Stratis’ trust-url directive is set.
- `handle_setup_reencrypt()` is designed to be rollback-capable; `handle_do_reencrypt()` is explicitly not rollback-capable.

Tests:
- Unit tests cover Tang/SSS trust-information detection and recursion-related Clevis config handling.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/device.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/device.rs

This file provides small Linux block-device ioctl helpers.

Key responsibilities:
- Defines ioctl bindings for `BLKGETSIZE64`, `BLKSSZGET`, and `BLKPBSZGET`.
- Exposes:
  - `blkdev_size()` for device byte size.
  - `blkdev_logical_sector_size()` for logical sector size.
  - `blkdev_physical_sector_size()` for physical sector size.

Important behavior:
- Uses `linux_raw_sys` constants and `nix`-style ioctl macros.
- Converts ioctl out-parameters into `devicemapper::Bytes`.
- Wraps syscall failures in `StratisError::Msg`.
- Uses checked integer conversions for sector-size results.

Tests:
- No local tests in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/device.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/devlinks.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/devlinks.rs

This file centralizes simple Stratis `/dev` link conventions.

Key responsibilities:
- Defines `UEVENT_CHANGE_EVENT` as `"change"`.
- Provides `filesystem_mount_path(pool_name, fs_name)` to build `/dev/stratis/<pool>/<filesystem>` paths from `DEV_PATH`.

Important behavior:
- Uses `PathBuf` collection from path components instead of string concatenation.

Tests:
- No local tests in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/devlinks.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/dm.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/dm.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/engine.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/engine.rs

This file implements `StratEngine`, the main async Stratis engine for real block storage.

Key responsibilities:
- Holds active pools in `AllOrSomeLock<PoolUuid, AnyPool>`.
- Holds discovered-but-not-active devices in `LiminalDevices`.
- Tracks devicemapper event numbers per watched pool device.
- Owns the kernel keyring action handler.
- Initializes the engine by setting up private namespace filesystem state, verifying external executables, discovering devices, and assembling started pools.

Major operations:
- `create_pool()` validates name, paths, key descriptions, integrity settings, existing ownership, and sector-size compatibility, then initializes V2 pools.
- Test-only `create_pool_legacy()` creates V1 pools for legacy coverage.
- `destroy_pool()` refuses pools with filesystems, removes the pool from the active table, attempts destruction, and on non-restorable failure moves remaining devices to liminal stopped state.
- `rename_pool()` updates pool metadata, reinserts the pool under the new name, and emits udev pool changes.
- `unlock_pool()` starts locked encrypted liminal pools enough to unlock devices and return unlocked device UUIDs.
- `start_pool()` delegates to `LiminalDevices::start_pool()` and moves the result into active pools.
- `stop_pool()` moves active pools into stopped or partially constructed liminal state.
- `refresh_state()` discards current engine state and rebuilds it from device discovery.
- `get_events()`, `pool_evented()`, and `fs_evented()` coordinate devicemapper event checks and timer-based checks.

Concurrency model:
- Async locks protect engine tables.
- Blocking storage and devicemapper work is run through `spawn_blocking`.
- Event handling intentionally takes broad write locks while promoting liminal devices into active pools to avoid duplicate pool registration.

Reporting:
- Implements `Into<Value>` and `Report` to expose active pools, stopped pools, partially constructed pools, and liminal lookup maps.

Tests:
- Integration-style tests cover setup persistence, pool rename, start/stop behavior, and rollback across keyring/Clevis bind, rebind, unbind, and cache cases using loopback and real-device harnesses.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/engine.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/keys.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/keys.rs

This file implements Stratis kernel keyring operations.

Key responsibilities:
- Accesses the root persistent keyring and process keyring via raw `keyctl` syscalls.
- Searches, reads, adds, updates, lists, and unlinks Stratis keys.
- Stores key contents in `SafeMemHandle`/`SizedKeyMemory`.
- Implements the engine `KeyActions` trait as `StratKeyActions`.

Important behavior:
- Persistent keyring is attached to the session keyring via `KEYCTL_GET_PERSISTENT`.
- Process keyring creation uses `KEYCTL_GET_KEYRING_ID`.
- `set_key_idem()` is idempotent and returns `Created`, `ValueChanged`, or `Identity`.
- New/updated keys trigger notification over an unbounded channel so other processing can react.
- Key listing reads key IDs, describes each key, parses the key description after the final semicolon, and filters to Stratis descriptions.
- Key permissions are set with `KEYCTL_SETPERM` after key insertion.

Tests:
- Test-only `StratKeyActions::set_no_fd()` allows inserting in-memory keys without a file descriptor.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/keys.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/device_info.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/device_info.rs

This file defines the data structures for devices known to Stratis but not necessarily assembled into active pools.

Key types:
- `LLuksInfo`: discovered Stratis-owned LUKS device, including device node, identifiers, encryption info, and optional pool name.
- `LStratisInfo`: discovered Stratis metadata device, optionally linked to its backing LUKS info.
- `LInfo`: enum over closed LUKS-only info and opened Stratis-device info.
- `DeviceSet`: map of device UUID to merged device information for one pool.
- `DeviceBag`: miscellaneous set that can contain duplicate UUID concepts for looser tracking.

Key responsibilities:
- Merge LUKS and Stratis observations for the same pool/device UUID.
- Detect conflicts in device number or encryption metadata and retain older known-good info when newer info conflicts.
- Represent whether a pool has closed encrypted devices.
- Convert complete opened sets into blockdev info for setup.
- Gather pool encryption info, pool name, feature metadata, stopped-pool info, locked-pool info, and metadata version.
- Process udev add/remove state transitions, including reverting an opened encrypted device back to a closed LUKS entry when the mapped Stratis device disappears.
- Serialize liminal device state to JSON.

Important behavior:
- `DeviceSet::into_opened_set()` refuses closed encrypted devices.
- `locked_pool_info()` filters out incomplete encrypted observations where a Stratis device lacks its associated LUKS info.
- `stopped_pool_info()` reports either physical LUKS nodes or direct Stratis nodes, depending on encryption state.
- Mixed metadata versions in one set are treated as an error.

Tests:
- No local tests in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/device_info.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/identify.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/identify.rs

This file discovers and classifies block devices that may belong to Stratis.

Key responsibilities:
- Defines raw discovery structs: `StratisDevInfo`, `LuksInfo`, `StratisInfo`, and `DeviceInfo`.
- Converts existing V1/V2 blockdev objects into `DeviceInfo`.
- Reads Stratis BDA metadata from device nodes through `bda_wrapper()`.
- Processes udev-identified LUKS devices by loading Stratis LUKS metadata through `CryptHandle::load_metadata()`.
- Processes udev-identified Stratis devices by reading BDA metadata and device numbers.
- Enumerates all Stratis-owned LUKS devices and all Stratis filesystem-type devices using libudev filters.
- Identifies a single block device from a udev event.

Important behavior:
- Initial enumeration uses udev filesystem type filters: crypto/LUKS for Stratis-owned LUKS devices and Stratis fs type for Stratis metadata devices.
- Ownership is rechecked with `decide_ownership()` to avoid acting on multipath members or unrelated devices.
- Uninitialized udev entries are ignored.
- Errors during metadata reads are logged and cause the specific device to be ignored rather than aborting enumeration.
- Public `find_all()` returns two maps keyed by pool UUID: LUKS infos and Stratis infos.

Tests:
- Tests cover uninitialized/non-Stratis devices, initialized legacy encrypted devices, initialized legacy unencrypted devices, and initialized V2 devices across loopback and real-device harnesses.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/identify.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/liminal.rs -->
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
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/liminal.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/mod.rs

This is the liminal module declaration and public re-export surface.

Key responsibilities:
- Declares submodules:
  - `device_info`
  - `identify`
  - `liminal`
  - `setup`
- Re-exports:
  - `DeviceSet`
  - `find_all`
  - `LiminalDevices`

Important behavior:
- The `liminal` submodule uses `#[allow(clippy::module_inception)]` because the module and file share the same name.

Tests:
- No local tests in this file.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/mod.rs -->