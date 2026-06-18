# File Research: sources/block-storage/lvm2/libdm/libdm-string.c

## Summary
Provides libdm string, formatting, escaping, device-name construction, and size/unit conversion helpers. These routines support command parsing, LVM device-mapper name encoding, safe formatted allocation, and human-readable size rendering.

## Main Responsibilities
- Splits whitespace-delimited strings with `dm_split_words()`.
- Splits hyphen-escaped LVM device names into VG, LV, and layer components.
- Builds escaped device-mapper names and UUIDs.
- Wraps `snprintf`, `vasprintf`, and `asprintf` with libdm allocation and legacy error semantics.
- Escapes/unescapes quotes, colons, and at signs.
- Implements bounded `dm_strncpy()`.
- Converts sector counts to formatted size strings.
- Parses unit suffixes and custom numeric units into byte factors.

## Key APIs
- `dm_split_words()`
- `dm_split_lvm_name()`
- `dm_snprintf()`, `dm_vasprintf()`, `dm_asprintf()`
- `dm_basename()`
- `dm_build_dm_name()`, `dm_build_dm_uuid()`
- `dm_escape_double_quotes()`, `dm_unescape_double_quotes()`
- `dm_unescape_colons_and_at_signs()`
- `dm_strncpy()`
- `dm_size_to_string()`
- `dm_units_to_factor()`

## Important Behavior
LVM name quoting uses doubled hyphens inside components and single hyphens between components. `_unquote()` terminates each component in place and returns the next component start.

`dm_snprintf()` treats truncation as `-1`, normalizing newer `snprintf()` behavior to the older libdm expectation.

`dm_vasprintf()` grows a temporary buffer until `vsnprintf()` fits, then returns the allocated string and reports the length including the terminating null byte.

`dm_size_to_string()` expects input sizes in 512-byte sectors, then formats them using binary, decimal, human-readable, sector, byte, or custom-unit modes. It supports suffix styles selected by `dm_size_suffix_t` and adds `<` for rounded human-readable output where requested.

`dm_units_to_factor()` parses optional leading numeric values, supports binary lowercase units, decimal uppercase units, sectors, bytes, and human-readable modes, and can reject multi-character suffixes in strict mode.

## State and Lifetime
Most returned strings are allocated from a caller-provided `dm_pool`; `dm_vasprintf()` and `dm_asprintf()` allocate with `dm_malloc`. Several unescape helpers mutate caller buffers in place.

## Risks
The split and target parsers are intentionally simple and mostly whitespace based; they do not implement shell-like quoting. In-place unquoting requires mutable buffers and can surprise callers using shared string storage.
