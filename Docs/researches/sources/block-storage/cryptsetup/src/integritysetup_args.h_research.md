# File Research: sources/block-storage/cryptsetup/src/integritysetup_args.h

## Purpose
Integritysetup-specific argument helper header. It defines action names, option allowlist macros, generated option IDs, and the static `tool_core_args` storage for the integritysetup binary.

## Actions
Supported actions are `format`, `open`, `close`, `resize`, `status`, and `dump`.

## Allowlist Highlights
- `--allow-discards` only applies to `open`.
- Deferred options only apply to `close`.
- Device/size options only apply to `resize`.
- Blkid disabling and no-wipe only apply to `format`.
- Inline, interleave, journal size, sector size, and tag size are format-only.
- Recalculate options apply to `open`.
- Wipe applies to `resize`.
- Progress JSON applies to format and resize.

## Generated Structures
- Enum IDs are generated from `integritysetup_arg_list.h`.
- `tool_core_args[]` is defined directly as a static array initialized from the same list, with index zero unused.

## Dependencies
Includes `utils_arg_names.h` and `utils_arg_macros.h`.
