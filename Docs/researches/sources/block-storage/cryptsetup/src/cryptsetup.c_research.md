# File Research: sources/block-storage/cryptsetup/src/cryptsetup.c

## Purpose
Main `cryptsetup` CLI implementation. It maps parsed command-line actions to libcryptsetup operations for plain dm-crypt, loop-AES, LUKS1/LUKS2, TCRYPT/VeraCrypt, BitLocker, FileVault2, OPAL-backed LUKS2, keyslot management, token management, benchmarking, resize, repair, reencryption dispatch, suspend/resume, and header backup/restore.

## Major State
- Global option storage is `tool_core_args[]`, generated from `cryptsetup_arg_list.h`.
- Action parsing uses `action_argv`, `action_argc`, and `action_types[]`.
- Key input globals track repeated options: `keyfiles`, `keyring_links`, `vks_in_keyring`, `vk_files`, and `key_sizes`.
- `device_type` defaults to `"luks"` and is changed by `--type`, legacy action aliases, or active-device refresh autodetection.
- `set_pbkdf` is shared with `utils_luks.c` to apply parsed PBKDF selection.

## Action Flow
- `main()` initializes aliases, locale, popt tables, option parsing, legacy action normalization, action lookup, action-specific checks, global conflict checks, optional debug/keyring/token disabling, then calls `run_action()`.
- `run_action()` installs signal handling, calls the selected action handler, normalizes positive keyslot/token return values to success, checks interruption, prints status, and returns translated errno.
- `tools_check_args()` enforces the action allowlist embedded in each option definition before action-specific verification functions run.

## Core Actions
- `action_open()` dispatches to `action_open_luks`, `action_open_plain`, `action_open_loopaes`, `action_open_tcrypt`, `action_open_bitlk`, or `action_open_fvault2`.
- `action_close()` deactivates mappings, with deferred and cancel-deferred support.
- `action_resize()` resizes active mappings and handles LUKS2 keyring-key requirements during resize.
- `action_status()` reports active mapping type, reencryption state, cipher/key details, OPAL mode, integrity metadata, backing loop file, sector size, size, offsets, mode, and activation flags.
- `action_benchmark()` benchmarks PBKDFs and common cipher/mode/key-size combinations.

## LUKS Formatting And Activation
- `luksFormat()` is the central LUKS formatter, exported through `utils_luks.h` for reencryption support.
- It validates LUKS1 vs LUKS2-only options, detached header creation, cipher/integrity parsing, metadata sizes, offsets, blkid signature handling, PBKDF setup, RNG selection, OPAL admin key input, volume key input, compatibility flags, and keyslot creation.
- LUKS2 integrity format can activate a temporary private device and wipe it to initialize integrity checksums.
- `action_open_luks()` handles detached headers, UUID/device lookup, test-passphrase mode, token unlock, keyring volume keys, volume-key files, two-key reencryption activation, keyring linking, persistent flags, and OPAL warning cases.

## Keyslot And Token Management
- Keyslot handlers include add, unbound add, remove by passphrase, kill slot, change key, convert key PBKDF/encryption, dump volume key, and dump unbound key.
- `verify_keyslot()` protects against deleting the last usable keyslot unless the user proves another passphrase or confirms.
- Token handlers support `token add`, `remove`, `import`, `export`, and `unassign`; built-in add creates `luks2-keyring` tokens.
- Token unlock/add paths handle `-ENOANO` by prompting for token PIN when allowed.

## Repair, Conversion, Erase
- `action_luksRepair()` loads/repairs LUKS metadata and follows with LUKS2 reencryption metadata repair/recovery when needed.
- `luks2_reencrypt_repair()` handles clean/crash/repair-needed reencryption metadata states.
- `action_luksErase()` destroys all LUKS keyslots or performs OPAL wipe/factory reset flows.
- `action_luksConvert()` converts between LUKS1 and LUKS2 with confirmation.
- `action_luksConfig()` updates LUKS2 keyslot priority and labels/subsystem labels.

## Header Dumps
- TCRYPT, BITLK, FVAULT2, and LUKS dump flows support sensitive volume-key dumps behind confirmation unless batch mode is used.
- Volume keys can be printed as hex or written to `--volume-key-file`.
- Dump paths use `crypt_dump()` or `crypt_dump_json()` for normal metadata reporting.

## Validation Notes
- Action validators enforce cross-option rules for open, close, resize, reencryption, config, format, addkey, luksDump, token, and TCRYPT dump.
- `basic_options_cb()` performs typed parsing plus extra semantic checks, such as sector alignment, key-size divisibility, repeated key limits, max reduce size, priority values, and keyring/volume-key list collection.
- Legacy aliases are preserved: `create`, `plainOpen`, `luksOpen`, `remove`, `luksClose`, `tcryptDump`, etc.

## Dependencies
- Heavy libcryptsetup use: `crypt_init*`, `crypt_load`, `crypt_format*`, `crypt_activate*`, `crypt_keyslot*`, `crypt_token*`, `crypt_reencrypt*`, `crypt_header_*`, `crypt_wipe*`.
- Uses shared helpers from `utils_luks.c`, `utils_password.c`, `utils_blockdev.c`, `utils_progress.c`, `utils_key_description.c`, `utils_keyslot_check.c`, `utils_tools.c`, and reencryption files.

## Implementation Risks
- This file is the central CLI compatibility surface; small option parsing changes can affect many historical aliases and scripts.
- Several flows intentionally accept dangerous operations under confirmation or batch mode, so prompt/batch behavior is security-relevant.
- Key material is generally freed with `crypt_safe_free`; new key-handling paths should follow the same pattern.
