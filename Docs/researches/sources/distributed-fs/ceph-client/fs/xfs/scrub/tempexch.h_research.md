<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempexch.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/tempexch.h

Purpose: declares the small repair-only interface for atomically exchanging a rebuilt temporary file's fork mappings with the metadata file being repaired.

Important APIs and types: `struct xrep_tempexch` wraps `struct xfs_exchmaps_req`, the exchange request consumed by XFS exchmaps code. `xrep_tempexch_trans_reserve()` prepares/reserves an existing transaction when ILOCKs cannot be dropped. `xrep_tempexch_trans_alloc()` creates a fresh transaction and locks/joins both files for a whole-fork exchange. `xrep_tempexch_contents()` performs the mapping exchange and finishes deferred work.

Control flow: repair modules include this header when they stage rebuilt file-based metadata in a temp inode. If they already hold a dirty transaction and both ILOCKs, they call the reserve variant; otherwise they let the alloc variant estimate resources, allocate a transaction, and lock both inodes. The final contents call swaps mappings and, when requested, file sizes.

State and persistence: the header declares persistent repair operations but only under `CONFIG_XFS_ONLINE_REPAIR`. When repair is disabled the interface is absent, forcing callers to compile only in repair-enabled paths. Dependencies include `struct xfs_scrub`, exchmaps request definitions, fork identifiers, file offsets, and block counts.

Risks and test signals: correctness depends on callers satisfying lock/transaction preconditions from `tempfile.c`. Header drift with the implementation can break repair modules at build time. Tests should compile repair-enabled and repair-disabled configs and run repairs that use both existing-transaction reservation and fresh transaction allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/tempexch.h -->
