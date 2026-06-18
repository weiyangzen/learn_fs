# File Research: sources/block-storage/kvdo/vdo/block-map-page.c

## Purpose

Implements formatting and validation for individual block map pages.

## Main Responsibilities

- Defines block map page version 4.1.
- Formats a page buffer with version, nonce, PBN, initialized bit, and zeroed entries.
- Validates page version, initialized status, nonce, and expected PBN.

## Important Functions

- `vdo_format_block_map_page()` clears the block, writes version/header metadata, and returns the page overlay.
- `vdo_validate_block_map_page()` returns:
  - valid,
  - invalid,
  - bad page at wrong disk location.

## Behavior Details

A page with wrong version, uninitialized flag, or wrong nonce is treated as invalid and can be reformatted by callers. A page with matching metadata but unexpected PBN is treated as bad/corrupt.

## Notable Details

The `initialized` bit supports torn-write protection: new pages may need to be written more than once before being considered fully initialized on disk.
