# Group Research: group_279_cryptsetup_sources_block_storage_cryptsetup_src_utils_reencrypt_c_so_68684dc60a66

Scope: `Docs/research_subset_a.md`, source tree `sources/block-storage/cryptsetup`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_reencrypt.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_reencrypt.c

This is the main `cryptsetup reencrypt` implementation for LUKS2 and the top-level dispatcher that falls back to the legacy LUKS1 reencryption path. It handles encrypt, decrypt, reencrypt, initialize-only, resume-only, active online reencryption, and forced offline modes.

Key responsibilities:
- Classifies devices as clean LUKS2, LUKS2 reencryption in progress, LUKS1, legacy LUKS1 reencryption, non-LUKS, or invalid.
- Enforces LUKS version conflicts and routes `--encrypt`, `--decrypt`, or normal reencryption to `_encrypt`, `_decrypt`, or `_reencrypt`.
- Initializes LUKS2 reencryption through `crypt_reencrypt_init_by_keyslot_context`.
- Resumes LUKS2 reencryption through `crypt_reencrypt_run`.
- Detects active dm holders for online reencryption unless `--force-offline-reencrypt` is used.
- Handles detached headers, data shifts, temporary headers, sector size changes, cipher changes, and volume key changes.
- Manages keyslot and token unlock contexts for reencryption.

Important control flow:
- `reencrypt()` is the public entry point. It loads by active name if `--active-name` is set, otherwise by header/data device, validates LUKS version expectations, checks resume/init-only conflicts, then dispatches.
- `load_luks()` loads LUKS metadata and detects LUKS2 online reencryption via persistent requirements. If normal load fails, it checks for the LUKS1 legacy unusable magic.
- `luks2_reencrypt_eligible()` rejects unsupported LUKS2 configurations: legacy offline reencryption requirement, OPAL, integrity profiles, or unknown cipher format.
- `reencrypt_luks2_load()` resumes an already initialized LUKS2 operation after validating requested options against stored reencryption parameters and unlocking the needed old/new volume key contexts.
- `encrypt_luks2_init()` formats a new LUKS2 header and initializes encryption over an existing plaintext data device. It supports detached header mode and temporary header placement for in-place header creation.
- `decrypt_luks2_init()` supports LUKS2 decryption only with detached headers and data offset zero. `decrypt_luks2_datashift_init()` handles the special case where a missing header file is exported first, then reencryption is initialized with datashift.
- `reencrypt_luks2_init()` handles LUKS2-to-LUKS2 reencryption, including cipher/mode changes, sector size changes, optional volume key replacement, keyslot duplication, token reassignment, and active mapping discovery.

Key data structures:
- `enum device_status_info` models device classification for dispatch.
- `struct keyslot_contexts` tracks candidate keyslots, token contexts, old/new volume key contexts, generated new volume key state, and new/old keyslot IDs.
- `struct crypt_params_reencrypt` is filled differently for encrypt, decrypt, resume, and reencrypt modes.

Keyslot/token handling:
- Token candidates are collected from token/keyslot assignments.
- Token unlock is attempted before passphrase prompts when token options are present.
- For volume key changes with active keyslots, new keyslots are created and token assignments are copied from old keyslots to new keyslots.
- `set_keyslot_params()` preserves keyslot encryption and PBKDF parameters unless CLI options request replacement. It replaces `cipher_null` keyslot encryption with default LUKS2 keyslot encryption.

Safety and validation:
- Active-holder auto-detection prevents accidental offline reencryption of active devices.
- Non-block-device data paths in batch mode require `--force-offline-reencrypt`.
- Sector size increases are rejected for offline devices when blkid probing is needed.
- Filesystem superblock block size is checked before increasing encryption sector size.
- Broken LUKS signatures are detected before encrypting a non-LUKS device.
- LUKS2 decryption requires `--header`; encryption without detached header requires device size reduction.
- Reencryption cannot proceed if no segment parameter changes are requested.

