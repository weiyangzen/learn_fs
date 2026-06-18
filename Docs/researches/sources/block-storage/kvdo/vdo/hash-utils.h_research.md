# File Research: sources/block-storage/kvdo/vdo/hash-utils.h

## Purpose
Defines how UDS chunk-name bytes are partitioned for volume index, chapter index, and sampling, and provides inline extraction/mapping helpers.

## Main Helpers
- `extract_volume_index_bytes()`: first 8 bytes as big-endian 64-bit value.
- `extract_chapter_index_bytes()`: next 6 bytes as a 48-bit value.
- `extract_sampling_bytes()`: final 2 bytes.
- `hash_to_chapter_delta_list()`: maps a name to chapter delta-list number.
- `hash_to_chapter_delta_address()`: maps a name to delta address within that list.
- `name_to_hash_slot()`: maps to an open-chapter hash slot.

## Dependencies
Uses geometry-derived address/list bit counts and unaligned big-endian accessors.
