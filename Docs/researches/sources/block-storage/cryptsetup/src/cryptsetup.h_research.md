# File Research: sources/block-storage/cryptsetup/src/cryptsetup.h

## Purpose
Shared header for cryptsetup-family CLI tools. It centralizes common includes, constants, logging macros, CLI argument storage types, utility declarations, signal/progress declarations, key I/O declarations, blkid/signature helper declarations, and keyring helper declarations.

## Key Definitions
- `DEFAULT_CIPHER(type)` composes cipher and mode defaults from build-time macros.
- `DEFAULT_WIPE_BLOCK` is `1 MiB`, used by wipe/progress paths.
- `MAX_ACTIONS` limits per-option action allowlists.
- `crypt_arg_type_info` enumerates supported option value types: bool, string, signed/unsigned 32/64-bit, and alias.
- `struct tools_arg` stores an option name, set flag, typed value union, alias target, and allowed action list.

## Public Helper Surface
- Logging/status: `tool_log`, `quiet_log`, `show_status`, `translate_errno`, package/version helpers.
- Prompting: `yesDialog`, `noDialog`, `usage`.
- Signals: `quit`, `set_int_block`, `set_int_handler`, `check_signal`, `tools_signals_blocked`.
- Key input: `tools_get_key`, `tools_passphrase_msg`, `tools_is_stdin`, `tools_read_vk`, `tools_write_mk`.
- Progress: `struct tools_progress_params`, `tools_progress`, `tools_get_device_name`.
- Blkid/device checks: `tools_detect_signatures`, `tools_wipe_all_signatures`, `tools_superblock_block_size`, `tools_blkid_supported`, `tools_lookup_crypt_device`.
- CLI parsing: `tools_parse_arg_value`, `tools_args_free`, `tools_check_args`.

## Dependencies
Includes libcryptsetup headers plus low-level utility headers under `lib/` for i18n, bit operations, loop devices, I/O, blkid wrappers, and macros.

## Notes
- Every utility binary must implement `tools_cleanup()`, allowing common code to call cleanup without knowing which CLI is linked.
- The `log_dbg`, `log_std`, `log_verbose`, and `log_err` macros route through `crypt_logf`.
