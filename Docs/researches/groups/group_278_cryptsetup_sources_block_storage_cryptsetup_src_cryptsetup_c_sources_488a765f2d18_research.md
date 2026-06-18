# Group Research: group_278_cryptsetup_sources_block_storage_cryptsetup_src_cryptsetup_c_sources_488a765f2d18

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup.h -->
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
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup_arg_list.h -->
# File Research: sources/block-storage/cryptsetup/src/cryptsetup_arg_list.h

## Purpose
Macro list defining every `cryptsetup` option. It is included multiple times with different `ARG(...)` definitions to generate enum IDs, `tools_arg` defaults, and popt option tables.

## Format
Each entry provides:
`long name, short name, popt type, help description, units, internal argument type, default value, allowed actions`.

## Main Option Groups
- General behavior: batch mode, verbose, debug, debug JSON, test args, timeout, disable locks, disable blkid.
- Device activation: type, readonly, allow discards, persistent flags, refresh, shared, size/device-size, offset/skip, sector size, IV large sectors, dm-crypt performance flags.
- Key input: key file, keyfile offset/size, key size, key slot, volume-key file/keyring, key descriptions, keyring linking.
- LUKS formatting/config: cipher, hash, UUID, label, subsystem, metadata/keyslot sizes, PBKDF selection/costs, RNG selection, force password, integrity options.
- Reencryption: encrypt/decrypt/init/resume modes, active name, hotzone, resilience, block size, direct I/O, fsync, write log, reduce device size, keep/new key options.
- Token handling: token ID/type/only/replace, new token ID, JSON file.
- TCRYPT/VeraCrypt: hidden/system/backup headers, VeraCrypt enable/disable, PIM and query-PIM.
- OPAL: `--hw-opal`, `--hw-opal-only`, `--disable-sum`, factory reset.
- Compatibility aliases: `--new`, `--dump-master-key`, `--master-key-file`.

## Defaults And Aliases
- Some options use libcryptsetup sentinel defaults such as `CRYPT_ANY_SLOT` and `CRYPT_ANY_TOKEN`.
- PBKDF memory and parallelism default from LUKS2 build defaults.
- Alias entries use `CRYPT_ARG_ALIAS` to redirect parsing into the canonical option.

## Notes
- This file deliberately contains no enum or array syntax outside the macro calls.
- Action allowlists are defined in `cryptsetup_args.h`; empty action arrays mean globally allowed.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup_arg_list.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup_args.h -->
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
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/cryptsetup_args.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/integritysetup.c -->
# File Research: sources/block-storage/cryptsetup/src/integritysetup.c

## Purpose
Main `integritysetup` CLI implementation for dm-integrity devices. It supports formatting, opening, closing, status reporting, metadata dump, and resizing integrity-protected volumes.

## Main Actions
- `action_format()` formats an integrity device with checksum/MAC algorithm, tag size, sector size, journal/bitmap/inline settings, optional detached data device, optional integrity/journal keys, blkid signature wiping, and initial checksum wipe unless `--no-wipe`.
- `action_open()` loads and activates an integrity device, building activation flags for no-journal, bitmap mode, recovery, recalculate, reset recalculate, and discards.
- `action_close()` deactivates an active mapping, with deferred and cancel-deferred support.
- `action_status()` reports active state, type, tag size, algorithm, data and metadata devices, sector/interleave sizes, failures, bitmap/journal/inline flags, and discards.
- `action_dump()` loads on-disk integrity metadata and calls `crypt_dump()`.
- `action_resize()` resizes active mappings and either wipes newly exposed space or reactivates with recalculate flags.

## Key Handling
- `_read_keys()` loads optional integrity key, journal integrity key, and journal encryption key from files.
- Key file options must be paired with explicit key-size options; journal key files also require corresponding journal algorithms.
- Loaded keys are freed with `crypt_safe_free`.

## Wipe And Progress
- `_wipe_data_device()` creates a temporary private mapping and calls `crypt_wipe()` with `tools_progress`.
- Format wipe initializes all integrity checksums.
- Resize wipe initializes only the newly extended region when `--wipe` is set.

