# Group Research: group_1780_stratisd_sources_block_storage_stratisd_src_engine_strat_engine_bac_385f38914b39

Scope checked against `Docs/research_subset_a.md`: `sources/block-storage/stratisd` is included. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/devices.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/devices.rs

Read status: complete, 1594 lines.

## Purpose

`devices.rs` is the Stratis backstore device discovery and initialization gate. It converts user-provided paths into verified device records, separates already-owned Stratis devices from unowned devices, initializes new Stratis metadata, and wipes initialized block devices during rollback or disown operations.

The file supports both legacy v1 encrypted block devices and newer v2 block devices.

## Main Types

- `BlockSizes`: physical and logical sector sizes read from a block device.
- `DeviceInfo`: device number, canonical path, optional `ID_WWN`, size, and block sizes.
- `StratisDevices`: map of Stratis-owned devices grouped by `PoolUuid` and `DevUuid`.
- `ProcessedPathInfos`: result of path processing, split into Stratis-owned and unclaimed devices.
- `UnownedDevices`: verified devices suitable for Stratis initialization.

## Discovery And Validation Flow

`ProcessedPathInfos::try_from(&[&Path])` is the main entry point for path processing.

It:

1. Canonicalizes inputs through `DevicePath::new`.
2. Deduplicates paths.
3. Calls `dev_info`.
4. Enforces the minimum device size of 1 GiB through `check_dev`.
5. Rejects duplicate device numbers.
6. Splits devices into:
   - `stratis_devices`, keyed by pool/device UUID from Stratis metadata.
   - `unclaimed_devices`, with no Stratis identifiers.

`dev_info` combines udev and blkid:

- `udev_info` reads ownership, device number, and optional `ID_WWN`.
- Devices identified as `Luks`, `MultipathMember`, or `Theirs` are rejected.
- Devices identified as `Stratis` or `Unowned` are additionally checked with blkid.
- `verify_device_with_blkid` enables superblock and partition probing, then rejects devices with partitions or unrelated superblocks.
- `device_identifiers` reads Stratis BDA metadata and must agree with udev if udev reported Stratis ownership.

## Public Helpers

- `get_devno_from_path`: uses `stat` and converts `st_rdev` into a devicemapper `Device`.
- `find_stratis_devs_by_uuid`: scans libblkid cache for Stratis devices matching a pool UUID and a target device UUID list. This is explicitly a workaround for cases where udev events cannot be processed due to internal stratisd locking.
- `get_logical_sector_size`: queries blkid topology for logical sector size.
- `wipe_blockdevs`: best-effort disown over `InternalBlockDev` instances, collecting failures into `BestEffortError`.

## Initialization Behavior

`initialize_devices_legacy` initializes v1 block devices. It supports encryption through `CryptHandle::initialize`.

For encrypted v1 devices:

- A LUKS2 device is initialized.
- Logical encrypted device size is read.
- Stratis BDA metadata is written to the activated metadata path.
- Hardware ID is discarded because encrypted devices are represented by devicemapper nodes.
- Failure after LUKS initialization triggers `CryptHandle::wipe`.

For unencrypted v1 devices:

- BDA metadata is written directly to the physical path.
- Failure triggers `disown_device`.

`initialize_devices` initializes v2 block devices. It writes v2 BDA metadata directly to device paths and constructs `v2::StratBlockDev`; encryption is not part of this function.

Both initialization paths use the global `BLOCKDEVS_IN_PROGRESS` mutex-protected set to reject concurrent initialization attempts involving the same paths.

## Rollback Semantics

Initialization is transactional at the batch level as far as practical:

- If one device fails to initialize, previously initialized devices in the batch are passed to `wipe_blockdevs`.
- Cleanup failures are logged and wrapped as rollback errors where applicable.
- The in-progress path set is always cleaned after initialization returns.

## Tests

The tests cover:

- Nonexistent paths produce errors rather than panics.
- Duplicate devnodes are deduplicated.
- v1 ownership behavior with and without encryption.
- v1 cleanup after failure, including LUKS metadata cleanup.
- v2 ownership behavior.
- v2 cleanup after failure.
- Loopback and real-device variants are used for many cases.
- Crypt tests depend on key insertion helpers and real/loopback device harnesses.

## Notable Dependencies

