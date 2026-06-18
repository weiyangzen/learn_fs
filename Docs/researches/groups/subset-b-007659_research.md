# subset-b-007659 Research

Grouped code research for Lustre llite statahead, superblock, symlink, VVP, xattr, and MDC batch/procfs files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/statahead.c -->
# sources/distributed-fs/lustre-release/lustre/llite/statahead.c

## Purpose
`statahead.c` implements llite metadata stat-ahead for directory traversal and regular numeric filename patterns. It predicts future child lookups, issues asynchronous metadata `getattr` intent RPCs, caches prepared `sa_entry` results by name, and optionally runs an asynchronous glimpse-lock (AGL) helper for regular files so later size/glimpse-sensitive paths avoid synchronous round trips.

## Important APIs, Types, And Functions
Core state is `struct sa_entry`, `struct ll_statahead_info`, and `struct ll_statahead_context`. Important entry points are `ll_authorize_statahead()`, `ll_deauthorize_statahead()`, `ll_start_statahead()`, `ll_revalidate_statahead()`, `ll_ioctl_ahead()`, and `ll_statahead_enter()`. The main workers are `ll_statahead_thread()` and `ll_agl_thread()`. `sa_alloc()`, `sa_get()`, `sa_put()`, `sa_make_ready()`, `sa_lookup()`, and `sa_revalidate()` manage cached predictions and async RPC completion.

## Control Flow
Directory open authorizes list-pattern statahead. The first stat on an eligible child calls `start_statahead_thread()`, which detects list or numeric filename patterns, allocates `sai`/`sax`, optionally starts AGL, and returns `-EAGAIN` so the triggering lookup proceeds normally. The worker scans directory pages or synthesizes names, calls `sa_statahead()`, and sends either batched metadata updates through `md_batch_add()` or direct `md_intent_getattr_async()`. Async callbacks run `ll_statahead_interpret()`, defer dangerous inode preparation to workqueue context when needed, install lock data, cache encryption context, and mark the `sa_entry` ready. Lookup revalidation later calls `ll_revalidate_statahead()` to splice or validate the cached inode and consume the entry.

## State And Persistence
State is in-memory only. Per-inode `lli_sai`, `lli_sax`, `lli_sa_pattern`, generation counters, locks, hidden-file counters, filename prediction counters, and cached `sa_entry` lists persist while a directory handle or advise request is active. `sai_hit`, `sai_miss`, `sai_sent`, `sai_replied`, `sai_cache_count`, and window `sai_max` tune behavior. Memory ordering around `sai_task` and `se_state` is explicit with acquire/release barriers; entries are freed after scanner use or worker shutdown.

## Dependencies And Integration Points
The file integrates with llite lookup/revalidate, directory-page reads, llcrypt name translation, MDC async intent getattr, MDC batch RPCs, LDLM intent locks, `ll_prep_inode()`, xattr cache insertion for encryption contexts, AGL via `cl_agl()`, and llite mount tunables such as `ll_sa_max`, `ll_sa_min`, batch limits, timeouts, and running limits.

## Risks And Edge Cases
The highest risks are races among lookup consumers, async RPC callbacks, worker shutdown, and directory close. Wrong-PID cache hits stop the worker, stale FID replies are rejected, low hit ratios disable statahead, and in-use entries delay final cleanup. Hidden file handling is adjusted when `ls -al` appears after skipped dot entries. The ptlrpcd callback avoids blocking inode preparation for striped directories and layout changes by scheduling work.

## Test Signals
Useful signals include `ls -l` and `ls -al` on large directories, mdtest-style numeric stat workloads, shared-directory multi-process patterns, ladvise ahead ranges, encrypted directory names, batch-RPC-capable and non-capable MDT connections, AGL enabled/disabled mounts, low-hit-ratio stop paths, close while RPCs are in flight, and fault injections for stale layout, pause, allocation, and async completion races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/statahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/super25.c -->
# sources/distributed-fs/lustre-release/lustre/llite/super25.c

## Purpose
`super25.c` is the Linux VFS superblock and module-registration layer for the Lustre client filesystem. It allocates llite inode slabs, exposes `lustre_super_operations`, implements mount/remount through `fs_context`, and initializes or tears down client-wide llite, VVP, xattr, tunable, and cache resources.

## Important APIs, Types, And Functions
Important functions include `ll_alloc_inode()`, `ll_destroy_inode()`, `ll_drop_inode()`, `ll_show_devname()`, `lustre_fill_super()`, `lustre_get_tree()`, `lustre_reconfigure()`, `lustre_init_fs_context()`, `lustre_kill_super()`, `lustre_init()`, and `lustre_exit()`. The exported VFS tables are `lustre_super_operations`, `lustre_fs_context_ops`, and `lustre_fs_type`.

