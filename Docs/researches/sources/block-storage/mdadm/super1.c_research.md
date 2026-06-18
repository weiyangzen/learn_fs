# File Research: sources/block-storage/mdadm/super1.c

## Purpose
Implements the `superswitch super1` backend for Linux md metadata formats `1.0`, `1.1`, and `1.2`. It covers superblock parsing, aligned IO, creation, update, examination, bitmap/PPL/bad-block-log handling, and v0-to-v1 conversion support.

## Main Responsibilities
- Computes v1 checksums over the variable-size superblock and device-role table.
- Provides 4K-safe aligned reads/writes for devices with larger physical sectors.
- Determines superblock placement:
  - `1.0`: near end of component device.
  - `1.1`: at start.
  - `1.2`: 4 KiB from start.
- Prints detailed, brief, export, and bad-block-list views.
- Converts metadata into `struct mdinfo`, including reshape state, replacement devices, consistency policy, PPL, bitmap, journal, and free-space hints.
- Initializes v1 metadata with UUID/name/homehost handling and RAID0 layout defaults.
- Writes initial metadata, preserves device UUIDs/events where appropriate, initializes journal meta blocks, bitmaps, and PPL headers.
- Updates metadata for assemble, force, UUID/name, bitmap/PPL/BBL changes, write-mostly/failfast flags, device-size refresh, RAID0 layout flags, and reshape rollback.
- Copies metadata, bitmap regions, and bad-block logs between devices.

## Integration
The file exports `struct superswitch super1`. It is central to mdadm’s modern native metadata flow and interacts with:
- shared mdadm metadata abstractions from `mdadm.h`;
- UUID helpers;
- bitmap and clustered bitmap structures;
- PPL/R5 journal structures and CRC32C;
- system geometry helpers from `util.c`;
- legacy conversion from `super0.c` through `super1_make_v0()`.

## Notable Behavior
- `load_super1()` can auto-detect the best 1.x minor version by trying all variants and choosing the newest creation time.
- `getinfo_super1()` derives usable/free space before and after data differently depending on whether metadata is before or after data.
- Bitmap support includes clustered bitmaps with per-node bitmap space calculations.
- PPL support excludes arrays with internal bitmap or journal and reserves up to the multi-PPL area size.
- RAID0 layout flags are conditional for older kernels but forced for Linux 5.4+ behavior.

## Risks and Edge Cases
- Many offsets are signed relative-sector fields stored in little-endian metadata; mistakes can corrupt bitmap, BBL, or data placement.
- `md_feature_any_ppl_on()` mixes CPU and little-endian conversions in a compact helper; callers must pass the expected representation.
- Device-size compatibility checks are bypassable through `ignore_hw_compat`, which is useful for probing but risky if misused.
- Reshape rollback has strict alignment requirements and special handling for no-backup offset reshape.
