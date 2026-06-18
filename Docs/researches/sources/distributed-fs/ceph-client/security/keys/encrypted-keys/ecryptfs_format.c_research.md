# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.c

Purpose: Provides helper functions that format encrypted-key payloads as eCryptfs authentication tokens.

Important APIs/types/functions: Exports `ecryptfs_get_auth_tok_key()`, `ecryptfs_get_versions()`, and `ecryptfs_fill_auth_tok()`.

Control flow: `ecryptfs_get_auth_tok_key()` returns the session key encryption key location inside an auth token. `ecryptfs_get_versions()` reports kernel-supported eCryptfs version constants. `ecryptfs_fill_auth_tok()` initializes token version, password token type, signature from key description, max key bytes, session-key-encryption flag, empty encrypted session key, default SHA-512 hash algorithm, and clears persistent-password flag. It intentionally leaves salt and session key material initialization to other code.

State and persistence: No local state. It mutates caller-provided `struct ecryptfs_auth_tok` that is later stored or used by encrypted/eCryptfs key code.

Dependencies and integration: Depends on Linux eCryptfs structures and is linked into encrypted keys. Exports symbols for users elsewhere in the kernel.

Risks and test signals: Risks include structure layout/version drift, signature truncation/padding behavior, fixed SHA-512 hash policy, and assumptions about external key material initialization. Tests should validate generated token fields and compatibility with eCryptfs consumers.
