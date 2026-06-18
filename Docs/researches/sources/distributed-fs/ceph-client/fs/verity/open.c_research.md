<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/open.c -->
# sources/distributed-fs/ceph-client/fs/verity/open.c

Purpose: Initializes and caches per-inode fs-verity metadata when verity files are opened, validates descriptors, computes file digests, and manages the global `fsverity_info` rhashtable.

Important APIs, types, and functions: Defines `fsverity_info_cachep`, `fsverity_info_hash`, `fsverity_init_merkle_tree_params()`, `compute_file_digest()`, `fsverity_create_info()`, `fsverity_set_info()`, `__fsverity_get_info()`, `validate_fsverity_descriptor()`, `fsverity_get_descriptor()`, `ensure_verity_info()`, `__fsverity_file_open()`, `fsverity_free_info()`, `fsverity_remove_info()`, `fsverity_cleanup_inode()`, and `fsverity_init_info_cache()`.

Control flow: Merkle parameter initialization validates hash id, optional salt, block-size limits, digest/block arity, tree level counts, and tree size. Descriptor loading asks the filesystem first for size and then contents, checks version, reserved fields, salt size, inode data size, and signature bounds. `fsverity_create_info()` builds parameters, copies root hash, computes the descriptor digest with signature excluded, verifies optional signature, and allocates a hash-block verification bitmap for sub-page tree blocks. Open rejects writable fds and ensures info is cached, tolerating races by freeing duplicate allocations when another thread inserts first.

State and persistence: Maintains a global rhashtable keyed by inode pointer and slab-allocated `fsverity_info` objects that live until inode cleanup. It reads persistent descriptors through filesystem operations but does not write them.

Dependencies and integration points: Depends on filesystem `get_verity_descriptor`, inode `S_VERITY` policy in public wrappers, rhashtable, slab usercopy cache, hash helpers, signature verification, and page-size/tree-size assumptions used by verify code.

Risks and test signals: Risks include descriptor size confusion, inode size mismatch, duplicate info races, bitmap sizing overflow, salt-state leaks, writable-open bypass, and stale rhashtable entries on inode eviction. Test concurrent opens, eviction cleanup, corrupted descriptors, signature-required files, block sizes smaller than page size, huge files near tree limits, and writable open attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/open.c -->
