# Group Research: group_1779_stratisd_sources_block_storage_stratisd_src_engine_strat_engine_bac_8328b7949cdd

Scope: `Docs/research_subset_a.md`; source tree `sources/block-storage/stratisd`. All eight listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/v1.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/v1.rs

This file implements the legacy v1 Stratis backstore: the object that exposes the pool's cap device to upper layers, allocates data-tier space, optionally inserts a dm-cache layer, and coordinates legacy per-block-device encryption metadata. `Backstore` owns an optional `CacheDev`, optional `CacheTier<StratBlockDev>`, a required `DataTier<StratBlockDev>`, an optional linear origin device, and `next`, the monotonically increasing cap-device allocation cursor.

The `InternalBackstore` implementation reports the active device as cache if present, otherwise linear, computes usable/available data-tier space, and implements allocation. Allocation first checks `available_in_backstore`, asks `DataTier::alloc` for the requested sector lengths, extends or creates the cap device, then returns contiguous logical cap offsets starting at `next`.

Setup and initialization are split between existing metadata and new pools. `setup()` rebuilds a data-tier linear origin from saved data segments, optionally rebuilds cache tier state, and creates the cache device via `make_cache()`. `initialize()` creates a new data tier and starts without a cap device until the first allocation. `init_cache()` converts an existing linear origin into a cache-backed device after some data allocation exists; `add_cachedevs()` extends cache/cache-meta dm tables when cache devices are added.

Device lifecycle methods remove dm backstore devices, destroy or teardown cache and data tiers, load/save pool metadata through the data tier only, and expose per-tier blockdev lookup and JSON/reportable state. `record()` serializes cache tier state, cap allocation as `(0, next)`, and data tier state; v1 has no cap crypt metadata allocation list.

Encryption is legacy per-block-device encryption. `encryption_info()` gathers consistent encryption state across all data and cache blockdevs. `bind_clevis`, `unbind_clevis`, `bind_keyring`, `unbind_keyring`, `rebind_keyring`, `prepare_reencrypt`, `reencrypt`, `rebind_clevis`, and `rename_pool` iterate over every owned blockdev. The shared `operation_loop()` backs up each LUKS header before mutation and restores/reloads already-touched devices on failure, returning rollback errors when restoration fails.

Growth is delegated to the data tier. `action_availability()` disables pool changes if block-size summaries for data or cache tiers are inconsistent. Tests cover cache initialization/addition, setup invariants, device identifiers, Clevis/keyring idempotence and unbind behavior, and loopback/real-device variants.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/v1.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/v2.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/v2.rs

This file implements the v2 Stratis backstore, moving encryption from per-blockdev LUKS handling to a single cap-device encryption layer and adding explicit cap metadata allocations. The main `Backstore` contains an optional cache tier, a required `DataTier<v2::StratBlockDev>`, and a `CapDevice`. `CapDevice` tracks origin, cache, encryption state, a placeholder linear device, user data allocations, and crypt metadata allocations.

`make_cache()` creates cache meta/cache subdevices and either sets up a new `CacheDev` or reloads an existing dm-cache table over a stable placeholder. `make_placeholder_dev()` builds a linear device with the cache role name so that upper layers can keep a stable device identity before/after cache insertion and encryption changes. `CapDevice::device()` prefers the encryption handle device, then cache, then placeholder.

Allocation is split between data allocations and crypt metadata allocations. `CapDevice::alloc()` allocates requested data sizes from the data tier, extends the cap device, and appends logical cap allocation tuples. `meta_alloc_cache()` allocates early metadata space before user data. `calc_next_cache()` enforces that crypt metadata can only be allocated at the beginning of the cache/placeholder device before encryption is active; `calc_next_cap()` computes the next user-visible offset, excluding crypt metadata when encrypted. `initialize()` always reserves `DEFAULT_CRYPT_DATA_OFFSET_V2` as crypt metadata space before returning.

`setup()` reconstructs data/cache tiers from `PoolSave`, creates origin/cache or origin/placeholder devices, validates the metadata encryption feature against an on-device header, and sets up a v2 `CryptHandle` when required. `extend_cap_device()` handles all device topologies: plain placeholder/origin, cache, encrypted cache, encrypted placeholder/origin, and delayed encryption initialization from `InputEncryptionInfo`.

