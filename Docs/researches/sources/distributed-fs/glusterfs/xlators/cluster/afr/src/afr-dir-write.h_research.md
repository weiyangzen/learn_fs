# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-dir-write.h

## Purpose
Declares AFR directory write-side entry points for namespace-mutating FOPs.

## Important APIs, types, and functions
Exports `afr_create()`, `afr_mknod()`, `afr_mkdir()`, `afr_unlink()`, `afr_rmdir()`, `afr_link()`, `afr_rename()`, and `afr_symlink()`. Signatures mirror Gluster fops, including umask, flags, `fd_t`, source/destination locs, linkpath, and xdata.

## Control flow
Callers enter these functions through the AFR fops table. Each implementation creates an AFR transaction frame, records operation parameters in `afr_local_t`, and delegates concurrency, locking, and changelog handling to common transaction code.

## State and persistence behavior
No state is declared here, but these prototypes expose operations that mutate namespace state and AFR pending changelog metadata on child bricks.

## Dependencies and integration points
Depends on Gluster core types and is coupled to `afr-dir-write.c` definitions and the translator fops registration code.

## Risks and test signals
Signature mismatch is the primary header-level risk. Build checks should catch drift, while integration tests should verify each declared operation appears in the AFR fops vector and preserves expected unwind argument order.
