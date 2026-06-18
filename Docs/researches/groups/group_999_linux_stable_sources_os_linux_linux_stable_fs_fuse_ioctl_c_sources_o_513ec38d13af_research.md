# Group Research: group_999_linux_stable_sources_os_linux_linux_stable_fs_fuse_ioctl_c_sources_o_513ec38d13af

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`, which is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/ioctl.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/ioctl.c

## Purpose
Implements FUSE ioctl handling, including CUSE/FUSE compatibility details, unrestricted ioctl retry/deep-copy behavior, fs-verity ioctl sizing, compat ioctl dispatch, and private ioctl helpers used for file attribute get/set.

## Key Interfaces
- `fuse_do_ioctl()` is the core ioctl request loop.
- `fuse_ioctl_common()`, `fuse_file_ioctl()`, and `fuse_file_compat_ioctl()` are VFS-facing dispatch wrappers.
- `fuse_fileattr_get()` and `fuse_fileattr_set()` tunnel Linux file attribute ioctls through FUSE.
- `fuse_priv_ioctl()` sends kernel-originated ioctl requests on a temporary FUSE file handle.

## Control Flow And Behavior
Restricted ioctls derive in/out iovecs from `_IOC_*` command encoding; unrestricted ioctls allow the server to return `FUSE_IOCTL_RETRY` with requested input/output iovecs. The kernel copies user memory into folios, sends `FUSE_IOCTL`, copies server output back to user iovecs, and validates retry iovecs for count, size, overflow, and compat pointer representation.

Older protocol minors use ABI-sensitive iovec decoding for 32-bit CUSE servers. `FS_IOC_MEASURE_VERITY` and `FS_IOC_ENABLE_VERITY` receive special setup so digest, salt, and signature buffer sizes are known.

## Dependencies
Uses FUSE request helpers, folio/page transfer helpers, iov iterators, compat ABI helpers, file attribute APIs, fs-verity structures, and private FUSE open/release helpers.

## Risks And Invariants
Server-provided retry vectors are untrusted and must stay within `fc->max_pages`. Restricted mode must reject retries. `-ENOSYS` is translated to `-ENOTTY` for ioctl semantics. Partial output larger than the declared output size is treated as protocol error.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/iomode.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/iomode.c

## Purpose
Coordinates mutually exclusive FUSE inode I/O modes: cached page-cache use, uncached direct/passthrough use, and backing-file passthrough. It prevents unsafe mixing of cached and uncached access.

## Key Interfaces
- `fuse_file_cached_io_open()` enters cached I/O mode.
- `fuse_inode_uncached_io_start()` and `fuse_inode_uncached_io_end()` manage uncached mode references.
- `fuse_file_io_open()` validates server open flags and selects cached, direct, or passthrough mode.
- `fuse_file_io_release()` drops the per-file mode reference.

## Control Flow And Behavior
Cached opens increment `fi->iocachectr` and set `FUSE_I_CACHE_IO_MODE`; uncached users decrement the same counter. Negative values represent active uncached users, positive values cached users. Cached opens wait for parallel direct I/O writers to drain unless the inode has entered passthrough mode.

Passthrough opens require `CONFIG_FUSE_PASSTHROUGH`, connection passthrough support, and a restricted set of open flags. A backing file ID is resolved and installed, then uncached mode is acquired so the FUSE page cache cannot coexist with passthrough.

## Dependencies
Uses `struct fuse_inode`, `struct fuse_file`, backing-file lookup/release from FUSE passthrough/backing code, inode spin locks, wait queues, and FUSE open flags.

## Risks And Invariants
A server must consistently use `FOPEN_PASSTHROUGH` once an inode has a backing file. `FOPEN_PARALLEL_DIRECT_WRITES` is only meaningful with `FOPEN_DIRECT_IO`. Conflicting cached and passthrough/uncached users fail with user-visible `EIO` after logging a debug message.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/iomode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/passthrough.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/passthrough.c

## Purpose
Implements FUSE passthrough operations that route reads, writes, splice, and mmap to a kernel backing file while preserving FUSE inode state updates.

## Key Interfaces
- `fuse_passthrough_read_iter()` and `fuse_passthrough_write_iter()` delegate buffered/direct file I/O.
- `fuse_passthrough_splice_read()` and `fuse_passthrough_splice_write()` delegate splice paths.
- `fuse_passthrough_mmap()` maps the backing file.
- `fuse_passthrough_open()` opens a per-FUSE-file backing file.
- `fuse_passthrough_release()` drops the opened backing file and credentials.

## Control Flow And Behavior
Operations fetch `ff->passthrough` and call backing-file helpers with a `backing_file_ctx` carrying the FUSE daemon credentials. Reads and mmap invalidate/update atime through `fuse_file_accessed()`. Writes and splice writes hold the FUSE inode lock and update FUSE write attributes through `fuse_passthrough_end_write()`.

## Dependencies
Uses Linux backing-file helpers, splice helpers, FUSE file private data, FUSE backing ID lookup, credentials, and inode attribute update helpers.

## Risks And Invariants
`backing_id` must be positive and resolvable. Each FUSE file gets its own opened backing file so path/accounting context is per open. Release must drop both file and credential references.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/passthrough.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/readdir.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/readdir.c

## Purpose
Implements FUSE directory iteration, READDIRPLUS inode linking, and optional directory entry caching for `FOPEN_CACHE_DIR`.

## Key Interfaces
- `fuse_readdir()` is the VFS readdir entry point.
- `fuse_readdir_uncached()` sends `FUSE_READDIR` or `FUSE_READDIRPLUS`.
- `fuse_readdir_cached()` serves entries from the per-inode directory cache.
- `parse_dirfile()` and `parse_dirplusfile()` validate and emit server entries.
- `fuse_direntplus_link()` instantiates or refreshes dentries/inodes from READDIRPLUS responses.

## Control Flow And Behavior
READDIRPLUS is selected when enabled, explicitly advised, automatic at offset zero, or not in auto mode. Uncached reads allocate a buffer, lock the inode around the FUSE request, parse entries, and optionally append them to the directory cache. READDIRPLUS links valid non-dot entries, handles stale dentries, increments lookup counts, updates attributes and entry timeouts, and forces FORGET if linking fails after the server returned a lookup reference.

The cached path validates mtime and i_version at directory offset zero, tracks per-file cache stream position/version, locks cache pages while parsing, and falls back to uncached reads when cache entries are missing or invalidated.

## Dependencies
Uses FUSE read argument filling, FUSE inode/dentry helpers, page cache APIs, inode versioning, ACL cache invalidation, and dir_context emission.

## Risks And Invariants
Dirents must have nonzero valid names, no slash, and record lengths within the reply/cache page. Cache append only succeeds at the current cache end and version. READDIRPLUS must balance lookup references by linking or sending forced FORGET.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/sysctl.c

## Purpose
Registers `/proc/sys/fs/fuse` tunables controlling FUSE request/page limits and request timeout defaults.

## Key Interfaces
- `fuse_sysctl_register()` registers the sysctl table.
- `fuse_sysctl_unregister()` unregisters it.
- Exposed tunables: `max_pages_limit`, `default_request_timeout`, and `max_request_timeout`.

## Design Notes
`max_pages_limit` is bounded by the u16 `fuse_init_out.max_pages` protocol field. Timeout values are also capped at `65535`, matching u16 request timeout fields.

## Dependencies
Uses Linux sysctl table registration and global FUSE tunable variables declared elsewhere.

## Risks And Invariants
The table header is stored globally and cleared on unregister. Bounds prevent users from configuring values the protocol cannot represent.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/trace.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/trace.c

## Purpose
Materializes FUSE tracepoints by defining `CREATE_TRACE_POINTS` and including `fuse_trace.h`.

## Key Interfaces
No runtime functions are defined here; this file exists to instantiate trace event definitions.

## Dependencies
Includes FUSE internal headers and `fuse_trace.h`, plus paging support needed by trace definitions.

## Risks And Invariants
This must be compiled exactly once with `CREATE_TRACE_POINTS` for the tracepoint definitions to link correctly.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/virtio_fs.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/virtio_fs.c

## Purpose
Implements the virtio-fs transport and filesystem registration layer, connecting FUSE request queues to virtqueues, exposing virtiofs instances in sysfs, handling mount-by-tag lookup, and supporting optional DAX shared memory windows.

## Key Interfaces
- Virtio driver callbacks: `virtio_fs_probe()`, `virtio_fs_remove()`, and suspend stubs.
- Filesystem callbacks: `virtio_fs_init_fs_context()`, `virtio_fs_get_tree()`, `virtio_fs_fill_super()`, and `virtio_kill_sb()`.
- FUSE queue ops: `virtio_fs_send_req()`, `virtio_fs_send_forget()`, `virtio_fs_send_interrupt()`, and `virtio_fs_fiq_release()`.
- Virtqueue helpers: `virtio_fs_enqueue_req()`, request/hiprio done workers, dispatch workers, and queue drain/start/stop helpers.
- DAX helpers: `virtio_fs_direct_access()`, `virtio_fs_zero_page_range()`, and `virtio_fs_setup_dax()`.

## Control Flow And Behavior
Probe reads the virtio tag, sets up one hiprio queue plus request queues, maps CPUs to request queues, optionally maps a DAX cache region, marks the device ready, and adds the instance to a global tag list and sysfs. Mount lookup finds an instance by source tag, creates a FUSE connection, constrains `max_pages_limit` to virtqueue capacity, and fills the superblock.

Normal requests are assigned unique IDs, converted into scatterlists containing headers, bounced argument buffers, and optional folios, then submitted to a CPU-selected request virtqueue. Completed requests are verified for length and unique ID, copied from the bounce buffer, zero-filled if needed, and ended. Blocking completions are moved to worker context. FORGET requests use the hiprio queue and are freed on completion.

Queue removal and unmount use `virtio_fs_mutex`, connected flags, in-flight counters, completions, and work flushing to avoid racing queue teardown with request completion.

## Dependencies
Uses virtio core, FUSE connection/device internals, FUSE DAX, sysfs/kobject APIs, fs_context parsing, scatterlists, CPU affinity helpers, devm memory remapping, and iomap/page primitives.

## Risks And Invariants
The global instance list enforces unique tags. Newlines in tags are rejected for sysfs/uevent safety. Requests must not outgrow virtqueue scatter capacity, so FUSE `max_pages_limit` is clamped. Queue teardown must stop new submissions, wait for in-flight requests, flush work, then reset/delete virtqueues. Interrupt requests are intentionally unimplemented.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/virtio_fs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/fuse/xattr.c

## Purpose
Implements FUSE extended attribute operations and installs a generic xattr handler.

## Key Interfaces
- `fuse_setxattr()`, `fuse_getxattr()`, `fuse_listxattr()`, and `fuse_removexattr()` send FUSE xattr protocol requests.
- `fuse_xattr_get()` and `fuse_xattr_set()` adapt VFS xattr handler calls.
- `fuse_xattr_handlers[]` exports the handler table.

## Control Flow And Behavior
Each operation checks per-connection `no_*xattr` feature-disable bits. `GETXATTR` and `LISTXATTR` use a size-query mode when the user buffer size is zero and clamp returned sizes to Linux maxima. `LISTXATTR` validates returned lists as NUL-terminated nonempty names. `SETXATTR` can use the extended setxattr input size when negotiated.

## Dependencies
Uses FUSE simple requests, Linux xattr and POSIX ACL xattr constants, inode bad-state checks, process permission checks, and ctime updates.

## Risks And Invariants
`-ENOSYS` permanently disables the corresponding operation on the connection and returns `-EOPNOTSUPP`. Successful set/remove updates ctime. Returned xattr lists are treated as protocol data and verified.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/fuse/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/Kconfig

## Purpose
Defines kernel configuration entries for GFS2 and optional DLM-based cluster locking.

## Key Interfaces
- `CONFIG_GFS2_FS` builds GFS2 as tristate filesystem support.
- `CONFIG_GFS2_FS_LOCKING_DLM` enables multi-node DLM locking support.

## Design Notes
GFS2 selects buffer heads, POSIX ACL support, CRC32, quota control, and iomap support. The help text describes GFS2 as a cluster filesystem for shared block devices, with built-in nolock support and optional DLM for clustered deployments.

## Dependencies
DLM locking depends on GFS2, networking, configfs, sysfs, and DLM availability compatible with the GFS2 build mode.

## Risks And Invariants
Cluster use generally requires DLM; local/nolock mode is built in by default.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/Makefile

## Purpose
Builds the `gfs2.o` composite object from GFS2 subsystem source files.

## Key Interfaces
- `obj-$(CONFIG_GFS2_FS) += gfs2.o`
- `gfs2-y` lists core GFS2 implementation objects.
- `gfs2-$(CONFIG_GFS2_FS_LOCKING_DLM)` conditionally adds `lock_dlm.o`.

## Design Notes
Adds `-I$(src)` include flags and composes the filesystem from ACL, block mapping, directory, xattr, glock, log, inode, quota, rgrp, superblock, transaction, and utility modules.

## Dependencies
Driven by Kbuild and the Kconfig symbols in the same directory.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/acl.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/acl.c

## Purpose
Implements GFS2 POSIX ACL get/set operations backed by system extended attributes.

## Key Interfaces
- `gfs2_get_acl()` retrieves ACLs under the inode glock.
- `__gfs2_set_acl()` serializes ACLs and writes system xattrs.
- `gfs2_set_acl()` is the VFS set-ACL entry point with quota and mode update handling.

## Control Flow And Behavior
ACL names are mapped from access/default ACL types to POSIX ACL xattr names. Gets reject RCU mode with `-ECHILD` and acquire a shared glock when needed. Sets enforce maximum ACL entry count, acquire quota data, take the inode glock exclusive when needed, update mode for access ACLs, write the xattr, update cached ACLs, and mark mode/ctime dirty when mode changes.

## Dependencies
Uses GFS2 xattr helpers, glocks, quota accounting, POSIX ACL conversion helpers, and inode dirtying.

## Risks And Invariants
ACL xattr access requires proper glock protection outside RCU lookup. Entry count is capped by block-size-derived `GFS2_ACL_MAX_ENTRIES`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/acl.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/acl.h

## Purpose
Declares GFS2 ACL interfaces and the maximum ACL entry calculation.

## Key Interfaces
- `GFS2_ACL_MAX_ENTRIES(sdp)` computes a block-size-scaled ACL entry cap.
- Declares `gfs2_get_acl()`, `__gfs2_set_acl()`, and `gfs2_set_acl()`.

## Dependencies
Includes `incore.h` for GFS2 internal structures and relies on Linux POSIX ACL types through included headers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/aops.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/aops.c

## Purpose
Implements GFS2 address-space operations for reading, readahead, writeback, bmap, folio invalidation/release, and journaled-data writeback.

## Key Interfaces
- `gfs2_jdata_writeback()` writes journaled-data folios while an exclusive glock is held.
- `gfs2_internal_read()` reads internal GFS2 files through the page cache.
- `adjust_fs_space()` updates statfs data after filesystem growth.
- `gfs2_release_folio()` releases journal buffer metadata.
- `gfs2_set_aops()` selects normal or journaled-data address-space operations.

## Control Flow And Behavior
Normal writeback uses iomap writepages and may force AIL flushing if no pages were written. Journaled-data writeback uses a custom write-cache loop that starts transactions before locking folios, marks checked folios, adds data buffers to transactions, and flushes the log during synchronous writeback.

Reads choose between iomap reads, stuffed-file reads from the dinode, and mpage reads for journaled data. Readahead skips stuffed files, uses mpage for journaled data, and iomap for ordinary files. Invalidation/discard paths remove buffers from GFS2 journal/AIL tracking before releasing them.

## Dependencies
Uses GFS2 bmap/iomap operations, glocks, log/transaction APIs, metadata I/O, quota/statfs helpers, buffer heads, folios, mpage, and iomap writeback.

## Risks And Invariants
Journaled-data writeback must start transactions before folio locks. Stuffed file reads must synthesize zero folios for extended but not yet unstuffed cases. Buffer release cannot free buffers still dirty, pinned, referenced, or attached to an active transaction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/aops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/aops.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/aops.h

## Purpose
Declares GFS2 address-space helper functions shared with other modules.

## Key Interfaces
- `adjust_fs_space()` updates statfs after grow/rindex changes.
- `gfs2_jdata_writeback()` writes journaled-data mappings.

## Dependencies
Includes `incore.h` for GFS2 inode/superblock types.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/aops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/bmap.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/bmap.c

## Purpose
Implements GFS2 block mapping, iomap integration, stuffed-file unstuffing, extent allocation, truncate/grow/shrink, hole punching, metadata-tree deallocation, journal extent caching, and writeback iomap callbacks.

## Key Interfaces
- Mapping/allocation: `gfs2_block_map()`, `gfs2_iomap_get()`, `gfs2_iomap_alloc()`, `gfs2_get_extent()`, `gfs2_alloc_extent()`.
- Size/deallocation: `gfs2_setattr_size()`, `gfs2_truncatei_resume()`, `gfs2_file_dealloc()`, `__gfs2_punch_hole()`.
- Stuffed data: `gfs2_unstuff_dinode()`.
- Journal mapping: `gfs2_map_journal_extents()` and `gfs2_free_journal_extents()`.
- Iomap tables: `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, and `gfs2_writeback_ops`.