- udev ownership helpers from `strat_engine::udev`.
- blkid probing through `libblkid_rs`.
- device sizing and sector size helpers from `strat_engine::device`.
- metadata initialization and disowning from `strat_engine::metadata`.
- v1 encryption through `crypt::handle::v1::CryptHandle`.

## Important Invariants

- Device paths in `ProcessedPathInfos` are unique.
- Device numbers in `ProcessedPathInfos` are unique.
- Device sizes must be at least 1 GiB.
- Devices with partitions or non-Stratis superblocks are not considered unowned.
- Duplicate Stratis identifiers across paths are rejected.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/devices.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/mod.rs

Read status: complete, 24 lines.

## Purpose

This is the module declaration and public re-export surface for the `strat_engine::backstore` subsystem.

## Module Structure

It declares:

- `backstore`
- `blockdev`
- `blockdevmgr`
- `cache_tier`
- `data_tier`
- `devices`
- `range_alloc`
- `shared`

Only selected symbols are re-exported.

## Public Re-exports

From `blockdev::v2`:

- `integrity_meta_space`

From `devices`:

- `find_stratis_devs_by_uuid`
- `get_devno_from_path`
- `get_logical_sector_size`
- `ProcessedPathInfos`
- `UnownedDevices`

Under `#[cfg(test)]`, it also re-exports:

- `initialize_devices`
- `initialize_devices_legacy`

## Role In The Tree

This file intentionally hides most backstore internals while exposing device discovery and block-device utility APIs needed outside the submodule.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/range_alloc.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/range_alloc.rs

Read status: complete, 631 lines.

## Purpose

`range_alloc.rs` implements a sector range allocator for block-device space. It tracks used ranges, coalesces adjacent ranges, rejects overlaps, computes complements, and allocates free space from the front or back of a device.

## Main Types

- `PerDevSegments`: ordered, coalesced used ranges for one device.
- `Iter`: double-ended iterator over `PerDevSegments`.
- `RangeAllocator`: allocation wrapper over `PerDevSegments`.

## PerDevSegments Invariants

The comments and tests enforce:

- No zero-length stored segment.
- No contiguous stored segments; adjacent ranges are coalesced.
- No overlapping segments.
- No segment extends beyond `limit`.

Ranges are stored in a `BTreeMap<Sectors, Sectors>` where the key is start offset and the value is length.

## Insert Logic

`insert`:

- Rejects starts past the limit.
- Ignores zero-length ranges.
- Locates previous and next candidate ranges with `locate_prev_and_next`.
- Uses `insertion_result` to detect overlap and decide whether to coalesce with left, right, or both neighbors.
- Removes merged neighbors and inserts the coalesced range.

`insert_all` is atomic:

- It first inserts into a temporary `PerDevSegments`.
- It then unions that temporary structure with `self`.
- `self` is only replaced after the union succeeds.

## Set Operations

`union` merges two `PerDevSegments` with the same limit. It rejects differing limits and inserts ranges into a new structure, preserving overlap detection.

`complement` returns the free ranges as another `PerDevSegments` with the same limit. Complement-of-complement is tested as an invariant.

## Allocation Behavior

`RangeAllocator::new` creates an allocator with initial used ranges.

`alloc_front`:

- Iterates free ranges from lowest offset.
- Allocates up to the requested amount.
- May return less than requested if insufficient space exists.
- Marks allocated ranges as used.

`alloc_back` does the same from highest offsets and is currently `#[allow(dead_code)]`.

`increase_size` raises the allocation limit and asserts the new size is larger.

## Tests

Tests cover:

- Basic allocation and exhaustion.
- Initial contiguous ranges coalescing into one range.
- Overlapping insertions on previous and next ranges.
- Full allocator overwrite failures.
- Limit overflow and `u64::MAX` arithmetic overflow.
- Empty and full search behavior.
- Searches past the limit.
- Zero-length insert behavior.
- Zero-sized allocator invariants.
- End-of-limit insertion rules.

## Notable Dependencies

- `devicemapper::Sectors`
- `metadata::BlockdevSize`
- `StratisError` and `StratisResult`

## Important Edge Cases

- `start + len` uses checked addition in `insertion_result`.
- A zero-length range at exactly the limit is accepted as a no-op.
- A nonzero range starting at the limit is rejected.
- Allocation can return fewer sectors than requested.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/range_alloc.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/shared.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/shared.rs

Read status: complete, 317 lines.

