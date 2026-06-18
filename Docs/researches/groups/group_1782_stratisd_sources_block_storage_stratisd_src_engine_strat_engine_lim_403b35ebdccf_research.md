# Group Research: group_1782_stratisd_sources_block_storage_stratisd_src_engine_strat_engine_lim_403b35ebdccf

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/stratisd`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/setup.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/liminal/setup.rs

## Purpose

`setup.rs` reconstructs pool setup inputs from liminal Stratis devices. It reads the newest available pool metadata, validates that discovered devices match that metadata, and converts device discovery records into ordered v1 or v2 `StratBlockDev` objects split by data and cache tier.

## Main Responsibilities

- Select the most recent pool metadata from BDAs by `last_update_time()`.
- Decode JSON metadata into `PoolSave`.
- Recover pool name and feature set only when discovered device UUIDs exactly match metadata UUIDs.
- Rebuild recorded allocation segment tables from `BackstoreSave`.
- Construct legacy v1 block devices, including encrypted underlying-device handles.
- Construct v2 block devices with integrity metadata allocations.
- Verify reconstructed devices against metadata, then sort them by recorded metadata order.

## Important Functions

- `get_metadata()` finds the BDA with the greatest update timestamp, opens its devnode, loads BDA state, and deserializes `PoolSave`.
- `get_name()` reads metadata, compares found UUIDs to recorded data/cache UUIDs, and returns `Name`.
- `get_feature_set()` performs the same UUID consistency check and returns `PoolFeatures`.
- `get_blockdevs_legacy()` builds v1 data/cache `StratBlockDev` vectors.
- `get_blockdevs()` builds v2 data/cache `StratBlockDev` vectors.
- `get_blockdev_legacy()` checks device size, locates tier metadata, sets up optional crypt handle, and calls `v1::StratBlockDev::new()`.
- `get_blockdev()` checks device size, locates tier metadata, asserts `info.luks == None`, carries integrity allocations, and calls `v2::StratBlockDev::new()`.
- `check_and_sort_devs()` rejects duplicate UUIDs, mixed metadata versions, and missing/extra devices, then sorts by metadata index.

## Behavior Details

The metadata read path is deliberately tolerant until it finds a candidate: devices without timestamps are ignored; the device with the newest timestamp is opened; failed open/load/deserialize attempts on that chosen device become a hard error because the timestamp says metadata should exist.

The block device setup path derives allocation segments from the metadata’s data-tier allocation list and, when present, cache-tier allocation lists. Those segments are keyed by parent device UUID and passed into each reconstructed block device.

Legacy setup handles encrypted devices by choosing the LUKS physical path when `info.luks` exists, attempting `CryptHandle::setup()`, and wrapping the result as `UnderlyingDevice::Encrypted` or `Unencrypted`. Current v2 setup expects the liminal device itself to be the usable devnode and asserts that no legacy `luks` info is attached.

## Dependencies and Interactions

- Consumes `LStratisInfo` from liminal device discovery.
- Uses BDA/MDA metadata loading through `info.bda`.
- Uses serde structures: `PoolSave`, `BackstoreSave`, `BaseBlockDevSave`, `PoolFeatures`.
- Constructs block devices from `backstore::blockdev::v1` and `v2`.
- Uses `blkdev_size()` to detect shrinkage before setup.
- Uses `CryptHandle` and `TokenUnlockMethod::None` for legacy encrypted setup.

## Notable Edge Cases

- A pool with timestamps but unreadable metadata returns an error rather than `None`.
- Found UUIDs must exactly equal metadata UUIDs for name and feature-set recovery.
- A device whose actual size is smaller than its recorded BDA size is rejected.
- Duplicate device UUIDs and mixed metadata versions are treated as setup errors.
- Missing or extra data/cache devices cause tier-specific consistency errors.
- `segments.unwrap_or(&vec![])` relies on temporary empty vectors only for the immediate constructor call.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/liminal/setup.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/bda.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/bda.rs

## Purpose

`bda.rs` defines the Block Device Area abstraction. A `BDA` combines the static Stratis signature/header with the variable metadata regions used to store serialized pool state on each member device.

## Main Responsibilities

- Build a new BDA from identifiers, signature version, metadata size, device size, and initialization time.
- Initialize on-disk static headers and MDA headers.
- Load MDA regions from a previously validated `StaticHeader`.
- Save and load variable-length metadata state.
- Expose device/pool identifiers, sizes, timestamps, and signature version.

## Key Types

- `BDA`
  - `header: StaticHeader`
  - `regions: mda::MDARegions`

## Important Methods

- `BDA::new()` creates a `StaticHeader` and matching `MDARegions`.
- `initialize()` writes both static headers, initializes all MDA region headers, and syncs.
- `load()` constructs `MDARegions` after a valid static header has already been found.
- `save_state()` delegates timestamped metadata writes to `MDARegions`.
- `load_state()` returns the newest valid metadata bytes, if any.
- `last_update_time()` exposes the latest MDA timestamp.
- `dev_uuid()`, `pool_uuid()`, `identifiers()` expose Stratis identity.
- `dev_size()`, `extended_size()`, `max_data_size()` expose layout sizes.
- `initialization_time()` and `sigblock_version()` expose header metadata.

## Behavior Details

BDA initialization writes the static header to both signature-block locations before initializing MDA region headers starting after `STATIC_HEADER_SIZE`. Loading assumes that a valid static header implies prior BDA initialization, so invalid MDA headers become errors rather than “not a BDA.”

`Default` creates a nil-UUID v1 BDA with default sizes and default timestamp, useful for tests and placeholder construction.

## Tests

The tests verify:

- Newly initialized BDAs have no update time.
- Saving metadata with an older timestamp than the newest written state is rejected.
- Saving, loading, reloading from static headers, and saving again preserve metadata bytes and update timestamps.

## Dependencies and Interactions

- Wraps `StaticHeader` and `MDARegions`.
- Uses `STATIC_HEADER_SIZE` to place MDA data after the static header.
- Requires `Seek + SyncAll` for initialization/save and `Read + Seek` for load.
- Exposes `StratisIdentifiers`, `BlockdevSize`, `MDADataSize`, and `BDAExtendedSize` to higher layers.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/bda.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mda.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mda.rs

## Purpose

`mda.rs` manages Stratis variable-length metadata regions. It stores pool metadata in two alternating primary regions, each mirrored by a secondary copy, with CRC-protected region headers and CRC-protected metadata payloads.

## Main Responsibilities

- Initialize all MDA region headers to default empty headers.
- Load primary MDA headers with fallback to mirrored copies.
- Save metadata to the older primary region and its mirror.
- Load metadata from the newer primary region, falling back to its mirror.
- Validate region header CRCs, versions, timestamps, sizes, and payload CRCs.
- Track the latest update timestamp.

## Key Constants

- `STRAT_REGION_HDR_VERSION = 1`
- `STRAT_METADATA_VERSION = 1`
- CRC algorithm: CRC-32C iSCSI/Castagnoli.
- Region header size is defined in `sizes.rs` as 32 bytes.
- There are two primary MDA regions and four total regions including mirrors.

## Key Types

- `MDARegions`
  - Holds one region size and two primary `Option<MDAHeader>` entries.
- `MetaDataSize`
  - Wraps actual metadata bytes used in a region.
- `MDAHeader`
  - `last_updated`
  - `used`
  - `data_crc`

## Important Functions and Methods

- `MDARegions::new()` derives region layout from `MDASize`.
- `mda_offset()` computes device offsets from static-header size, region index, and region size.
- `initialize()` writes a default MDA header to every primary and mirrored region.
- `load()` reads primary regions and falls back to mirrored regions on invalid primary headers.
- `save_state()` rejects non-monotonic timestamps and oversized metadata, writes header plus payload to older primary and mirror, then updates in-memory header state.
- `load_state()` reads the newer primary region, falling back to its mirror.
- `older()` and `newer()` select alternating regions; ties favor writing region 1 and reading region 0.
- `MDAHeader::from_buf()` validates header CRC and versions.
- `MDAHeader::to_buf()` serializes header fields and recomputes CRC.
- `MDAHeader::load_region()` reads payload bytes and checks payload CRC.

## Behavior Details

An empty MDA header is not all zeroes: it has valid CRC and version bytes, while the `used` field is zero. `MDAHeader::parse_buf()` returns `None` when `used == 0`, meaning no variable metadata has been written.

The save path writes both primary and mirrored copies for the chosen older region. The load path chooses the newer primary based on header timestamps, then attempts that primary and its mirror. It does not try the older region if the newer region’s primary and mirror both fail.

## Tests

The tests cover:

- Default header layout.
- Failure to load all-zero uninitialized MDA headers.
- Successful load after initialization.
- Header round-trips with arbitrary data and timestamps.
- CRC failure detection.

## Notable Edge Cases

- `save_state()` rejects equal timestamps as “Overwriting newer data” because it uses `>=`.
- Header timestamps must be representable as non-negative unsigned timestamps.
- Load falls back from an invalid primary header to the corresponding mirror during `MDARegions::load()`.
- `load_state()` treats a known header as a promise that payload bytes must exist and validate.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mda.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mod.rs

## Purpose

`metadata/mod.rs` is the public module facade for Stratis metadata support. It defines the `bytes!` helper macro, declares metadata submodules, and re-exports the metadata types and functions used elsewhere in the engine.

## Contents

- Defines `bytes!($number)` to convert a sector count into bytes via `devicemapper::SECTOR_SIZE`.
- Declares private submodules:
  - `bda`
  - `mda`
  - `sizes`
  - `static_header`
- Re-exports:
  - `BDA`
  - `BlockdevSize`
  - `MDADataSize`
  - `device_identifiers`
  - `disown_device`
  - `static_header`
  - `MetadataLocation`
  - `StaticHeader`
  - `StaticHeaderResult`
  - `StratisIdentifiers`

## Role

This file keeps the metadata subsystem’s internal layout private while exposing the stable engine-facing API for BDA handling, static-header discovery/repair, and selected size types.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/sizes.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/sizes.rs

## Purpose

`sizes.rs` defines strongly typed metadata layout sizes for Stratis block devices. It prevents mixing static-header, MDA, BDA, reserved, and block-device size concepts while centralizing sector/byte conversion rules.

## Static Header Layout

`static_header_size` defines:

- 1 sector of pre-signature padding.
- 1 sector signature block.
- 6 sectors post-signature padding.
- Two such signature regions.
- Total static header size: 16 sectors.
- First signature block starts at sector 1.
- Second signature block starts at sector 9.

`StaticHeaderSize` wraps the constant total size and exposes `sectors()`.

## MDA Layout

`mda_size` defines:

- MDA region header size: 32 bytes.
- Minimum metadata data region size: 260,064 bytes.
- Two primary MDA regions.
- Four total regions, because each primary has a mirrored copy.

Key types:

- `MDASize(Sectors)` represents the whole MDA.
- `MDARegionSize(Sectors)` represents one MDA region.
- `MDADataSize(Bytes)` represents usable variable metadata payload bytes.

Conversions:

- `MDASize::region_size()` divides total MDA size by four.
- `MDASize::bda_size()` adds static header sectors.
- `MDARegionSize::mda_size()` multiplies by four.
- `MDARegionSize::data_size()` subtracts the 32-byte header.
- `MDADataSize::region_size()` adds the header and rounds up to full sectors.

## BDA Layout

`bda_size` defines:

- `BDASize`
  - The BDA proper, excluding reserved space.
- `BDAExtendedSize`
  - BDA plus reserved space.
- `ReservedSize`
  - Space immediately after the BDA proper.

Each wraps `Sectors` and exposes `new()` plus `sectors()`.

## Block Device Size

`blkdev_size::BlockdevSize` wraps the total size of a Stratis member block device. In encrypted pools this is the dm-crypt device size, not the underlying physical block device size.

## Notable Details

- `MDADataSize::new()` floors small requested values to the design minimum.
- Comments note `MDADataSize::new()` is currently dead due to an issue requiring future client-specified metadata size.
- The type system documents construction invariants: valid MDA sizes are produced either from device metadata or from validated region/data size conversions.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/sizes.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/static_header.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/metadata/static_header.rs

## Purpose

`static_header.rs` implements Stratis static signature-block metadata. It reads, writes, repairs, parses, and wipes the two redundant static headers at the start of each Stratis member device.

## Main Responsibilities

- Encode and decode the Stratis signature block.
- Store pool UUID, device UUID, block device size, sigblock version, MDA size, reserved size, and initialization time.
- Read both redundant signature blocks independently.
- Repair missing, stale, unreadable, or corrupted copies when a valid peer exists.
- Distinguish non-Stratis devices from corrupted Stratis devices.
- Wipe Stratis identifying information from the static-header region.

## Key Constants

- `RESERVED_SECTORS`: 3 MiB of reserved space.
- `STRAT_MAGIC`: Stratis magic bytes.
- CRC algorithm: CRC-32C iSCSI/Castagnoli.
- Static header layout constants come from `sizes::static_header_size`.

## Key Types

- `StaticHeaderResult`
  - Holds read bytes or read error plus optional parsed header result.
  - Invariant: read error means no parsed header.
- `MetadataLocation`
  - `Both`, `First`, `Second`.
- `StratisIdentifiers`
  - Pool UUID and device UUID.
- `StaticHeader`
  - block device size, sigblock version, identifiers, MDA size, reserved size, flags, initialization time.

## Public Functions

- `device_identifiers()` reads and repairs sigblocks, then returns identifiers.
- `static_header()` reads and repairs sigblocks, then returns the full header.
- `disown_device()` wipes the static header region.

## Important Methods

- `StaticHeader::new()` builds a header and truncates initialization time to whole seconds.
- `read()` reads both sigblock sectors separately.
- `write()` writes one or both static-header regions, including zeroed padding and `sync_all()`.
- `bda_extended_size()` returns BDA plus reserved space.
- `read_sigblocks()` returns bytes plus parse results for both locations.
- `write_header()` is the repair callback that writes a header.
- `do_nothing()` is a repair callback for read-only validation behavior.
- `repair_sigblocks()` reconciles the two sigblock reads.
- `sigblock_to_buf()` serializes the signature block and writes its CRC.
- `sigblock_from_buf()` validates magic, CRC, version, UUIDs, sizes, and timestamp.
- `wipe()` zeroes the full static-header region.

## Repair Semantics

If both sigblocks parse successfully:

- Equal headers are accepted.
- Different initialization times choose the newer header and rewrite the older location.
- Same initialization time with differing contents is an error.

If one sigblock is valid and the other is missing, invalid, or unreadable:

- The valid sigblock is returned.
- The other location is repaired when the provided callback writes.

If both locations lack Stratis magic:

- Returns `Ok(None)`.

If metadata looks like Stratis but neither sigblock validates:

- Returns an error.

If neither sigblock location can be read:

- Returns an error.

## Tests

The tests verify:

- Ownership detection before write, after write, and after wipe.
- One-corrupt-copy repair.
- Both-copy corruption behavior, including magic-byte corruption treated as non-Stratis when both magic values are gone.
- Serialization round-trip of header fields.
- Rewriting older sigblocks from newer sigblocks.

## Notable Edge Cases

- The `flags` field is carried in memory but not meaningfully parsed from disk here; parsed headers set it to `0`.
- Timestamp parsing uses unsigned seconds with zero nanoseconds.
- Repair behavior is parameterized by callback, allowing no-write scans.
- Static header writes sync after each region write.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/metadata/static_header.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/mod.rs

## Purpose

`strat_engine/mod.rs` is the module root and public facade for the Stratis engine implementation. It declares the internal implementation modules and re-exports the engine types and helpers used by the rest of stratisd.

## Declared Modules

- `backstore`
- `cmd`
- `crypt`
- `device`
- `devlinks`
- `dm`
- `engine`
- `keys`
- `liminal`
- `metadata`
- `names`
- `ns`
- `pool`
- `serde_structs`
- `shared`
- `thinpool`
- `udev`
- `writing`

## Public Re-exports

Always exported:

- `integrity_meta_space`
- crypt token helpers and constants
- `get_dm`, `get_dm_init`
- `StratEngine`
- process keyring helpers and `StratKeyActions`
- `StaticHeader`, `StaticHeaderResult`, `BDA`
- `unshare_mount_namespace`
- `ThinPoolSizeParams`

With `extras` feature:

- `ProcessedPathInfos`
- `pool_inspection`
- v1 `StratPool`

## Role

The file controls module visibility for the engine and exposes selected implementation details without making all submodules public.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/names.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/names.rs

## Purpose

`names.rs` centralizes Stratis naming conventions for kernel key descriptions and device-mapper names/UUIDs. It ensures generated names fit DM name and UUID buffer limits and remain versioned.

## Key Constants

- `FORMAT_VERSION = 1`
- Stratis key descriptions use prefix `stratis-1-key-`.
- Volume-key descriptions use prefix `stratis-1-vk-`.

## Key Description Handling

`KeyDescription` extensions:

- `from_system_key_desc()` recognizes Stratis-owned system key descriptions, strips the prefix, rejects empty descriptions, and validates the application key description.
- `to_system_string()` adds the Stratis key prefix for kernel keyring registration.

`VolumeKeyKeyDescription::to_system_string()` formats a pool volume-key description from its UUID.

## Device-Mapper Name Formatting

- `format_crypt_name(dev_uuid)`
  - `stratis-1-private-<dev_uuid>-crypt`
- `format_crypt_backstore_name(pool_uuid)`
  - `stratis-1-private-<pool_uuid>-crypt`
- `format_flex_ids(pool_uuid, role)`
  - private flex device names and UUIDs.
- `format_thin_ids(pool_uuid, role)`
  - thin filesystem names and UUIDs.
- `format_thinpool_ids(pool_uuid, role)`
  - private thinpool names and UUIDs.
- `format_backstore_ids(pool_uuid, role)`
  - physical/cache-layer names and UUIDs.

## Role Enums

- `FlexRole`
  - `MetadataVolume`, `ThinData`, `ThinMeta`, `ThinMetaSpare`
- `ThinRole`
  - `Filesystem(FilesystemUuid)`
- `ThinPoolRole`
  - `Pool`
- `CacheRole`
  - `Cache`, `CacheSub`, `MetaSub`, `OriginSub`

## Behavior Details

The formatting functions build a single string and use it both as the DM name and UUID when appropriate. Each function documents length arithmetic showing the maximum allowed displayed `FORMAT_VERSION` length before `DmNameBuf` or `DmUuidBuf` construction could fail.

## Tests

The key-description test checks:

- Empty Stratis-prefixed key descriptions are ignored.
- Non-prefixed descriptions are ignored.
- Valid prefixed descriptions are parsed.
- Application descriptions may themselves contain the Stratis prefix text after the leading system prefix is stripped.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/names.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/ns.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/ns.rs

## Purpose

`ns.rs` manages mount namespace isolation for stratisd private mounts. It can unshare the current thread from the root mount namespace and create a private tmpfs area under `/run/stratisd/ns_mounts`.

## Key Constants

- `INIT_MNT_NS_PATH = "/proc/1/ns/mnt"`
- `NS_TMPFS_LOCATION = "/run/stratisd/ns_mounts"`

## Public Functions

- `unshare_mount_namespace()`
  - Checks if the current thread is in the root mount namespace.
  - Calls `unshare(CLONE_NEWNS)` only when needed.
  - Asserts afterward that the thread is no longer in the root mount namespace.
- `is_in_root_mount_namespace()`
  - Compares device and inode of `/proc/1/ns/mnt` with `/proc/self/task/<tid>/ns/mnt`.

## Key Type

`MemoryFilesystem` represents a mounted tmpfs used for private namespace mounts.

`MemoryFilesystem::new()`:

- Ensures `NS_TMPFS_LOCATION` exists and is a directory.
- If a mount already exists there, attempts to unmount it.
- Mounts a 1 MiB tmpfs.
- Remounts it as recursive slave/private enough to keep nested mounts from propagating out.
- Returns a guard object.

`Drop` for `MemoryFilesystem` unmounts the tmpfs and logs warnings on failure.

## Dependencies and Interactions

- Uses `nix::sched::unshare`.
- Uses `nix::mount::{mount, umount}`.
- Uses `stat()` to detect namespace identity and existing mounts.
- Converts filesystem errors into `StratisError`.

## Notable Edge Cases

- The precondition notes container behavior: if running in a container, PID must not be 1 or the container must share host PID.
- Existing non-directory path at `NS_TMPFS_LOCATION` is an error.
- Existing mounted filesystem at the namespace mount path is best-effort unmounted before remounting.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/ns.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/dispatch.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/dispatch.rs

## Purpose

`dispatch.rs` defines `AnyPool`, an enum wrapper that erases whether a pool is backed by the v1 or v2 implementation while still implementing the common `Pool` trait.

## Key Type

- `AnyPool`
  - `V1(Box<v1::StratPool>)`
  - `V2(Box<v2::StratPool>)`

## Main Responsibilities

- Forward every `Pool` trait method to the matching v1 or v2 pool.
- Preserve a single engine-facing pool type while allowing metadata-version-specific implementations.
- Normalize trait object returns for filesystems and block devices.

## Forwarded Behavior

The implementation delegates:

- Cache initialization and blockdev addition/growth.
- Filesystem creation, deletion, rename, snapshot, size limits, and merge scheduling.
- Encryption binding, rebinding, unbinding, pool encryption, reencryption, decryption, token slots, and volume-key loading.
- Pool metadata queries.
- Pool size, allocation, overprovisioning, and availability queries.
- Blockdev user info mutation.
- Current/last pool and filesystem metadata dumps.
- Metadata version reporting.

## Dependencies and Interactions

- Bridges `pool::v1` and `pool::v2`.
- Implements the `engine::Pool` trait.
- Uses shared action/result types such as `CreateAction`, `DeleteAction`, `RenameAction`, `SetCreateAction`, `PoolDiff`, and `ActionAvailability`.

## Notable Details

This file contains almost no business logic. Its correctness depends on exact delegation parity: each trait method must call the corresponding implementation on both variants.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/dispatch.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/inspection.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/inspection.rs

## Purpose

`inspection.rs` provides extras-feature metadata inspection utilities. It converts serialized `PoolSave` allocation metadata into human-readable allocation maps and consistency checks for data, cache, crypt, cap, and flex devices.

## Core Model

The file defines small allocation models around `IndexMap<Sectors, (Use, Sectors)>`, where the key is an extent start sector and the value is a usage label plus length.

Shared helpers:

- `sum()` totals extents matching selected use labels.
- `filled()` inserts synthetic unused extents between recorded extents.
- `add()` inserts allocations and rejects duplicate start-sector keys.
- `display()` prints sorted extent tables.
- `check_overlap()` reports overlapping extents by sorted start sector.

## Device Models

- `CapDevice`
  - Uses `Allocated` and `Unused`.
  - Offset depends on encryption: encrypted starts at 0, unencrypted starts after `DEFAULT_CRYPT_DATA_OFFSET_V2`.
- `DataDevice`
  - Starts with Stratis metadata occupying 8192 sectors.
  - Tracks Stratis metadata, integrity metadata, allocated data, and unused space.
  - Checks overlap, integrity metadata 4 KiB alignment, and zero-allocation integrity specs.
- `CacheDevice`
  - Starts with Stratis metadata occupying 8192 sectors.
  - Tracks cache metadata and cache data extents.
- `CryptAllocs`
  - Tracks crypt metadata allocation.
  - Expects exactly one extent at sector 0 with length `DEFAULT_CRYPT_DATA_OFFSET_V2`.
- `FlexDevice`
  - Tracks metadata volume, thin data, thin metadata, thin metadata spare, and unused space.
  - Checks that thin metadata and spare metadata allocations have equal total size.
  - Offset depends on encryption similarly to `CapDevice`.

## Metadata Extraction

- `data_devices()` builds per-device data allocation maps from data-tier device records, integrity metadata allocations, and data-tier blockdev allocations.
- `cache_devices()` builds per-device cache allocation maps from cache-tier device records and two cache allocation lists.
- `crypt_allocs()` extracts crypt metadata allocations from backstore cap metadata.
- `flex_device()` maps thinpool/flex allocation lists into a `FlexDevice`.
- `cap_device()` maps cap-device allocations.

## Public Inspectors

`inspectors::check(metadata)`:

- Determines whether encryption is enabled from pool features.
- Builds each allocation model.
- Runs consistency checks.
- Returns all errors joined by newline in one `StratisError::Msg`.

`inspectors::print(metadata)`:

- Prints thinpool settings, integrity spec, data-device allocations, cache-device allocations, crypt allocations, cap allocations, and flex allocations.

## Notable Edge Cases

- Duplicate start sectors are rejected even before overlap checks.
- `CryptAllocs::check()` records “no allocations” and “multiple allocations” errors, but then expects one extent while inspecting the last entry; malformed empty input can therefore panic instead of returning only accumulated errors.
- Cache device errors are not prefixed with UUID in `inspectors::check()`, unlike data device errors.
- The tool is gated behind `extras` through `pool/mod.rs`, so it is diagnostic code rather than normal runtime setup logic.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/inspection.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/mod.rs

## Purpose

`pool/mod.rs` is the pool module facade. It declares pool implementation modules and re-exports the version-dispatch wrapper.

## Contents

- Declares:
  - `dispatch`
  - `inspection` behind `extras`
  - `v1`
  - `v2`
- Re-exports:
  - `AnyPool`

## Role

This file keeps pool implementation organization explicit while making `AnyPool` the main engine-facing pool type.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/v1.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/pool/v1.rs

## Purpose

`pool/v1.rs` implements the v1 Stratis pool runtime. It coordinates the v1 backstore, thinpool, filesystems, metadata persistence, cache handling, device growth, availability state, and legacy encryption-token behavior.

## Key Type

`StratPool` contains:

- `backstore: Backstore`
- `thin_pool: ThinPool<Backstore>`
- `action_avail: ActionAvailability`
- `metadata_size: Sectors`
- `last_reencrypt: Option<DateTime<Utc>>`

## Metadata Consistency Helpers

- `next_index()` computes the next free cap-device sector by looking at the last allocation in each flex device list.
- `check_metadata()` verifies:
  - cap allocation length matches flex-device usage,
  - flex allocation totals match the computed next index,
  - data-tier allocations are nonzero,
  - cap/flex usage does not exceed data-tier allocation.
- `get_pool_state()` limits pool actions when encryption metadata is inconsistent or when the backstore reports limited availability.

## Initialization and Setup

- `initialize()` creates a new pool from unowned devices:
  - validates encryption key descriptions,
  - creates a new pool UUID,
  - initializes the v1 backstore,
  - creates the thinpool using usable data-tier size,
  - rolls back backstore initialization on thinpool sizing/setup failures,
  - writes initial metadata.
- `setup()` reconstructs a pool from metadata and block devices:
  - runs `check_metadata()`,
  - sets up backstore and thinpool,
  - derives action availability,
  - rewrites metadata when old fields need migration or `started` is not true,
  - optionally wipes removed cache devices or their crypt handles,
  - returns pool name and pool object.

## Core Pool Operations

Important inherent methods:

- `record()` serializes runtime state into `PoolSave`.
- `write_metadata()` serializes `record()` and saves it through the backstore.
- `event_on()` checks thinpool status, computes diffs, and writes metadata if state changed.
- `fs_event_on()` checks filesystem events.
- `stop()` writes metadata with `started = false`, tears down thinpool/backstore, and returns a `DeviceSet`.
- `destroy()` tears down thinpool and destroys backstore metadata.
- `udev_pool_change()` emits synthetic udev change events for all filesystems.
- `rename_pool()` updates encrypted pool name metadata through backstore.
- `check_fs_limit()` and `check_overprov()` enforce filesystem count and overprovisioning policy.

## Pool Trait Behavior

The `Pool` implementation is annotated with `strat_pool_impl_gen` and pool-action macros that gate actions by availability and update maintenance state on rollback errors.

Major behaviors:

- `init_cache()` validates paths, rejects cache for encrypted pools when unsupported, checks device ownership, sector-size compatibility, suspends the thinpool, initializes cache in backstore, points thinpool at the new backstore cap device, resumes, writes metadata, and supports idempotent cache initialization.
- `add_blockdevs()` handles cache and data tiers separately:
  - cache additions require an existing cache and thinpool suspend/resume,
  - data additions update backstore without suspending the thinpool,
  - both validate ownership and sector sizes,
  - data additions update queue mode and out-of-metadata flags and can return `PoolDiff`.
- `create_filesystems()` validates specs, filesystem names, existing same-name size compatibility, filesystem limit, and overprovisioning before creating missing filesystems.
- `destroy_filesystems()`, `rename_filesystem()`, and `snapshot_filesystem()` delegate to thinpool with validation.
- Size queries combine backstore and thinpool data; allocated and used sizes include Stratis metadata size.
- Blockdev and filesystem getters expose trait objects backed by internal types.
- `set_blockdev_user_info()` validates optional user info as a name, mutates backstore metadata, and writes pool metadata on change.
- `set_fs_limit()` and `set_overprov_mode()` write metadata only when thinpool reports a save is needed.
- `grow_physical()` grows a block device, refreshes thinpool queue/out-of-space state, writes metadata when needed, and returns diffs.
- `set_fs_size_limit()` validates and changes per-filesystem size limits.
- `current_metadata()` and `last_metadata()` return current serialized JSON and last persisted metadata.
- `current_fs_metadata()` and `last_fs_metadata()` delegate to thinpool filesystem metadata helpers.

## Encryption Behavior

v1 supports legacy encryption-token operations but rejects v2-only conversion/decryption flows.

Supported:

- `bind_clevis()` only with legacy token slot input; returns `CLEVIS_LUKS_TOKEN_ID`.
- `bind_keyring()` only with legacy token slot input; verifies key presence and returns `LUKS2_TOKEN_ID`.
- `rebind_keyring()` and `rebind_clevis()` reject explicit token slots.
- `unbind_keyring()` and `unbind_clevis()` reject explicit token slots.
- `start_reencrypt_pool()`, `do_reencrypt_pool()`, and `finish_reencrypt_pool()` support reencryption and update `last_reencrypt`.

Rejected as v2-only:

- `start_encrypt_pool()`
- `do_encrypt_pool()`
- `finish_encrypt_pool()`
- `decrypt_pool_idem_check()`
- `do_decrypt_pool()`
- `finish_decrypt_pool()`

`free_token_slots()` returns `None`, and volume-key load checks return `false` because v1 does not expose v2 token-slot semantics.

## State Diff Support

`StratPoolState` captures:

- metadata size,
- out-of-allocation-space status,
- total physical size.

Its `StateDiff` implementation produces `StratPoolDiff`. `DumpState` refreshes metadata size from backstore when dumping.

## Tests

The test module covers:

- Cache initialization preserving existing filesystem data.
- Adding data devices after cache initialization.
- Extending a pool that has run out of allocation space.
- Maintenance-mode transitions from rollback errors.
- Overprovisioning enable/disable behavior.
- Physical device growth and resulting pool diffs.
- Stopping and restarting a pool without cache.
- Online reencryption with keyring and Clevis metadata.

## Notable Edge Cases

- `setup()` may leave a pool running if metadata rewrite fails only because actions are disabled by limited availability.
- Cache removal during setup is represented by `paths_to_wipe` and best-effort wiping with warnings.
- Cache and data tier addition reject devices already known to the same pool but recorded in the wrong tier.
- v1 token-slot APIs intentionally reject non-legacy explicit token-slot input and direct users to migrate to v2.
- `record()` always writes empty `features` for v1 metadata while preserving `last_reencrypt`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/pool/v1.rs -->