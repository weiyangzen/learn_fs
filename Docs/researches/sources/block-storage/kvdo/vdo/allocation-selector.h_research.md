# File Research: sources/block-storage/kvdo/vdo/allocation-selector.h

## Purpose

Declares the allocation selector used for round-robin physical-zone allocation.

## Contents

- Documents allocation selectors.
- Defines `struct allocation_selector`:
  - `allocation_count`,
  - `next_allocation_zone`,
  - `last_physical_zone`.
- Declares construction and next-zone selection APIs.

## Notable Details

The comment says “last_physical_cone” for the `last_physical_zone` field, which is a typo in documentation only.
