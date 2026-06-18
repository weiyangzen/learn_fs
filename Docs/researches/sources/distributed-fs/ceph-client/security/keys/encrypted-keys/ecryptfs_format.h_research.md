# sources/distributed-fs/ceph-client/security/keys/encrypted-keys/ecryptfs_format.h

Purpose: Declares eCryptfs formatting helpers for encrypted keys.

Important APIs/types/functions: Defines `PGP_DIGEST_ALGO_SHA512` and prototypes `ecryptfs_get_auth_tok_key()`, `ecryptfs_get_versions()`, and `ecryptfs_fill_auth_tok()`.

Control flow: Header-only interface.

State and persistence: No state; callers pass auth-token storage.

Dependencies and integration: Includes `linux/ecryptfs.h` and is consumed by encrypted key implementation.

Risks and test signals: Risks are constant mismatch with eCryptfs expectations and prototype drift. Build and token compatibility tests provide coverage.
