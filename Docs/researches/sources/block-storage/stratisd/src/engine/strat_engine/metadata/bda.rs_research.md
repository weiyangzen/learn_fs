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
