# Group Research: group_976_linux_stable_sources_os_linux_linux_stable_fs_erofs_super_c_sources__a9166ad3908e

Scope confirmed against `Docs/research_subset_a.md`: all listed files are within `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/super.c

This file is the EROFS superblock, mount-context, module-lifetime, and VFS super-operations hub.

Major responsibilities:
- Provides EROFS logging via `_erofs_printk()` and creates/frees the `erofs_inode` slab cache.
- Reads and validates the on-disk superblock in `erofs_read_superblock()`, including magic, block size, unsupported feature bits, superblock checksum, 48-bit layout fields, metabox fields, xattr-prefix metadata, compression configuration, and device-table metadata.
- Handles multi-device and non-block-device mounting through `erofs_scan_devices()` and `erofs_init_device()`, including block-device paths, file-backed paths, fscache cookies, DAX discovery, device-table tags, and 48-bit block counts.
- Defines default and parsed mount options: `user_xattr`, `acl`, `cache_strategy`, `dax`, `device`, `fsid`, `domain_id`, `directio`, `fsoffset`, and `inode_share`.
- Implements `fs_context` operations for parsing, tree creation, reconfiguration, and cleanup.
- Fills the VFS superblock in `erofs_fc_fill_super()`: sets read-only/noatime behavior, block size, bdi, export ops, xattr handlers, POSIX ACL flags, compressed-cache state, packed/metabox/root inodes, shrinker registration, xattr prefixes, and sysfs registration.
- Supports block-device, fscache nodev, and file-backed nodev mounts in `erofs_fc_get_tree()`.
- Implements NFS export support through file-handle encode/decode and parent lookup.
- Owns superblock shutdown via `erofs_put_super()` and `erofs_kill_sb()`, releasing sysfs, shrinker, xattr prefixes, internal inodes, device contexts, fscache state, DAX references, opened files, and mount strings.
- Registers/unregisters the filesystem and subsystem dependencies in module init/exit.

Important invariants and validations:
- EROFS is mounted read-only and noatime.
- Supported block sizes are constrained by page size; fscache mode rejects non-page block sizes.
- `fsoffset` must be block-size aligned and is rejected for fscache mode.
- File-backed mounts reject stacked filesystems and nested file-backed EROFS to avoid stack-depth recursion.
- `inode_share` requires `domain_id`, is incompatible with forced DAX, and is disabled if the on-disk ishare-xattr feature is absent.
- DAX is disabled if the backing block/device path cannot provide DAX or if the block size is unsupported.
- Unknown incompatible features reject the mount.
- Metabox self-loop and invalid ishare-prefix ids are treated as corrupted metadata.

External interfaces:
- Exports `erofs_sops`.
- Registers `erofs_fs_type`.
- Optionally registers `erofs_anon_fs_type` for ondemand/page-cache-share features.
- Calls into EROFS xattr, sysfs, shrinker, fscache, compression, metabox, and inode-lookup subsystems.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/sysfs.c

This file implements EROFS sysfs registration and runtime attributes under `/sys/fs/erofs`.

Major responsibilities:
- Defines the root EROFS kset, the global `features` kobject, and per-superblock kobjects.
- Publishes supported feature attributes: `compr_cfgs`, `big_pcluster`, `chunked_file`, `device_table`, `compr_head2`, `sb_chksum`, `ztailpacking`, `fragments`, `dedupe`, `48bit`, and `metabox`.
- Publishes per-superblock tunables including `dir_ra_bytes`, and when compression is enabled, `sync_decompress` and `drop_caches`.
- Publishes compression-accelerator configuration through `accel` when `CONFIG_EROFS_FS_ZIP_ACCEL` is enabled.
- Implements generic attribute show/store dispatch through `struct erofs_attr`, struct-offset metadata, and attr ids.
- Registers per-superblock sysfs directories with `erofs_register_sysfs()` and removes them with `erofs_unregister_sysfs()`.
- Initializes and exits global sysfs state through `erofs_init_sysfs()` and `erofs_exit_sysfs()`.

Runtime behavior:
- Feature attributes read as `supported`.
- Unsigned integer and boolean attributes are read/written directly through validated struct offsets.
- `sync_decompress` writes are range-checked against EROFS sync-decompression modes.
- `drop_caches` accepts values 1 through 3 and can invalidate managed compressed-cache pages and/or shrink cached pclusters.
- `accel` writes disable all crypto acceleration engines, then enables newline-separated engine names from the input buffer.

Lifetime model:
- Per-superblock kobject release completes `s_kobj_unregister`, and unregister waits for that completion.
- Failed per-superblock kobject creation calls `kobject_put()` and waits for release, avoiding leaking partially initialized sysfs objects.
- Global init registers the `erofs` kset under `fs_kobj`, then adds the `features` kobject; failure unwinds through `erofs_exit_sysfs()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/xattr.c