External dependencies:
- Heavy use of libcryptsetup APIs: `crypt_init*`, `crypt_load`, `crypt_reencrypt_status`, `crypt_reencrypt_init_by_keyslot_context`, `crypt_reencrypt_run`, `crypt_activate_by_keyslot_context`, keyslot/token APIs, persistent flags, integrity info, and header backup/restore.
- Uses cryptsetup helpers from other files: argument macros, `luksFormat`, token unlock helpers, PBKDF setup, progress reporting, blkid/signature helpers, volume key helpers, and signal handling.
- Calls `reencrypt_luks1()` and `reencrypt_luks1_in_progress()` for legacy LUKS1 behavior.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_reencrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_reencrypt_luks1.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_reencrypt_luks1.c

This file implements legacy offline LUKS1 reencryption. Unlike the LUKS2 path, it performs reencryption by creating temporary headers, activating old/new temporary mappings, copying data between them, and tracking progress in an external log file.

Key responsibilities:
- Supports LUKS1 reencrypt, encrypt, decrypt, resume, and keep-key modes.
- Creates and manages temporary files named from the LUKS UUID:
  - `LUKS-<uuid>.org`
  - `LUKS-<uuid>.new`
  - `LUKS-<uuid>.log`
- Marks an original LUKS1 header unusable by replacing the normal magic with `LUKS dead` style `NOMAGIC`.
- Detects an in-progress legacy LUKS1 reencryption by checking for the unusable magic.
- Activates two private temporary dm-crypt mappings, one with the old header and one with the new header.
- Copies data forward or backward depending on whether the device size is reduced.
- Restores the final LUKS1 header after copying completes.

Main state:
- `struct reenc_ctx` stores device/header paths, UUID, mode, direction, offsets, temporary file names, dm paths, log file descriptor/buffer, passphrases per slot, selected keyslot, and resume byte count.
- Modes are `REENCRYPT`, `ENCRYPT`, and `DECRYPT`.
- Directions are `FORWARD` and `BACKWARD`.

Important control flow:
- `reencrypt_luks1()` allocates and initializes the context, gathers passphrases, prepares backup/fake headers, marks the original header unusable when needed, activates temporary mappings, copies data unless `--keep-key` is set, then restores or finalizes headers.
- `initialize_context()` prepares filenames, validates exclusive device open, initializes UUID, removes stale temporary mappings, opens/parses the log, and sets initial mode/direction.
- `open_log()` creates a new log or opens an existing one to resume.
- `write_log()` and `parse_log()` store/restore version, UUID, direction, mode, offset, and shift in a single sector.
- `backup_luks_headers()` saves the original LUKS1 header and creates the new LUKS1 header for reencryption.
- `backup_fake_header()` creates `cipher_null` fake headers for encrypt/decrypt transitions.
- `activate_luks_headers()` opens private temporary mappings for old and new views of the same data device.
- `copy_data_forward()` and `copy_data_backward()` perform the actual IO and update the log.
- `restore_luks_header()` restores the completed new header to the real header location or renames it for new detached-header encryption.
- `destroy_context()` closes mappings, removes clean temporary files, and clears passphrase memory.

Safety and recovery:
- The original LUKS1 header is intentionally made unusable during reencryption to prevent accidental normal activation of partially converted data.
- The `.log` file is the resume source; deleting or editing it breaks recovery.
- `stained` controls whether temporary files are retained after failure.
- IO errors during copy are reported and leave recovery artifacts.
- Signal interruption returns retryable/resumable errors and writes the current log.
- For decrypt, extra space in the now-plain device may be zeroed to remove leftover encrypted tail data.

Limitations and notable behavior:
- The implementation is offline-only and requires exclusive device access.
- It relies on passphrase material stored in memory per keyslot during the operation.
- It has a FIXME noting non-PBKDF2 PBKDFs should be blocked.
- The file-level comment and surrounding LUKS2 code indicate this is legacy behavior retained for LUKS1 compatibility.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_reencrypt_luks1.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_tools.c -->
# File Research: sources/block-storage/cryptsetup/src/utils_tools.c

This file provides common command-line utility support used across cryptsetup tools.

Key responsibilities:
- Global interrupt handling through `quit`, SIGINT/SIGTERM handlers, and signal blocking/unblocking.
- Common logging callbacks for normal, verbose, error, and debug output.
- Interactive confirmation prompts requiring uppercase `YES`.
- Exit/status translation and user-facing command status messages.
- UUID shorthand conversion for `UUID=<uuid>` into `/dev/disk/by-uuid/<uuid>`.
- POPT usage cleanup and version/debug command reporting.
- Keyslot/token success and token error messages.
- Device-size string parsing with binary/decimal/unit suffixes.
- Volume key file read/write helpers.
- Package feature flag printing.
- Device-mapper name validation.

