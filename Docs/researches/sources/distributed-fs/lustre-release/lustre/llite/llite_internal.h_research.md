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