## Purpose

`shared.rs` contains common backstore structures and helpers used by data and cache tiers: segment representation, devicemapper target construction, allocated-segment recording, block-size validation, and metadata segment reconstruction.

## Main Types

- `Segment`: continuous sector range on a concrete device number.
- `BlkDevSegment`: `Segment` plus Stratis device UUID.
- `AllocatedAbove`: ordered list of block-device segments allocated to a higher layer.
- `BlockDevPartition`: borrowed split of block devices into used and unused sets.
- `BlockSizeSummary`: used/unused block-size groups.
- `SectorSizes`: private helper grouping base and optional crypt sector sizes.

## Segment Recording

`AllocatedAbove` implements `Recordable<Vec<BaseDevSave>>`.

Each `BlkDevSegment` becomes a `BaseDevSave` containing:

- parent device UUID
- start sector
- length

This is the persistence form for upper-layer allocations.

## Devicemapper Mapping

`AllocatedAbove::map_to_dm` converts ordered segments into linear devicemapper target lines.

It:

- Preserves segment order.
- Builds `LinearTargetParams` from physical device and start offset.
- Tracks cumulative logical start offset.
- Emits `TargetLine<LinearDevTargetParams>` entries.

## Coalescing

`coalesce_blkdevsegs` appends new segments while merging adjacent segments only when:

- UUIDs match.
- The left segment end equals the right segment start.

It preserves order and does not attempt global sorting.

## Block Size Validation

`BlockSizeSummary::validate` checks whether current used and unused device sector sizes are safe for future extension.

Key behavior:

- If there are no used devices, more than one unused size group is an error.
- If there are used devices, unused logical sector sizes must not exceed the largest used logical sector-size tuple.
- Unused physical sector sizes must not exceed the largest used physical sector-size tuple.
- On success, it returns a representative `StratSectorSizes`.

This prevents adding larger-sector unused devices later in a way that could make filesystems unmountable after extension.

## Metadata Reconstruction

`metadata_to_segment` maps persisted `BaseDevSave` records back to `BlkDevSegment`.

It requires a UUID-to-device-number map and returns an error if metadata references a missing Stratis device UUID.

## Notable Dependencies

- `InternalBlockDev` for block-size extraction.
- `StratSectorSizes` and `BlockSizes`.
- devicemapper target types.
- serde save structs: `BaseDevSave`, `Recordable`.

## Important Assumptions

- Segment ordering in `AllocatedAbove` is meaningful and preserved.
- Coalescing is local to adjacent list entries.
- Sector-size validation is conservative because crypt and base sector sizes may differ.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/backstore/shared.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/cmd.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/cmd.rs

Read status: complete, 616 lines.

## Purpose

`cmd.rs` centralizes stratisd invocation of external executables. It discovers fixed command paths, verifies required tools, wraps command execution and error reporting, and provides helper functions for XFS, thin-provisioning tools, Clevis, and cryptsetup reencryption operations.

## Executable Discovery

`find_executable` searches only known directories, not `$PATH`.

Default search directories:

- `/usr/sbin`
- `/sbin`
- `/usr/bin`
- `/bin`

They can be overridden at compile time through `EXECUTABLES_PATHS`.

`EXECUTABLES` lazily records paths for required non-Clevis commands:

- `mkfs.xfs`
- `thin_check`
- `thin_repair`
- `xfs_db`
- `xfs_growfs`
- `thin_metadata_size`
- `cryptsetup`
- `udevadm` in tests

`verify_executables` must be called at engine initialization and errors on the first missing required executable.

Clevis commands are checked dynamically by `get_clevis_executable`, which requires the full Clevis support command set.

## Command Execution

`execute_cmd` runs a `Command` and delegates output handling.

`handle_output`:

- Returns success on zero exit.
- On failure, includes command debug output, exit reason, stdout, and stderr in the `StratisError`.

## XFS Helpers

`create_fs` invokes `mkfs.xfs`.

Important behavior:

- Uses `-f`.
- Optionally sets filesystem UUID.
- Reads `mkfs.xfs -V` and enables `-i nrext64=0` for xfsprogs >= 6.0.0.
- If version probing fails, it assumes the option is supported and lets command failure surface naturally.

`xfs_growfs` runs `xfs_growfs <mount> -d`.

`set_uuid` runs `xfs_db -x -c "uuid <uuid>" <devnode>`.

