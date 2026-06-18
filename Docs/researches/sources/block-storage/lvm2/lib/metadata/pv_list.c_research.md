# File Research: sources/block-storage/lvm2/lib/metadata/pv_list.c

## Scope

`pv_list.c` builds and clones command-scoped PV selection lists. It parses user-supplied PV arguments, optional physical-extent ranges, and tag selectors into `struct pv_list` entries with `pe_ranges` suitable for allocation and pvmove-style operations.

## Primary Functions

- `_add_pe_range()` appends a `struct pe_range` to a selected PV after rejecting overlap with existing ranges.
- `_xstrtouint32()` wraps `strtoul()` with error, no-progress, and `UINT32_MAX` overflow checks.
- `_parse_pes()` parses PE selectors after a PV name. With no selector it selects the whole PV; otherwise it accepts colon-prefixed single extents, start/end ranges, and start-plus-length forms.
- `_create_pv_entry()` validates PV availability, filters non-allocatable/missing/full PVs when requested, coalesces repeated references to the same device, initializes `pe_ranges`, and delegates PE parsing.
- `create_pv_list()` is the public entry point. It accepts explicit PV names, optional PE ranges, and `@tag` selectors, then returns a memory-pool-owned `dm_list` of selected PVs.
- `clone_pv_list()` shallow-copies a PV list into a new memory-pool-owned list.
- `pv_list_to_dev_list()` converts selected PVs with usable devices and aliases into `device_list` entries.

## Summary

`pv_list.c` normalizes user or caller PV selections into memory-pool-owned `pv_list` records with explicit PE ranges. Its main correctness responsibilities are argument parsing, overlap prevention, allocation eligibility filtering, and preserving selected ranges for later free-space mapping.