## Control Flow
Module initialization sets up libcfs, slab caches (`lustre_inode_cache`, `ll_file_data`, `ll_pcc_inode`, quota iterator), llite tunables, VVP global state, a cl environment for inode finalization, xattr cache infrastructure, and finally registers the `lustre` filesystem type. Mounting calls `lustre_fill_super()`, initializes Lustre mount state, waits for OBD zombie cleanup, rejects or redirects server mounts, starts the MGC for client mounts, and calls `ll_fill_super()`. Remount synchronizes the filesystem, pushes read-only state to the MDT import, toggles `SB_RDONLY`, and swaps mount options.

## State And Persistence
Persistent runtime state includes slab caches, the registered filesystem type, per-superblock `lustre_sb_info`/`ll_sb_info`, mount data in `fs_context->fs_private`, and client/VVP/xattr global registrations. Inode objects are allocated from `ll_inode_cachep`; final freeing is RCU-delayed to allow VFS readers and llcrypt state to drain.

## Dependencies And Integration Points
This file binds the VFS to lower Lustre layers: `lustre_init_lsi()`, `lustre_start_mgc()`, `ll_fill_super()`, `ll_put_super()`, `ll_delete_inode()`, `ll_statfs()`, `ll_umount_begin()`, `llite_tunables_register()`, `vvp_global_init()`, `ll_xattr_init()`, and server mount handling when built with server support.

## Risks And Edge Cases
Initialization has many staged resources and must unwind in reverse order on failure. Mount disables lockdep around special Lustre mount locking. Remount read-only transitions can fail if the MDT import rejects `KEY_READ_ONLY`. `ll_drop_inode()` depends on inode cache and encryption policy decisions. Exit must call `rcu_barrier()` before destroying the inode cache.

## Test Signals
Test mount/unmount loops, failed mount injection at each init stage, client versus server target mount attempts, remount read-only/read-write, inode allocation pressure, encrypted inode eviction, module unload after active inodes, and `/proc/mounts` device-name rendering for MGS and direct-device mount data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/super25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/symlink.c -->
# sources/distributed-fs/lustre-release/lustre/llite/symlink.c

## Purpose
`symlink.c` implements Lustre llite symlink resolution and symlink-specific getattr. It fetches link targets from MDT metadata, validates and optionally decrypts them, caches usable targets in `lli_symlink_name`, and makes encrypted symlink `st_size` match the userspace-visible target.

## Important APIs, Types, And Functions
Key functions are `ll_readlink_internal()`, `ll_get_link()`, `ll_put_link()`, and `ll_getattr_link()`. The file exports `ll_fast_symlink_inode_operations` with `.get_link`, `.getattr`, `.setattr`, `.permission`, and `.listxattr`.

## Control Flow
`ll_get_link()` takes `lli_size_mutex`, calls `ll_readlink_internal()`, and returns either a cached target or a target backed by the MDT reply buffer with a delayed `ptlrpc_req_put()`. `ll_readlink_internal()` prepares metadata op data, requests `OBD_MD_LINKNAME`, checks the MDT body and expected length, retrieves `RMF_MDT_MD`, validates NUL termination for unencrypted links, and decrypts or no-key-encodes encrypted links through llcrypt helpers. `ll_getattr_link()` first delegates to `ll_getattr()` and, for encrypted links, resolves the link target to override `stat->size`.

## State And Persistence
The only durable local state is `ll_inode_info::lli_symlink_name`, allocated after a successful read. Encrypted no-key targets are intentionally not cached because adding the key later changes the visible target. RPC-backed buffers are held alive with delayed-call cookies until the VFS is done with the returned pointer.

## Dependencies And Integration Points
The file integrates with `md_getattr()`, request capsules (`RMF_MDT_BODY`, `RMF_MDT_MD`), llite inode metadata helpers, llcrypt symlink decoding, `ll_has_encryption_key()`, and normal llite attribute/permission/xattr operations.

## Risks And Edge Cases
Bad server replies are guarded by explicit protocol checks for missing `OBD_MD_LINKNAME`, mismatched `mbo_eadatasize`, missing target buffers, and missing NUL termination. `ll_get_link()` rejects RCU path-walk calls by returning `-ECHILD`. Encrypted symlink getattr is heavier than normal because it may need to read and decode the target.

## Test Signals
Cover cached and uncached symlink reads, malformed MDT reply handling, encrypted symlinks with and without keys, repeated `lstat()` size stability, request lifetime under delayed calls, `readlink()` races with inode eviction, and VFS path-walk behavior when `dentry` is NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_dev.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_dev.c

## Purpose
`vvp_dev.c` implements VVP (`Vfs Vm Posix`) cl-device type registration, per-context storage allocation, superblock cl-stack setup, and the debugfs `dump_page_cache` walker for llite mounts.