## Thin-Provisioning Helpers

`thin_check` runs `thin_check --auto-repair`.

`thin_repair` runs `thin_repair -i <meta_dev> -o <new_meta_dev>`.

`thin_metadata_size` runs `thin_metadata_size`, parses sector count output, multiplies by an empirical factor of 8, rounds up to the pool block size, and caps at `MAX_META_SIZE`.

## Clevis Helpers

`clevis_luks_bind` supports two authentication forms:

- Existing token slot through `Either::Left`.
- Passphrase/key material through stdin via `Either::Right`.

It calls `clevis luks bind` with device, optional existing slot, optional target slot, pin, and JSON config.

`clevis_luks_unbind` runs forced unbind for a keyslot.

`clevis_luks_regen` regenerates a Clevis binding.

`clevis_decrypt` safely extracts a passphrase from a JWE:

1. Pipes JSON to `jose jwe fmt -i- -c`.
2. Pipes formatted output to `clevis decrypt`.
3. Reads decrypted bytes into `SafeMemHandle`.
4. Returns `SizedKeyMemory`.

## Cryptsetup Reencryption Helpers

- `run_encrypt`: `cryptsetup reencrypt --encrypt --resume-only --token-only <path>`
- `run_reencrypt`: `cryptsetup reencrypt --resume-only --token-only <path>`
- `run_decrypt`: `cryptsetup reencrypt --decrypt --resume-only --token-only <path>`

Each first ensures access to the persistent keyring.

## Notable Dependencies

- `libcryptsetup_rs::SafeMemHandle`
- `serde_json::Value`
- `semver` for `mkfs.xfs` version checks
- Stratis keyring helpers
- devicemapper `MetaBlocks` and `Sectors`

## Important Notes

- The module assumes executable locations are fixed once discovered.
- Clevis support is all-or-nothing based on the required executable list.
- Some helper functions call `wait` twice after `spawn`; this is observable in `get_mkfs_xfs_version` and `thin_metadata_size` and should be considered carefully if modified.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/cmd.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/consts.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/consts.rs

Read status: complete, 43 lines.

## Purpose

`consts.rs` defines shared crypt/LUKS2 token constants, default metadata sizing constants, and Clevis-related constants.

## Token JSON Keys

- `TOKEN_TYPE_KEY`
- `TOKEN_KEYSLOTS_KEY`
- `STRATIS_TOKEN_DEVNAME_KEY`
- `STRATIS_TOKEN_POOL_UUID_KEY`
- `STRATIS_TOKEN_DEV_UUID_KEY`
- `STRATIS_TOKEN_POOLNAME_KEY`

## Token IDs

- `STRATIS_TOKEN_ID = 0`
- `LUKS2_TOKEN_ID = 1`
- `CLEVIS_LUKS_TOKEN_ID = 2`

These fixed IDs are used heavily by legacy v1 crypt handling.

## Token Types

- `LUKS2_TOKEN_TYPE = "luks2-keyring"`
- `STRATIS_TOKEN_TYPE = "stratis"`
- `CLEVIS_TOKEN_TYPE = "clevis"`

## Crypt Sizing Constants

- `STRATIS_MEK_SIZE`: 512-bit media encryption key size.
- `LUKS2_SECTOR_SIZE`: 4096 bytes.
- `DEFAULT_CRYPT_METADATA_SIZE_V1`: 16 KiB.
- `DEFAULT_CRYPT_METADATA_SIZE_V2`: 64 KiB.
- `DEFAULT_CRYPT_KEYSLOTS_SIZE`: 16352 KiB.
- `DEFAULT_CRYPT_DATA_OFFSET_V2`: 34816 sectors.

## Clevis Constants

- `CLEVIS_TANG_TRUST_URL`: Stratis-specific JSON key allowing Tang URL trust.
- `CLEVIS_TOKEN_NAME`: null-terminated `clevis`.
- `CLEVIS_RECURSION_LIMIT`: 20.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/consts.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/mod.rs

Read status: complete, 6 lines.

## Purpose

This file declares the crypt handle version modules.

## Modules

- `v1`
- `v2`

It has no logic beyond module exposure.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/v1.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/v1.rs

Read status: complete, 1756 lines.

## Purpose