This file implements EROFS extended-attribute lookup, listing, long-prefix loading, POSIX ACL extraction, and page-cache-share fingerprint generation.

Major responsibilities:
- Lazily initializes each inode’s xattr metadata in `erofs_init_inode_xattrs()`, loading the ibody header, name filter, shared-xattr count, and shared-xattr id array.
- Iterates inline xattrs stored after the inode body and shared xattrs stored in the global xattr area.
- Implements `erofs_getxattr()` and `erofs_listxattr()` using `struct erofs_xattr_iter`.
- Supports long xattr prefixes through superblock-level prefix tables loaded by `erofs_xattr_prefixes_init()`.
- Provides VFS xattr handlers for `user.*`, `trusted.*`, and, when enabled, `security.*`.
- Implements POSIX ACL lookup with `erofs_get_acl()` and a fast xattr-filter helper `erofs_inode_has_noacl()`.
- Implements inode-share fingerprint extraction with `erofs_xattr_fill_inode_fingerprint()` when page-cache sharing is enabled.

Important data flow:
- `erofs_init_inode_xattrs()` uses `EROFS_I_BL_XATTR_BIT` as a bit lock and `EROFS_I_EA_INITED_BIT` as the published initialized state.
- Memory barriers pair the initialized bit with loaded inode fields so other threads do not observe partially initialized xattr state.
- Inline iteration walks entries within `vi->xattr_isize`; shared iteration maps global xattr entries by id relative to `sbi->xattr_blkaddr`.
- `getxattr` can use the on-disk xxhash name filter to reject definitely absent names without scanning entries.
- Long-prefix entries match both the stored prefix base index and the dynamic infix before comparing the rest of the xattr name.

Validation and error handling:
- Missing xattrs return `-ENODATA`; absent lists become length zero.
- Malformed ibody sizes, shared counts, overlong names, malformed prefix lengths, and entry sizes extending beyond `xattr_isize` return corruption or range errors.
- User xattrs honor the `XATTR_USER` mount option.
- Trusted xattrs are listable only by `CAP_SYS_ADMIN`.
- POSIX ACL RCU lookup returns `-ECHILD`, forcing non-RCU lookup.

External interfaces:
- Exports `erofs_xattr_handlers`, `erofs_listxattr()`, `erofs_xattr_prefixes_init()`, `erofs_xattr_prefixes_cleanup()`, and optional ACL/fingerprint helpers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/erofs/xattr.h

This header declares EROFS xattr and ACL integration points used by the rest of the filesystem.

Primary contents:
- Includes EROFS internals plus Linux POSIX ACL xattr and generic xattr declarations.
- When `CONFIG_EROFS_FS_XATTR` is enabled, declares:
  - `erofs_xattr_handlers`
  - `erofs_xattr_prefixes_init()`
  - `erofs_xattr_prefixes_cleanup()`
  - `erofs_listxattr()`
- When xattrs are disabled, provides no-op prefix init/cleanup and maps `erofs_listxattr` and `erofs_xattr_handlers` to `NULL`.
- When `CONFIG_EROFS_FS_POSIX_ACL` is enabled, declares `erofs_get_acl()`; otherwise maps it to `NULL`.
- Declares inode-share and ACL-filter helpers:
  - `erofs_xattr_fill_inode_fingerprint()`
  - `erofs_inode_has_noacl()`

Design role:
- Lets `super.c` always wire `sb->s_xattr` and inode ACL operations through configuration-safe symbols.
- Keeps feature-dependent VFS hooks centralized, so callers do not need to duplicate xattr/ACL `#ifdef` logic.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/zdata.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/zdata.c

This file implements compressed EROFS data readout: pcluster lifecycle, compressed-page caching, bio submission, decompression queues, read_folio, and readahead.