The public API mirrors v1 for cache/datadev add, blockdev enumeration, metadata save/load, user info, block-size summaries, action availability, and lifecycle teardown/destroy. Destroy wipes the cap crypt handle when present and unloads the volume key from the process keyring.

Encryption operations now target the single cap crypt handle. Binding/unbinding Clevis or keyring accepts optional token-slot inputs and returns slot-aware results. Rebind methods reject mismatched token mechanisms. `prepare_encrypt`, `do_encrypt`, and `finish_encrypt` support online encryption by creating the crypt layer, shifting cap allocation offsets, suspending/resuming the thinpool, and rolling back header setup on preparation failure. `do_decrypt` and `finish_decrypt` reverse that flow, wiping crypt header space and shifting offsets back. Reencryption operates on exactly one crypt device and wraps irreversible failures in action-availability errors.

Tests cover cache insertion with stable exposed device identity, v2 invariants including crypt metadata accounting, Clevis/keyring token-slot behavior, and loopback/real-device paths.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/backstore/v2.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/mod.rs

This module is the shared block-device interface layer for the backstore. It declares the v1 and v2 blockdev submodules and defines common types/traits used by `BlockDevMgr`, `DataTier`, `CacheTier`, and both backstore versions.

`StratSectorSizes` stores base block-size information and optional crypt-layer block-size information. Its `Display` implementation emits both base and crypt values, using `None` for unencrypted/no crypt cases. v1 blockdevs can populate both fields because encryption is per physical blockdev; v2 normally has only base sizes because encryption is above the assembled cap device.

`InternalBlockDev` is the central internal trait for backstore-owned physical devices. It exposes identity (`bda`, `uuid`, `device`, `physical_path`, metadata version), physical/logical size accounting (`total_size`, `available`, `metadata_size`, `max_stratis_metadata_size`, `in_use`), allocation (`alloc`), detected growth (`calc_new_size`), pool-level metadata persistence (`load_state`, `save_state`), lifecycle teardown, and destructive disowning.

The trait documents an important device-number distinction: `device()` must be the device number used to construct cap-device dm tables. For unencrypted devices this is physical; for v1 encrypted devices it is the unlocked logical LUKS device. The trait also establishes destructive semantics for `disown()`: encrypted devices must destroy keyslots and wipe the LUKS2 header, while unencrypted devices wipe Stratis metadata so blkid/stratisd no longer recognize ownership.

This file contains no tests or implementations beyond formatting; its role is to keep the manager/tier code generic over v1 and v2 block-device implementations.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/v1.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/v1.rs

This file implements a legacy v1 Stratis block device. A `StratBlockDev` wraps a `Device`, `BDA`, `RangeAllocator`, user/hardware info, `UnderlyingDevice`, detected `new_size`, and block-size summary. `UnderlyingDevice` is either `Encrypted(CryptHandle)` or `Unencrypted(DevicePath)`, and centralizes physical path, metadata path, and mutable/immutable crypt-handle access.

Construction reserves the BDA extended metadata region plus caller-provided allocated segments in a `RangeAllocator`, reads physical block sizes, and for encrypted devices also reads the activated crypt device block sizes. The metadata path is the activated LUKS dm device for encrypted blockdevs and the physical path for unencrypted blockdevs.

The public methods expose pool/device identity, physical and metadata paths, optional LUKS device number, encryption info, pool name stored in crypt metadata, user-info mutation, and crypt metadata reload. Clevis/keyring bind, unbind, rebind, and Clevis regeneration are thin wrappers around the per-device v1 `CryptHandle`, returning an error if the blockdev is not encrypted.

Size handling subtracts legacy crypt metadata size when scanning encrypted physical devices. `set_new_size()` records shrink/growth observations and warns on shrink. `grow()` rescans the physical path, rejects shrink, no-ops on equal size, resizes the crypt device first when encrypted, writes the new static header to both metadata locations, updates BDA and allocator size, and rolls back crypt resize if header update fails.

