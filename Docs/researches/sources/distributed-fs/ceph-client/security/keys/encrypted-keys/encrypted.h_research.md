<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.h -->
# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.h

## Purpose
`encrypted.h` is the private header for encrypted-key support. It exposes the trusted-master-key accessor when trusted keys are available and defines no-op or active key-material dump helpers depending on `ENCRYPTED_DEBUG`.

## Important APIs, Types, and Functions
`request_trusted_key()` is declared when trusted keys can be linked with encrypted keys; otherwise an inline stub returns `-EOPNOTSUPP`. Debug helpers are `dump_master_key()`, `dump_decrypted_data()`, `dump_encrypted_data()`, and `dump_hmac()`.

## Control Flow
Compile-time configuration controls whether encrypted keys can ask the trusted key type for a master key. Debug helpers either call `print_hex_dump()`/`pr_info()` or compile to empty inline functions, so callers in `encrypted.c` do not need local `#ifdef` blocks.

## State and Persistence
The header stores no state. It only provides function declarations and inline wrappers. When debugging is enabled, helper calls expose transient key material to kernel logs; otherwise they have no runtime effect.

## Dependencies and Integration Points
The trusted-key declaration matches `masterkey_trusted.c` and depends on `CONFIG_TRUSTED_KEYS` or the module combination where both trusted and encrypted keys are modules. The dump helpers rely on `struct encrypted_key_payload` from public encrypted-key headers included by the C file.

## Risks
The main risk is accidental key disclosure if `ENCRYPTED_DEBUG` is changed from zero. The trusted-key stub must preserve the same signature as the real function so `encrypted.c` cleanly handles unavailable trusted-key support.

## Test Signals
Build encrypted keys with trusted keys built-in, as modules, and disabled. Verify `trusted:` master descriptions fail with `-EOPNOTSUPP` when unsupported, while `user:` masters still work. Audit debug builds to confirm logs contain expected dumps only when deliberately enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/encrypted-keys/encrypted.h -->