Major responsibilities:
- Defines `struct z_erofs_pcluster`, which tracks one compressed physical cluster, its compressed pages, output bvecs, decompression length, algorithm, offsets, cache state, and queue linkage.
- Creates pcluster slab caches sized for different maximum compressed cluster page counts.
- Optionally creates per-CPU kthread workers and CPU hotplug hooks for decompression work.
- Initializes global compression state in `z_erofs_init_subsystem()` and tears it down in `z_erofs_exit_subsystem()`.
- Creates a per-superblock managed-cache inode and xarray in `z_erofs_init_super()`.
- Registers or reuses pclusters in `managed_pslots`, using lockref, xarray compare/exchange, RCU freeing, and shrinker-visible refcount state.
- Binds compressed data to the managed cache when cache strategy and mapping conditions prefer cached I/O.
- Builds output bvec chains for file folios and chooses whether pages can be used for inplace I/O.
- Submits compressed-data bios to block devices, file-backed I/O, or fscache, then kicks decompression after bio completion.
- Decompresses pclusters into primary output pages and secondary copies, handling overlap, short-lived bounce pages, cached folios, inline metadata data, and partial decompression.
- Implements `z_erofs_read_folio()` and `z_erofs_readahead()` address-space operations.

Key concurrency/lifetime details:
- Pcluster fields are divided by comments into initialization-only, pcluster-lock protected, and atomic/parallel fields.
- `pcl->lock` serializes pcluster decompression and bvec state reset.
- `pcl->lockref` protects reuse/release and coordinates xarray shrinker removal.
- Existing pclusters can be linked into a request chain or recognized as inflight, avoiding duplicate decompression.
- Managed compressed folios use folio private data to remember their pcluster; release/invalidate hooks detach them only when safe.
- Pcluster freeing is RCU-delayed after xarray removal because lookup/release paths can race.

Read path:
- `z_erofs_scan_folio()` maps logical ranges with `z_erofs_map_blocks_iter()`, handles fragments, holes, inline/meta pclusters, and mapped compressed pclusters, and adds split online-folio accounting.
- `z_erofs_submit_queue()` separates bypass queues from queues requiring I/O, merges adjacent bio vectors, marks readahead I/O, and uses PSI memstall annotations for workingset pages.
- `z_erofs_runqueue()` chooses synchronous foreground decompression or background work based on `sync_decompress` and readahead size.
- Readahead scans folios in reverse order for better metadata I/O behavior and may expand around whole pclusters.

Important error behavior:
- Bio errors set queue `eio`, resulting in `-EIO` decompression completion.
- Decompressor string errors become `-EFSCORRUPTED`; error pointers propagate directly.
- Failed compressed page allocation records an error pointer in the compressed bvec and is surfaced during input parsing.
- All online folios are ended with success or error, and temporary pagepool pages are released after each request.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/zdata.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/zmap.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/zmap.c

This file translates compressed EROFS logical offsets into physical compressed extents and implements FIEMAP reporting for compressed files.

Major responsibilities:
- Defines `struct z_erofs_maprecorder`, a transient decoder for compressed lcluster metadata.
- Loads full-format lcluster indexes with `z_erofs_load_full_lcluster()`.
- Loads compact-format lcluster indexes with `z_erofs_load_compact_lcluster()`, including 2-byte and 4-byte compact packs, lookback distances, big-pcluster compressed block counts, and derived physical block numbers.
- Loads extent-format compressed mappings with `z_erofs_map_blocks_ext()`, including binary search for variable records and compact sequential formats.
- Initializes compressed inode mapping metadata once in `z_erofs_fill_inode()`.
- Maps normal compressed layouts with `z_erofs_map_blocks_fo()`, handling nonhead lookback, tailpacking, fragments, partial refs, big pclusters, algorithm selection, and decompressed-length discovery.
- Exposes `z_erofs_map_blocks_iter()` as the main compressed block-mapping iterator.
- Implements `z_erofs_iomap_report_ops` for FIEMAP/reporting paths.

Important mapping behavior:
- Post-EOF mappings are reported as unmapped extents with a length that lets iomap progress.
- Fragment-only files can map the full file as `EROFS_MAP_FRAGMENT`.
- Ztailpacking maps inline compressed data as `EROFS_MAP_META` and validates that inline data does not cross a filesystem block.
- Fragment tail extents update inode fragment metadata during `EROFS_GET_BLOCKS_FINDTAIL`.
- Algorithm format is selected from plain/interlaced/shifted encodings or per-inode compressed algorithm slots.
- FIEMAP and readmore paths can force full decompressed-length calculation so extents are reported as complete rather than partial.