`InternalBlockDev` implements allocation from the front of the free range, metadata load/save with consistency checks between state and update time, teardown by deactivating crypt devices, and disown by wiping crypt headers or Stratis metadata. `BlockDev` exposes user-facing fields; JSON conversion includes path, uuid, encryption info if present, size/new_size, block sizes, and `in_use`.

`Recordable<BaseBlockDevSave>` stores uuid, user/hardware info, and an empty integrity allocation list because v1 has no per-device integrity metadata reservation. `DumpState` tracks new-size diffs for external reporting. This file has no local test module; behavior is exercised by manager, tier, and backstore tests.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/v1.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/v2.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/v2.rs

This file implements a v2 Stratis physical block device. Unlike v1, it does not own a per-device crypt handle. It stores a physical `Device`, `BDA`, `RangeAllocator`, user/hardware info, device path, detected `new_size`, base block sizes, and `integrity_meta_allocs` reserved from the back of the device.

`integrity_meta_space()` computes the sector space required for dm-integrity metadata for a total device size and `ValidatedIntegritySpec`. It includes optional superblock space, journal size, and rounded tag space. The comment notes that it intentionally overestimates by basing the calculation on whole-disk size.

Construction reserves the BDA extended metadata region, existing upper-layer segments, and existing integrity metadata allocations in the allocator, then reads base block sizes from the physical device. `alloc_int_meta_back()` allocates integrity metadata from the back of the allocator and records the reserved segments.

Growth rescans the physical device, rejects shrink, no-ops on equal size, updates the static header and BDA size on growth, increases allocator size, computes additional integrity metadata required for the new size, and reserves that extra space at the back. This makes v2 growth sensitive to integrity settings, unlike v1.

`InternalBlockDev` reports physical identity, base-only block sizes, metadata version, total size, available space, metadata size as BDA extended metadata plus integrity allocations, and `in_use` as allocator used space beyond metadata. It allocates normal data from the front, loads/saves BDA state from the physical path with update-time consistency checks, has no teardown work, and disowns by wiping Stratis metadata.

`BlockDev` exposes physical path as both devnode and metadata path. JSON output includes path, uuid, size/new_size, block sizes, and in-use state. `Recordable<BaseBlockDevSave>` persists uuid, user/hardware info, and integrity metadata allocations. `DumpState` mirrors v1 new-size diff reporting. This file has no local test module; v2 manager/tier/backstore tests cover construction, allocation, growth accounting, and serialization assumptions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdev/v2.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdevmgr.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdevmgr.rs

This file implements `BlockDevMgr<B>`, the generic manager for collections of backstore block devices. It owns the vector of blockdevs and a monotonic `TimeStamp` used for pool-level metadata writes. `TimeStamp::next()` returns current UTC time unless that would not advance beyond the last saved timestamp, in which case it adds one nanosecond.

The v1 specialization initializes devices through `initialize_devices_legacy()` with pool name, encryption info, and optional sector size. Adding v1 devices verifies pool UUID consistency, checks that existing encrypted pools can still be unlocked with their configured key/Clevis mechanisms, initializes new devices with default MDA size, and extends the device list. It also gathers pool encryption info across devices, reports encryption state, and delegates growth to the matching blockdev.

The v2 specialization initializes with `initialize_devices()` and has no per-device encryption parameters. Adding v2 devices only validates pool UUID and initializes new devices with default MDA size. Growth requires a `ValidatedIntegritySpec` and delegates to v2 blockdev growth.

The generic implementation provides UUID-to-device maps for rebuilding saved segment tables, destructive wipe of all blockdevs, immutable/mutable blockdev listing and lookup, removal of specified blockdevs followed by metadata wiping, atomic allocation, metadata replication, metadata loading, size/metadata/available accounting, and teardown. Allocation first checks aggregate free space, then walks blockdevs in order allocating partial ranges until each request is satisfied; because it checks total availability first, it asserts each request is fully allocated and returns all segment lists or `None`.

`save_state()` writes pool metadata to up to `MAX_NUM_TO_WRITE` randomly sampled candidate devices whose MDA can hold the metadata. It advances the timestamp only if at least one write succeeds. `load_state()` scans all devices and returns the newest metadata by update time, erroring if no metadata is available or any device reports a load error.

