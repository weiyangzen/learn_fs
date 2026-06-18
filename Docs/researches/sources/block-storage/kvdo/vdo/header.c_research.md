# File Research: sources/block-storage/kvdo/vdo/header.c

## Purpose
Implements encoding, decoding, and validation of versioned VDO on-disk structure headers.

## Main Behavior
- `vdo_validate_version()` checks exact major/minor match and logs mismatch.
- `vdo_validate_header()` verifies component id, version, and size constraints.
- `vdo_encode_header()` writes component id, packed version, and size to a buffer in little-endian format.
- `vdo_decode_header()` reads those fields back.
- `vdo_encode_version_number()` / `vdo_decode_version_number()` handle packed version numbers.

## Dependencies
Uses VDO buffer helpers, status codes, logger, and header packing helpers from the header.

## Invariants
Header validation can require exact size or allow actual size to be larger than expected. Version validation here requires exact match; the separate upgradable-version predicate is declared in the header but not used here.
