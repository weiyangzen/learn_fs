# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/afr-inode-read.h

## Purpose
Declares AFR inode read-side FOP entry points and the quota-size helper used by read response aggregation.

## Important APIs, types, and functions
Exports `afr_access()`, `afr_stat()`, `afr_fstat()`, `afr_readlink()`, `afr_readv()`, `afr_getxattr()`, `afr_fgetxattr()`, `afr_seek()`, and `afr_handle_quota_size()`. The declarations separate path-based and fd-based variants and preserve Gluster fop callback argument shapes.

## Control flow
The translator fops table routes inode read operations through these functions. Implementations initialize AFR frame state and commonly delegate child selection and retry behavior to `afr_read_txn()`.

## State and persistence behavior
The header declares no storage. Its functions mostly expose transient read behavior, except special xattr commands in the implementation can initiate heal-related side effects.

## Dependencies and integration points
Depends on AFR types such as `afr_local_t`, Gluster core types, `gf_seek_what_t`, and dict/xdata APIs. It is coupled to read transaction and self-heal implementation files.

## Risks and test signals
Header risks are prototype drift and missing registration. Compile coverage plus smoke tests for all inode read fops, including `seek` and quota xattr paths, are the relevant signals.
