# File Research: sources/cow-pools/bcachefs-tools/src/key.rs

Manages bcachefs passphrases and kernel keyring integration for encrypted filesystems.

Core concepts:
- `BCH_KEY_MAGIC` identifies plaintext/decrypted filesystem keys.
- `sb_is_encrypted` checks whether a superblock crypt field contains an encrypted passphrase-protected key.
- `unencrypted_key` wraps a raw key as a plaintext `bch_encrypted_key`.
- `Keyring` selects session, user, or user-session keyring IDs.
- `UnlockPolicy` controls fail, wait, ask, or stdin passphrase acquisition.

Key handling:
- `KeyHandle::new` validates a passphrase against the superblock, then adds the derived passphrase key to the selected kernel keyring under `bcachefs:<uuid>`.
- `new_from_search` checks session, user, and user-session keyrings.
- `wait_for_unlock` polls once per second until a key appears.

Passphrase acquisition:
- `Passphrase` is `ZeroizeOnDrop` and stores a `CString`.
- Terminal input disables echo with `rustix::termios`.
- Non-terminal stdin reads one line.
- `/dev/null` stdin triggers `systemd-ask-password` fallback.
- New passphrases can be prompted twice and compared.
- Passphrase files are read into `Zeroizing<String>`.

Crypto operations:
- Passphrase derivation calls C `derive_passphrase`.
- `check` decrypts the superblock key with `bch2_chacha20` and validates magic.
- `encrypt_key` encrypts a filesystem key with a passphrase-derived key.

Potential concerns:
- `CString` rejects interior NULs; passphrases containing NUL cannot be used.
- `systemd-ask-password` output is wrapped directly in `CString`; trailing newline handling differs from stdin/file paths.
- `wait_for_unlock` has no timeout or cancellation beyond process interruption.
