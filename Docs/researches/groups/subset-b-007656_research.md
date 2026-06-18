# Research Group: subset-b-007656

This grouped report covers the Lustre llite client superblock, inode, mmap, and NFS export code assigned to `subset-b-007656`. Each section preserves its source path for reconciliation into the final source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_internal.h -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_internal.h

## Purpose

`llite_internal.h` is the central private interface for Lustre's llite client filesystem layer. It defines the in-memory per-dentry, per-inode, per-superblock, per-file, readahead, statahead, CLIO, mmap, xattr, layout, project quota, encryption, foreign symlink, and NFS-export-facing state used by the llite implementation files. It also declares most llite-local entry points that connect VFS operations to the metadata client, object client, LDLM locking, page cache, persistent client cache, crypto, quota, and export subsystems.

The header is not just declarations. It embeds important locking helpers and policy predicates, including the custom truncate semaphore used to avoid mmap-lock/truncate-lock deadlocks, dentry invalidation helpers, layout generation accessors, ACL cache ownership helpers, mount capability predicates, file-size and directory-striping helpers, metadata operation builders, and ioctl/statfs/export prototypes.

## Important APIs, Types, And Functions

- `struct ll_dentry_data`: dentry-private state containing statahead generation and an invalid bit. `set_lld_invalid()`, `d_lustre_invalid()`, `d_lustre_invalidate()`, and `d_lustre_revalidate()` update or inspect this state under RCU/dentry locking.
- `struct ll_inode_info`: llite's inode extension. It stores the Lustre FID, project id, open handles and open counts, cached MDS timestamps, layout generation, xattr cache lists, CL object pointer, page invalidation seqlock, and a directory/file union. Directory state includes statahead state, directory depth, LMV stripe/default layout objects, and lock protection. File state includes range locks, size/setattr/truncate locks, glimpse state, async write errors, heat counters, job info, PCC state, group lock state, cached lazy size/block values, and symlink storage.
- `struct ll_trunc_sem` plus `trunc_sem_down_read_nowait()`, `trunc_sem_down_read()`, `trunc_sem_down_write()`, and matching unlock helpers: a specialized read/write exclusion primitive used around truncate and I/O paths. The nowait reader intentionally bypasses waiting writers for page-fault paths that already hold `mmap_lock`.
- `enum ll_file_internal_flags`: per-inode flags for modified data, restore state, xattr cache validity, project inheritance, atime update behavior, foreign-removal policy, ACL validity, and xattr-cache fill state.
- `struct ll_sb_info`: llite's superblock-private state. It tracks MDT/OST exports and devices, connect capabilities, feature flags, root FID, read-ahead limits/workqueue, client page cache, debugfs/sysfs state, stats, statahead counters and tunables, clustered-NFS device identity, root squash state, statfs caching, file heat settings, open-lock caching thresholds, hybrid I/O thresholds, filesystem name, PCC superblock, foreign symlink config, security-context xattr name, user principal, project statfs cache table, and SSK key id.
- `struct lustre_client_ocd`: mount-wide connect flag aggregation across imports, updated by `cl_ocd_update()`.
- Readahead and statistics types: `struct ll_ra_info`, `struct ll_readahead_state`, `struct ra_io_arg`, `struct ll_readahead_work`, process extent histograms, and operation counter enum values.
- `struct ll_file_data`: file-private state for open handle, lease handle, read-ahead state, partial readdir result, mirror/resync selection, group lock, PCC file state, and per-process statahead.
- Statahead types: `enum ll_sa_pattern`, `struct ll_statahead_info`, and `struct ll_statahead_context`, with `dentry_may_statahead()` deciding whether lookup/revalidation should interact with the statahead cache.
- CLIO bridge types: `struct vvp_io_args`, `enum lcc_type`, `struct ll_cl_context`, `struct ll_thread_info`, `ll_env_info()`, `ll_env_args()`, and `ll_io_init()`.
- Mount/feature helpers: `ll_need_32bit_api()`, `ll_sbi_has_fast_read()`, `ll_sbi_has_tiny_write()`, `ll_sbi_has_file_heat()`, `ll_sbi_has_foreign_symlink()`, `ll_sbi_has_parallel_dio()`, `ll_sbi_has_unaligned_dio()`, and encryption/security connect-flag helpers.
- Major declared integration entry points include `ll_fill_super()`, `ll_put_super()`, `ll_kill_super()`, `ll_update_inode()`, `ll_prep_inode()`, `ll_prep_md_op_data()`, `ll_finish_md_op_data()`, `ll_setattr_raw()`, `ll_statfs_internal()`, `ll_file_mmap()`, `ll_filemap_fault()`, `lustre_export_operations`, and many file, directory, xattr, layout, HSM, quota, crypto, PCC, and foreign-file functions.