## Argument Flow
- Uses `integritysetup_args.h` for option definitions and static `tool_core_args`.
- `main()` parses popt options, handles legacy aliases `create` to `open` and `remove` to `close`, validates action arity, runs `tools_check_args()`, enforces option conflicts, enables debug, and dispatches.
- `needs_size_conversion()` applies human-size parsing only to `--journal-size` and `--device-size`.

## Validation Rules
- Integrity key file and size must both be specified.
- Journal integrity/encryption key file and size must both be specified.
- Journal key files require their journal algorithms.
- Recovery and bitmap mode are mutually exclusive.
- Journal options cannot be combined with bitmap mode.
- Bitmap options require bitmap mode.
- Inline mode excludes journal/bitmap options and a separate data device.
- Deferred and cancel-deferred are mutually exclusive.

## Dependencies
Uses common cryptsetup helpers for logging, confirmation, progress, blkid probing, key reads, and argument parsing. Links libcryptsetup functions such as `crypt_format`, `crypt_format_inline`, `crypt_load`, `crypt_activate_by_volume_key`, `crypt_resize`, and `crypt_get_integrity_info`.

## Notes
The default integrity algorithm is `crc32c` via `DEFAULT_ALG_NAME`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/integritysetup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/integritysetup_arg_list.h -->
# File Research: sources/block-storage/cryptsetup/src/integritysetup_arg_list.h

## Purpose
Macro list defining all `integritysetup` options. Like the cryptsetup option list, it is consumed by enum, storage, and popt table generation.

## Option Groups
- General: batch mode, verbose, debug.
- Activation/deactivation: allow discards, deferred, cancel deferred, size/device-size.
- Format geometry: buffer sectors, interleave sectors, journal size, journal watermark, journal commit time, sector size, tag size.
- Bitmap mode: bitmap mode flag, sectors per bit, flush time.
- Integrity algorithm and keys: integrity algorithm, integrity key file/size, journal integrity algorithm/key, journal encryption algorithm/key.
- Compatibility: legacy padding, legacy HMAC, legacy recalculation.
- Operational modes: no journal, recovery mode, recalculate, recalculate reset, inline integrity.
- Data placement: separate data device.
- Wipe/progress: no wipe, wipe after resize, progress frequency, progress JSON.
- Signature probing: disable blkid.

## Defaults
- `--integrity` defaults to `DEFAULT_ALG_NAME` (`crc32c`).
- `--sector-size` defaults to 512 bytes.
- Other numeric options default to zero unless specified.

## Notes
The comment omits “allowed actions” in its prose, but entries use the same eight-argument macro shape as the cryptsetup list, including action allowlists.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/integritysetup_arg_list.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/integritysetup_args.h -->
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
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/integritysetup_args.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/meson.build -->
# File Research: sources/block-storage/cryptsetup/src/meson.build

## Purpose
Meson build definition for cryptsetup-family command-line executables and SSH token helper source grouping.

## Build Targets
- `cryptsetup` is built when `get_option('cryptsetup')` is enabled.
- `veritysetup` is built when `get_option('veritysetup')` is enabled.
- `integritysetup` is built when `get_option('integritysetup')` is enabled.

## cryptsetup Sources
Includes `cryptsetup.c`, common arg/blockdev/LUKS/password/progress/tools helpers, reencryption helpers, key description, keyslot check, and `lib_tools_files`.

## veritysetup Sources
Includes `veritysetup.c`, `utils_args.c`, `utils_tools.c`, and `lib_tools_files`.

## integritysetup Sources
Includes `integritysetup.c`, `utils_args.c`, `utils_blockdev.c`, `utils_progress.c`, `utils_tools.c`, and `lib_tools_files`.

## Dependencies
- `cryptsetup`: `popt`, `pwquality`, `passwdqc`, `uuid`, `blkid`.
- `veritysetup`: `popt`, `blkid`.
- `integritysetup`: `popt`, `uuid`, `blkid`.
- All three link with `libcryptsetup`, use common link args and tool include directories, and install into `sbindir`.

## Notes
`src_ssh_token_files` is defined for SSH token support and includes `utils_password.c` and `utils_tools.c`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_arg_macros.h -->
# File Research: sources/block-storage/cryptsetup/src/utils_arg_macros.h

