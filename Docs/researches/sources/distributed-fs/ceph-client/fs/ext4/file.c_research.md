# sources/distributed-fs/ceph-client/fs/ext4/file.c

## Purpose
`file.c` implements ext4 regular-file VFS operations: read, write, splice read/write, mmap preparation, DAX faults, llseek, open/release, direct-I/O policy, atomic-write validation, and operation tables. It is the main bridge between generic VFS file methods and ext4-specific journaling, DAX, iomap, delayed allocation, fscrypt, fsverity, quota, and writeback rules.

## Important APIs, types, and functions
The exported operation tables are `ext4_file_operations` and `ext4_file_inode_operations`; `ext4_llseek` is a visible helper. Key internal functions are `ext4_should_use_dio`, `ext4_dio_read_iter`, `ext4_dax_read_iter`, `ext4_file_read_iter`, `ext4_file_splice_read`, `ext4_release_file`, `ext4_unaligned_io`, `ext4_extending_io`, `ext4_overwrite_io`, `ext4_generic_write_checks`, `ext4_write_checks`, `ext4_buffered_write_iter`, `ext4_handle_inode_extension`, `ext4_inode_extension_cleanup`, `ext4_dio_write_end_io`, `ext4_dio_write_checks`, `ext4_dio_write_iter`, `ext4_dax_write_iter`, `ext4_file_write_iter`, `ext4_dax_huge_fault`, `ext4_file_mmap_prepare`, `ext4_sample_last_mounted`, and `ext4_file_open`.

## Control flow
Reads first reject forced shutdown and zero-length atime-only work. DAX reads take the DAX iomap path under the shared inode lock and fall back if DAX changed. Direct reads use `iomap_dio_rw` only when `ext4_dio_alignment()` says ext4 feature state allows direct I/O; otherwise they clear `IOCB_DIRECT` and use generic buffered reads.

Writes reject emergency state, route DAX to `dax_iomap_rw`, validate atomic-write sizes against superblock AWU bounds, and choose direct or buffered I/O from `IOCB_DIRECT`. Buffered writes take the exclusive inode lock, run generic and ext4-specific checks, zero a partial block when writing beyond EOF, call `generic_perform_write`, and then `generic_write_sync`. Direct writes start optimistically with a shared lock for likely overwrites, upgrade to exclusive locking for security changes, extending writes, non-overwrites, and dangerous unaligned unwritten writes, and may force synchronous DIO to serialize partial-block zeroing. Extending DIO/DAX adds the inode to the orphan list, updates size in `ext4_handle_inode_extension`, and cleans up with truncate/orphan removal on failure or race.

`ext4_file_open` samples the mount path into the superblock once, opens fscrypt and fsverity state, attaches a `jbd2_inode` for writers, advertises atomic-write capability, and sets `FMODE_NOWAIT` and `FMODE_CAN_ODIRECT`. `ext4_release_file` drains delayed allocation on close and discards preallocations for the last writer.

## State and persistence behavior
Persistent changes include file size, `i_disksize`, orphan-list membership, inode timestamps/security changes, superblock `s_last_mounted`, and extent conversion from unwritten to written after DIO. Orphan handling protects extending DIO/DAX writes from crashes between block allocation and size update. DAX page faults start journal handles only for shared write faults and finish synchronous faults with `dax_finish_sync_fault`.

## Dependencies and integration points
This file depends on VFS iter I/O, iomap, DAX, page-fault machinery, fscrypt, fsverity, quota, xattrs/ACLs, ext4 journaling, delayed allocation, extent mapping, inode state flags, block zeroing, file leases, and traceable writeback errors. `fsync` is delegated to `ext4_sync_file`.

## Risks and test signals
Risks include direct-I/O fallback semantic regressions, unaligned unwritten DIO corruption, orphan cleanup errors after extending writes, atomic-write flag misuse, DAX versus non-DAX races, mmap support mismatches for synchronous mappings, stale page-cache contents after partial DIO fallback, and incorrect maxbytes handling for non-extent files. Test signals include buffered/direct/DAX reads and writes, NOWAIT lock failures, unaligned DIO to holes and unwritten extents, extending DIO with injected ENOSPC/EIO, atomic-write min/max validation, DAX shared and COW faults, fscrypt/fsverity opens, read-only and forced-shutdown behavior, SEEK_HOLE/SEEK_DATA, last-writer preallocation discard, and mount-path sampling.
