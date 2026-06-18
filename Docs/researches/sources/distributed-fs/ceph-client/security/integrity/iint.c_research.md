<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/iint.c -->
# sources/distributed-fs/ceph-client/security/integrity/iint.c

## Purpose
Provides shared integrity subsystem helpers for securityfs setup, raw kernel file reads used by IMA hashing, and late loading of IMA/EVM X509 keys.

## Important APIs, Types, And Functions
- Global `struct dentry *integrity_dir`.
- `integrity_kernel_read()` wraps `__kernel_read()` without normal lock/security checks relevant to user reads.
- `integrity_load_keys()` invokes `ima_load_x509()` and conditionally `evm_load_x509()`.
- `integrity_fs_init()` and `integrity_fs_fini()` create and remove the shared `integrity` securityfs directory.

## Control Flow
IMA/EVM callers request the shared securityfs root through `integrity_fs_init()`. The function is idempotent if the directory already exists and reports non-`ENODEV` creation failures. On teardown, `integrity_fs_fini()` removes the directory only when present and empty. Key loading occurs once rootfs is ready through the integrity key-loading hook.

## State And Persistence
The only in-kernel state here is the `integrity_dir` dentry pointer. Securityfs directory presence is runtime state. Loaded X509 certificates persist in kernel keyrings for the boot.

## Dependencies And Integration Points
This file is a shared dependency for IMA and EVM securityfs code and for IMA file hashing in `ima_crypto.c`. It integrates with securityfs, key-loading helpers, and generated configuration controlling whether IMA or EVM owns X509 loading.

## Risks And Edge Cases
Securityfs may be unavailable, returning `-ENODEV`; callers must handle that as initialization failure or unsupported runtime interface. The raw read helper intentionally bypasses normal checks, so it should remain limited to integrity internals.

## Test Signals
Boot logs for integrity securityfs creation failures, presence of `/sys/kernel/security/integrity`, successful IMA/EVM key loading, and IMA hashes over files that require `integrity_kernel_read()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/iint.c -->