Tests cover allocation accounting, encrypted v1 add behavior with same/changed keyring keys, prevention of stealing blockdevs from another pool, and corresponding v2 ownership/accounting tests across loopback and real devices.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/blockdevmgr.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/cache_tier.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/cache_tier.rs

This file implements `CacheTier<B>`, the backstore layer that manages block devices dedicated to dm-cache. It owns a `BlockDevMgr<B>`, cache data segments, and cache metadata segments. The implementation is generic over v1/v2 blockdevs for setup, serialization, destruction, partitioning, and invariants, with version-specific add/lookup wrappers.

`MAX_CACHE_SIZE` caps the cache subdevice at 32 TiB. The comments describe this as temporary, tied to the cache block size and the fixed 1 Mi-sector metadata subdevice size. Both v1 and v2 `add()` methods initialize new cache blockdevs through their manager, reject additions that would exceed the maximum cache size, roll back added blockdevs by removing/wiping them on that error, then allocate all newly available free space to the cache subdevice. They currently never grow the metadata subdevice and return `(cache_changed=true, meta_changed=false)`.

`setup()` reconstructs an existing cache tier from saved metadata. It requires the block manager to have no unallocated space, builds a uuid-to-device map, maps saved metadata and cache segment records back to dm target segments, and stores them as `AllocatedAbove`. This guards against metadata corruption where cache devices have free space that is not represented in saved allocations.

`new()` creates a fresh cache tier by allocating a fixed 1 Mi-sector metadata subdevice and all remaining available space to the cache subdevice. It asserts devices are large enough, destroys all newly initialized cache blockdevs if the resulting cache would exceed `MAX_CACHE_SIZE`, and returns the allocated segment sets.

`destroy()` wipes all managed cache blockdevs. `partition_cache_by_use()` separates blockdevs by whether their allocator has allocations beyond metadata. The test-only invariant requires all cache-tier blockdevs to be in use and to match the union of cache and meta segment UUIDs. Serialization records cache allocs first, metadata allocs second, and blockdev records.

Tests for both v1 and v2 create a cache tier, verify all free space is consumed, add more cache devices, verify size/accounting changes, and destroy the tier.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/cache_tier.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/data_tier.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/data_tier.rs

This file implements `DataTier<B>`, the base data layer under the cap device. It owns a `BlockDevMgr<B>`, the upper-layer data segments allocated from managed blockdevs, and an optional `ValidatedIntegritySpec`. The generic implementation handles setup, allocation, size accounting, persistence, destruction, use partitioning, invariants, and serialization; v1/v2 specializations handle version-specific construction, add, lookup, and growth.

For v1, `new()` creates an empty data tier with no integrity spec and no allocated upper segments. Adding devices delegates to the v1 block manager with pool name, pool UUID, devices, and optional sector size. Growth delegates directly to v1 manager growth.

For v2, `new()` requires an integrity spec and immediately reserves integrity metadata from the back of every managed blockdev using `integrity_meta_space(total_size, spec)`. Adding v2 devices initializes them, filters the newly added UUIDs, asserts all were found, and reserves integrity metadata for each new blockdev. Growth delegates to v2 manager growth with the stored integrity spec.

`setup()` reconstructs an existing data tier by mapping saved allocation records through a uuid-to-device-number map and preserving the saved integrity spec. `alloc()` asks the block manager for requested sector lengths and, if successful, coalesces all returned block-device segments into the tier's `AllocatedAbove` segment list. It returns a boolean rather than the segments, because the tier stores the canonical allocation map internally.

Accounting methods report allocated upper data, raw size, metadata size, and usable size. Metadata size comes from blockdev metadata accounting; for v2 this includes BDA plus per-device integrity reservations, while cap-level crypt metadata is accounted in v2 backstore rather than here. `save_state()` and `load_state()` delegate pool metadata replication to the block manager. `partition_by_use()` supports action availability checks by splitting blockdevs into used and unused sets.

Serialization writes one allocation vector for data segments, blockdev records, and the optional integrity spec. Tests for both versions allocate data, add devices, verify allocation is unchanged after add, force allocation onto new devices, check invariants, and destroy the tier.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/data_tier.rs -->