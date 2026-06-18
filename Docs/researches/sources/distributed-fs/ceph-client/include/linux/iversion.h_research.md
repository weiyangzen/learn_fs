# sources/distributed-fs/ceph-client/include/linux/iversion.h

## Purpose
Defines the VFS inode change-attribute helper API around `inode->i_version`. It supports kernel-managed change counters for filesystems that set `SB_I_VERSION`, while allowing self-managed filesystems such as NFS, AFS, and Ceph to store opaque server-provided version values.

## Important APIs, Types, And Functions
Important constants are `I_VERSION_QUERIED` and `I_VERSION_INCREMENT`, which reserve the low bit as a queried flag and shift observable values above it. Raw helpers include `inode_set_iversion_raw()`, `inode_peek_iversion_raw()`, `inode_set_max_iversion_raw()`, and `inode_inc_iversion_raw()`. Kernel-managed helpers include `inode_set_iversion()`, `inode_set_iversion_queried()`, `inode_inc_iversion()`, `inode_peek_iversion()`, `inode_query_iversion()`, `inode_eq_iversion()`, and `inode_maybe_inc_iversion()`. `time_to_chattr()` synthesizes a change attribute from ctime.

## Control Flow
Setters encode the externally visible value by shifting left one bit; queried setters also set the low-bit flag. Querying is expected to mark the value so the next modification must increment. `inode_set_max_iversion_raw()` loops with `atomic64_try_cmpxchg()` and only installs a larger raw value, which is relevant for Ceph-like server versions.

## State And Persistence
The only state is the atomic64 `inode->i_version`. For persistent kernel-managed counters, filesystems should load on-disk values with `inode_set_iversion_queried()` and persist values with `inode_peek_iversion()` so storing to disk is not treated as an observer query.

## Dependencies And Integration Points
Depends on `linux/fs.h`, `struct inode`, and atomic64 operations. Integrates with NFSv4 cache coherency, knfsd, IMA, VFS write paths, and distributed filesystems that compare remote change attributes.

## Risks
Calling raw helpers on kernel-managed counters can expose the internal queried bit. Failing to set the queried flag when loading persisted counters can allow the same visible value to be reused after a crash. Equality should use the helper because raw values may differ in flag bits.

## Test Signals
Useful tests cover query-then-modify increments, repeated unqueried modifications, crash/reload behavior with queried loads, ctime fallback monotonicity, raw max update races, and Ceph/NFS paths that use self-managed opaque values.
