# File Research: sources/block-storage/kvdo/vdo/block-map-recovery.h

## Purpose

Declares the recovery-journal replay representation for block map recovery.

## Contents

- `struct numbered_block_mapping`
  - target block map slot,
  - packed block map entry,
  - serial replay number.
- `vdo_recover_block_map()` public API.

## Role

The serial number lets recovery sort entries by logical location while preserving original order for repeated updates to the same mapping.