## Control Flow And Behavior
A compact `metapath` represents the path through dinode and indirect blocks. Lookup builds or walks metadata paths, computes holes and extents, and returns inline, mapped, or hole iomaps. Write begin allocates quota/reservation, starts transactions, unstuffs if needed, grows metadata height/depth, allocates indirect/data blocks, and marks new iomaps. Iomap end releases reservations/quotas and punches back newly allocated unwritten tail blocks after short writes.

Truncation first updates size and marks `GFS2_DIF_TRUNC_IN_PROG`, truncates page cache with special revoke handling for jdata files, walks metadata bottom-up/right-to-left to free data and indirect blocks per resource group, then clears truncate-in-progress. Hole punching zeros partial blocks, flushes page cache range, journals/truncates cached data, and frees whole-block ranges.

## Dependencies
Uses GFS2 glocks, metadata I/O, rgrp allocation/freeing, quota, statfs, transactions, ordered write tracking, log thresholds, iomap, buffer heads, and tracepoints.

## Risks And Invariants
Metadata deallocation is transaction-boundary sensitive: dinode block counts are rewritten at boundaries for crash recovery. Direct writes to holes/stuffed files return `-ENOTBLK` to fall back to buffered I/O. No open transaction may surround `gfs2_block_zero_range()` because iomap write starts its own transactions. `GFS2_DIF_TRUNC_IN_PROG` enables truncate resume after interruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/bmap.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/bmap.h

