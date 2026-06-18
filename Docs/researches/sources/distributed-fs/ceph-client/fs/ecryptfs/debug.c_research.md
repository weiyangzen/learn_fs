# sources/distributed-fs/ceph-client/fs/ecryptfs/debug.c

## Purpose

`debug.c` contains eCryptfs-only debug printers. It does not participate in filesystem behavior except when other code paths ask it to dump authentication tokens or raw bytes for diagnosis. Its outputs are intentionally gated by `ecryptfs_verbosity`, but when enabled they can expose cryptographic material.

## Important APIs, types, and functions

The file exports `ecryptfs_dump_auth_tok()` and `ecryptfs_dump_hex()`. `ecryptfs_dump_auth_tok()` understands `struct ecryptfs_auth_tok`, password-token salt/signature fields, persistent password flags, private-key token identification, and `session_key` flags such as decrypted key, encrypted key, userspace decrypt request, and userspace encrypt request. `ecryptfs_dump_hex()` wraps `print_hex_dump()` with the `ecryptfs:` prefix and prints only when verbosity is at least 1.

## Control flow

Callers pass an auth token to `ecryptfs_dump_auth_tok()`. The function emits token type, password salt and signature for passphrase tokens, then reports session-key flags and optionally dumps decrypted or encrypted key buffers. It uses `ecryptfs_to_hex()` for salt formatting and `ecryptfs_printk()` for level-aware logging. `ecryptfs_dump_hex()` exits immediately unless `ecryptfs_verbosity >= 1`, then prints a 16-byte-row hex dump.

## State and persistence behavior

No persistent state is modified. The only state read is the passed token/buffer plus the global `ecryptfs_verbosity`. The file can leak transient secrets to persistent kernel logs when verbosity is enabled, especially FEKs, encrypted session keys, and session-key-encryption keys passed by callers in crypto and keystore code.

## Dependencies and integration points

The file depends on `ecryptfs_kernel.h`, Linux string helpers, `print_hex_dump()`, and constants from the eCryptfs public auth-token ABI. It is called from verbose paths in `crypto.c` and `keystore.c`, including FEK generation/decryption, IV derivation, key packet parsing, and candidate auth-token matching.

## Risks

The core risk is operational: enabling verbosity writes sensitive values to syslog. The implementation also uses a flag check against `auth_tok->flags & ECRYPTFS_PRIVATE_KEY`, while token type is usually represented through `auth_tok->token_type`; tests should ensure the printed type remains accurate for the ABI in use. Because this is debug-only, error handling is intentionally minimal.

## Test signals

Signals include booting/loading with default verbosity and confirming no hex dumps, setting `ecryptfs_verbosity=1` and exercising mount/open/key lookup paths, verifying password tokens print salt/signature while private-key tokens do not read password-only fields, and checking that dumps are absent in normal production logs.
