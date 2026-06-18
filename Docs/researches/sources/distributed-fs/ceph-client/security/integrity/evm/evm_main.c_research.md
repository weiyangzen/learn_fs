<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_main.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_main.c

## Purpose
Implements the EVM LSM integration that protects `security.evm` and the metadata covered by it. The file verifies EVM HMACs and signatures, blocks unsafe metadata/xattr changes, initializes EVM inode state, and updates `security.evm` after approved mutations.

## Important APIs, Types, And Functions
- Global state: `evm_initialized`, `evm_hmac_attrs`, `evm_config_xattrnames`, `evm_fixmode`.
- Verification: `evm_verify_hmac()`, exported `evm_verifyxattr()`, `evm_verify_current_integrity()`, `evm_read_protected_xattrs()`.
- Mutation gates: `evm_inode_setxattr()`, `evm_inode_removexattr()`, `evm_inode_setattr()`, `evm_inode_set_acl()`, `evm_inode_remove_acl()`.
- Post-change updates: `evm_inode_post_setxattr()`, `evm_inode_post_removexattr()`, `evm_inode_post_setattr()`, ACL post hooks, `evm_update_evmxattr()` callers.
- Initialization and integration: `evm_inode_init_security()`, `evm_inode_alloc_security()`, `evm_file_release()`, `evm_post_path_mknod()`, `DEFINE_LSM(evm)`.

## Control Flow
Boot initializes default protected xattr names, parses `evm=fix`, initializes the EVM keyring, and creates securityfs controls. Runtime LSM hooks first decide whether a mutation touches protected metadata, then verify current EVM integrity unless metadata writes are temporarily allowed. On success, post hooks reset cached status and recalculate the HMAC for `security.evm` when HMAC support is active. Verification reads `security.evm`, distinguishes HMAC, normal digital signature, and portable immutable signature formats, then compares a calculated HMAC or verifies a signature against the EVM keyring.

## State And Persistence
Persistent state is stored in xattrs, primarily `security.evm` and the protected xattrs listed in `evm_config_xattrnames`. Per-inode volatile state lives in `struct evm_iint_cache`, especially `evm_status`, `EVM_NEW_FILE`, and `EVM_IMMUTABLE_DIGSIG`. The code also tracks global initialization bits that determine whether HMACs, X509 verification, metadata-write allowance, setup completion, or sigv3 requirements are active.

## Dependencies And Integration Points
This file depends on VFS xattr operations, LSM hooks, integrity keyrings, crypto digest helpers, EVM digest/HMAC helpers from `evm.h`, POSIX ACL helpers, filesystem flags such as `SB_I_EVM_HMAC_UNSUPPORTED`, and IMA interactions via `security.ima` and `evm_verifyxattr()`. Overlay/copy-up handling permits only portable EVM signatures to be copied up.

## Risks And Edge Cases
Risk centers on stale iint cache state, filesystems without xattr/i_version support, unsupported HMAC filesystems, portable signatures that intentionally make metadata immutable, and fix mode accidentally masking labeling gaps. ACL changes are risky because system ACL xattrs can alter `i_mode`, which is covered by EVM. Secure boot disables `evm=fix`, and missing setup completion changes how unlabeled metadata updates are treated.

## Test Signals
Useful signals include successful/failed xattr and chmod/chown operations under EVM appraisal, audit messages for `update_metadata` and `appraise_metadata`, `security.evm` HMAC updates after metadata changes, immutable portable-signature behavior, overlay copy-up behavior, and boot logs showing initialized protected xattrs and HMAC attrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_main.c -->
