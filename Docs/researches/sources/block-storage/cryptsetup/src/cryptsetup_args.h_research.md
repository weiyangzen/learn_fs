# File Research: sources/block-storage/cryptsetup/src/cryptsetup_args.h

## Purpose
Cryptsetup-specific argument helper header. It defines canonical action names, per-option action allowlists, option enum IDs generated from `cryptsetup_arg_list.h`, and the external declaration for `tool_core_args`.

## Action Names
Defines CLI action constants including `open`, `close`, `resize`, `status`, `benchmark`, `repair`, `reencrypt`, `erase`, `convert`, `config`, `luksFormat`, key management actions, dump actions, suspend/resume, header backup/restore, and token handling.

## Option Allowlist Model
- Each `OPT_*_ACTIONS` macro expands to a fixed array of action names.
- `tools_check_args()` later validates that every set option is allowed for the selected action.
- Examples:
  - `OPT_ALLOW_DISCARDS_ACTIONS` is only `open`.
  - PBKDF-related options apply to benchmark, format, add/change/convert key, and reencryption.
  - LUKS2 metadata sizing applies to format and reencryption.
  - Token replace applies only to token actions.

## Generated IDs
The `enum` starts with `OPT_UNUSED_ID = 0` because popt reserves/complicates zero handling, then includes each macro entry as `<option>_ID`.

## Dependencies
Includes `utils_arg_names.h` for option string constants and `utils_arg_macros.h` for access macros.

## Notes
`tool_core_args` storage is defined in `cryptsetup.c`, unlike `integritysetup_args.h`, which defines a static array in the header for that smaller binary.