## Important APIs, Types, And Functions
The file defines kmem descriptors for `ll_thread_info`, `vvp_object`, `vvp_session`, and `vvp_thread_info`; context keys `ll_thread_key`, `vvp_session_key`, and `vvp_thread_key`; `vvp_device_type`; and lifecycle functions `vvp_global_init()`, `vvp_global_fini()`, `cl_sb_init()`, and `cl_sb_fini()`. Debugfs support is exposed through `vvp_dump_pgcache_file_ops`.

## Control Flow
Global init creates caches and registers the VVP lu device type. Superblock init obtains a cl environment and builds a VVP cl-device over the data target lu device, saving `ll_cl` and `ll_site` in the superblock. Device allocation creates a `vvp_device`, initializes a cl site, and wires the lower device into the same lu site. The page-cache dump opens a seq file, grabs a cl environment, walks the lu-site object hash, finds each object's page-cache pages, maps them back to `cl_page`, and prints FID, index, writeback state, page count, and page flags.

## State And Persistence
Persistent state includes global slabs, context-key allocations, the `vvp_device_type`, per-superblock cl-device/site pointers, and temporary seq-file state in `struct vvp_seq_private`. Device teardown unwinds lower lu stack state and clears superblock pointers.

## Dependencies And Integration Points
This file sits between llite superblock setup and the cl/lov/osc stack. It depends on lu/cl context APIs, `lu_kmem_init()`, `lu_device_type_init()`, `cl_type_setup()`, rhashtable object storage, page-cache helpers, and `vvp_object_inode()` from the VVP object layer.

## Risks And Edge Cases
Device init and cleanup require a usable cl environment; memory pressure can make `cl_sb_fini()` fail loudly. The seq walker must handle rhashtable `-EAGAIN`, object references, page references, and mount teardown. `dump_page_cache` returns `-ENODATA` until common client fill-super succeeded.

## Test Signals
Exercise module init/fini, mount/unmount cl stack creation, failure injection for cache and site allocation, debugfs page-cache dumps while pages are dirty/writeback/evicted, rhashtable iteration during object churn, and cleanup under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_internal.h -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_internal.h

## Purpose
`vvp_internal.h` is the private contract for the llite VVP layer. It defines per-I/O, per-session, per-thread, object, and device structures plus helper accessors used by VVP device, object, page, and I/O implementations.

## Important APIs, Types, And Functions
Important types are `struct vvp_io`, `struct vvp_fault_io`, `struct vvp_thread_info`, `struct vvp_session`, `struct vvp_object`, and `struct vvp_device`. Helper APIs include `vvp_env_info()`, `vvp_env_new_lock()`, `vvp_env_new_attr()`, `vvp_env_new_io()`, `vvp_env_session()`, `vvp_env_io()`, `vvp2lu_dev()`, `lu2vvp_dev()`, `cl2vvp_dev()`, `cl2vvp()`, `lu2vvp()`, and `vvp_object_inode()`. It declares `vvp_io_init()`, `vvp_io_write_commit()`, `vvp_page_init()`, `vvp_object_alloc()`, `vvp_global_init()`, and `vvp_global_fini()`.

## Control Flow
The header has no standalone runtime flow, but it determines how VVP code obtains scratch objects from `lu_env`, attaches a `vvp_io` slice to each `cl_io`, locates the VVP object from a cl/lu object, and routes page/object/device allocation through the lower cl stack.

## State And Persistence
`struct vvp_io` persists for one cl I/O session and stores iterator, total bytes, file/iocb pointers, layout generation, readahead window state, and read/write or fault-specific queues. `struct vvp_object` persists with a Lustre inode and tracks mmap count plus one-shot discard warning state. `struct vvp_device` holds the VVP cl device and next lower cl device.

## Dependencies And Integration Points
The header depends on cl-object infrastructure, lu contexts, Linux VM/file types, and llite inode ownership. It is included by VVP device, object, page, and I/O source files and by llite superblock setup for VVP initialization.

## Risks And Edge Cases
Incorrect context-key use causes per-thread/session storage corruption. The `CLOBINVRNT` macro becomes a no-op unless expensive checks are enabled, so invariant coverage varies by build. Structure layout changes affect slab sizes declared in `vvp_dev.c` and assumptions in I/O and page callbacks.

## Test Signals
Build all supported kernel-compat configurations, run cl I/O paths for reads/writes/faults/setattr/lseek, enable expensive invariant checks, validate mmap count transitions, and exercise module load/unload to ensure declared sizes match allocated slabs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_io.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_io.c

## Purpose
`vvp_io.c` implements VVP `cl_io_operations`, bridging Linux VFS page-cache and VM operations to Lustre cl/lov/osc I/O. It manages DLM lock descriptions, layout-version validation, read/write iteration, dirty-page commit, truncate/fallocate/setattr, page faults and mkwrite, fsync bookkeeping, readahead preparation, and lseek locking.

