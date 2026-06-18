# sources/distributed-fs/ceph-client/fs/ocfs2/mmap.c

## Purpose
`mmap.c` implements OCFS2 memory-mapped file fault handling, especially write faults in a clustered filesystem where page allocation, inode size, and remote truncation must be serialized with cluster locks.

## Important APIs, types, and functions
- `ocfs2_mmap_prepare()` installs OCFS2 VM operations and updates atime under an inode lock.
- `ocfs2_fault()` wraps `filemap_fault()` with OCFS2 signal blocking to avoid interruption issues during cluster lock paths.
- `ocfs2_page_mkwrite()` handles write faults by taking pagefault write accounting, blocking signals, taking the inode metadata lock, and taking `ip_alloc_sem`.
- `__ocfs2_page_mkwrite()` validates folio mapping/uptodate/size, calls `ocfs2_write_begin_nolock()` with `OCFS2_WRITE_MMAP`, and completes with `ocfs2_write_end_nolock()`.
- `ocfs2_file_vm_ops` installs `.fault` and `.page_mkwrite`.

## Control flow
On mmap setup, OCFS2 takes an atime-aware inode lock and assigns VM ops. Read faults simply call the generic filemap fault under blocked signals. Write faults start pagefault accounting, block signals, lock the inode exclusively, take the allocation semaphore, and run the no-lock write-begin/end path to allocate and prepare the page range. If the folio no longer belongs to the mapping, is not uptodate, or lies beyond current size, the function returns `VM_FAULT_NOPAGE` so the VM can retry.

## State and persistence behavior
Mmap write faults can allocate clusters and dirty file metadata through the write-begin/end implementation. The local file's page cache and disk extents become persistent through the normal OCFS2 write and journal paths. The code itself mainly coordinates runtime locks and fault return values.

## Dependencies and integration points
It integrates Linux VM fault operations, OCFS2 inode locks, allocation semaphore, write path helpers from `aops.h`, atime locking, superblock pagefault accounting, and OCFS2 tracepoints.

## Risks and edge cases
- Remote truncation and data-lock downconversion can detach or invalidate folios; the mapping and uptodate checks are required before allocation.
- Last-page writes adjust length to `i_size`, avoiding allocation beyond EOF.
- Signal blocking is used because cluster lock paths may otherwise return restart errors into VM fault handling.
- `ocfs2_mmap_prepare()` returns success even if the atime lock failed after logging, because it always sets VM ops and returns 0 in the current implementation.

## Test signals
Test mmap read/write faults, write faults racing with truncate from another node, writes to the last partial page, ENOSPC propagation through `vmf_error()`, local pagecache invalidation retry paths, atime update locking, and pagefault behavior under signal delivery.