## Control Flow

The header organizes llite around VFS objects. Superblock setup creates and fills `ll_sb_info`, connects MDT/OST exports, then stores llite operation tables on the VFS superblock. Inode creation and update paths populate `ll_inode_info`, attach a CL object for regular files, and attach directory LMV state for directories. File open paths allocate `ll_file_data`, which becomes the shared anchor for read-ahead, open handles, mirror selection, group locks, and PCC decisions. Mmap and buffered/direct I/O paths move through CLIO context helpers and update per-inode/per-file counters.

Metadata operations generally build `struct md_op_data` with FIDs, names, directory layout objects, supplementary groups, project id, flags for 32-bit API or 64-bit hashes, and optional encrypted filename/security context information. The matching finish helper releases layout references, security contexts, encrypted names, and operation storage.

Locking flow is explicit in the type layout. Directory layout objects are guarded by `lli_lsm_sem`; file sizes and KMS are guarded by `lli_size_mutex`; layout generation by `lli_layout_lock`; open handles by `lli_och_mutex`; xattr cache lists by `lli_xattrs_list_rwsem` and `lli_xattrs_enq_lock`; job info by seqlock; and page invalidation by `lli_page_inv_lock`. The truncate semaphore is documented as a deliberate workaround for reversed `mmap_lock` and truncate lock acquisition orders.

## State And Persistence Behavior

The header defines in-memory client-side state rather than on-disk formats. Persistent effects happen through declared operations in implementation files: metadata RPCs to MDTs, object updates to OSTs, xattr/security/encryption contexts, project quota state, HSM dirty flags, and layout updates. Locally, llite caches negotiated capabilities, ACLs, xattrs, directory stripe/default-layout objects, readahead windows, statfs/project-statfs results, PCC attachment state, foreign symlink policy, and per-file/per-process statistics.

Several fields intentionally mirror authoritative server state with validity bits: cached timestamps, `lli_attr_valid`, lazy encrypted-file sizes, ACL validity, xattr-cache fill state, layout generation, and connect capability flags. Code using this header must preserve those validity semantics because stale metadata can otherwise leak into VFS attributes, layout decisions, or RPC packing.

## Dependencies And Integration Points

The header depends on Lustre core headers (`obd.h`, `lustre_disk.h`, `lustre_lmv.h`, `lustre_mdc.h`, `lustre_intent.h`, `lustre_crypto.h`), CL object interfaces, range locks, Linux VFS/mm/aio/parser/compat APIs, and llite-local `vvp_internal.h`, `pcc.h`, and `foreign_symlink.h`.

It is the integration surface for `llite_lib.c`, directory/namei/file/rw/xattr/glimpse/statahead/crypto/foreign modules, LDLM blocking callbacks, `md_*` metadata RPC operations, CLIO object/page operations, PCC, llcrypt, NFS export operations, debugfs/lprocfs/sysfs tunables, and quota/project-statfs handling.

## Risks And Edge Cases

- The file has many kernel-version and config-condition branches. API compatibility macros for user namespaces, ACL prototypes, read folios, fileattr, crypto, and filldir behavior must be tested across supported kernels.
- `struct ll_inode_info` uses a directory/file union. Callers must only access the matching side after checking inode type.
- The custom truncate semaphore solves a real deadlock but can starve truncate behind heavy mmap fault traffic.
- Many helpers return borrowed pointers or require external lifetime rules, especially superblock exports, CL objects, LMV objects, ACLs, PCC state, and `file->private_data`.
- Dentry invalidation uses RCU plus dentry locks. Missing `d_fsdata` or racing teardown must remain harmless.
- Metadata operation setup owns encrypted names, security contexts, and LMV references; every error path must call `ll_finish_md_op_data()` when ownership has been transferred.
- Feature predicates depend on negotiated mount flags, not just build-time availability.

