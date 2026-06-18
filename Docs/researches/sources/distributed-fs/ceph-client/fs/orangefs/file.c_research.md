## sources/distributed-fs/ceph-client/fs/orangefs/file.c

### Purpose
This file implements OrangeFS regular file operations and the synchronous direct-I/O bridge to the userspace daemon.

### Important APIs, types, and functions
- `flush_racache()` sends `ORANGEFS_VFS_OP_RA_FLUSH`.
- `wait_for_direct_io()` is the central I/O operation: allocates a bufmap slot, copies write data into shared memory, services the op, handles daemon purge/retry, copies read data out, and returns amount complete.
- `orangefs_revalidate_mapping()` invalidates stale page cache under a bitlock and timeout.
- `orangefs_file_read_iter()`, `orangefs_file_splice_read()`, and `orangefs_file_write_iter()` wrap generic file I/O with OrangeFS cache revalidation and counters.
- `orangefs_fault()` and `orangefs_file_mmap_prepare()` handle mmap faults and VMA setup.
- `orangefs_fsync()`, `orangefs_file_llseek()`, `orangefs_lock()`, and `orangefs_flush()` implement fsync, size-aware seek, local locking, and close-time writeback flush.
- `orangefs_file_operations` exports the file operation vector.

### Control flow
Buffered reads take `i_rwsem`, revalidate page cache, then call generic read/splice. Writes revalidate when writing beyond EOF, then use generic write, which reaches OrangeFS address-space operations in `inode.c`. Direct I/O and writeback call `wait_for_direct_io()`: allocate op and shared slot, populate credentials and permission workaround uid, copy data for writes, call `service_operation()`, retry with a new slot if the daemon purged the op, copy read data from shared memory, release slot and op. Fsync first writes dirty page cache then sends `ORANGEFS_VFS_OP_FSYNC`.

### State and persistence behavior
Persistent data transfer is performed by the userspace daemon/server after upcall service. Local state includes page-cache mapping timeout, bitlock serialization, read/write stats, bufmap slot usage, and per-file local locks when mounted with `local_lock`.

### Dependencies and integration points
Depends on bufmap APIs, operation service/waitqueue, OrangeFS inode private data, sysfs timeout globals, generic filemap helpers, mmap VMA operations, POSIX locks, and feature flags from superblock setup. It is installed on regular files by `orangefs_init_iops()`.

### Risks
The I/O path straddles page cache, shared memory, and a userspace daemon. Interrupt handling must avoid reporting `EINTR` after writes that may already have reached the daemon. Purged retry must revert iov_iter state for writes before recopying. The uid override to 0 for already-opened files is a semantic workaround and should be scrutinized in permission/security tests. Cache invalidation uses a custom bitlock and timeout, which can affect coherency and latency.

### Test signals
Run buffered and direct read/write tests, mmap read/write faults, write beyond EOF, fsync durability, close flush behavior, daemon restart during I/O, large I/O spanning bufmap slots, interrupted I/O, local_lock on/off behavior, and cache timeout coherency across clients.
