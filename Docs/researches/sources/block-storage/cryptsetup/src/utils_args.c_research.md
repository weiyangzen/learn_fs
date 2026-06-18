# File Research: sources/block-storage/cryptsetup/src/utils_args.c

## Purpose
Common typed command-line argument parser and action allowlist checker.

## Parsing
`tools_parse_arg_value()` parses popt arguments according to `crypt_arg_type_info`:
- Bool options only mark set.
- Strings use `poptGetOptArg()` and replace any previous value.
- Integer types use `strtoll` or `strtoull` with full-string and range validation.
- `CRYPT_ARG_UINT64` can call a caller-provided size-conversion predicate and `tools_string_to_size()`.
- Alias entries recursively parse into their canonical target.

## Cleanup
`tools_args_free()` frees set string values and clears all `set` flags.

## Action Enforcement
- `action_allowed()` treats an empty action list as globally allowed.
- `tools_check_args()` walks all set options and emits a usage error if an option is not permitted with the selected action.

## Error Behavior
Invalid parse or disallowed action calls `usage(..., EXIT_FAILURE, ...)`, which exits rather than returning an error code.

## Notes
This file is shared by multiple CLI binaries and depends on `struct tools_arg` from `cryptsetup.h`.