## Purpose
Declares GFS2 block mapping, iomap, truncate, allocation, journal extent, and hole punching interfaces.

## Key Interfaces
- `gfs2_write_calc_reserv()` estimates data and indirect block reservations for writes.
- Extern iomap tables: `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`.
- Declares mapping/allocation helpers, size-changing helpers, journal extent helpers, allocation-required checks, and `__gfs2_punch_hole()`.

## Design Notes
Reservation calculation accounts for direct data blocks plus indirect tree growth using the filesystem pointer geometry.

## Dependencies
Uses Linux iomap types and GFS2 inode/superblock internals.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/bmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/dentry.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/dentry.c

## Purpose
Provides GFS2 dentry operations for clustered lookup coherency, GFS2 directory hashing, and dentry deletion decisions.

## Key Interfaces
- `gfs2_drevalidate()` validates cached dentries against the parent directory.
- `gfs2_dhash()` computes on-disk-compatible name hashes.
- `gfs2_dentry_delete()` drops dentries when iopen glocks are being demoted.
- `gfs2_dops` exports the dentry operation table.

## Control Flow And Behavior
Revalidation rejects RCU mode, accepts local/nolock mode immediately, otherwise takes the parent directory glock shared when not already held and checks whether the dentry still matches directory contents. Negative dentries are valid only if lookup returns `-ENOENT`.

