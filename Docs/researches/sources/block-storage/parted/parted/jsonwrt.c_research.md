# File Research: sources/block-storage/parted/parted/jsonwrt.c

## Purpose

`jsonwrt.c` is a small public-domain JSON writer used by the `parted` frontend for JSON output formatting.

## Main Responsibilities

- Escapes JSON string values.
- Optionally uppercases or lowercases ASCII/non-ASCII bytes while writing quoted strings.
- Maintains indentation level.
- Opens and closes JSON objects, arrays, and values.
- Handles comma insertion between closed elements.
- Writes raw values, strings, unsigned 64-bit numbers, booleans, and nulls.

## Important Functions

- `ul_jsonwrt_init()`
- `ul_jsonwrt_indent()`
- `ul_jsonwrt_open()`
- `ul_jsonwrt_close()`
- `ul_jsonwrt_value_raw()`
- `ul_jsonwrt_value_s()`
- `ul_jsonwrt_value_u64()`
- `ul_jsonwrt_value_boolean()`
- `ul_jsonwrt_value_null()`

## Behavior Details

String escaping handles double quotes, backslashes, standard control-character escapes, and other control characters as `\u00XX`. Object member names are lowercased by `ul_jsonwrt_open()` when a name is provided.

The writer uses three spaces per indent level. `after_close` controls whether commas/newlines are emitted before the next sibling.

## Notable Edge Cases

The case-conversion loop treats `char` bytes as unsigned for indexing but uses `toupper()`/`tolower()` on non-ASCII byte values; this is byte-oriented, not full Unicode case conversion. `ul_jsonwrt_close()` has special root-object behavior when `indent == 1`.