## Test Signals

Useful test signals include mount option parsing and display for every `ll_sbi_flags` token, negotiated enable/disable of ACL/xattr/encryption/fast-read/hybrid-DIO capabilities, inode initialization for regular files, directories, symlinks, and special nodes, directory LMV updates and inheritance, project quota statfs caching, dentry invalidation/revalidation, truncate-vs-mmap fault stress, `md_op_data` cleanup under encrypted filenames and security contexts, and build coverage across ACL, crypto, fileattr, user namespace, and folio compatibility variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_lib.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_lib.c

## Purpose

`llite_lib.c` implements the main Lustre llite client superblock and inode support. It initializes and frees `ll_sb_info`, parses llite mount options, connects the mount to MDT and OST client devices, negotiates capabilities, creates the root inode, wires VFS operation tables, handles unmount teardown, updates inodes from Lustre metadata replies, manages directory LMV layout state, performs setattr/truncate coordination across MDT and OST/PCC state, implements statfs/project-statfs, provides common ioctls, builds metadata RPC operation descriptors, and supports parent/link lookup helpers used by user APIs.

This file is the bridge between Linux VFS lifecycle and Lustre's remote metadata/data services. It owns most mount-time and inode-time state transitions for llite.

## Important APIs, Types, And Functions

- `struct proj_sfs_cache`: per-project cached `kstatfs` entry stored in `ll_sb_info::ll_proj_sfs_htable`.
- `ll_init_sbi()` and `ll_free_sbi()`: allocate/free superblock-private state, including PCC, readahead workqueue, CL client cache, foreign symlink defaults, root squash state, feature defaults, statfs/project cache, file heat/open-cache defaults, and tunables.
- `client_common_fill_super()`: core mount connection routine. It connects to the MDT, fetches statfs and root FID, validates required server features, adapts local flags, connects to the OST/LOV stack, initializes CL state, creates the root inode, installs superblock operation tables, export operations, xattr handlers, crypto ops, sysfs links, clustered-NFS `s_dev`, and read-ahead limits.
- `ll_options()`: parses llite mount options into `ll_sbi_flags` and related values such as foreign symlink prefix, user principal, checksum selection, dummy encryption, SSK key id, flock mode, lazy statfs, user xattrs, and statfs-project behavior.
- `ll_fill_super()`, `ll_put_super()`, `client_common_put_super()`, and `ll_kill_super()`: VFS mount/unmount entry points. They process config logs, create per-instance OBD names, register debugfs, connect/disconnect devices, wait for statahead shutdown, restore clustered-NFS device numbers, clean OBD devices, free crypto policy, and purge CL env caches.
- `ll_lli_init()`, `ll_read_inode2()`, `ll_update_inode()`, `ll_clear_inode()`, `ll_delete_inode()`: inode initialization, update, final writeback/discard, and teardown.
- Directory layout helpers: `ll_iget_anon_dir()`, `ll_init_lsm_md()`, `ll_update_default_lsm_md()`, `ll_update_lsm_md()`, `ll_dir_default_lmv_inherit()`, and `ll_update_dir_depth_dmv()`.
- Attribute and truncate path: `ll_md_setattr()`, `ll_io_zero_page()`, `volatile_ref_file()`, `ll_setattr_raw()`, and `ll_setattr()`.
- Statfs APIs: `ll_statfs_internal()`, `ll_statfs_project()`, `ll_statfs()`, and `ll_obd_statfs()`.
- File attribute/ioctl helpers: `fileattr_get()`, `fileattr_set()`, `ll_fileattr_get()`, `ll_fileattr_set()`, `ll_iocontrol()`, `ll_flush_ctx()`, `ll_umount_begin()`, `ll_open_cleanup()`.
- Metadata operation helpers: `ll_prep_md_op_data()`, `ll_finish_md_op_data()`, and `ll_unlock_md_op_lsm()`.
- User data helpers: `ll_copy_user_md()`, `ll_compute_rootsquash_state()`, `ll_getparent()`, `ll_get_obd_name()`, and `ll_get_sb_uuid()`.

