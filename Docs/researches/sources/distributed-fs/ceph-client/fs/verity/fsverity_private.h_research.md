<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/fsverity_private.h -->
# sources/distributed-fs/ceph-client/fs/verity/fsverity_private.h

Purpose: Private fs-verity header defining internal data structures, constants, logging helpers, conditional feature stubs, and prototypes shared by core implementation files.

Important APIs, types, and functions: Defines `FS_VERITY_MAX_LEVELS`, `struct fsverity_hash_alg`, `union fsverity_hash_ctx`, `struct merkle_tree_params`, `struct fsverity_info`, and `FS_VERITY_MAX_SIGNATURE_SIZE`. Declares hash, init/logging, BPF, open/info-cache, signature, and workqueue functions and includes fs-verity trace events.

Control flow: No runtime control flow. The header encodes invariants used by all fs-verity code: supported tree depth, hash algorithm metadata, precomputed salted hash state, tree topology fields, per-inode cached root/file digest, inode hash table linkage, and optional bitmap for verified hash blocks.

State and persistence: Defines the in-memory `fsverity_info` cache shape. Persistent descriptor and Merkle tree data are referenced through public `linux/fsverity.h` structures and filesystem operations, not stored in the header.

Dependencies and integration points: Depends on `linux/fsverity.h`, rhashtable support, crypto SHA contexts, trace events, optional BPF syscall support, and optional builtin signature config.

Risks and test signals: Risks are mismatch between declared invariants and implementation assumptions, especially digest/block power-of-two requirements, maximum tree levels, and conditional stubs. Test with compile coverage for `CONFIG_BPF_SYSCALL` and `CONFIG_FS_VERITY_BUILTIN_SIGNATURES`, plus large-tree and sub-page block-size cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/fsverity_private.h -->