## Purpose
Typed accessor and setter macros for `tool_core_args[]`.

## Accessors
- `ARG_SET(id)` checks whether an option was supplied.
- `ARG_STR`, `ARG_INT32`, `ARG_UINT32`, `ARG_INT64`, and `ARG_UINT64` assert the expected stored type and return the value.

## Setters
- `ARG_SET_TRUE` marks a boolean option as set.
- `ARG_SET_STR`, `ARG_SET_INT32`, `ARG_SET_UINT32`, `ARG_SET_INT64`, and `ARG_SET_UINT64` assert that the option was previously unset and of the expected type, then store the value and mark it set.
- String setter takes ownership of the supplied allocated string.

## Alias Initialization
`ARG_INIT_ALIAS(id)` resolves a `CRYPT_ARG_ALIAS` entry by storing a pointer to the canonical `tools_arg` target.

## Notes
These macros are GNU C statement expressions for getters, not standard C expressions. They rely on a visible `tool_core_args` symbol in each CLI translation unit.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_arg_macros.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_arg_names.h -->
# File Research: sources/block-storage/cryptsetup/src/utils_arg_names.h

## Purpose
Central list of long command-line option names used by cryptsetup, integritysetup, veritysetup, and related utilities.

## Contents
Defines `OPT_*` string macros for:
- Cryptsetup/LUKS options: cipher, hash, header, UUID, key file, keyslot, PBKDF, labels, tokens, OPAL, reencryption, performance flags.
- Integritysetup options: journal, bitmap, tag size, integrity key, no-wipe/wipe, recalculate, inline mode.
- Verity-related options also present in the shared namespace: FEC, root hash, salt, corruption handling, data/hash block sizing.
- Compatibility aliases: master key names, new, etc.

## Design Role
This header avoids string duplication between option-list files and any code that needs stable option names for diagnostics.

## Notes
Several macros are not used by the files in this group directly because the name namespace spans multiple cryptsetup utilities.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_arg_names.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_args.c -->
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
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_args.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_blockdev.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_blockdev.c

## Purpose
Linux block-device helper functions for dm device lookup, blkid signature detection/wiping, superblock block-size probing, and blkid availability checks.

## Device Mapper Lookup
- `dm_prepare_uuid()` constructs a device-mapper UUID prefix from a crypt type and libcryptsetup UUID, removing UUID dashes.
- `lookup_holder_dm_name()` scans `/sys/dev/block/<major>:<minor>/holders`, inspects holder `dm/uuid` and `dm/name`, counts holders, and returns a matching dm name.
- `tools_lookup_crypt_device()` prepares a dm UUID prefix, stats the data device, requires a block device, and searches holders for a crypt mapping.

## Signature Detection
- `tools_detect_signatures()` initializes a blkid probe, applies a filter mode (`none`, filter LUKS, or only LUKS), prints warnings for partition and superblock signatures, and returns count/status.
- Batch mode downgrades signature warnings to debug logs.

## Signature Wiping
- `tools_wipe_all_signatures()` opens the target read-write, optionally exclusive for block devices, initializes blkid wipe probes, optionally restricts to LUKS superblocks, wipes detected signatures, and fsyncs after each wipe.

## Superblock Size
`tools_superblock_block_size()` probes the first superblock, returns the detected block size and superblock name when available, and treats empty probes as non-errors.

## Notes
- All blkid functionality is skipped when compiled without blkid support.
- Sysfs scanning intentionally handles symlinked `dm` entries and validates regular `uuid`/`name` files before reading.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_blockdev.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_key_description.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_key_description.c

## Purpose
Helpers for parsing kernel keyring key descriptions used for volume-key retrieval and volume-key linking.

## Volume Key Description
`tools_parse_vk_description()` applies a default `%user:` key type prefix when the user-supplied key description does not start with `%`; otherwise it duplicates the supplied typed description.

## Link Description Parsing
`parse_single_vk_and_keyring_description()` parses `--link-vk-to-keyring` values in the form:
`<keyring>::[%<type>:]<key-description>`

It:
- Splits keyring and key description on `::`.
- Extracts optional key type from the key part.
- Ignores an explicit type on the keyring part with a verbose warning.
- Accepts numeric/keyring-special values directly or prefixes normal keyring names with `%:`.
- Duplicates parsed keyring, key, and optional type output parts.