Important functions:
- `set_int_handler()`, `set_int_block()`, `check_signal()` implement cooperative cancellation semantics used by reencryption and wipe/progress loops.
- `tool_log()` and `quiet_log()` are callbacks passed into libcryptsetup.
- `yesDialog()` and `noDialog()` wrap `_dialog()` and temporarily unblock signals while reading from the terminal.
- `translate_errno()` maps negative errno-style results into cryptsetup’s compact exit codes.
- `tools_string_to_size()` parses suffixes such as sectors, K/M/G/T, KiB/MiB/GiB/TiB, and decimal KB/MB/GB/TB.
- `tools_read_vk()` reads an exact-size volume key into secure memory.
- `tools_write_mk()` creates a new key file with exclusive create semantics.
- `tools_check_newname()` rejects overlong dm names and names containing `/`.

Behavioral notes:
- `uuid_or_device()` uses a static buffer and only rewrites strings with a valid `UUID=` prefix containing hex digits and dashes.
- `tools_token_error_msg()` distinguishes missing PIN, wrong keyslot passphrase, missing resource, and no usable token.
- Dialogs default to their caller-provided answer if stdin is not a TTY.
- `tools_write_mk()` creates files with read permission for the owner only.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/utils_tools.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/veritysetup.c -->
# File Research: sources/block-storage/cryptsetup/src/veritysetup.c

This is the standalone `veritysetup` command implementation for dm-verity devices. It parses CLI options, dispatches actions, formats verity metadata, verifies hashes, opens readonly verity mappings, closes mappings, prints status, and dumps on-disk metadata.

Supported actions:
- `format <data_device> <hash_device>`
- `verify <data_device> <hash_device> [<root_hash>]`
- `open <data_device> <name> <hash_device> [<root_hash>]`
- `close <name>`
- `status <name>`
- `dump <hash_device>`

Aliases:
- `create` maps to `open` with historical argument swapping.
- `remove` maps to `close`.

Important control flow:
- `main()` builds POPT option tables from `veritysetup_arg_list.h`, parses the action, validates action-specific argc, checks option/action compatibility, rejects conflicting corruption/deferred options, enables debug logging, then calls `run_action()`.
- `run_action()` executes the selected action handler, displays status, and returns translated exit code.
- `tools_cleanup()` frees parsed core args.

Formatting:
- `action_format()` creates the hash image if needed, creates the FEC image if requested, initializes a crypt device on the hash device, prepares `struct crypt_params_verity`, calls `crypt_format(CRYPT_VERITY)`, dumps metadata, and optionally writes the root hash as hex to `--root-hash-file`.
- `_prepare_format()` fills hash algorithm, data device, FEC settings, salt, block sizes, data block count, offsets, format type, and flags. `--salt -` means no salt; explicit salt is hex-decoded; absent salt uses the default salt size.

Open/verify:
- `_activate()` is shared by `action_open()` and `action_verify()`.
- It initializes the crypt device using the hash device plus data device, loads an on-disk verity superblock unless `--no-superblock` is set, or formats in-memory parameters for no-superblock mode.
- It reads the root hash either from argv or `--root-hash-file`, validates exact hex length against `crypt_get_volume_key_size()`, optionally reads a root hash signature, then calls `crypt_activate_by_signed_key()`.
- `action_open()` validates the dm name and activates readonly by default.
- `action_verify()` passes a NULL dm name and `CRYPT_VERITY_CHECK_HASH` to verify without creating a persistent mapping.

Close/status/dump:
- `action_close()` supports deferred removal and cancellation of deferred removal.
- `action_status()` prints active/inactive state, type, corruption/verification status, verity parameters, data/hash/FEC devices and loop backing files, offsets, repaired FEC event count, root hash, readonly mode, and activation flags.
- `action_dump()` loads verity metadata and calls `crypt_dump()`.