## Control Flow

Mount starts in `ll_fill_super()`. It allocates config state, creates `ll_sb_info` with defaults, parses mount options, sets default dentry operations, generates a per-mount UUID, derives the Lustre fsname, renames the SSK key, configures the backing device info, registers debugfs, processes the Lustre config log, resolves profile MDT/OST names, appends the per-superblock instance id, and calls `client_common_fill_super()`.

`client_common_fill_super()` first connects the metadata export with a large set of MDT feature flags. It handles MDT/fileset `-EROFS` by forcing a read-only retry, validates the root FID and required connect flags, fetches final connect data, sets VFS superblock limits, and updates client feature bits based on server support. It then connects the data export with OST feature flags and checksum/grant settings, updates aggregate connect flags, installs VFS operations, fetches root metadata, initializes CL state, constructs the root inode with `ll_iget()`, handles root security/encryption context, applies checksum settings, creates `s_root`, changes `s_dev` to a hash of the MDT UUID for clustered NFS, computes whole-file readahead limits, and creates sysfs links.

Unmount flow calls `ll_put_super()`. It ends config logs, marks matching OBD devices forced when needed, disconnects MDT/OST if mount setup completed, cleans up SSK keys and OBD devices, unregisters BDI/debugfs state, frees dummy crypto policy and `ll_sb_info`, calls common Lustre super teardown, and purges CL env caches. `ll_kill_super()` handles early kill-super behavior and waits for running statahead references before final teardown.

Inode update flow starts with a Lustre metadata reply. `ll_prep_inode()` decodes `lustre_md`, either updates an existing inode or calls `ll_iget()` for a new one, applies piggyback layout locks only when an intent lock contains layout state, updates default LMV deletion, applies foreign-file policy, and cleans up open handles if an open reply cannot be consumed. `ll_update_inode()` initializes CL file state when EA size is present, updates directory LMV state, replaces ACL cache, updates VFS inode number/generation/timestamps/mode/owner/project/link/rdev/FID/size/block fields, preserves lazy plaintext size for encrypted files without keys, and tracks HSM restore state.

Setattr flow uses `ll_setattr()` for VFS validation and encryption preparation, then `ll_setattr_raw()`. The raw path validates size against VFS and Lustre limits, sets missing ctime/mtime/atime values, drops the inode lock for regular files before the MDT RPC, always asks the MDT to authorize the change, updates local inode metadata from the reply, and then updates PCC or OST attributes for regular files. Encrypted truncates may zero the tail page through CLIO before OST setattr. Restored files may need a follow-up HSM dirty-state RPC.

Statfs flow asks MDT first, optionally asks OSTs when the MDT did not return a summed result, merges block/object/free counts, downshifts values on 32-bit kernels, and optionally clips results by project quota using cached quota-derived limits.

## State And Persistence Behavior

Persistent state is remote. Mount setup changes server-side connection state and negotiates capabilities with MDT/OST imports. Metadata mutations go through MDT RPCs; size, time, flag, and truncation effects for regular files are propagated to OSTs or PCC depending on cache state. HSM dirty flags, project inheritance, xattrs, security/encryption context names, directory layouts, and linkEA data are all server-backed.

Client-local state includes mount flags, feature negotiation results, root FID, read-ahead workqueue/cache, statfs and project-statfs caches, PCC state, foreign symlink configuration, security context xattr name, root squash match result, open and layout caches, inode ACL/xattr/LMV state, and VFS inode fields. The file explicitly changes `sb->s_dev` to a stable hash for clustered NFS and restores the original value during kill-super.

## Dependencies And Integration Points

`llite_lib.c` depends on Linux VFS, mm, statfs, uid/gid, fileattr, key, and ioctl APIs; Lustre OBD connect/statfs/info/ioctl/disconnect APIs; MGC config logs; MDC/LMV/LOV metadata and layout interfaces; CL object/page/cache APIs; LDLM layout locks; PCC; llcrypt; root squash/NID utilities; lprocfs/debugfs/sysfs; quota ioctls; linkEA parsing; HSM; and llite-local file, dir, xattr, namei, mmap, NFS, foreign, and crypto modules.

