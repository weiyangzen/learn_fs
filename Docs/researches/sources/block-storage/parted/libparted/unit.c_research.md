# File Research: sources/block-storage/parted/libparted/unit.c

## Purpose

`unit.c` implements libparted’s `PedUnit` parsing and formatting layer. It converts sectors/bytes to user-facing location strings and parses user-provided locations into sectors plus optional fuzzy geometry ranges.

## Main Responsibilities

- Maintains a global default unit, initially `PED_UNIT_COMPACT`.
- Defines unit names for sectors, bytes, SI units, IEC units, compact, cylinders, CHS, and percent.
- Returns byte sizes for units on a specific device.
- Formats byte or sector locations in a requested or default unit.
- Implements compact formatting by choosing B/kB/MB/GB/TB based on magnitude.
- Parses CHS triplets.
- Parses numeric values with unit suffixes.
- Handles negative offsets as positions from the end of the device.
- Builds an optional `PedGeometry` range around fuzzy unit-based inputs.
- Treats IEC unit inputs as precise locations with zero fuzz radius.
- Clips parsed sectors to the device boundary after validating the range.

## Important Functions

- `ped_unit_set_default()` and `ped_unit_get_default()`.
- `ped_unit_get_size()`, `ped_unit_get_name()`, and `ped_unit_get_by_name()`.
- `ped_unit_format_custom_byte()`, `ped_unit_format_byte()`, `ped_unit_format_custom()`, and `ped_unit_format()`.
- `ped_unit_parse()` and `ped_unit_parse_custom()`.
- Internal helpers:
  - `strip_string()`,
  - `find_suffix()`,
  - `is_chs()`,
  - `parse_chs()`,
  - `parse_unit_suffix()`,
  - `geometry_from_centre_radius()`.

## Behavior Details

Formatting rounds cylinder, sector, and byte units down. Other units use decimal precision based on magnitude and a small epsilon adjustment to avoid surprising IEEE-754 round-half behavior.

Parsing rejects positive values less than 1 and asks callers to use a smaller unit. If no suffix is provided and the requested unit is compact, parsing falls back to the global default unit, or MB if the global default is also compact.

## Notable Edge Cases

- `ped_unit_get_size()` throws an error for `PED_UNIT_COMPACT`.
- CHS parsing accepts any punctuation as separators as long as exactly two punctuation characters are present.
- `strip_string()` removes spaces in place inefficiently and can skip adjacent whitespace because it shifts without decrementing the index.
- Percent unit size is integer-truncated to one percent of total device bytes.
