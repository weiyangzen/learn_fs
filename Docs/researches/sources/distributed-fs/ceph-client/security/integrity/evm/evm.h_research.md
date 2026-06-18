# sources/distributed-fs/ceph-client/security/integrity/evm/evm.h

Purpose: internal EVM header defining initialization flags, inode-cache metadata, protected xattr list entries, digest layout, globals, and crypto/securityfs function prototypes.

Important APIs, types, and functions: defines `EVM_INIT_HMAC`, `EVM_INIT_X509`, `EVM_ALLOW_METADATA_WRITES`, `EVM_SIGV3_REQUIRED`, `EVM_SETUP_COMPLETE`, `EVM_KEY_MASK`, `EVM_INIT_MASK`, `struct xattr_list`, `struct evm_iint_cache`, `struct evm_digest`, `evm_iint_inode()`, and prototypes for `evm_protected_xattr()`, `evm_init_key()`, `evm_update_evmxattr()`, `evm_calc_hmac()`, `evm_calc_hash()`, `evm_init_hmac()`, and `evm_init_secfs()`.

Control flow: the inline `evm_iint_inode()` returns the EVM portion of an inode security blob using `evm_blob_sizes.lbs_inode`, or NULL when no security blob exists.

State and persistence: declares global initialization state, HMAC attributes, and configured protected xattr names. `evm_iint_cache` stores per-inode EVM status and metadata attributes.

Dependencies and integration: included by EVM implementation files and depends on the integrity header, LSM blob sizing, inode security blobs, and xattr APIs.

Risks and test signals: blob offset correctness is critical because the inline pointer arithmetic assumes LSM blob layout. Test signals include inode blob allocation with EVM enabled, EVM status caching, and protected xattr list behavior.