It exports `lustre_super_operations` consumers through the header and installs `lustre_export_operations` for NFS export when stack size allows. It also communicates with userspace through ioctl payloads, mount options, statfs, and copied user LOV metadata.

## Risks And Edge Cases

- Mount setup has many partial-failure labels. Resource ownership across MDT connect, OST connect, CL init, root inode creation, sysfs links, and allocated buffers must stay balanced.
- Feature negotiation can silently disable requested features such as xattr cache, ACLs, encryption, name encryption, and hybrid I/O depending on server replies.
- `ll_setattr_raw()` deliberately unlocks and later relocks regular inodes around network operations; races with truncation, DIO, HSM restore, PCC, and encrypted tail-zeroing are high-risk.
- Directory LMV updates reject non-monotonic layout versions for striped directories. Tests should cover split/merge/restripe and stale reply races.
- `ll_prep_md_op_data()` owns encrypted names, security contexts, and LMV references. Missing finish calls leak or double-free state.
- Project statfs caching can return stale quota-clipped capacity until `ll_statfs_max_age` expires.
- `ll_dirty_page_discard_warn()` cannot drop dentries synchronously because it may be called in ptlrpc/page-completion contexts, so it schedules deferred `dput()`.
- `ll_umount_begin()` force-marks exports and waits only heuristically for unmount readiness.

## Test Signals

Useful tests include successful mount/unmount, read-only retry on MDT/fileset `-EROFS`, failed mount cleanup at each connection/root/CL/sysfs step, mount option parsing/display, server capability downgrades for ACL/xattr/encryption/hybrid I/O, root inode creation for normal and fileset mounts, directory LMV inheritance and layout-version conflicts, setattr/truncate on encrypted and unencrypted files, PCC setattr paths, HSM restored-file dirty handling, volatile encrypted migration without keys, statfs merging and 32-bit downshift, project quota statfs caching, ioctls for FID/path/name/UUID/encryption/project, forced unmount, open-cleanup after failed open consumption, and `md_op_data` cleanup under encrypted filename/security context combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_mmap.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_mmap.c

## Purpose

`llite_mmap.c` implements llite's VFS mmap integration. It installs Lustre-specific `vm_operations_struct` callbacks for page faults, page-mkwrite, VMA open, and VMA close; translates VM ranges into Lustre LDLM extent policies; initializes CLIO fault operations; cooperates with the persistent client cache; updates mmap/fault/write statistics; and handles races among page faults, truncation, page invalidation, lock cancellation, and dirty-page writeback.

The file is the entry point for memory-mapped reads and writes on Lustre files. It must preserve Linux VM semantics while acquiring Lustre locks and coordinating object-client I/O.

## Important APIs, Types, And Functions

- `policy_from_vma()`: converts a virtual address and byte count inside a VMA into an LDLM extent policy based on `vm_start` and `vm_pgoff`.
- `our_vma()`: scans VMAs under the caller-held mmap lock for a shared VMA using llite's `ll_file_vm_ops`.
- `ll_fault_io_init()`: creates and initializes a CLIO `CIT_FAULT` operation for a page index. It rejects nolock files, binds the fault to the inode CL object, records mmap read pattern flags, marks lock requirements mandatory, and stores `ll_file_data` in the VVP IO state.
- `__ll_page_mkwrite()`: CLIO-backed implementation for making an mmap page writable. It blocks all signals except `SIGKILL`/`SIGTERM`, runs the fault write operation, locks the page, detects truncation or dirty/writeback races, marks data modified, retries when needed, and delays after `-ENODATA` to reduce contention livelock.
- `to_fault_error()`: maps internal negative errors to `VM_FAULT_*` values.
- `ll_filemap_fault()`: wrapper around `filemap_fault()` that retries a SIGBUS result when `lli_page_inv_lock` changed during the fault.
- `__ll_fault()`: main read fault implementation. It tries fast page-cache fault when `LL_SBI_FAST_READ` is enabled, falls back to CLIO mandatory-lock fault, tracks CL mmap context, and propagates VM fault flags and pages.
- `ll_fault()`: public `.fault` callback. It gives PCC first chance, blocks nonfatal signals, bounds offsets by `MAX_LFS_FILESIZE`, retries pages invalidated under heavy contention, updates read/fault stats, and logs trace data.
- `ll_page_mkwrite()`: public `.page_mkwrite` callback. It gives PCC first chance, updates file time, loops over retryable write faults, maps errors to VM fault codes, and tallies write/mkwrite stats.
- `ll_vm_open()` and `ll_vm_close()`: VMA lifecycle callbacks. They increment/decrement `vvp_object::vob_mmap_cnt` for normal Lustre mappings or delegate to PCC VMA handlers for cached mappings.
- `ll_file_mmap()`: VFS `.mmap` implementation. It rejects nolock files, asks PCC to map cached files, calls `generic_file_mmap()`, installs llite VM ops, opens the VMA, glimpses size for non-PCC mappings, and tallies mmap latency.