## Multi-Key Linking
`tools_parse_vk_and_keyring_description()` parses up to two link descriptions, ensures both volume keys use the same key type and same keyring, then calls `crypt_set_keyring_to_link()`.

## Error Handling
Invalid syntax returns `-EINVAL` and logs an invalid value message. `-EAGAIN` from libcryptsetup is converted into a “supply more key names” diagnostic.

## Notes
The `cd` parameter is required for the final libcryptsetup keyring-link setup, not for the string parsing itself.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_key_description.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_keyslot_check.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_keyslot_check.c

## Purpose
Post-repair/randomness heuristic for detecting likely corrupted encrypted LUKS keyslot binary areas.

## Algorithm
- `bitcount()` manually counts set bits in 64-bit words.
- `chisquared_bytes()` computes a chi-squared statistic over byte frequency buckets.
- `chisquared_bits()` computes a chi-squared statistic over bit frequency buckets.
- `run_analysis()` scans keyslot data in 4096-byte blocks using a byte-distribution chi-squared threshold. Suspicious blocks are further scanned in 128-byte subblocks using a bit-distribution threshold.

## Public Entry
`luks_check_keyslots()`:
- Skips checks during reencryption.
- Opens the header/device read-only.
- Iterates active bound keyslots.
- Uses `crypt_keyslot_area()` and `crypt_keyslot_get_key_size()` to determine the actual encrypted keyslot data length.
- Reads the keyslot area and runs analysis.
- Prints up to three suspected offsets per keyslot and suggests a `hexdump` command if any suspicious offsets were found.

## Important Limits
- This is explicitly a hint, not proof of corruption.
- It skips inactive and unbound slots.
- It can produce false positives and cannot detect all corruption.
- It assumes encrypted keyslot material should look pseudorandom.

## Dependencies
Uses libcryptsetup keyslot metadata APIs plus common logging and `read_buffer`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_keyslot_check.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_luks.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_luks.c

## Purpose
Shared LUKS helper implementation for cryptsetup actions and reencryption code. It handles type normalization, passphrase verification policy, activation flags, PBKDF setup, retry policy, adjusted key sizes, JSON token I/O, keyslot context creation, token unlock, and volume-key context setup.

## Type And Policy Helpers
- `luksType()` maps user-facing `luks`, `luks1`, and `luks2` strings to libcryptsetup type constants.
- `isLUKS1()` and `isLUKS2()` check concrete libcryptsetup type strings.
- `verify_passphrase()` disables verification in batch mode unless `--verify-passphrase` is set, and disables it on non-tty input with an error if explicitly requested.
- `set_tries_tty()` only retries interactive stdin use; keyring descriptions reduce tries to one.

## Activation And PBKDF
- `set_activation_flags()` maps CLI flags to libcryptsetup activation flags, including readonly, discards, performance flags, persistent override, unbound key testing, keyring key activation, serialized memory-hard PBKDF, no journal, and large IV sectors.
- `set_pbkdf_params()` builds a `crypt_pbkdf_type` from defaults plus CLI overrides and supports forced-iteration no-benchmark mode.
- `get_adjusted_key_size()` implements optional XTS default key-size doubling and adds integrity key size.

## JSON I/O
- `tools_read_json_file()` reads token JSON from a file or stdin up to `LUKS2_MAX_MDA_SIZE`, temporarily unblocks signals, optionally prompts on tty, NUL-terminates the buffer, and zeroes on failure.
- `tools_write_json_file()` writes token JSON to a file or stdout and handles signal interruption.

## Keyslot Contexts
- `luks_init_keyslot_context()` creates a keyslot context from keyring description, keyfile, or interactive/passphrase input.
- `luks_try_token_unlock()` initializes a token keyslot context, tries activation or resume, reports token/keyslot errors, and optionally prompts for PIN when the token requires it.
- `luks_init_keyslot_contexts_by_volume_keys()` creates one or two keyslot contexts from volume-key files or keyring descriptions, with file input taking precedence.