Validation:
- Rejects unknown lcluster types, invalid cluster offsets, bogus lookback distances, inconsistent big-pcluster features, unsupported algorithms, and invalid physical address ranges.
- Ensures advertised compression algorithms exist in the mounted superblock’s available-compressor bitmap.
- Rejects compressed extents whose physical length is impossible for the logical length, or plain extents whose physical length is too short.
- Enforces pcluster maximum compressed and decompressed sizes.
- Rejects physical ranges beyond the filesystem’s 48-bit physical block address limit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/zmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/zutil.c -->
# File Research: sources/os/linux/linux-stable/fs/erofs/zutil.c

This file provides utility infrastructure for compressed EROFS: global decompression buffers, reserved page handling, pagepool release, and the global shrinker.

Major responsibilities:
- Defines per-CPU-ish global buffers (`struct z_erofs_gbuf`) used by decompressors.
- Exposes module parameters:
  - `global_buffers`
  - `reserved_pages`
- Initializes and exits the global buffer pool with `z_erofs_gbuf_init()` and `z_erofs_gbuf_exit()`.
- Allows global buffers to grow, never shrink, through `z_erofs_gbuf_growsize()`.
- Provides `z_erofs_get_gbuf()` / `z_erofs_put_gbuf()` with migration disabled and a per-buffer spinlock.
- Implements `__erofs_allocpage()` and `erofs_release_pages()` for decompression pagepool and reserved-page fallback.
- Maintains a global list of mounted EROFS superblocks participating in compressed-cache shrinking.
- Registers/unregisters each superblock with the shrinker list through `erofs_shrinker_register()` and `erofs_shrinker_unregister()`.
- Implements shrinker count/scan callbacks and global shrinker init/exit.

Important details:
- Buffer selection uses `raw_smp_processor_id() % z_erofs_gbuf_count`, guarded by `migrate_disable()` so the caller stays on the selected CPU while holding the buffer.
- Growing global buffers allocates any missing pages, vmaps a new buffer, swaps it under the buffer spinlock, and unmaps the old buffer afterward.
- Reserved pages are consumed before normal allocation when requested and are replenished before pages are released back to the allocator.
- Superblock shrinker unregister drains all managed pclusters before removing the superblock from the global list.
- Shrinker scans rotate processed superblocks to the list tail for fairness and use each superblock’s `umount_mutex` with trylock to avoid racing unmount.
- `erofs_global_shrink_cnt` is the global count hint used by the shrinker to decide whether work exists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/erofs/zutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/eventfd.c -->
# File Research: sources/os/linux/linux-stable/fs/eventfd.c

This file implements Linux `eventfd`, a pollable anonymous-file counter used by userspace and kernel subsystems for event notification.

Major responsibilities:
- Defines `struct eventfd_ctx` with a kref, waitqueue, 64-bit counter, flags, and fdinfo id.
- Implements kernel signaling through `eventfd_signal_mask()`, exported for in-kernel users.
- Implements read/write/poll/release file operations for eventfd anonymous inodes.
- Provides fdinfo output under procfs when enabled.
- Provides kernel helpers:
  - `eventfd_fget()`
  - `eventfd_ctx_fdget()`
  - `eventfd_ctx_fileget()`
  - `eventfd_ctx_put()`
  - `eventfd_ctx_do_read()`
  - `eventfd_ctx_remove_wait_queue()`
- Implements `eventfd2` and legacy `eventfd` syscalls.

Counter semantics:
- Writes add a user-supplied `u64` value, except `ULLONG_MAX` is invalid.
- Reads return and clear the full count, or return/decrement by one in `EFD_SEMAPHORE` mode.
- Kernel `eventfd_signal_mask()` increments by one and may let the counter reach `ULLONG_MAX`, which poll reports as `EPOLLERR`.
- Poll reports readable when count is nonzero, writable when at least one less than `ULLONG_MAX`, and error on overflow.

Concurrency and wakeups:
- `ctx->wqh.lock` protects `count` and waitqueue operations.
- Poll relies on `poll_wait()` waitqueue locking as an ordering barrier, allowing a lockless `READ_ONCE(ctx->count)` after registration.
- Wakeups set `current->in_eventfd` to avoid recursive waitqueue wakeups causing deadlock or stack overflow.
- Release wakes waiters with `EPOLLHUP` and drops the context reference.
- `eventfd_ctx_remove_wait_queue()` atomically removes a waitqueue entry and reads/resets the counter under the same lock.