## Control Flow

`ll_file_mmap()` is called when a file is mapped. It first rejects files opened with lock-ignoring semantics, then asks PCC whether the mapping should be served from a local cache copy. After `generic_file_mmap()` succeeds, it replaces `vma->vm_ops` with llite's operations, calls the open callback to track mmap count or PCC state, and performs a glimpse-size update for non-PCC mappings.

On read fault, `ll_fault()` delegates to PCC if the VMA is PCC-backed. Otherwise it blocks nonfatal signals and checks the page offset against the Lustre maximum file size. `__ll_fault()` then attempts a fast path when fast read is enabled: it temporarily forces retry-nowait semantics, adds an `LCC_MMAP` context without a CLIO operation, and calls `ll_filemap_fault()`. If the page cache cannot satisfy the fault cleanly, it initializes a CLIO `CIT_FAULT` operation, attaches VVP fault state, adds a mmap CL context, runs `cl_io_loop()`, removes the context, and returns the resulting page or fault flags. The wrapper verifies that a returned page is still mapped and has Lustre private state, retrying and eventually warning under persistent contention.

On write fault, `ll_page_mkwrite()` gives PCC first chance, updates file timestamps, and loops on `__ll_page_mkwrite()` while it reports a retry race. The internal function creates a write fault CLIO operation, blocks nonfatal signals, runs CLIO, locks the VM page, handles pages truncated out from under the fault, detects pages cleaned by ptlrpcd between unlock and mkwrite, and sets `LLIF_DATA_MODIFIED` on success. Public error mapping returns `VM_FAULT_LOCKED`, `VM_FAULT_NOPAGE`, `VM_FAULT_OOM`, `VM_FAULT_RETRY`, or `VM_FAULT_SIGBUS`.

VMA open and close maintain `vob_mmap_cnt` so lock cancellation and cache-pressure logic can account for active mmaps. PCC-backed VMAs use `vm_private_data` and are delegated to PCC callbacks.

## State And Persistence Behavior

The file does not persist data itself, but mmap writes modify page-cache and CL object state that is later flushed to OSTs. It updates inode flags (`LLIF_DATA_MODIFIED`), VVP object mmap counters, file timestamps through `file_update_time()`, VFS page state, CLIO page associations, PCC VMA state, and llite read/write/fault/mmap statistics.

Fault paths rely on `lli_page_inv_lock` to detect invalidation racing with filemap faults and on page private state to reject pages invalidated or truncated during the fault. The mmap count helps retain or avoid cancelling locks covering mapped ranges.

## Dependencies And Integration Points

`llite_mmap.c` integrates Linux VM fault APIs, mmap locking compatibility, filemap fault handling, page locking, signal masks, generic file mmap, and VMA iterators with Lustre CLIO (`cl_io_init`, `cl_io_loop`, `cl_io_fini`), VVP environment state, LDLM lock policy, PCC mmap/fault/mkwrite hooks, llite file-private data, inode feature flags, and lprocfs/rw statistics.

It depends on `ll_file_nolock()`, `ll_i2info()`, `ll_i2sbi()`, `ll_glimpse_size()`, `ll_cl_add()`, `ll_cl_remove()`, `ll_rw_stats_tally()`, and `ll_stats_ops_tally()` from the broader llite layer.

