# File Research: sources/block-storage/mdadm/maps.c

## Role

`maps.c` centralizes string-to-number and number-to-string mappings for mdadm concepts: RAID levels, layouts, command modes, faulty personalities, consistency policies, sysfs array states, and supported update options.

## Mappings

- `r5layout[]` maps RAID5 layouts including left/right symmetric/asymmetric, parity-first/last, abbreviations, and DDF-compatible names.
- `r6layout[]` maps RAID6 layouts including RAID5-compatible names, DDF rotating layouts, and intermediate `*-6` layouts used during conversion.
- `r0layout[]` captures RAID0 layout compatibility names for the Linux 3.14 layout bug: original, alternate, numeric aliases, and dangerous.
- `pers[]` maps RAID personality names and synonyms to md level constants.
- `modes[]` maps command mode names to mdadm mode constants.
- `faultylayout[]` maps faulty personality injection modes and aliases.
- `consistency_policies[]` maps consistency policy names to internal constants.
- `sysfs_array_states[]` maps sysfs `array_state` strings to enum-like constants.
- `update_options[]` maps `--update=` names to internal update option constants.

## Functions

- `map_num()` returns the first mapping name for a numeric value or `NULL`.
- `map_num_s()` is the assert-backed variant for call sites that require a valid numeric value.
- `map_name()` returns the numeric value for a string, or the terminal entry’s value, usually `UnSet` or an undefined sentinel.

## Dependencies

This file depends on constants from `mdadm.h` and kernel md layout constants. It is used by CLI parsing, reporting, manpage-consistent validation, and metadata-specific update handling.

## Important Invariants

- Terminal entries are meaningful: callers rely on the final `num` value as the “not found” sentinel.
- Name ordering matters for `map_num()` because the first matching numeric value becomes the canonical display string.
- Mapping names must remain consistent with documented options in `mdadm.8.in` and `mdadm.conf.5.in`.

## Risks

Adding a synonym with the same number before an existing canonical name can change displayed output. Adding a new update/layout/policy option requires coordinated changes in parser validation, implementation code, and documentation.