Resource lifetime:
- Contexts are reference-counted with `kref`.
- IDs are allocated with a global `IDA` for fdinfo and freed with the context.
- Anonymous file creation uses the eventfd fops and publishes the prepared fd only after setup succeeds.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/eventfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/eventpoll.c -->
# File Research: sources/os/linux/linux-stable/fs/eventpoll.c

This file implements Linux `epoll`: scalable event-interest sets, readiness collection, wakeup callbacks, nested epoll handling, and the epoll syscalls.

Major responsibilities:
- Defines core objects:
  - `struct eventpoll`: one epoll instance with mutex, waitqueues, ready list, overflow list, rb-tree interest set, owning user, refcount, wakeup source, nesting metadata, and optional busy-poll state.
  - `struct epitem`: one watched target file/fd and event mask, linked into the epoll rb-tree, ready list, target file list, waitqueue list, and optional wakeup source.
  - `struct eppoll_entry`: one installed waitqueue callback on a target file.
- Implements epoll file operations: release, poll, fdinfo, ioctl, and llseek.
- Implements creation through `epoll_create()` / `epoll_create1()`.
- Implements control operations through `do_epoll_ctl()` and `epoll_ctl()`.
- Implements event delivery through `epoll_wait()`, `epoll_pwait()`, `epoll_pwait2()`, compat wrappers, and `epoll_sendevents()`.
- Maintains per-user watch accounting and `/proc/sys/fs/epoll/max_user_watches`.
- Supports optional network busy-poll parameters through `EPIOCSPARAMS` / `EPIOCGPARAMS`.

Locking model:
- The documented lock order is `epnested_mutex` first, then `ep->mtx`, then `ep->lock`.
- `epnested_mutex` serializes nested epoll insertion checks and prevents racing cycle creation.
- `ep->mtx` protects the rb-tree interest set, pollwait registration/removal, event transfer, ctl operations, and release cleanup.
- `ep->lock` protects ready-list and overflow-list manipulation from wakeup callbacks, including IRQ-context wakeups.
- Nested epoll polling uses lockdep nesting depth to annotate multiple `ep->mtx` acquisitions.

Ready-event flow:
- `ep_ptable_queue_proc()` installs `ep_poll_callback()` into target waitqueues during add.
- `ep_poll_callback()` filters disabled masks, requested event masks, and `EPOLLEXCLUSIVE`, then appends the item to `rdllist` or `ovflist` and wakes epoll waiters.
- `ep_start_scan()` steals `rdllist` into a private transfer list and enables `ovflist` so callbacks can queue events while userspace copies are in progress.
- `ep_send_events()` re-polls each ready item, copies events to userspace, applies `EPOLLONESHOT`, and requeues level-triggered items.
- `ep_done_scan()` merges overflow events back into `rdllist`, restores overflow-list inactive state, and wakes waiters if readiness remains.
- `ep_poll()` handles timeout conversion, waitqueue sleeps, signals, busy polling, and final locked readiness checks to avoid missed events.

Nested epoll and path limits:
- `ep_loop_check()` prevents cycles and chains deeper than `EP_MAX_NESTS`.
- `ep_loop_check_proc()` walks downward through nested epoll rb-trees and records reachable non-epoll files for reverse path checks.
- `ep_get_upwards_depth_proc()` walks upward through target-file backreferences under RCU.
- `reverse_path_check()` limits fanout paths from watched files to avoid wakeup storms.
- `attach_epitem()` links an epitem into `file->f_ep`; ordinary files get an allocated `epitems_head`, while epoll files reuse their `refs` list.

Lifetime and cleanup:
- `eventpoll_release_file()` removes all epoll watches that reference a file being closed.
- `ep_clear_and_put()` unregisters poll callbacks, removes all epitems, wakes poll waiters, and drops the epoll reference.
- Epitems are RCU-freed after removal; eventpoll structs are RCU-freed because upward-depth checks can still observe them.
- File references in `epi_fget()` are safe under `ep->mtx` because file teardown blocks in `eventpoll_release_file()`.

User-visible semantics:
- `EPOLLWAKEUP` requires `CAP_BLOCK_SUSPEND` when power management sleep is enabled.
- `EPOLLEXCLUSIVE` is allowed only on add, not modify, and not for nested epoll targets.
- `EPOLLERR` and `EPOLLHUP` are always added for add/modify interest masks.
- `epoll_wait` validates maxevents, userspace writeability, and that the fd is an epoll file before polling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/eventpoll.c -->