`crypt/handle/v1.rs` implements legacy per-block-device LUKS2 handling for Stratis. It formats encrypted devices, stores and validates Stratis LUKS2 token metadata, activates devices through keyring or Clevis, manages bindings, handles reencryption hooks, resizes encrypted devices, deactivates devices, and wipes LUKS2 metadata.

## Metadata Model

v1 stores a Stratis-specific LUKS2 token in fixed token slot `STRATIS_TOKEN_ID`.

`StratisLuks2Token` contains:

- activation devicemapper name
- pool UUID
- device UUID
- optional pool name

The token serializes with type `stratis`, empty keyslots, activation name, pool UUID, device UUID, and optional pool name.

The custom deserializer rejects:

- Missing required fields.
- Unknown keys.
- Wrong token type.
- Non-empty keyslots.
- Invalid UUIDs or devicemapper names.

## Crypt Metadata

`CryptMetadata` contains:

- physical LUKS2 path
- Stratis identifiers
- `EncryptionInfo`
- activation name
- activated path
- optional pool name
- physical device number

`load_crypt_metadata` reads the Stratis token, encryption info, and device number.

## Device Recognition

`setup_crypt_device` loads a possible LUKS2 device and returns it only if `is_encrypted_stratis_device` succeeds.

v1 recognition requires:

- Valid Stratis token.
- Either a LUKS2 keyring token or Clevis token.
- Valid LUKS2 token type if present.

## Initialization

`CryptHandle::initialize`:

1. Builds activation name from device UUID.
2. Optionally configures LUKS2 sector size.
3. Initializes a cryptsetup context.
4. Sets v1 metadata and keyslot sizes.
5. Calls `initialize_with_err`.
6. Reads encryption info from metadata.
7. Builds a `CryptHandle`.
8. On error, attempts rollback through `ensure_wiped`.

`initialize_with_err`:

- Formats LUKS2 as `aes` / `xts-plain64`.
- Uses `STRATIS_MEK_SIZE`.
- Asserts crypt data offset matches `crypt_metadata_size`.
- Initializes keyring, Clevis, or both based on `InputEncryptionInfo::into_parts_legacy`.
- Writes the Stratis token.
- Activates the device.

## Unlock Methods

Supported initialization modes:

- Keyring only: `initialize_with_keyring`.
- Clevis only: `initialize_with_clevis`, using a temporary random passphrase and then destroying the temporary keyslot.
- Keyring plus Clevis: `initialize_with_both`.

`CryptHandle::setup` can activate by token method and optional passphrase.

`CryptHandle::can_unlock` simulates unlock via keyring and/or Clevis and logs failures as warnings.

## Binding Management

`clevis_bind` adds a Clevis binding using the existing keyring token.

`clevis_unbind` refuses to remove Clevis if no keyring binding remains.

`rebind_clevis` regenerates Clevis data and reloads LUKS2 metadata.

`bind_keyring` adds a keyring binding using a passphrase decrypted from Clevis.

`unbind_keyring` refuses to remove keyring binding if no Clevis binding remains.

`rebind_keyring` replaces the key description using the old key description as authentication.

These operations maintain cached `EncryptionInfo`.

## Reencryption And Resize

`setup_reencrypt` delegates to shared reencryption setup.

`do_reencrypt` delegates to shared reencryption execution.

`resize`:

- Rejects explicit zero size.
- Reads a passphrase from keyring or Clevis.
- Activates by passphrase with `KEYRING_KEY`.
- Calls cryptsetup resize.

## Lifecycle Operations

- `deactivate`: ensures devicemapper crypt device is inactive.
- `wipe`: safely wipes LUKS2 metadata.
- `logical_device_size`: reads active device size through libcryptsetup runtime handle.
- `rename_pool_in_metadata`: updates pool name in the Stratis token.
- `reload_metadata`: refreshes cached metadata from disk.

## Tests

Tests cover:

- Failed initialization rollback when key is missing.
- `can_unlock` across active, inactive, and wiped states.
- Encryption behavior by writing random data through logical device and scanning physical disk for plaintext.
- Default crypt metadata sizes.
- Custom sector size initialization.
- Initialization with both keyring and Clevis.
- Clevis-only initialization.
- Tang config validation requiring the Stratis trust flag.
- Clevis SSS config validation.
- Unlock using a provided passphrase after key removal.

Tests include loopback and real-device paths, plus Clevis tests that depend on `TANG_URL`.