## Important APIs, Types, And Functions
Externally relevant functions are `vvp_io_init()` and `vvp_io_write_commit()`. Major internal functions include `vvp_prep_size()`, `vvp_io_rw_lock()`, `vvp_io_read_start()`, `vvp_io_write_start()`, `vvp_io_commit_sync()`, `vvp_set_batch_dirty()`, `vvp_io_setattr_start/end()`, `vvp_io_fault_start/end()`, `vvp_io_lseek_start/end()`, and the `vvp_io_ops` table.

## Control Flow
`vvp_io_init()` adds the VVP slice, records byte counts/job info, refreshes layout for most operations, and optionally locks page-cache invalidation. Lock callbacks build page-index lock extents, account for group locks, nonblocking/no-expand flags, lockless I/O, direct I/O, and mmap buffers. Read start validates layout, reserves LRU pages, prepares size/KMS with possible glimpse, initializes readahead, and calls `generic_file_read_iter()` with retry on page invalidation sequence changes. Write start handles append position, max file size, LRU reserve, generic write, writeback sync, and `vvp_io_write_commit()`. Fault start handles normal faults and mkwrite quota/dirty preparation. Fini checks restore/write-intent/layout changes and requests restarts as needed.

## State And Persistence
Per-I/O state is kept in `struct vvp_io`: iterator position, remaining bytes, layout generation, readahead span, file/iocb, and read/write or fault queues. Persistent inode state affected here includes `lli_trunc_sem`, `lli_setattr_mutex`, `lli_layout_gen`, `lli_jobinfo`, `lli_page_inv_lock`, `LLIF_DATA_MODIFIED`, and restoring/layout flags. Page dirty/writeback state is updated through Linux page-cache and cl-page ownership.

## Dependencies And Integration Points
This file integrates with cl locks/pages/queues, llite layout refresh/write intent/restore, LOV/OSC async commit, Linux generic file read/write/fault helpers, memcg dirty accounting compatibility shims, mmap VMA scanning, PCC file helpers, HSM restore bits, LSOM attr merge, and LDLM group-lock semantics.

## Risks And Edge Cases
Layout can change mid-I/O, so many paths set `ci_need_restart` or stop continuation. Append writes must re-check size under locks. Async commit can fall back to sync on quota or high priority. mkwrite must avoid dirtying pages beyond EOF and convert quota failures to VM-visible errors. The batching dirty path relies on pages sharing a mapping and on kernel-version-specific dirty accounting behavior.

## Test Signals
Use buffered and direct reads/writes, append races, truncate/fallocate/setattr under load, mmap reads and writes, page fault versus truncate races, HSM restore, layout swap/write-intent restarts, group-lock files, quota exhaustion, dirty accounting across supported kernels, lseek past EOF, and failpoints for lost layout, short commit, and fault pauses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_object.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_object.c

## Purpose
`vvp_object.c` implements VVP `cl_object` and `lu_object` behavior for regular-file inodes. It exposes inode attributes to lower cl layers, reacts to layout invalidation, prunes page cache, provides glimpse data, fills request attributes, and allocates/frees VVP objects.

## Important APIs, Types, And Functions
Important functions include `vvp_object_invariant()`, `vvp_attr_get()`, `vvp_attr_update()`, `vvp_conf_set()`, `vvp_prune()`, `vvp_object_glimpse()`, `vvp_req_attr_set()`, `vvp_req_projid_set()`, `cl_inode2vvp()`, and `vvp_object_alloc()`. Operation tables are `vvp_ops` and `vvp_lu_obj_ops`.

## Control Flow
Object allocation creates a `vvp_object`, initializes a cl object header, installs operation tables, and adds it as the top lu object. Object init allocates the lower object from `vdv_next`, links it into the stack, stores the inode, and initializes cl page slices. Attribute get/update translate between inode fields and `cl_attr`. Config invalidation clears layout generation, invalidates PCC layout state, and unmaps VM mappings. Prune syncs local dirty data then truncates final pages. Freeing is RCU-delayed after lu object/header finalization.

## State And Persistence
`vvp_object` persists with `vob_inode`, `vob_mmap_cnt`, and `vob_discard_page_warned`. It reflects inode uid/gid/time/project-id/block/size state and updates inode version on KMS changes. Request attribute filling stores parent FID, project ID, and job info for downstream OST RPC scheduling and accounting.

## Dependencies And Integration Points
The file integrates with llite inode info, cl object/page/io operations, lower lov/osc devices, PCC layout invalidation, Linux inode version/time helpers, dirty page accounting, and lfsck failpoint support for parent FID mutation.

## Risks And Edge Cases
Only regular files or zero-mode objects satisfy the invariant. Layout invalidation must unmap mmaps because userspace can otherwise read stale installed pages. Prune failures leave dirty data and must be surfaced. Attribute updates cross user-namespace uid/gid conversion boundaries.