## Dependencies
Uses GFS2 directory search/check helpers, glocks, lock module state, inode bad-state checks, and Linux dcache operations.

## Risks And Invariants
Clustered dentry validation must not proceed in RCU mode because it may need glock acquisition. Hashing must match the GFS2 on-disk directory hash.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/dentry.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/dir.c

## Purpose
Implements GFS2 directory storage, lookup, readdir, add/delete/move operations, stuffed-to-exhash conversion, extendible hashing, leaf splitting/chaining, hash table caching, and exhash deallocation.

## Key Interfaces
- Lookup/read: `gfs2_dir_search()`, `gfs2_dir_check()`, and `gfs2_dir_read()`.
- Mutation: `gfs2_dir_add()`, `gfs2_dir_del()`, and `gfs2_dir_mvino()`.
- Allocation/deallocation: `gfs2_diradd_alloc_required()`, `gfs2_dir_get_new_buffer()`, and `gfs2_dir_exhash_dealloc()`.
- Cache helper: `gfs2_dir_hash_inval()`.

## Control Flow And Behavior
Small directories are stuffed in the dinode. Larger directories convert to exhash: the directory file becomes a hash table of leaf block pointers, while dirents live in leaf blocks that may be shared by multiple hash-table entries. Full leaves are split when possible; otherwise the hash table is doubled up to `GFS2_DIR_MAX_DEPTH`, then overflow leaves are chained.