## Notable Dependencies

- `libcryptsetup_rs`
- `devicemapper`
- shared crypt helpers for activation, token checks, keyslot management, Clevis decrypt, wipe, and reencryption.
- `cmd.rs` Clevis command wrappers.
- Stratis name formatting and key types.

## Important Invariants

- v1 uses fixed token slots from `consts.rs`.
- Stratis token must be present and well-formed.
- Removing an unlock method is blocked when it would leave the device inaccessible.
- Encrypted devices drop hardware ID when initialized in the backstore because devicemapper nodes do not have hardware IDs.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/v1.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/v2.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/v2.rs

Read status: complete, 1495 lines.

## Purpose

`crypt/handle/v2.rs` implements newer pool-scoped LUKS2 handling. Compared with v1, it removes the per-device Stratis token model, supports flexible token slots, tracks encrypted backstore devices by pool UUID, and includes online encryption and decryption workflows for pools.

## Metadata Model

`CryptMetadata` contains:

- physical LUKS2 path
- pool UUID
- `EncryptionInfo`
- activation name
- activated path

The activation name is derived from the pool UUID with `format_crypt_backstore_name`.

`load_crypt_metadata` does not parse a Stratis token. Instead, it derives activation name from the provided pool UUID and reads encryption info from LUKS2 metadata.

## Device Recognition

`is_encrypted_stratis_device` checks whether `encryption_info_from_metadata` returns at least one unlock token. This is less token-schema-specific than v1.

`setup_crypt_device` returns a crypt device only if this check succeeds.

## Setup And Activation

`setup_crypt_handle`:

- Loads metadata for the physical path and pool UUID.
- If the devicemapper activation path does not exist, activates using the requested `TokenUnlockMethod` and optional passphrase.
- If already active, attempts to load the volume key into the keyring.
- Reads activated device number and size.
- Returns a `CryptHandle`.

## CryptHandle State

v2 `CryptHandle` stores:

- `CryptMetadata`
- active devicemapper `Device`
- size in sectors

It exposes physical path, activation name, device number, encryption info, and test-only activated path/size accessors.

## Initialization

`CryptHandle::initialize`:

1. Derives activation name from pool UUID.
2. Optionally builds LUKS2 params with a sector size.
3. Initializes a cryptsetup context on the physical path.
4. Calls `initialize_with_err`.
5. Reads encryption info.
6. Reads activated device number and size.
7. Constructs `CryptHandle`.
8. On failure, reloads crypt state and rolls back with wipe logic.

`initialize_unlock_methods`:

- Sets v2 metadata size and keyslot size.
- Sets default data offset to `DEFAULT_CRYPT_DATA_OFFSET_V2`.
- Formats LUKS2 as `aes` / `xts-plain64`.
- Splits `InputEncryptionInfo` into key descriptions and Clevis infos, both with and without explicit token IDs.
- Creates temporary passphrase material if no key-description token exists for Clevis binding.
- Adds keyring slots.
- Calls Clevis bind for Clevis entries.
- Reloads LUKS2 state after Clevis changes.
- Deletes temporary keyslot if one was created.
- Returns reconstructed `EncryptionInfo`.

## Binding Management

`bind_clevis`:

- Checks free token slots.
- Interprets Clevis config.
- Gets an existing passphrase from current metadata.
- Calls Clevis bind with optional requested token slot.
- Reloads encryption info.
- Returns the newly added token slot by diffing old and new encryption info.

`unbind_clevis`:

- Refuses to remove the binding if it is the only unlock method.
- Looks up the associated keyslot.
- Calls Clevis unbind.
- Removes cached token info.

`rebind_clevis` regenerates Clevis data for a token slot and updates cached info from the token JSON.

`bind_keyring`:

- Checks free token slots.
- Gets an existing passphrase.
- Selects requested or free token slot.
- Adds keyring keyslot.
- Updates cached `EncryptionInfo`.

`unbind_keyring`:

- Refuses to remove the binding if it is the only unlock method.
- Destroys associated keyslot.
- Removes token.
- Updates cached `EncryptionInfo`.

`rebind_keyring` replaces the key description at a token slot and rejects attempts to rebind a Clevis token as keyring.

## Online Encryption

`setup_encrypt` prepares encryption for an existing unencrypted pool.

It:

