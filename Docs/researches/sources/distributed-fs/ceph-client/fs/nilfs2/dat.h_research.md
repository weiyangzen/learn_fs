# sources/distributed-fs/ceph-client/fs/nilfs2/dat.h

## Purpose
`dat.h` declares the disk address translation API for virtual block number allocation, lifetime management, block translation, GC movement, and metadata inode loading.

## Important APIs
- Translation and info: `nilfs_dat_translate()` and `nilfs_dat_get_vinfo()`.
- Allocation lifecycle: `prepare_alloc`, `commit_alloc`, and `abort_alloc`.
- Write lifecycle: `prepare_start`, `commit_start`, `prepare_end`, `commit_end`, and `abort_end`.
- Copy-on-write update lifecycle: `prepare_update`, `commit_update`, and `abort_update`.
- Maintenance: `nilfs_dat_mark_dirty()`, `nilfs_dat_freev()`, `nilfs_dat_move()`, and `nilfs_dat_read()`.

## Control flow and persistence behavior
The API is deliberately transactional. Callers prepare palloc/entry resources, then either commit to dirty metadata buffers or abort to release prepared state. The header separates allocation, start, end, update, and move because B-tree/direct propagation, segment assignment, and cleaner operations need different phases of the same DAT entry lifecycle.

## Dependencies and integration points
It forward-declares `struct nilfs_palloc_req` and includes VFS and on-disk NILFS types. It is consumed by block-map implementations, node cache reads, GC cache reads, ioctl cleaner preparation, and mount-time DAT loading.

## Risks and test signals
Callers must match every prepare with the correct commit or abort and must pass `dead` correctly when ending lifetimes. Tests should verify mixed direct/B-tree callers, GC movement, and error unwinding.