## Test Signals
Test object allocation/free under RCU, attr get/update for uid/gid/times/project ID, layout invalidation with active mmap, page-cache prune after writeback failures, glimpse block reporting for dirty sparse files, and request attribute contents on read/write RPCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_object.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_page.c -->
# sources/distributed-fs/lustre-release/lustre/llite/vvp_page.c

## Purpose
`vvp_page.c` implements the VVP `cl_page` slice for Linux page-cache pages. It connects `struct page` private pointers to `struct cl_page`, handles read/write completion, tracks discarded readahead, clears stale uptodate state on deletion, and reports VM-level writeback errors.

## Important APIs, Types, And Functions
Important functions are `vvp_page_init()`, `vvp_page_delete()`, `vvp_page_discard()`, `vvp_vmpage_error()`, `vvp_page_complete_read()`, and `vvp_page_complete_write()`. Operation tables are `vvp_page_ops` for cacheable pages and `vvp_transient_page_ops` for direct-I/O/transient pages.

## Control Flow
Cacheable page init takes a page reference, increments cl-page refcount, sets `PagePrivate`, stores the cl-page pointer in `page->private`, and installs VVP page ops. Delete reverses the page-private mapping, drops the cache-held cl-page refcount, and clears `PageUptodate` under `lli_page_inv_lock` so racing reads/faults can detect invalidation. Read completion sets `PageUptodate` unless readahead deferred it, handles `-EAGAIN` mirror retry by removing the folio, and unlocks async pages. Write completion marks mapping errors for async writes and ends writeback.

## State And Persistence
State is mostly in Linux page flags and `page->private`. `vvp_object::vob_discard_page_warned` suppresses repeated discard warnings. Readahead accounting is decremented for deferred uptodate pages. Mapping error state persists in `address_space` for later fsync/writeback reporting.

## Dependencies And Integration Points
The file depends on cl-page ownership and completion APIs, Linux page flags/writeback, llite readahead stats, inode page invalidation seqlock, `cl_inode2vvp()`, and dirty-page discard warning helpers.

## Risks And Edge Cases
Transient pages intentionally do not take user page references. Clearing uptodate on delete is required to avoid stale data and SIGBUS races. Async write errors need mapping-level propagation because applications may not wait on individual I/O. Mirror read retry must destroy wrong-subpage cache state.

## Test Signals
Cover cacheable and transient page init, read completion success and error, deferred readahead accounting, mirror retry `-EAGAIN`, async writeback error propagation, page deletion during fault/read, and repeated eviction/discard warning suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/vvp_page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr.c -->
# sources/distributed-fs/lustre-release/lustre/llite/xattr.c

## Purpose
`xattr.c` implements llite VFS extended-attribute handlers. It filters namespaces, forwards get/set/list operations to MDT metadata RPCs or the client xattr cache, handles Lustre layout xattrs (`lov`, `lmv`, `dmv`, `lma`, `link`), ACL shortcuts, security-label filtering, and list sanitization.

## Important APIs, Types, And Functions
Important functions are `get_xattr_type()`, `ll_xattr_set_common()`, `ll_xattr_set()`, `ll_xattr_list()`, `ll_xattr_get_common()`, `ll_getxattr_lov()`, `ll_listxattr()`, and handlers in `ll_xattr_handlers[]`. Layout helpers include `ll_adjust_lum()` and `ll_setstripe_ea()`.

## Control Flow
Set paths validate namespace support, ACL ownership, trusted capability, user.* inode type, security context policy, and special cases. `lov` sets regular-file striping or directory defaults, with copied layout offsets reset and release flags cleared unless HSM archived. Generic sets call `md_setxattr()`, disabling user_xattr if the server rejects it. Get paths serve cached ACLs, call `ll_xattr_cache_get()` when safe, or request MDT xattrs with `md_getxattr()`. `lov` gets are synthesized from cl object layout or directory default stripe data and sanitized before userspace sees them. List paths filter unsupported namespaces and append virtual `lustre.lov`.

## State And Persistence
The file updates server-side xattrs through MDT RPCs and marks `lli_synced_to_mds` false after successful set/remove. It may clear `LL_SBI_USER_XATTR` on server incompatibility. It reads cached ACL and xattr cache state but does not own the cache memory.

## Dependencies And Integration Points
It integrates with Linux xattr handlers, llite security helpers, POSIX ACL conversion, MDC metadata RPCs, LOV/LMV layout structures, HSM state ioctls, cl object layout get, directory stripe helpers, project ID inheritance, and llite operation statistics.

## Risks And Edge Cases
Layout xattrs are binary ABI surfaces with endian and size checks. Exposing `security.c` encryption context is blocked for compatibility. `trusted.projid` is hidden on inherited-project trees. `lov` layout generation is sanitized so archive tools do not restore stale stripe offsets. Cache bypass is required for ACLs, security labels, SOM, and pinned Lustre xattrs.

