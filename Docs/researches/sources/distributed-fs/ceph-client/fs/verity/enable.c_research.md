<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/enable.c -->
# sources/distributed-fs/ceph-client/fs/verity/enable.c

Purpose: Implements `FS_IOC_ENABLE_VERITY`, building a file’s Merkle tree, constructing and validating the fs-verity descriptor, caching `fsverity_info`, and asking the filesystem to finalize verity enablement.

Important APIs, types, and functions: Defines `struct block_buffer`, `hash_one_block()`, `write_merkle_tree_block()`, `build_merkle_tree()`, `enable_verity()`, and exported `fsverity_ioctl_enable()`.

Control flow: The ioctl copies and validates `fsverity_enable_arg`, requires a regular readable fd with write permission but no writable access, rejects append/dir/non-regular files, obtains mount write access, and calls `deny_write_access()`. `enable_verity()` creates a descriptor, copies salt and optional builtin signature, initializes Merkle parameters, calls filesystem `begin_enable_verity()` under inode lock, builds the Merkle tree by reading every data block and cascading hashes into tree blocks, creates/verifies `fsverity_info`, inserts it into the global hash, and calls filesystem `end_enable_verity()` with descriptor and tree size. On build or validation failure it rolls back with `end_enable_verity(NULL, 0, tree_size)`.

State and persistence: Writes Merkle tree blocks and the descriptor to filesystem-specific storage through `fsverity_operations`. On success the filesystem sets `S_VERITY`, making the file read-only and verifiable; in-memory `fsverity_info` is cached before finalization.

Dependencies and integration points: Depends on filesystem `begin_enable_verity`, `write_merkle_tree_block`, and `end_enable_verity` operations, kernel reads, mount write accounting, file write denial, signals, tracepoints, hash helpers, descriptor parsing, and optional signature verification.

Risks and test signals: Risks include racing file size changes, partial tree writes, descriptor/signature size overflow, block-size incompatibility, rollback failures, stale pagecache assumptions, and finalization without `S_VERITY`. Test empty files, large files, interrupted builds, invalid salt/signature/reserved fields, unsupported hash/block sizes, concurrent writers, read-only mounts, duplicate enable, filesystem operation failures, and post-enable read verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/enable.c -->
