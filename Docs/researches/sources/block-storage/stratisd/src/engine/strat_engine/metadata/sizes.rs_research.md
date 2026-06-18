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