## Test Signals
Test user/trusted/security/system/lustre namespaces, capability and ownership failures, POSIX ACL get/set, `lov`/`lmv`/`dmv` layout xattrs, endian-swapped input, HSM released layout copies, encrypted-file security.c denial, xattr list filtering, cache and no-cache paths, and server `-EOPNOTSUPP` disabling user_xattr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_cache.c -->
# sources/distributed-fs/lustre-release/lustre/llite/xattr_cache.c

## Purpose
`xattr_cache.c` implements an inode-local client cache for MDT xattrs. It fetches whole xattr sets under an LDLM xattr lock, stores name/value pairs in a protected list, serves get/list operations, preserves encryption context across cache emptying, and invalidates the cache on lock cancellation or explicit destroy.

## Important APIs, Types, And Functions
The cache entry type is `struct ll_xattr_entry`. Public functions are `ll_xattr_init()`, `ll_xattr_fini()`, `ll_xattr_cache_destroy()`, `ll_xattr_cache_empty()`, `ll_xattr_cache_get()`, and `ll_xattr_cache_insert()`. Internal helpers include `ll_xattr_find_get_lock()`, `ll_xattr_cache_refill()`, `ll_xattr_cache_add()`, `ll_xattr_cache_del()`, and `ll_xattr_cache_list()`.

## Control Flow
`ll_xattr_cache_get()` takes a read lock and refills if the full cache is needed and not filled. Refill serializes enqueue with `lli_xattrs_enq_lock`, tries to match an existing `MDS_INODELOCK_XATTR` PR lock, otherwise enqueues an intent that requests names, values, and lengths. It validates reply capsules, initializes the cache if needed, filters ACL access, security labels, and `trusted.som`, adds the rest, marks `LLIF_XATTR_CACHE_FILLED`, attaches lock data, and drops the intent lock. Reads then copy a single value, list names, or synthesize virtual `trusted.projid`.

## State And Persistence
State lives in `ll_inode_info::lli_xattrs`, protected by `lli_xattrs_list_rwsem`, with flags `LLIF_XATTR_CACHE` and `LLIF_XATTR_CACHE_FILLED`. `xattr_kmem` backs entry objects, while names and values are separately allocated. Lock state is held by LDLM and tied back to the inode through `ll_set_lock_data()`.

## Dependencies And Integration Points
The file depends on llite inode flags/locks, MDC intent locks, request capsules (`RMF_EADATA`, `RMF_EAVALS`, `RMF_EAVALS_LENS`), LDLM xattr inodebits locks, operation statistics, encryption xattr naming, project IDs, and failpoints for pause/ENOMEM.

## Risks And Edge Cases
There is no atomic match-or-enqueue API, so refill uses an explicit enqueue mutex to avoid duplicate fetches. Protocol validation must catch broken name NULs and value lengths. Duplicate encryption contexts are ignored because they are immutable. `-ERANGE` during refill is converted to `-EAGAIN` so callers can fall back to direct getxattr.

## Test Signals
Cover cache hit/miss/refill, parallel refill races, lock match versus enqueue, cancellation/error paths, list buffer sizing, virtual project ID reads, encryption context insert/preserve, cache empty/destroy, malformed server replies, and failpoints for pause and allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_security.c -->
# sources/distributed-fs/lustre-release/lustre/llite/xattr_security.c

## Purpose
`xattr_security.c` handles Lustre security-label integration. It discovers which `security.*` xattr is managed by the active LSM, initializes create-time security contexts, stores or filters the context xattr name, and notifies the Linux security layer when server-provided contexts are applied.

## Important APIs, Types, And Functions
Public functions include `ll_dentry_init_security()`, `ll_inode_init_security()`, `ll_inode_notifysecctx()`, `ll_secctx_name_free()`, `ll_secctx_name_store()`, `ll_secctx_name_get()`, and `ll_security_secctx_name_filter()`. `ll_initxattrs()` is the callback passed to `security_inode_init_security()`.

## Control Flow
At mount/setup time, `ll_secctx_name_store()` asks the LSM for the security xattr name using `security_inode_listsecurity()`, validates the `security.` prefix, and stores it in `ll_sb_info`. Create paths call `ll_dentry_init_security()` or `ll_inode_init_security()` only when security xattrs are wanted. The dentry path asks `security_dentry_init_security()` for context bytes and validates returned xattr name on kernels that provide it. The inode path uses `security_inode_init_security()` with `ll_initxattrs()` to set each returned security xattr through the Lustre VFS setxattr wrapper.

## State And Persistence
The cached policy name is stored in `sbi->ll_secctx_name` and `ll_secctx_name_size`. Security context values themselves are server xattrs or LSM-managed inode state; this file only allocates temporary names/contexts and frees the cached name at teardown.

