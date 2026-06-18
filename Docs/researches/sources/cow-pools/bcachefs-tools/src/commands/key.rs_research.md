# File Research: sources/cow-pools/bcachefs-tools/src/commands/key.rs

## Purpose
Implements encryption key management commands: unlocking an encrypted filesystem, setting/changing a passphrase, and removing passphrase protection from an encrypted filesystem.

## Main Interfaces
- Commands:
  - `CMD_UNLOCK`
  - `CMD_SET_PASSPHRASE`
  - `CMD_REMOVE_PASSPHRASE`
- CLI structs:
  - `UnlockCli`
  - `SetPassphraseCli`
  - `RemovePassphraseCli`
- Key helpers:
  - `parse_device_list`
  - `open_nostart`
  - `open_and_verify`
  - `set_crypt_key`

## Behavior
- `unlock` reads a device superblock, verifies it is encrypted, optionally exits after `--check`, then adds the key to the selected keyring.
- Unlock can read passphrase from a file or prompt interactively.
- On incorrect passphrase, unlock retries up to two additional interactive attempts.
- `set-passphrase` opens an unmounted filesystem with `nostart`, verifies current encryption state, prompts for a new passphrase twice, encrypts the raw key, revokes the old key, and writes the superblock.
- `remove-passphrase` verifies the current key and writes an unencrypted key into the crypt field.
- Device arguments for passphrase operations can be multiple paths or one colon-separated list.

## Dependencies and Coupling
- Uses `crate::key` primitives: `Passphrase`, `KeyHandle`, `Keyring`, `sb_is_encrypted`, and `unencrypted_key`.
- Uses `sb_io::read_super` for direct superblock reads and `device_scan::open_scan` for multi-device operations.
- Mutates `bch_sb_field_crypt` via `sb_field_get_mut`.
- Calls `bch2_revoke_key` when setting a new passphrase.

## Important Implementation Notes
- `open_and_verify` handles both passphrase-protected and `--no_passphrase` encrypted filesystems.
- `set_crypt_key` is unsafe and documents that the caller must hold the superblock lock, though callers rely on single-threaded nostart mutation and `fs.write_super`.

## Risks and Edge Cases
- Incorrect-passphrase detection matches error string contents.
- The safety comment for `set_crypt_key` is stricter than what callers visibly enforce with a lock.
- `unlock --check` fails if not encrypted and succeeds if encrypted, without validating a passphrase.