- Creates a temporary file and writes 4096 bytes so cryptsetup can initialize on it.
- Initializes LUKS2 metadata with a data offset.
- Chooses sector size from thinpool minimum logical sector size or the unencrypted path’s logical sector size.
- Initializes unlock methods against the temporary device.
- Sets up cryptsetup reencryption metadata in initialize-only mode.
- Restores the LUKS2 header onto the real unencrypted path.
- Activates the crypt mapping with shared mode.
- Returns sector size and key info needed for the actual operation.

`do_encrypt` resumes the prepared encryption operation on the real device using cryptsetup reencryption and then calls `run_encrypt`.

`finish_encrypt` reconstructs a `CryptHandle` after encryption completes.

## Reencryption And Decryption

`setup_reencrypt` and `do_reencrypt` delegate to shared helpers.

`decrypt`:

- Gets a passphrase from existing encryption info.
- Initializes cryptsetup reencryption in decrypt mode.
- Calls `run_decrypt`.
- Logs that the operation may take a while.

## Resize And Wipe

`resize`:

- Rejects explicit zero size.
- Reads pool volume key from process keyring using `VolumeKeyKeyDescription`.
- Activates by volume key with `KEYRING_KEY`.
- Resizes the active mapping.
- Refreshes cached size from the activated path.

`wipe` calls `ensure_wiped`.

`rollback` uses `ensure_wiped`, and if that fails, falls back to manual wipe over the v2 data-offset range.

## Tests

Tests cover:

- Failed initialization rollback for missing keys.
- Encryption behavior by writing random data through logical path and scanning physical disk for plaintext.
- Custom sector size.
- Keyring plus Clevis initialization with explicit token slots.
- Clevis-only initialization.
- v2 metadata/keyslot size defaults.
- Tang config validation requiring the Stratis trust flag.
- Clevis SSS config validation.
- Unlock using provided passphrase after removing key.

Tests include loopback and real-device variants and Clevis tests requiring `TANG_URL`.

## Notable Dependencies

- `libcryptsetup_rs` reencryption APIs.
- `ThinPool<v2::Backstore>` for online encryption sector-size selection.
- `cmd.rs` wrappers for Clevis and cryptsetup resume operations.
- shared crypt helpers for activation, passphrase retrieval, volume-key keyring loading, wipe, and reencryption.
- `get_logical_sector_size` from backstore device helpers.

## Important Differences From v1

- Activation is pool-scoped, not device-UUID-scoped.
- Token slots are flexible rather than fixed to legacy constants.
- No Stratis-specific token deserializer is used in this file.
- Online encrypt/decrypt workflows are present.
- Resize uses pool volume key from the process keyring instead of direct passphrase/Clevis lookup.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/handle/v2.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/macros.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/macros.rs

Read status: complete, 17 lines.

## Purpose

Defines one local macro, `log_on_failure!`, used by crypt code to log failed operations while preserving normal `?` error propagation.

## Macro Behavior

`log_on_failure!($op, $fmt, ...)`:

1. Evaluates `$op`.
2. If the result is `Err`, logs a warning using the provided format plus `; failed with error: {}`.
3. Applies `result?`, so success unwraps and failure returns from the caller.

## Role

This macro keeps cryptsetup-related operations concise while ensuring failures include contextual warnings before bubbling up.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/macros.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/mod.rs -->
# File Research: sources/block-storage/stratisd/src/engine/strat_engine/crypt/mod.rs

Read status: complete, 21 lines.

## Purpose

This is the module declaration and public export surface for `strat_engine::crypt`.

## Module Structure

It declares:

- `macros` with `#[macro_use]`
- `consts`
- `handle`
- `shared`

## Public Re-exports

From `consts`:

- `CLEVIS_LUKS_TOKEN_ID`
- `CLEVIS_TANG_TRUST_URL`
- `DEFAULT_CRYPT_DATA_OFFSET_V2`
- `LUKS2_TOKEN_ID`

From `handle::v1`:

- `crypt_metadata_size`

From `shared`:

- `back_up_luks_header`
- `manual_wipe`
- `register_clevis_token`
- `restore_luks_header`
- `set_up_crypt_logging`

## Role In The Tree

This file exposes stable crypt helpers and constants while keeping most implementation details inside `consts`, `handle`, and `shared`.
<!-- END FILE RESEARCH: sources/block-storage/stratisd/src/engine/strat_engine/crypt/mod.rs -->