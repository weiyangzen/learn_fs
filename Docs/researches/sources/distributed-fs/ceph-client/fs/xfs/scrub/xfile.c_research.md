<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.c -->
## sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.c

Purpose: Implements the online scrub "xfile" abstraction, a private unlinked shmem file used as pageable temporary memory for scrub/repair staging data. It lets scrub code store large indexed arrays without requiring all data to remain resident, while avoiding user-visible file descriptors.

Important APIs and functions: `xfile_create` allocates `struct xfile`, creates a shmem kernel file with `VMA_NORESERVE`, assigns a dedicated inode lockdep class, and forces page-cache allocations to use `GFP_KERNEL` to avoid highmem pages. `xfile_destroy` restores the inode lock class and drops the shmem file. `xfile_load` and `xfile_store` copy byte ranges between caller buffers and shmem folios, translating absent folios on reads into zeroes. `xfile_get_folio` exposes a locked folio for a single-folio object, optionally allocating it with `XFILE_ALLOC`; `xfile_put_folio` unlocks and releases it. `xfile_seek_data` delegates to `SEEK_DATA`, and `xfile_discard` truncates a shmem range.

Control flow: Create returns a single handle that callers must serialize. Load/store validate `MAX_RW_COUNT` and superblock maxbytes, enter NOFS allocation context, walk page-sized or folio-sized chunks via `shmem_get_folio`, check mapping writeback errors, copy data, and release folios. Store grows `i_size` before SGP_CACHE allocation and marks written folios dirty. Direct folio access similarly validates bounds, gets a folio in SGP_READ or SGP_CACHE mode, rejects cross-folio spans, checks writeback errors, and marks allocated folios dirty to keep backing memory from disappearing after the last reference.

State and persistence: Data lives in a tmpfs/shmem page cache backing file, not in XFS metadata or user-visible namespace. It can be reclaimed/swapped by the VM and is destroyed by `fput` in `xfile_destroy`. Dirty folios are used to pin memory-object contents in cache semantics, not to persist filesystem state. `xfile_bytes` in the header observes backing blocks through `i_blocks`.

Dependencies and integration: Depends on Linux shmem APIs, folios, VFS file/inode helpers, NOFS context, scrub tracepoints, and scrub GFP policy. It is used by online scrub support such as xfarray-style temporary indexes, where XFS repair must avoid filesystem recursion while allocating memory.

Risks: Callers must provide all synchronization; there are no VFS inode/freezer locks for normal xfile access. Any short read/write, shmem allocation failure, writeback error, or oversize access is collapsed to `-ENOMEM` or `-EIO`, so consumers should treat failures as fatal memory staging failures. `xfile_discard` assumes nonzero count because it subtracts one from `pos + count`.

Test signals: Exercise create/destroy, sparse reads returning zeroes, writes crossing folio boundaries, allocation failure paths, writeback error propagation, single-folio object access, discard plus `seek_data`, and lockdep noise around private shmem inode locking during scrub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/xfile.c -->
