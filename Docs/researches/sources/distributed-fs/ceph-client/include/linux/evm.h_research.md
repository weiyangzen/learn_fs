# sources/distributed-fs/ceph-client/include/linux/evm.h

Purpose: Extended Verification Module interface for protecting and validating file metadata/xattrs.

Important APIs/types/functions: `evm_set_key()`, `evm_verifyxattr()`, `evm_fix_hmac()`, `evm_inode_init_security()`, `evm_revalidate_status()`, `evm_protected_xattr_if_enabled()`, `evm_read_protected_xattrs()`, `evm_metadata_changed()`, and `posix_xattr_acl()` helper/stub.

Control flow: LSM/integrity and filesystem paths call EVM when setting security xattrs, verifying protected xattrs, initializing inode security, or detecting metadata changes. Disabled stubs allow callers to compile while returning permissive or unsupported results.

State/persistence: EVM HMAC/signature values are stored in protected xattrs on files; key material is runtime kernel state.

Dependencies/integration: integrity subsystem, IMA/EVM, dentries/inodes, xattrs, POSIX ACLs, LSM security initialization.

Risks/test signals: risks are accepting stale metadata after protected xattr changes, disabled-config semantic differences, key setup failures, and ACL xattr classification errors. Test xattr verification/fixup, metadata mutation, key loading, fs with/without ACLs, IMA/EVM policy, and config-off behavior.
