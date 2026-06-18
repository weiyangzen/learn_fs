<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/ishare.c -->
# sources/distributed-fs/ceph-client/fs/erofs/ishare.c

## Purpose
`ishare.c` implements experimental EROFS page-cache sharing for files with identical content fingerprints. It maps multiple real EROFS inodes to anonymous shared inodes so their cached pages can be reused.

## Important APIs, types, and functions
Important functions include `erofs_ishare_fill_inode`, `erofs_ishare_free_inode`, `erofs_real_inode`, `erofs_init_ishare`, `erofs_exit_ishare`, and file-operation wrappers for open/read/mmap/release/fadvise. It exports `erofs_ishare_fops`.

## Control flow
When a regular inode is filled, the code obtains a fingerprint from xattrs plus domain id, hashes it with xxhash, and looks up or creates an anonymous shared inode in a private EROFS anon mount. New shared inodes receive the real file's aops and size; existing ones must match aops and size. Real inodes are linked under the shared inode. Opening an ishare file creates a backing file pointing at the shared inode and original user path; reads and mmap use that realfile. `erofs_real_inode` resolves anonymous shared inodes back to any live real inode for mapping.

## State and persistence
Runtime state includes the anonymous mount, shared inode fingerprints, shared-to-real inode lists, spinlocks, backing file objects, and references. No on-disk state changes; fingerprints come from persistent xattrs.

## Dependencies and integration points
It depends on xattr fingerprint helpers, xxhash, anonymous filesystem mounts, VFS backing files, security mmap checks, page cache, and `erofs_get_aops`.

## Risks and test signals
Risks include fingerprint collision or stale xattr assumptions, size/aops mismatch, list lifetime races, O_DIRECT rejection behavior, mmap security checks, and anonymous mount teardown. Test signals include two images/files with identical fingerprints, mismatched sizes with same fingerprint, read/mmap/fadvise through ishare fops, inode eviction, concurrent opens while freeing real inodes, and feature exclusion with fscache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/erofs/ishare.c -->
