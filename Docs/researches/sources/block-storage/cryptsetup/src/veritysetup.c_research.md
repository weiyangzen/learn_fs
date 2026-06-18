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