## Notes
This file depends on the cryptsetup CLI option globals from `cryptsetup_args.h`; it is not a generic library helper independent of CLI state.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_luks.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_luks.h -->
# File Research: sources/block-storage/cryptsetup/src/utils_luks.h

## Purpose
Header declaring LUKS helper functions shared across cryptsetup source files.

## Declared Areas
- Type helpers: `luksType`, `isLUKS1`, `isLUKS2`.
- CLI policy: `verify_passphrase`, `set_activation_flags`, `set_pbkdf_params`, `set_tries_tty`, `get_adjusted_key_size`.
- Formatting and reencryption entry points: `luksFormat`, `reencrypt`, `reencrypt_luks1`, `reencrypt_luks1_in_progress`.
- Keyslot context helpers: passphrase/keyfile/keyring context initialization, token unlock, two-volume-key context initialization.
- Diagnostics: `luks_check_keyslots`.

## Dependencies
Forward-declares `struct crypt_device` and includes basic integer/bool headers.

## Notes
This header bridges `cryptsetup.c`, `utils_luks.c`, `utils_reencrypt*.c`, and keyslot check code.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_luks.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_password.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_password.c

## Purpose
Password/passphrase and keyfile input handling, including optional password quality checks through pwquality or passwdqc.

## Password Quality
- If built with pwquality, `tools_check_pwquality()` loads default settings/config and validates the password.
- If built with passwdqc, `tools_check_passwdqc()` loads passwdqc config and validates.
- If neither is enabled, quality checking is a no-op.
- `tools_check_password()` selects the compiled backend.

## Terminal Input
- `interactive_pass()` opens `/dev/tty` when available, disables echo with termios, writes the prompt, reads with optional timeout, restores terminal state, and prints a newline.
- `crypt_get_key_tty()` allocates safe buffers, reads the passphrase, optionally verifies by asking twice, and returns the passphrase length.
- Reads stop at newline or max interactive length; reaching max length logs a trimming warning.

## Main Key Input API
`tools_get_key()`:
- Temporarily unblocks signals if needed.
- For stdin on a tty, prompts interactively and rejects keyfile offsets.
- For stdin not on a tty, reads binary input through `crypt_keyfile_device_read`; absent `key_file` enables EOL stop behavior.
- For file input, reads through `crypt_keyfile_device_read`.
- Runs password quality only for passphrase input, not keyfile input.
- Uses cryptsetup device names or loop backing files in generated prompts.

## Diagnostics
`tools_passphrase_msg()` maps common unlock errors to user-facing messages:
- `-EPERM`: no key available with this passphrase.
- `-ENOENT`: no usable keyslot.

## Notes
All password buffers use `crypt_safe_alloc`/`crypt_safe_free` so secrets are wiped on free.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_password.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_progress.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_progress.c

## Purpose
Progress reporting utility for wipe and long-running data operations. Supports human terminal progress and JSON progress output.

## Time And Unit Helpers
- `time_diff()` computes microsecond deltas between `timeval` values.
- `bytes_to_units()` converts byte counts into MiB/GiB/TiB/PiB/EiB display units.
- `time_to_human_string()` formats ETA/time as minutes, hours, or days depending on duration.

## Human Progress
- `tools_time_progress()` throttles updates according to `frequency` or defaults to frequent single-line terminal updates.
- `log_progress()` prints percentage, ETA, written amount, and speed.
- `log_progress_final()` prints total time, written amount, and average speed.
- `tools_clear_line()` clears the current terminal line for in-place progress updates.

## JSON Progress
- `tools_time_progress_json()` computes speed/ETA and calls `log_progress_json()`.
- JSON fields include device, bytes written, device size, speed bytes/sec, ETA milliseconds, and elapsed milliseconds.

## Public Callback
`tools_progress()` is the callback passed to libcryptsetup wipe operations:
- Emits JSON if requested.
- Emits human progress only outside batch mode.
- Checks interruption with `check_signal()`.
- Clears the line and prints the configured interrupt message when interrupted.

## Device Name Helper
`tools_get_device_name()` returns a loop backing file path if the device is loop-backed; otherwise it returns the original device string and hands ownership of any allocated backing path to the caller.

## Notes
Progress state is carried in `struct tools_progress_params`, defined in `cryptsetup.h`.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_progress.c -->