## Dependencies And Integration Points
The file depends on Linux LSM hooks, kernel-version compatibility around `lsm_context`, llite security/xattr predicates, `ll_vfs_setxattr()`, `LL_SBI_FILE_SECCTX`, and the security-name filter used by `xattr.c` and MDC packing.

## Risks And Edge Cases
Older kernels may not return the xattr name, so the code relies on SELinux conventions. Unsupported LSM hooks return success with no context. Name mismatches are rejected to avoid storing under a label Lustre did not request. `ll_inode_notifysecctx()` deliberately avoids `inode_lock()` to prevent a client deadlock.

## Test Signals
Test SELinux enabled/disabled, no LSM security xattr, name mismatch, create-time context setting, server-provided context notification, kernels with and without `lsm_context`, filtering of unmanaged security labels, and teardown freeing/replacing cached names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_security.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/Makefile -->
# sources/distributed-fs/lustre-release/lustre/mdc/Makefile

## Purpose
The MDC `Makefile` declares the Lustre Metadata Client kernel module object composition. It builds `mdc.o` from request, reintegration, procfs, library, lock, changelog, device, and batch metadata sources, with ACL support included conditionally.

## Important APIs, Types, And Functions
There are no C APIs here. Build variables are `obj-m`, `mdc-objs-y`, `mdc-objs-$(CONFIG_FS_POSIX_ACL)`, `mdc-objs`, and optional `GCOV_PROFILE`.

## Control Flow
Kbuild sees `obj-m += mdc.o`, expands `mdc-objs-y` into the module's component objects, appends `mdc_acl.o` when `CONFIG_FS_POSIX_ACL` is enabled, and assigns the final list to `mdc-objs`. If Lustre GCOV profiling is configured, it enables `GCOV_PROFILE := y` for this directory.

## State And Persistence
The file affects build-time module composition only. Its persistent output is the generated `mdc.o` kernel module and optional coverage instrumentation metadata.

## Dependencies And Integration Points
It ties together the MDC implementation files used by llite metadata operations, including `lproc_mdc.c`, `mdc_batch.c`, and optional `mdc_acl.c`. The conditional ACL object must match C preprocessor use of `CONFIG_FS_POSIX_ACL`.

## Risks And Edge Cases
Omitting an object breaks link-time symbol resolution for metadata operations or tunables. Enabling `mdc_acl.o` without POSIX ACL kernel support would fail compilation, while disabling it removes ACL unpacking support.

## Test Signals
Build with and without `CONFIG_FS_POSIX_ACL`, build with `CONFIG_GCOV_PROFILE_LUSTRE`, inspect `mdc.o` link inputs, and run metadata operations that exercise request, lock, changelog, batch, procfs, and ACL code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/lproc_mdc.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/lproc_mdc.c

## Purpose
`lproc_mdc.c` exposes MDC tunables and diagnostics through sysfs/lprocfs/debugfs. It lets operators inspect and change import activity, RPC concurrency, dirty/cache limits, checksums, DOM inline reply sizing, LSOM updates, grant shrink behavior, adaptive timeout parameters, and runtime statistics.

## Important APIs, Types, And Functions
Primary entry point is `mdc_tunables_init()`. Attribute handlers include `active_show/store`, `max_rpcs_in_flight_show/store`, `max_mod_rpcs_in_flight_show/store`, `max_dirty_mb_show/store`, `checksums_show/store`, `checksum_dump_show/store`, `dom_min_repsize_show/store`, `lsom_show/store`, grant shrink handlers, and grant byte readers. Seq/debugfs handlers include `mdc_cached_mb`, `mdc_unstable_stats`, `mdc_rpc_stats`, `mdc_batch_stats`, and `mdc_stats`.

## Control Flow
`mdc_tunables_init()` attaches the sysfs attribute group and debugfs variable table, sets up OBD lprocfs state, allocates metadata stats, attaches sptlrpc proc entries, and registers ptlrpc proc information. Store handlers parse booleans, integers, or memory sizes, then update `obd_import`, `client_obd`, OSC cache, or adaptive timeout fields under the appropriate locks. Seq write handlers clear histograms or shrink caches; seq show handlers print current counters and histograms.

## State And Persistence
State lives in `struct obd_device`, `struct client_obd`, `struct obd_import`, OSC stats, lprocfs histograms, and ptlrpc registration. Tunables persist for the lifetime of the MDC import/device and directly influence live RPC scheduling, dirty cache behavior, checksum use, grant shrinking, and debug counters.

## Dependencies And Integration Points
The file depends on `obd_class`, `lprocfs_status`, OSC cache/grant APIs, ptlrpc import state, sptlrpc proc attachment, cl environment allocation for LRU shrinking, and common Lustre attribute macros.

