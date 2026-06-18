<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/read_metadata.c -->
# sources/distributed-fs/ceph-client/fs/verity/read_metadata.c

Purpose: Implements `FS_IOC_READ_VERITY_METADATA`, allowing userspace to read a verity file’s Merkle tree, descriptor without builtin signature, or builtin signature.

Important APIs, types, and functions: Defines `fsverity_read_merkle_tree()`, `fsverity_read_buffer()`, `fsverity_read_descriptor()`, `fsverity_read_signature()`, and exported `fsverity_ioctl_read_metadata()`.

Control flow: The ioctl requires cached `fsverity_info`, copies and validates the read request, rejects overflowed offset+length, clamps length to `INT_MAX`, and dispatches by metadata type. Merkle tree reads clamp to tree size, optionally trigger filesystem readahead under shared invalidate lock, iterate pages via `read_merkle_tree_page`, map pages, and copy byte ranges to userspace while checking fatal signals. Descriptor reads reload and validate the descriptor, zero `sig_size`, and copies only the fixed descriptor portion. Signature reads reload the descriptor and returns `-ENODATA` when no builtin signature exists.

State and persistence: Read-only access to persistent verity metadata through filesystem operations and pagecache. No state is modified except normal cache/readahead effects.

Dependencies and integration points: Depends on `fsverity_get_info()`, `fsverity_get_descriptor()`, filesystem `read_merkle_tree_page` and optional `readahead_merkle_tree`, user copy helpers, highmem mapping, and backing-dev/pagecache synchronization.

Risks and test signals: Risks include leaking builtin signatures through descriptor reads, offset overflow, partial copy semantics, signal interruption, wrong tree-size clamping, and filesystem page read errors. Test all metadata types, offsets at and past EOF, short buffers, missing signatures, corrupted descriptors, readahead-enabled filesystems, and user fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/verity/read_metadata.c -->
