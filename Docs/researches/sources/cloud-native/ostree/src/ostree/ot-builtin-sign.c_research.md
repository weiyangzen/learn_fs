# sources/cloud-native/ostree/src/ostree/ot-builtin-sign.c

## Purpose
Implements `ostree sign`, the non-GPG signapi command for signing commits and verifying commit signatures, defaulting to Ed25519 when available.

## Important APIs, Types, And Functions
`ostree_builtin_sign()` is the command entry. `usage_error()` prints help for argument failures. The implementation uses `ostree_sign_get_by_name()`, `ostree_sign_set_sk()`, `ostree_sign_set_pk()`, `ostree_sign_add_pk()`, `ostree_sign_load_pk()`, `ostree_sign_commit()`, `ostree_sign_commit_verify()`, `ostree_sign_read_sk()`, and `OstreeBlobReader`.

## Control Flow
The command requires a commit. Signing mode requires at least one key ID unless a keys file is used; verify mode may use provided public key IDs, a keys file, or system configuration. It resolves the commit, initializes the selected sign type, and loops over key arguments. In verify mode it tries each key as a public key and returns success on the first valid signature. In signing mode it treats each key argument as a secret key string and signs. Verify mode then optionally loads public keys from a file or system/custom key directory and verifies. Signing mode optionally reads multiple encoded secret keys from a file and signs with each. If verify mode finds no valid signatures and no lower-level error remains, it returns a "No valid signatures found" error. Successful verification clears earlier per-key errors.

## State And Persistence
Signing persists signatures in commit detached metadata through signapi. Verification is read-only. The command does not update refs or summaries.

## Dependencies And Integration Points
It depends on `ostree-sign`, private core definitions, GLib file streams, and optional Ed25519 build support for keys-file/keys-dir options. It overlaps with commit-time signing and static delta signature verification.

## Risks And Edge Cases
The `--delete` option is declared but not implemented in control flow in this file, so users may expect deletion that does not occur. Verification ignores keys that cannot be set and continues, clearing errors if a later key succeeds. Keys from command-line strings are sensitive. File reading checks regular-file status for signing files but verification file loading is delegated to signapi.

## Test Signals
Tests should cover signing with string keys, signing with multiple file keys, verifying with explicit public keys, verifying from keys-file and keys-dir/system config, unsupported sign types, no-valid-signature errors, error clearing after later success, and the current behavior of the declared `--delete` option.
