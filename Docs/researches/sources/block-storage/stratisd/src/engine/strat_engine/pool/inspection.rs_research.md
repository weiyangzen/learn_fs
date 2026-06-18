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