## Risks And Edge Cases

- Fault handling must never return an unlocked page as `VM_FAULT_LOCKED`; assertions check this but race coverage matters.
- The fast fault path temporarily mutates `vmf->flags`; it must restore caller-visible retry flags correctly.
- Page invalidation during `filemap_fault()` can otherwise produce a false SIGBUS, hence the seqlock retry wrapper.
- `page_mkwrite` races with truncation, ptlrpcd cleaning, and lock cancellation. It uses retry and `-ENODATA` delay to avoid tight livelock.
- Signal masking intentionally allows only administrative termination signals during fault/mkwrite.
- PCC-backed and normal mappings split behavior through `vm_private_data`; incorrect state can misroute VMA open/close or fault handling.
- `our_vma()` depends on caller-held mmap lock and compatibility iterator semantics.

## Test Signals

Useful tests include mmap read faults satisfied from page cache and CLIO, fast-read fallback on retry/error, mmap write faults under concurrent writeback, truncate racing with read and write faults, page invalidation producing SIGBUS retry instead of user-visible failure, PCC-backed mmap/fault/mkwrite, nolock files returning `-EOPNOTSUPP`, max-file-size SIGBUS, VMA open/close mmap count balance, heavy contention warning paths, and stats increments for mmap, fault, and mkwrite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_nfs.c -->
# sources/distributed-fs/lustre-release/lustre/llite/llite_nfs.c

## Purpose

`llite_nfs.c` implements NFS export support for Lustre llite. It encodes Lustre FIDs into export file handles, decodes file handles back into dentries, resolves parent handles, finds names for child dentries by scanning directories, assigns a stable clustered-NFS device id from the MDT UUID, and handles special `.lustre` and `.lustre/fid` objects used for FID-based access.

The file provides `lustre_export_operations`, which is installed on the superblock during mount when the kernel stack is large enough.

## Important APIs, Types, And Functions

- `get_uuid2int()`: hashes an MDT UUID string into a 32-bit value used by `llite_lib.c` to set a stable `s_dev` for clustered NFS exports.
- `search_inode_for_lustre()`: looks up an inode by Lustre FID. It first tries `ilookup5()` with `ll_test_inode_by_fid()`, then issues an MDT getattr by FID and builds/updates an inode with `ll_prep_inode()`.
- `ll_iget_for_nfs()`: converts a FID to a dentry for exportfs. It validates FID sanity, handles root FID, resolves normal objects through `search_inode_for_lustre()`, creates aliases with `d_obtain_alias()`, and special-cases `.lustre` and `.lustre/fid` dentries for `LU_DOT_LUSTRE_FID` and `LU_OBF_FID`. It also adjusts regular-file operations for `nfsd` kthreads to disable splice.
- `ll_encode_fh()`: encodes a `struct lustre_file_handle` containing child FID and optional parent FID into the NFS file-handle buffer and returns `FILEID_LUSTRE`.
- `do_nfs_get_name_filldir()` and `ll_nfs_get_name_filldir()`: directory fill callbacks that compare each `lu_dirent` FID to the target child FID and copy the matching name.
- `ll_get_name()`: implements exportfs `.get_name` by preparing metadata op data, reading the parent directory with `ll_dir_read()`, and returning the name matching the child inode FID.
- `ll_fh_to_dentry()` and `ll_fh_to_parent()`: decode Lustre export file handles into child or parent dentries.
- `ll_dir_get_parent_fid()`: asks the MDT for `".."` on a directory and extracts the returned parent FID.
- `ll_get_parent()`: exportfs `.get_parent` implementation using `ll_dir_get_parent_fid()` and `ll_iget_for_nfs()`.
- `lustre_export_operations`: exportfs operation table with `.get_parent`, `.encode_fh`, `.get_name`, `.fh_to_dentry`, and `.fh_to_parent`.

## Control Flow

NFS file-handle creation starts in `ll_encode_fh()`. It verifies the caller's buffer is large enough for `struct lustre_file_handle`, stores the child FID and optional parent FID, updates the word count, and returns Lustre's file-handle type. If the buffer is too small it returns `FILEID_INVALID` after reporting the needed size.