Directory scanning validates record lengths, alignment, block type, name lengths, and sentinel rules. Readdir gathers dirents into arrays, assigns cookies based on hash or local offset, sorts where needed to keep hash collisions stable, and emits entries via `dir_emit()`. Add operations reuse saved allocation probes when possible, initialize dirents, update leaf/directory entry counts and timestamps, and increment parent nlink for subdirectories. Delete merges dirent record space or marks the first entry as empty, updates counts/timestamps, and drops parent nlink for directories.

## Dependencies
Uses GFS2 bmap allocation, metadata I/O, transactions, resource groups, quota, hash helpers, buffer heads, sort/vmalloc allocation, and inode dirtying.

## Risks And Invariants
Dirent corruption triggers consistency warnings and `-EIO`. Hash cache size must equal inode size for exhash directories. Leaf split/double operations must invalidate hash cache. Exhash deallocation rewrites hash table entries to zero and can temporarily change the inode mode to regular file on final deallocation to avoid double-free after crash.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/dir.h -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/dir.h

## Purpose
Declares GFS2 directory APIs, directory-add state, qstr helpers, and on-disk dirent initialization helpers.

## Key Interfaces
- `struct gfs2_diradd` carries allocation/addition state including block count, target dirent, buffer, and save flag.
- Declares directory search/check/add/delete/read/move, exhash deallocation, allocation-required probing, new directory buffer allocation, and hash invalidation.
- Defines `gfs2_disk_hash()`, `gfs2_str2qstr()`, and `gfs2_qstr2dirent()`.

