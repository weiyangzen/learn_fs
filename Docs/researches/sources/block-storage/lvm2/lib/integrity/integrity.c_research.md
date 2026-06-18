# File Research: sources/block-storage/lvm2/lib/integrity/integrity.c

## Summary
Implements the LVM segment type for device-mapper `integrity` targets, including text metadata import/export, target-line construction, module reporting, and segtype registration.

## Main Responsibilities
- Imports integrity segment metadata: origin LV, optional metadata LV, data sectors, mode, tag/block sizes, internal hash, recalculation flag, and optional journal/bitmap/discard settings.
- Exports the same fields back to text metadata.
- Marks the owning LV as `INTEGRITY` and optional metadata LV as `INTEGRITY_METADATA`.
- Checks for the dm-integrity target and enforces minimum target version 1.6.0.
- Adds the `dm-integrity` module requirement and builds dm-tree integrity target lines.

## State And Dependencies
The segment stores settings in `seg->integrity_settings`, uses segment area 0 for the origin LV, optionally references `seg->integrity_meta_dev`, and integrates with segtype handler callbacks, activation, dm-tree, and LV dependency tracking.

## Risks And Invariants
The import path requires several fields to be present and type-correct. Optional settings have separate “set” flags, but export uses direct value checks for some fields, so zero-valued optional settings may need care. Activation requires a sufficiently new kernel target.