File-handle decode enters `ll_fh_to_dentry()` or `ll_fh_to_parent()`, validates the handle type, and calls `ll_iget_for_nfs()` with the relevant FID. Normal FIDs go through `search_inode_for_lustre()`: the local inode cache is checked first, then MDT getattr-by-FID retrieves metadata, and `ll_prep_inode()` constructs the inode. The resulting inode is wrapped with `d_obtain_alias()`.

Special FIDs need explicit dcache construction. For `.lustre`, `ll_iget_for_nfs()` looks up or allocates the `.lustre` child under the root and attaches the resolved inode. For the object-by-FID pseudo-directory, it ensures `.lustre` exists, then looks up or allocates the `fid` child and attaches the OBF inode. Locks on the root or `.lustre` inode serialize dentry construction.

Name lookup for exportfs uses `ll_get_name()`. It verifies the parent is a directory with file operations, builds `md_op_data`, locks the directory inode, calls `ll_dir_read()` with a filldir callback, unlocks, and returns `-ENOENT` if no directory entry FID matched the child.

Parent lookup uses `ll_dir_get_parent_fid()`, which prepares metadata op data for `".."`, calls `md_getattr_name()`, reads `RMF_MDT_BODY`, copies `mbo_fid1` if valid, and lets `ll_iget_for_nfs()` resolve that parent FID.

## State And Persistence Behavior

This file does not write persistent filesystem state. It creates and reuses VFS dentries/inodes to represent server-backed Lustre FIDs to exportfs and NFS. It can populate the local inode cache by fetching attributes from the MDT and can create dcache aliases for `.lustre` and `.lustre/fid` pseudo-objects. `get_uuid2int()` contributes to persistent export identity at the mount level by making `s_dev` stable across clients using the same MDT UUID.

The code also modifies in-memory regular-file operations for `nfsd` kthreads to select a no-splice file operations table, avoiding a kernel NFS/splice interaction. On older kernels it forces the open-lock caching threshold for NFS lookups.

## Dependencies And Integration Points

`llite_nfs.c` integrates Linux exportfs with Lustre FIDs, MDT getattr operations, llite inode preparation, directory reading, LDLM/name lookup helpers, dcache aliasing, and special Lustre FID constants such as root, `.lustre`, and OBF. It depends on `ll_get_default_mdsize()`, `md_getattr()`, `md_getattr_name()`, `ll_prep_inode()`, `ll_prep_md_op_data()`, `ll_finish_md_op_data()`, `ll_dir_read()`, `ll_select_file_operations()`, `cl_fid_build_ino()`, and `ll_need_32bit_api()`.

The export operation table is installed by `client_common_fill_super()` in `llite_lib.c`, and the stable `s_dev` hash is also used there for clustered NFS behavior.

## Risks And Edge Cases

- Stale NFS handles commonly refer to deleted or moved objects. The code suppresses noisy logs for failed getattr-by-FID and returns stale-style errors through exportfs.
- Special `.lustre` and OBF dentry construction manually allocates dentries and attaches inodes. Error paths must avoid leaking inode references or dentries.
- `ll_dir_get_parent_fid()` may receive replies without a valid parent FID; the comment notes MDTs may lose parent FID information, so callers must tolerate unresolved parents.
- `ll_get_name()` depends on directory entries carrying `lu_dirent` FIDs and uses container-style access to recover the enclosing record from the name pointer.
- File-handle buffer sizing is in 32-bit words and must match `struct lustre_file_handle`.
- Disabling splice for `nfsd` changes file operation selection for regular inodes resolved through NFS.

## Test Signals

Useful tests include NFS export handle encode/decode for regular files, directories, root, `.lustre`, and `.lustre/fid`; stale FID handling after unlink or MDT lookup failure; parent lookup for normal and remote/striped directories; `.get_name` over large and striped directories; small file-handle buffer behavior; clustered NFS clients producing the same `s_dev` from the same MDT UUID; nfsd regular-file operation selection with splice disabled; and error cleanup for failed dentry allocation or `.lustre` inode lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/llite_nfs.c -->
