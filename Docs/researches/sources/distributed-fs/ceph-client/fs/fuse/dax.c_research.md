# sources/distributed-fs/ceph-client/fs/fuse/dax.c

## Purpose
`dax.c` implements FUSE/virtio-fs DAX mapping management. It maps file offsets to windows in a DAX device, serves read/write/mmap through iomap, and reclaims DAX windows by asking the userspace daemon to set up or remove mappings.

## Important APIs, Types, and Functions
- `struct fuse_dax_mapping` describes one DAX window range, its inode/file interval, writability, and in-use refcount.
- `struct fuse_inode_dax` holds an interval tree and semaphore per inode.
- `struct fuse_conn_dax` holds the DAX device, free/busy mapping lists, reclaim work, and waitqueue.
- `fuse_setup_one_mapping()` sends `FUSE_SETUPMAPPING`.
- `dmap_removemapping_list()`/`dmap_removemapping_one()` send `FUSE_REMOVEMAPPING`.
- `fuse_iomap_begin()`/`fuse_iomap_end()` implement iomap lookup/setup/refcount release.
- `fuse_dax_read_iter()`, `fuse_dax_write_iter()`, and `fuse_dax_mmap()` are data path entry points.
- `fuse_dax_conn_alloc/free()`, `fuse_dax_inode_alloc/init/cleanup()`, `fuse_dax_cancel_work()`, and `fuse_dax_check_alignment()` manage lifecycle.

## Control Flow
Connection allocation enumerates the DAX device size via `dax_direct_access()`, divides it into 2 MiB windows, and seeds a free list of `fuse_dax_mapping` objects. Iomap begin looks for an interval covering the requested file index; if found it fills an iomap and increments the mapping refcount, upgrading read-only mappings to writable by sending `FUSE_SETUPMAPPING` when necessary. If no mapping exists, it allocates a free range or reclaims one inline, sends `FUSE_SETUPMAPPING`, inserts the mapping into the inode interval tree and busy list, then returns an iomap. Iomap end decrements the temporary ref.

Reads and non-extending writes call `dax_iomap_rw()`. Extending writes fall back to FUSE direct I/O so data write and size growth are not split across DAX mapping semantics. Faults call `dax_iomap_fault()` under the mapping invalidate lock; if no free mapping is available in fault context, `-EAGAIN` causes wait/retry. Reclaim selects idle busy ranges, grabs the inode, breaks DAX layouts, writes back and invalidates page cache, removes the interval, sends `FUSE_REMOVEMAPPING`, and returns the range to the free list.

## State and Persistence
Mapping state is in memory only. The userspace daemon maintains the actual mapping behind `FUSE_SETUPMAPPING`/`FUSE_REMOVEMAPPING`; the kernel tracks file-index intervals and DAX window offsets. `S_DAX` and address-space ops are set per inode when connection mode and `FUSE_ATTR_DAX` allow it. Delayed reclaim is scheduled when free ranges drop below a 20 percent threshold.

## Dependencies and Integration Points
The file depends on virtio-fs DAX negotiation, `linux/dax.h`, iomap, interval trees, page-cache invalidation, inode eviction, FUSE request helpers, and daemon support for setup/removal opcodes. It is selected by `CONFIG_FUSE_DAX`.

## Risks
Lock ordering is delicate: reclaim takes mapping invalidate lock and inode DAX semaphore to serialize against faults/read/write, while fault context cannot do inline reclaim. Refcounts must prevent reclaim of mappings in active iomap use. Failed `FUSE_REMOVEMAPPING` is tolerated on disconnected connections but otherwise warns. Extending writes intentionally bypass DAX; missing this fallback can expose non-atomic size/data updates. Alignment negotiation must reject daemon map alignments larger than the fixed 2 MiB range size.

## Test Signals
Test DAX read/write/mmap faults, write upgrades, extending writes fallback, truncate/evict cleanup, mapping exhaustion and reclaim, memory pressure, daemon disconnect during removemapping, alignment negotiation, inode-mode toggling of `FUSE_ATTR_DAX`, and lockdep with concurrent mmap faults and reclaim.
