# sources/cloud-native/composefs-rs/crates/composefs-boot/src/os_release.rs

## Purpose
This module parses freedesktop-style `os-release` content and derives boot menu labels. It is used by UKI parsing to convert a `.osrel` PE section into a display label and can also support generated boot entries.

## Important APIs, types, and functions
`dequote` is a private parser for the quoting subset needed by `os-release`. It supports unquoted text, double quotes with simple backslash handling, single quotes, and adjacent quoted/unquoted fragments.

`OsReleaseInfo<'a>` stores a borrowed `HashMap<&str, &str>` of raw assignments. `parse(content)` filters comments and lines without `=`, then stores key/value slices. `get_value(keys)` returns the first dequoted value among a priority list. `get_pretty_name` prefers `PRETTY_NAME`, then `NAME`, then `ID`. `get_version` prefers `VERSION_ID`, then `VERSION`. `get_boot_label` combines the selected name and optional version.

## Control flow
Parsing is intentionally shallow: each non-comment assignment is split once on `=`, and values are dequoted lazily during lookup. If dequoting fails for a higher-priority key, lookup falls through to the next key. Boot-label generation requires a name-like field but treats version absence as non-fatal.

## State and persistence behavior
The parsed map borrows from the input string and holds no owned file content. Returned values are owned `String`s because dequoting may transform escapes and remove quotes. No filesystem state is read or written.

## Dependencies and integration points
The module only uses `std::collections::HashMap`. `uki.rs` calls `OsReleaseInfo::parse(...).get_boot_label()` after extracting a UKI `.osrel` section. It is therefore on the boot-menu label path for Type 2 entries.

## Risks
Duplicate keys are collapsed by `HashMap::from_iter`; later entries overwrite earlier ones based on iterator behavior. The parser does not trim assignment keys or values before storing, except inside `dequote`, so unusual whitespace around keys can affect lookup. It does not implement the full shell language, by design. Invalid quoting silently causes fallback to a lower-priority field rather than surfacing a parse warning.

## Test signals
Tests cover empty strings, single/double quotes, adjacent quote fragments, selected escape cases, malformed quotes returning `None`, and fallback order for boot labels when preferred fields are missing or malformed. Tests are table-driven and protect the intended partial-shell behavior.