## Risks And Edge Cases
User input validation is critical because these knobs can throttle or disrupt metadata/data paths. Dirty limits are capped at one quarter RAM and maximum MB bounds. Import access must be protected by `with_imp_locked()` and reference helpers. Grant shrink toggling modifies import flags under spinlock.

## Test Signals
Test sysfs reads/writes for every attribute, invalid parse and range failures, active import toggling, RPC concurrency changes under load, dirty-cache shrink requests, checksum toggles, histogram reset/show, grant shrink interval updates, lprocfs setup failure unwinds, and concurrent reads while imports disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/lproc_mdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_acl.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_acl.c

## Purpose
`mdc_acl.c` unpacks POSIX ACL metadata from MDT replies into Linux `struct posix_acl` objects for llite metadata consumers.

## Important APIs, Types, And Functions
The single exported function is `mdc_unpack_acl(struct req_capsule *pill, struct lustre_md *md)`. It uses `struct mdt_body::mbo_aclsize`, request-capsule field `RMF_ACL`, `posix_acl_from_xattr()`, and `posix_acl_valid()`.

## Control Flow
If the MDT body reports zero ACL size, the function sets `md->posix_acl` to NULL and returns success. Otherwise it retrieves the exact-sized ACL buffer from the server capsule, converts the xattr-format bytes to a POSIX ACL object in the initial user namespace, validates the ACL, and stores it in `md->posix_acl`. Conversion or validation failures log an error and release partially built ACL state.

## State And Persistence
The function does not own persistent cache state. It transfers a referenced `struct posix_acl` to `lustre_md`; callers must release it according to Lustre metadata lifetime rules.

## Dependencies And Integration Points
It is compiled only when POSIX ACL support is enabled through the MDC Makefile. It integrates with MDT reply unpacking, llite inode preparation, Linux ACL conversion/validation helpers, and Lustre request capsules.

## Risks And Edge Cases
The MDT can legally set ACL-valid bits with zero ACL size, which must not be treated as protocol failure. Missing `RMF_ACL` with nonzero size is a protocol error. Invalid ACL data must be rejected before reaching VFS inode state.

## Test Signals
Cover replies with no ACL, valid access/default ACLs, missing ACL capsules, malformed xattr bytes, invalid ACL entries, memory allocation failures in conversion, and caller cleanup of returned ACL references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_batch.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_batch.c

## Purpose
`mdc_batch.c` implements client-side packing and interpretation for batched metadata getattr updates. It lets llite statahead aggregate many getattr intent requests into batch RPCs while preserving LDLM lock enqueue semantics and callback delivery.

## Important APIs, Types, And Functions
Public entry point is `mdc_batch_add()`. Internal helpers include `mdc_ldlm_lock_pack()`, `mdc_batch_getattr_pack()`, `mdc_batch_getattr_interpret()`, and opcode dispatch tables `mdc_update_packers[]` and `mdc_update_interpreters[]` indexed by `MD_OP_GETATTR`.

## Control Flow
`mdc_batch_add()` validates the metadata opcode, allocates a sub-request capsule, and delegates to `cli_batch_add()`. Packing initializes an `RQF_BUT_GETATTR` subrequest, sizes the name and optional security-context-name field, writes the LDLM intent, calls `mdc_getattr_pack()`, creates and packs an LDLM inodebits lock request with lookup/update policy, declares expected reply fields for layout, ACL, default LMV, security context, and encryption context, and marks the subrequest opcode `BUT_GETATTR`. Interpretation rebuilds the reply capsule, finalizes LDLM enqueue, normalizes lock reply status, calls `mdc_finish_enqueue()`, then invokes the original item callback.

## State And Persistence
Per-item state is carried in `struct md_op_item`: op data, lookup intent, enqueue info, lock flags/handle, callback, and allocated sub-pill. Batch-level state is in `struct batch_update_head` and lower `lu_batch`; this file does not persist state beyond request completion.

## Dependencies And Integration Points
It integrates with MDC getattr packing, LDLM client enqueue/finish, batch update infrastructure, security context name forwarding, encryption-context fetching for encrypted connections, ACL maximum sizing, DOM glimpse callback setup, and llite statahead's `sa_getattr()` batching path.

## Risks And Edge Cases
Subrequest size is checked against remaining batch space and returns `-E2BIG` when too large. Unsupported opcodes return `-EFAULT`. The glimpse callback is installed before enqueue to avoid Data-on-MDT races. Security and encryption reply sizing must match server capabilities and intent operation bits.

## Test Signals
Test batched statahead getattr with and without security/encryption context requests, batch full `-E2BIG`, unsupported opcodes, LDLM enqueue failures, callback error propagation, DOM glimpse callback behavior, ACL/default-MEA reply sizing, and mixed batch/non-batch statahead operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_batch.c -->
