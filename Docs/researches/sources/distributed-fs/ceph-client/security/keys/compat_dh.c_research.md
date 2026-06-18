# sources/distributed-fs/ceph-client/security/keys/compat_dh.c

Purpose: Converts 32-bit compatibility KDF parameters for `KEYCTL_DH_COMPUTE` before invoking the native DH implementation.

Important APIs/types/functions: Implements `compat_keyctl_dh_compute()` and maps `struct compat_keyctl_kdf_params` to `struct keyctl_kdf_params`.

Control flow: If no KDF pointer is supplied, it forwards directly with NULL. Otherwise it copies the compat struct from userspace, converts `hashname` and `otherinfo` pointers via `compat_ptr()`, copies length and spare fields, and calls `__keyctl_dh_compute()`.

State and persistence: No local state.

Dependencies and integration: Used by `compat.c` for DH operations and depends on native `dh.c` implementation.

Risks and test signals: Risks include bad pointer conversion and spare field mismatch. Compat DH tests should cover no-KDF, KDF, bad userspace pointer, and reserved-field validation in the native path.
