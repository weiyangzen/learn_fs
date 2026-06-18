# File Research: sources/cow-pools/bcachefs-tools/linux/unicode/utf8-core.c

## Purpose
High-level Linux Unicode normalization and casefolding helpers.

## Key APIs
- `utf8_validate()`
- `utf8_strncmp()`
- `utf8_strncasecmp()`
- `utf8_strncasecmp_folded()`
- `utf8_casefold()`
- `utf8_normalize()`
- `utf8_load()`
- `utf8_unload()`

## Behavior
- Uses NFDI for validation/normalization and NFDICF for case-insensitive comparison/folding.
- Cursor-based functions compare normalized byte streams.
- `utf8_load()` allocates a `unicode_map`, checks the requested Unicode version, and selects versioned normalization tables.
- Returns `-EINVAL` for invalid cursors/input or unsupported table versions.

## Dependencies
Depends on generated `utf8_data_table` and lower-level cursor/trie functions from `utf8-norm.c`.