## Dependencies
Uses Linux dcache/qstr, CRC32, GFS2 inode and dirent structures, and buffer heads.

## Risks And Invariants
`gfs2_qstr2dirent()` initializes empty inode fields and copies exactly `name->len` bytes with no terminator, matching on-disk dirent layout.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/export.c -->
# File Research: sources/os/linux/linux-stable/fs/gfs2/export.c

## Purpose
Implements NFS/exportfs file handle encoding and decoding for GFS2.

## Key Interfaces
- `gfs2_encode_fh()` encodes inode and optional parent formal inode/address pairs.
- `gfs2_fh_to_dentry()` and `gfs2_fh_to_parent()` decode file handles.
- `gfs2_get_name()` scans a parent directory to recover a child name.
- `gfs2_get_parent()` resolves `..`.
- `gfs2_export_ops` exports the operation table.

## Control Flow And Behavior
Small handles store the child formal inode and block address; large handles additionally store the parent. Old handle size is accepted for compatibility. Decoding rejects zero formal inode as stale and uses `gfs2_lookup_by_inum()`. Name recovery takes the parent directory glock shared and scans entries until the child block address is found.

## Dependencies
Uses exportfs, GFS2 directory read/lookup helpers, glocks, inode lookup by inum, endian conversion, and `d_obtain_alias()`.

## Risks And Invariants
Handle length negotiation returns `FILEID_INVALID` when the caller-provided buffer is too small. Parent/name recovery requires valid directory inodes and glock protection.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/gfs2/export.c -->