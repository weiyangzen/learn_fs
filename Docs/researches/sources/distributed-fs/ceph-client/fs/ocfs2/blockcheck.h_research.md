# sources/distributed-fs/ceph-client/fs/ocfs2/blockcheck.h

## Purpose
`blockcheck.h` defines the public OCFS2 metadata checksum/ECC interface and the statistic structure used by debugfs.

## Important APIs, types, and functions
`struct ocfs2_blockcheck_stats` stores a spinlock, check/failure/recovery counters, and the debugfs parent dentry. The header declares high-level metadata ECC wrappers, lower-level raw block and buffer-head checksum functions, debugfs install/remove functions, and Hamming encode/fix helpers for whole buffers or offset hunks.

## Control flow
Metadata code includes this header to compute check fields before write and validate them after read. The high-level wrappers choose whether to execute based on the mounted filesystem’s meta-ECC feature; the lower-level functions assume the caller has already selected the correct policy.

## State and persistence behavior
The header contributes no state, but its declarations control both persistent `ocfs2_block_check` updates and in-memory statistics. Callers must initialize the stats spinlock and hold valid buffers while validation may repair data in place.

## Dependencies and integration points
It depends on OCFS2 on-disk `struct ocfs2_block_check`, Linux buffer heads, debugfs dentries, spinlocks, and integer types. It is used by metadata I/O paths such as superblock and inode/extent validation.

## Risks and test signals
Risks are incorrect use of lower-level APIs when the feature is disabled, uninitialized stats locks, and misuse of hunk offsets in Hamming helpers. Test signals include compile coverage with and without debugfs, meta-ECC enabled/disabled mounts, and callers validating both single-buffer and multi-buffer metadata.
