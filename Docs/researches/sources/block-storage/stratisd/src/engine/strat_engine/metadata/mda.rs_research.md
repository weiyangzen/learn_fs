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
