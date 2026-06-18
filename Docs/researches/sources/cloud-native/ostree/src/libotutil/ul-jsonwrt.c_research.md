<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.c -->
# sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.c

## Purpose
Implements a compact JSON writer adapted from util-linux for OSTree status output and other simple structured CLI output.

## Important APIs and Types
The core functions are `ul_jsonwrt_init`, `ul_jsonwrt_is_ready`, `ul_jsonwrt_indent`, `ul_jsonwrt_open`, `ul_jsonwrt_empty`, `ul_jsonwrt_close`, `ul_jsonwrt_flush`, and typed value writers for raw strings, JSON strings, sized strings, `uint64`, doubles, and booleans. `fputs_quoted_case_json` handles string escaping and optional case conversion.

## Control Flow
Open/empty/value calls print commas and indentation based on `after_close`, then emit object, array, or value syntax. Close calls decrement indentation and writes closing delimiters. String writers wrap values in quotes and escape control characters, double quotes, and backslashes.

## State and Persistence
State is just `FILE *out`, current indentation level, and `after_close`. Persistence is bytes written to the target stream; there is no buffering beyond stdio.

## Dependencies and Integration Points
Uses stdio, integer format macros, GLib ASCII case helpers, and assertions. `ot-admin-builtin-status.c` uses it for `ostree admin status --json`.

## Risks
The writer is stateful and does not maintain a stack of object/array types, so callers must close in the same order they open. `ul_jsonwrt_value_raw` can emit invalid JSON if passed unsafe data. Non-ASCII case conversion falls back to locale-sensitive `toupper`/`tolower`.

## Test Signals
Tests should parse emitted JSON for nested objects/arrays, strings with control characters and backslashes, null handling, status JSON output, and bad call ordering assertions in debug builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/ul-jsonwrt.c -->
