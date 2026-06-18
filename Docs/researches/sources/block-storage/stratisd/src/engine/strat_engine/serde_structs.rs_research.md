# File Research: sources/block-storage/stratisd/src/engine/strat_engine/serde_structs.rs

## Purpose
Defines serde-friendly save structures for Stratis on-disk JSON metadata. These structures intentionally differ from richer in-memory engine objects so persistence remains stable and simple.

## Main Components
- `Recordable<T>` trait abstracts conversion from runtime objects into serializable save records.
- `PoolFeatures` enumerates optional pool features: `Raid`, `Integrity`, `Encryption`, `KeyDescriptionEnabled`, and `ClevisEnabled`.
- `impl From<Vec<PoolFeatures>> for Features` maps persisted feature flags to API-facing feature booleans.
- `PoolSave` is the top-level variable-length pool metadata record.
- `FilesystemSave` is per-filesystem metadata stored separately on the metadata volume.
- Supporting structs describe backstore, block devices, allocations, cap device, cache tier, flex devices, and thinpool metadata.

## Serialization Details
String metadata is capped at `MAXIMUM_STRING_SIZE` bytes. `safe_split_at()` truncates only at UTF-8 character boundaries, using `our_floor_char_boundary()` to avoid invalid string slices. This applies to pool/filesystem names and optional block-device `user_info`/`hardware_info`.

`last_reencrypt` is serialized as a Unix timestamp integer and deserialized back into `DateTime<Utc>`. The serializer expects the option to be `Some` when invoked, and the field uses `skip_serializing_if = "Option::is_none"`.

Several fields are optional for backward compatibility and have TODO comments indicating they should become required in Stratis 4.0:
- `PoolSave.started`
- `ThinPoolDevSave.feature_args`
- `ThinPoolDevSave.fs_limit`
- `ThinPoolDevSave.enable_overprov`

## Metadata Model
`PoolSave` contains:
- pool name,
- `BackstoreSave`,
- `FlexDevsSave`,
- `ThinPoolDevSave`,
- started flag,
- feature list,
- last reencryption timestamp.

`BackstoreSave` contains data tier, cap device, and optional cache tier. `DataTierSave` includes blockdev metadata plus optional integrity spec. `BlockDevSave` stores allocation lists and base device records. `CapSave` stores cap allocations and optional crypt metadata allocations.

`FilesystemSave` records filesystem name, UUID, thin ID, size, creation timestamp, optional size limit, optional origin UUID, and merge flag.

## Tests
A property test verifies `safe_split_at()` always returns a prefix, respects UTF-8 boundaries, and truncates within a bounded byte delta caused by multibyte characters.

## Research Notes
This file is central for metadata compatibility. Most structs are plain data carriers, but the UTF-8-safe truncation and optional-field defaults are important compatibility behavior for older metadata and user-controlled strings.
