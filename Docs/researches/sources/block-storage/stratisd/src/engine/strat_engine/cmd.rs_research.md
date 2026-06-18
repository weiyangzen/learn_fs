# File Research: sources/block-storage/stratisd/src/engine/strat_engine/cmd.rs

Read status: complete, 616 lines.

## Purpose

`cmd.rs` centralizes stratisd invocation of external executables. It discovers fixed command paths, verifies required tools, wraps command execution and error reporting, and provides helper functions for XFS, thin-provisioning tools, Clevis, and cryptsetup reencryption operations.

## Executable Discovery

`find_executable` searches only known directories, not `$PATH`.

Default search directories:

- `/usr/sbin`
- `/sbin`
- `/usr/bin`
- `/bin`

They can be overridden at compile time through `EXECUTABLES_PATHS`.

`EXECUTABLES` lazily records paths for required non-Clevis commands:

- `mkfs.xfs`
- `thin_check`
- `thin_repair`
- `xfs_db`
- `xfs_growfs`
- `thin_metadata_size`
- `cryptsetup`
- `udevadm` in tests

`verify_executables` must be called at engine initialization and errors on the first missing required executable.

Clevis commands are checked dynamically by `get_clevis_executable`, which requires the full Clevis support command set.

## Command Execution

`execute_cmd` runs a `Command` and delegates output handling.

`handle_output`:

- Returns success on zero exit.
- On failure, includes command debug output, exit reason, stdout, and stderr in the `StratisError`.

## XFS Helpers

`create_fs` invokes `mkfs.xfs`.

Important behavior:

- Uses `-f`.
- Optionally sets filesystem UUID.
- Reads `mkfs.xfs -V` and enables `-i nrext64=0` for xfsprogs >= 6.0.0.
- If version probing fails, it assumes the option is supported and lets command failure surface naturally.

`xfs_growfs` runs `xfs_growfs <mount> -d`.

`set_uuid` runs `xfs_db -x -c "uuid <uuid>" <devnode>`.

## Thin-Provisioning Helpers

`thin_check` runs `thin_check --auto-repair`.

`thin_repair` runs `thin_repair -i <meta_dev> -o <new_meta_dev>`.

`thin_metadata_size` runs `thin_metadata_size`, parses sector count output, multiplies by an empirical factor of 8, rounds up to the pool block size, and caps at `MAX_META_SIZE`.

## Clevis Helpers

`clevis_luks_bind` supports two authentication forms:

- Existing token slot through `Either::Left`.
- Passphrase/key material through stdin via `Either::Right`.

It calls `clevis luks bind` with device, optional existing slot, optional target slot, pin, and JSON config.

`clevis_luks_unbind` runs forced unbind for a keyslot.

`clevis_luks_regen` regenerates a Clevis binding.

`clevis_decrypt` safely extracts a passphrase from a JWE:

1. Pipes JSON to `jose jwe fmt -i- -c`.
2. Pipes formatted output to `clevis decrypt`.
3. Reads decrypted bytes into `SafeMemHandle`.
4. Returns `SizedKeyMemory`.

## Cryptsetup Reencryption Helpers

- `run_encrypt`: `cryptsetup reencrypt --encrypt --resume-only --token-only <path>`
- `run_reencrypt`: `cryptsetup reencrypt --resume-only --token-only <path>`
- `run_decrypt`: `cryptsetup reencrypt --decrypt --resume-only --token-only <path>`

Each first ensures access to the persistent keyring.

## Notable Dependencies

- `libcryptsetup_rs::SafeMemHandle`
- `serde_json::Value`
- `semver` for `mkfs.xfs` version checks
- Stratis keyring helpers
- devicemapper `MetaBlocks` and `Sectors`

## Important Notes

- The module assumes executable locations are fixed once discovered.
- Clevis support is all-or-nothing based on the required executable list.
- Some helper functions call `wait` twice after `spawn`; this is observable in `get_mkfs_xfs_version` and `thin_metadata_size` and should be considered carefully if modified.