Safety and validation:
- `--ignore-corruption` and `--restart-on-corruption` are mutually exclusive.
- `--panic-on-corruption` and `--restart-on-corruption` are mutually exclusive.
- `--error-as-corruption` is only valid with panic or restart behavior.
- `--cancel-deferred` and `--deferred` cannot be combined.
- Root hash files must be regular and large enough for the expected hex hash.
- Signature files must be regular and non-empty.
- Mapping names are validated through `tools_check_newname()`.

External dependencies:
- Uses libcryptsetup dm-verity APIs: `crypt_format`, `crypt_load`, `crypt_activate_by_signed_key`, `crypt_get_verity_info`, `crypt_get_active_device`, `crypt_get_verity_repaired`, `crypt_volume_key_get`, and `crypt_dump`.
- Uses shared tool helpers for logging, argument parsing, cleanup, size/key reads, status translation, and package version output.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/veritysetup.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/veritysetup_arg_list.h -->
# File Research: sources/block-storage/cryptsetup/src/veritysetup_arg_list.h

This header is an X-macro list of all `veritysetup` command-line options. It is included multiple times with different `ARG(...)` definitions to generate POPT options, enum IDs, and `struct tools_arg` metadata.

Each entry provides:
- Long option name.
- Short option character, if any.
- POPT argument type.
- Help text.
- Unit/help suffix.
- Internal argument type.
- Default value.
- Allowed actions list, where empty means global.

Defined options:
- Deferred close controls: `--deferred`, `--cancel-deferred`.
- Verification behavior: `--ignore-corruption`, `--restart-on-corruption`, `--panic-on-corruption`, `--error-as-corruption`, `--ignore-zero-blocks`, `--check-at-most-once`, `--use-tasklets`.
- Format/load parameters: `--data-block-size`, `--data-blocks`, `--hash-block-size`, `--hash-offset`, `--hash`, `--format`, `--salt`, `--uuid`, `--no-superblock`.
- FEC parameters: `--fec-device`, `--fec-offset`, `--fec-roots`.
- Root hash inputs/outputs: `--root-hash-file`, `--root-hash-signature`.
- Activation sharing: `--shared`.
- Common output controls: `--debug`, `--verbose`.

Defaults encoded here:
- Data block size defaults to `DEFAULT_VERITY_DATA_BLOCK`.
- Hash block size defaults to `DEFAULT_VERITY_HASH_BLOCK`.
- FEC roots defaults to `DEFAULT_VERITY_FEC_ROOTS`.
- Format defaults to `1`.
- Hash defaults to `DEFAULT_VERITY_HASH`.

Notable design:
- Action restrictions are symbolic macros from `veritysetup_args.h`, so invalid option/action combinations can be caught centrally by `tools_check_args()`.
- The list is intentionally declarative and contains no executable logic.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/veritysetup_arg_list.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/cryptsetup/src/veritysetup_args.h -->
# File Research: sources/block-storage/cryptsetup/src/veritysetup_args.h

This header defines the argument metadata infrastructure for `veritysetup`.

Key contents:
- Include guard `VERITYSETUP_ARGS_H`.
- Includes shared argument name and macro helpers.
- Defines action name constants: `close`, `dump`, `format`, `open`, `status`, and `verify`.
- Defines per-option action allowlists used by `veritysetup_arg_list.h`.
- Generates option enum IDs from `veritysetup_arg_list.h`.
- Generates the global `tool_core_args[]` table from the same X-macro list.

Action allowlists:
- `--deferred` applies to `close`.
- Corruption behavior options apply to `open`.
- `--root-hash-file` applies to `format`, `open`, and `verify`.
- `--root-hash-signature`, `--use-tasklets`, and `--shared` apply to `open`.

Generated structures:
- The enum starts with `OPT_UNUSED_ID = 0`, then appends one `_ID` per option.
- `tool_core_args[]` begins with an unused placeholder, then one `struct tools_arg` per option with name, set flag, internal type, default value, and allowed actions.

Design role:
- Keeps `veritysetup.c` small by centralizing action names, option IDs, default values, and action restrictions.
- Shares the same declarative option source with POPT table generation, reducing drift between parsing, validation, and internal option lookup.
<!-- END FILE RESEARCH: sources/block-storage/cryptsetup/src/veritysetup_args.h -->