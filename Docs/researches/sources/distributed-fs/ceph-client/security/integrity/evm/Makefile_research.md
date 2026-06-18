# sources/distributed-fs/ceph-client/security/integrity/evm/Makefile

Purpose: builds the EVM object from core, crypto, securityfs, and optional POSIX ACL support.

Important APIs, types, and functions: Kbuild rules create `evm.o` from `evm_main.o`, `evm_crypto.o`, `evm_secfs.o`, and conditionally `evm_posix_acl.o`.

Control flow: object inclusion is controlled by `CONFIG_EVM` and `CONFIG_FS_POSIX_ACL`.

State and persistence: no runtime state directly.

Dependencies and integration: ties EVM build output into the integrity Makefile and optional ACL xattr handling.

Risks and test signals: missing optional ACL object can alter protected metadata coverage when POSIX ACLs are configured. Test signals are build inclusion and EVM ACL behavior under `CONFIG_FS_POSIX_ACL`.
