# sources/distributed-fs/ceph-client/fs/ceph/io.c

## Purpose
`io.c` provides the CephFS client helpers that serialize buffered I/O and direct I/O against each other. It uses `inode->i_rwsem` and the Ceph inode `CEPH_I_ODIRECT` flag to switch an inode between buffered and direct I/O modes without allowing stale page-cache data or overlapping mode transitions.

## Important APIs, types, and functions
The exported API is `ceph_start_io_read`, `ceph_end_io_read`, `ceph_start_io_write`, `ceph_end_io_write`, `ceph_start_io_direct`, and `ceph_end_io_direct`. Internal helpers are `ceph_block_o_direct`, which clears direct-I/O mode and waits for outstanding direct I/O, and `ceph_block_buffered`, which sets direct-I/O mode and flushes buffered dirty data. State is held in `struct ceph_inode_info::i_ceph_flags`, specifically `CEPH_I_ODIRECT_BIT`, protected by `i_ceph_lock` and ordered with atomic memory barriers.

## Control flow
Buffered reads optimistically take `i_rwsem` for read and check whether direct mode is already clear. If direct mode is set, they drop the read lock, take the write lock, clear `CEPH_I_ODIRECT`, wait for in-flight DIO via `inode_dio_wait`, downgrade to a read lock, and proceed. Buffered writes take the write lock up front and force direct mode off.

Direct I/O mirrors the read path. `ceph_start_io_direct` optimistically takes the read lock and returns immediately if `CEPH_I_ODIRECT` is already set. If not, it upgrades through a write lock, sets direct mode, flushes dirty buffered pages with `filemap_write_and_wait`, downgrades to a read lock, and lets parallel direct I/O proceed. End helpers release the corresponding read or write lock.

## State and persistence behavior
The mode bit is purely in-memory and is not persisted to the MDS. It is a local coherency guard that allows multiple operations of the same mode to run concurrently under shared `i_rwsem` while serializing mode transitions under the write side. The helpers also synchronize with VFS direct I/O accounting and page-cache writeback state.

## Dependencies and integration points
The implementation depends on Linux inode rwsems, spinlocks, memory-barrier primitives, `inode_dio_wait`, and `filemap_write_and_wait`. Ceph file read/write paths call these helpers before buffered or direct read/write operations; `file.c` contains the main call sites around sync/direct read and write paths.

## Risks
The key risks are missed mode-bit ordering, failure to wait for outstanding direct I/O before buffered access, failure to flush buffered data before direct I/O, lock leaks on error paths at call sites, and starvation under frequent direct/buffered mode switching. The `FIXME` about `unmap_mapping_range` signals that mappings may need stronger handling if direct mode must exclude already-mapped cached pages.

## Test signals
Exercise mixed buffered and O_DIRECT reads/writes from multiple threads, signal interruption while acquiring `i_rwsem`, direct writes after dirty buffered writes, buffered reads after in-flight direct writes, mmap plus direct I/O workloads, and tracing that every successful start helper is matched by the right end helper.
