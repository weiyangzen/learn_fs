# sources/distributed-fs/ceph-client/fs/coda/file.c

## Purpose
`file.c` implements Coda regular-file operations by forwarding IO to a Venus-provided container file while notifying Venus of access intents, managing mmap redirection, and syncing local/container state.

## Important APIs, Types, And Functions
Important functions are `coda_file_read_iter()`, `coda_file_write_iter()`, `coda_file_splice_read()`, `coda_file_mmap()`, `coda_open()`, `coda_release()`, and `coda_fsync()`. `struct coda_vm_ops` wraps host vm operations with Coda lifetime tracking. The exported table is `coda_file_operations`.

## Control Flow
Open asks Venus for a container file and stores it in `struct coda_file_info`. Reads, writes, splice reads, and mmap send access-intent begin/finish upcalls when supported, then call VFS helpers on the container file. Writes update Coda inode size, blocks, mtime, and ctime from the host inode. Mmap swaps the VMA file to the host file, redirects open/close vm operations, and tracks cnode/file map counts. Release calls `venus_close()`, unwinds mmap mapping state, fputs the container, and frees private data. Fsync flushes local mapping, fsyncs the host file, then asks Venus to fsync for full-data sync.

## State, Persistence, And Dependencies
Open-file state is in `struct coda_file_info`; mmap state is split between inode/file map counts and allocated `struct coda_vm_ops`. Persistent file data is handled by the container file and Venus cache/server. Dependencies include VFS iter/splice/mmap/fsync helpers, Venus open/close/access_intent/fsync, and cnode locks.

## Integration Points
Directory operations reuse open/release/fsync for directories. Cnode state tracks mapping redirection, while psdev/upcall code implements the Venus side of file operations.

## Risks
Risks include access-intent begin/finish imbalance, mmap lifetime/refcount errors, mapping mismatch when Venus changes container files, write metadata drift, and ignored errors from `release()`.

## Test Signals
Test read/write/splice/mmap/fsync/open/release, unsupported access-intent fallback, mmap then release, concurrent mmaps with container changes, write size updates, daemon failures, and lock/refcount validation.
