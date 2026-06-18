# Group Research: group_1429_openzfs_sources_cow_pools_openzfs_module_os_linux_zfs_zio_crypt_c_s_8f2822710877

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zio_crypt.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zio_crypt.c

## Purpose
Implements OpenZFS block encryption and authentication mechanics for Linux/OpenZFS, including key initialization/wrapping, HKDF-derived data keys, IV/salt/MAC encoding in block pointers and ZIL headers, AEAD encrypt/decrypt execution, HMAC-based authentication for non-encrypted metadata, indirect MAC checksums, and special layouts for ZIL and dnode blocks.

## Main APIs and Data
- `zio_crypt_table[]` maps ZFS encryption function IDs to ICP mechanism names, crypt type, key length, and user-visible algorithm names.
- `zio_crypt_key_init()`, `zio_crypt_key_destroy()`, `zio_crypt_key_wrap()`, `zio_crypt_key_unwrap()` manage dataset crypto keys and wrapping-key AEAD.
- `zio_crypt_key_get_salt()` and `zio_crypt_key_change_salt()` rotate salts after `zfs_key_max_salt_uses`, defaulting to 400,000,000 uses.
- `zio_do_crypt_data()` and `zio_do_crypt_abd()` are the primary block encryption/decryption entry points.
- `zio_crypt_encode_params_bp()`, `zio_crypt_decode_params_bp()`, `zio_crypt_encode_mac_bp()`, `zio_crypt_decode_mac_bp()`, `zio_crypt_encode_mac_zil()`, and `zio_crypt_decode_mac_zil()` serialize cryptographic metadata into on-disk structures.
- `zio_crypt_do_objset_hmacs()` computes portable and local objset MACs.
- `zio_crypt_do_indirect_mac_checksum()` and `_abd()` compute or verify indirect-block SHA512 checksums over child MAC/auth metadata.

## Control Flow
Key initialization generates a key GUID, master key, HMAC key, and initial salt, derives the current encryption key via HKDF-SHA512, and opportunistically creates ICP context templates. Key unwrap performs AEAD decryption of stored master/HMAC key material using wrapping-key AAD containing GUID, crypt algorithm, and key version, then derives a fresh current data key.

Block encryption chooses the key by comparing the block salt to the cached current salt. Matching salts use `zk_current_key`; older salts derive a temporary key from the master key. For simple blocks, `zio_crypt_init_uios_normal()` creates plaintext/ciphertext UIOs. For ZIL and dnode blocks, custom parsers split encrypted payload from plaintext authenticated data. `zio_do_crypt_uio()` then dispatches AES-CCM or AES-GCM through ICP. Large normal blocks may use QAT acceleration, falling back to software on failure.

Authentication is layered. Level-0 encrypted blocks store AEAD MACs in checksum words. Authenticated-but-not-encrypted metadata uses HMAC-SHA512. Indirect blocks carry SHA512 digests of child MAC/portable blk_prop data. Objsets maintain separate portable and local MAC roots so raw sends can preserve portable authentication while local user-accounting data remains host-local.

## Integration Points
This file sits below DMU/ZIO logic and is consumed by block I/O, raw send/receive, dataset encryption, ZIL, dnode, objset, and scrub/claim paths. It depends on SPL/ICP crypto APIs, HKDF, SHA2, ABD buffer borrowing, DMU object type rules, block pointer encoding macros, and optional QAT acceleration.

## Invariants and Edge Cases
- AES-GCM/CCM IV uniqueness is enforced by salt rotation plus random 96-bit IVs for non-dedup blocks.
- Dedup derives salt and IV from HMAC(plaintext), intentionally exposing equality only where dedup already does.
- Byte-order handling is explicit because blkptrs and objsets may be byteswapped below this layer.
- ZIL leaves `zil_chain_t` and write/clone block pointers plaintext but authenticates them as AAD.
- Dnode blocks leave core dnode fields and block pointers plaintext, encrypting only encrypted bonus buffers.
- Version 0 compatibility affects authenticated blk_prop padding and nonportable masking.
- Notable review point: `zio_crypt_key_init()` assigns `zk_hmac_key.ck_data` differently from unwrap path, using `&key->zk_hmac_key` instead of `key->zk_hmac_keydata`; this is security-sensitive and should be checked against upstream intent.

## Risks and Testing Signals
Primary risks are cryptographic metadata drift, endian/portable-field mismatches, ZIL/dnode parser mistakes, salt rotation races, and fallback differences between QAT and software crypto. Coverage should include encrypted dataset read/write, raw send/receive, dedup encryption, ZIL replay/claim, dnode bonus encryption, objset MAC verification, cross-endian import, key rewrap/unwrap, and negative MAC corruption tests.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zio_crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_ctldir.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_ctldir.c

## Purpose
Provides Linux VFS operation tables and callbacks for ZFS control directories: `.zfs`, `.zfs/snapshot`, and `.zfs/shares`. These entries expose snapshots and share definitions through normal directory lookup/readdir while bridging to `zfsctl_*` internals.

## Main APIs and Data
- `zpl_fops_root` / `zpl_ops_root` implement `.zfs`.
- `zpl_fops_snapdir` / `zpl_ops_snapdir` implement `.zfs/snapshot`.
- `zpl_fops_shares` / `zpl_ops_shares` implement `.zfs/shares`.
- `zpl_common_open()` rejects write opens for control directories.
- `set_snapdir_dentry_ops()` installs automount/revalidate dentry operations for snapshot dentries.

## Control Flow
The root `.zfs` directory emits `.`/`..`, `snapshot`, and `shares` unless the control directory is disabled. Lookups delegate to `zfsctl_root_lookup()` and splice the returned inode into the dentry cache.

Snapshot lookup calls `zfsctl_snapdir_lookup()`, marks filesystem transaction context, and installs `DCACHE_NEED_AUTOMOUNT` plus custom dentry ops. Automount uses `zfsctl_snapshot_mount()` and returns `NULL` so the userspace mount collision path does not double-add the vfsmount. Snapshot readdir enumerates snapshots with `dmu_snapshot_list_next()` under DSL pool config locks and emits synthetic inode numbers. Snapshot mkdir/rmdir/rename map to snapshot create, remove, and rename operations via `zfsctl_snapdir_*`.

Shares lookup and iteration delegate either to `zfsctl_shares_lookup()` or, when a real shares directory is configured, to `zfs_zget()` and `zfs_readdir()` for that object. Attribute handlers return synthetic empty-directory stats when absent or real stats for the configured shares object.

## Integration Points
This file is the Linux-facing entry point for the cross-platform ZFS control directory implementation in `zfs_ctldir`. It relies on `zpl_enter()`/`zpl_exit()`, SPL fstrans markers, ZFS credentials, DSL snapshot listing, and kernel dentry automount behavior.

## Invariants and Edge Cases
- Control directories are read-only through `open`.
- Negative snapshot dentries are not trusted because snapshots may appear later.
- Existing snapshot mountpoint dentries are kept to avoid immediate automount/unmount churn.
- Kernel-version compatibility is handled for dentry op installation and idmapped getattr/mkdir/rename signatures.
- `.zfs/shares` gracefully behaves as an empty directory when `z_shares_dir == 0`.

## Risks and Testing Signals
Test snapshot listing, lookup, creation, deletion, rename, automount from multiple namespaces, `.zfs` disabled behavior, shares directory absence/presence, and compatibility with kernels where dentry ops must be modified directly.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_ctldir.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_export.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_export.c

## Purpose
Implements Linux `export_operations` for NFS/export support on ZFS, including file-handle encoding, resolving file handles back to dentries, parent lookup, reverse name lookup, and metadata commit.

## Main APIs and Data
- `zpl_export_operations` exposes `.encode_fh`, `.fh_to_dentry`, `.fh_to_parent`, `.get_name`, `.get_parent`, and `.commit_metadata`.
- `zpl_encode_fh()` packs ZFS `fid_t` data into Linux `struct fid` buffers, optionally appending a parent fid for subtree checking.
- `zpl_fh_to_dentry()` and `zpl_fh_to_parent()` reverse the encoding.
- `zpl_get_name()` and `zpl_get_parent()` provide NFS reverse traversal support.
- `zpl_commit_metadata()` maps NFS metadata commit to `zfs_fsync()`.

## Control Flow
Encoding computes the caller-provided buffer size, prepares an inline `fid_t`, calls either `zfsctl_fid()` or `zfs_fid()`, and updates `max_len` to the required rounded word count. If a parent inode is provided, its fid is packed immediately after the child fid and `FILEID_INO32_GEN_PARENT` is returned.

Decoding validates handle type and embedded lengths before calling `zfs_vget()`. `ENOENT` is translated to `ESTALE` so NFS clients retry lookups when cached file handles no longer point at the current object. Parent decoding slices the second embedded fid and reuses dentry decoding.

Name lookup locks the parent inode shared and calls `zfs_get_name()`. Parent lookup performs `zfs_lookup(..., "..")`. Metadata commit skips synthetic control nodes and fsyncs real ZFS inodes.

## Integration Points
This is NFS glue over ZFS vnode-style operations and ZFS control-directory special nodes. It uses SPL fstrans markers, credentials, inode locking, and Linux `d_obtain_alias()` for disconnected dentries.

## Invariants and Edge Cases
- Handle length validation prevents parsing past provided buffers.
- Control-directory nodes use `zfsctl_*` fid handling.
- Long names beyond Linux’s hardcoded export buffer can lead to `ESTALE`, as noted by the file comment.
- `zpl_commit_metadata()` is a no-op for control nodes.

## Risks and Testing Signals
Test NFS export with and without subtree checking, stale file handles after rename/delete/recreate, snapshot/control-directory exports, long filenames, parent handle decoding, and metadata commit behavior under sync errors.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_export.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file.c

## Purpose
Provides Linux file and address-space operations for regular files and directories on ZFS. It adapts VFS open/read/write/fsync/mmap/writeback/fallocate/ioctl/fadvise/splice/range-copy callbacks to ZFS vnode/DMU operations.

## Main APIs and Data
- `zpl_file_operations` implements regular-file operations.
- `zpl_dir_file_operations` implements directory file operations.
- `zpl_address_space_operations` implements page-cache operations needed primarily for mmap.
- `zpl_open()`, `zpl_release()`, `zpl_iter_read()`, `zpl_iter_write()`, `zpl_fsync()`, `zpl_mmap()`, `zpl_writepages()`, and `zpl_fallocate()` are the core callbacks.
- Ioctl handlers expose Linux flags, xflags/project IDs, DOS flags, generation, and ZFS rewrite support.
- Tunable `zfs_fallocate_reserve_percent` controls legacy fallocate capacity reservation inflation.

## Control Flow
Open first runs `generic_file_open()` then calls `zfs_open()`. Release marks atime dirty inodes before `zfs_close()`. Readdir delegates to `zfs_readdir()`.

Read/write iterators build `zfs_uio_t` wrappers around Linux `iov_iter`, translate `kiocb` flags to ZFS-style `O_*` flags, call `zfs_read()` or `zfs_write()`, update file offset by residual count, and update access time with ZFS relatime awareness.

Fsync first pushes dirty mmap/page-cache pages into the DMU/ZIL using `zpl_write_cache_pages()` in non-sync mode with `for_sync` semantics, then calls `zfs_fsync()`. Writeback similarly writes dirty pages to the DMU, optionally commits the ZIL once for `WB_SYNC_ALL`, then performs a second pass because non-sync page collection may not catch every dirty page.

Mmap is intentionally double-cached: ARC remains ZFS’s primary cache while Linux page cache backs mapped VM pages. `readpage`/`read_folio` fills page-cache pages from ZFS, and `writepage`/`writepages` pushes mmap-dirtied pages back through `zfs_putpage()`.

Fallocate supports punch-hole and zero-range via `zfs_space(F_FREESP)`. Allocation mode is emulated with capacity checks and optional size extension because persistent preallocation conflicts with COW semantics.

Ioctl paths translate Linux immutable/append/nodump/projinherit and xflags to ZFS `z_pflags`/xattrs via `zfs_setattr()`, expose project IDs, support DOS attributes, and call `zfs_rewrite()` for rewrite requests.

## Integration Points
This file ties Linux VFS to `zfs_vnops`, `zfs_znode`, DMU prefetch/evict, ZIL commit, project quota-aware `zfs_statvfs()`, Linux page-cache compatibility wrappers, file range cloning declarations, ACL/xattr-related setattr behavior, and kernel ioctl ABIs.

## Invariants and Edge Cases
- Generic direct_IO should never be reached; the callback panics because direct I/O is handled by read/write iterators.
- `zpl_fsync()` returns early on page flush errors because a later ZIL commit may not surface them reliably.
- `ZFS_SYNC_ALWAYS` forces sync writeback behavior.
- O_DIRECT, O_SYNC, O_DSYNC, and append are derived from `kiocb` flags when available.
- Fallocate reserve percentage `0` disables allocation-mode emulation.
- Setting immutable/append requires `CAP_LINUX_IMMUTABLE`; flag updates require owner/capability checks.
- Compat ioctl only maps 32-bit get/set version/flags.

## Risks and Testing Signals
Important tests include mmap read/write/fsync consistency, writeback error propagation, syncfs/fsync under suspended pool, fallocate modes and quota/project quota interactions, direct I/O read/write, fadvise prefetch/evict, ioctl flag races, project ID set/get, DOS flags, and rewrite permission checks.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file_range.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file_range.c

## Purpose
Implements Linux range-copy and reflink-style operations for ZFS block cloning. It maps `copy_file_range`, `FICLONE`, `FICLONERANGE`, and remap callbacks to `zfs_clone_range()` where possible, with generic copy fallback for `copy_file_range`.

## Main APIs and Data
- `zpl_clone_file_range_impl()` is the shared block-clone implementation.
- `zpl_copy_file_range()` attempts clone first, then falls back to generic byte-copy APIs when available and appropriate.
- `zpl_remap_file_range()` implements modern remap/reflink entry point.
- `zpl_clone_file_range()` supports older clone-file-range VFS API.
- `zpl_dedupe_file_range()` currently returns unsupported.

## Control Flow
The clone implementation checks the global block-clone tunable and destination pool feature flag `SPA_FEATURE_BLOCK_CLONING`. It locks source shared when source and destination differ, locks destination exclusive, holds credentials, marks fstrans, and calls `zfs_clone_range()` with mutable offsets/length. The returned cloned length may be shorter than requested.

`copy_file_range()` requires zero flags, tries clone, and falls back for `EOPNOTSUPP`, `EINVAL`, `EXDEV`, or `EAGAIN` depending on available kernel helper (`generic_copy_file_range`, `splice_copy_file_range`, or old-kernel `-EOPNOTSUPP` signaling).

`remap_file_range()` rejects unsupported flags, rejects dedupe, expands zero length to EOF, attempts clone, and enforces full-length cloning unless `REMAP_FILE_CAN_SHORTEN` is set. The older `clone_file_range()` similarly requires full cloning.

## Integration Points
This file bridges Linux file-range APIs to ZFS block cloning in `zfs_vnops` and feature detection in `zfeature`. It is referenced by `zpl_file_operations`.

## Invariants and Edge Cases
- Destination pool must have block cloning enabled.
- Dedupe is explicitly unsupported.
- Zero-length clone/remap means clone from offset to EOF.
- Short clones are valid only where the VFS API allows shortening.
- Copy fallback behavior depends on kernel version/configuration.

## Risks and Testing Signals
Test cross-filesystem failures, same-file cloning, dirty data causing shortened clones, old and new kernel VFS entry points, copy fallback correctness, feature-disabled behavior, and unsupported dedupe requests.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_file_range.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_inode.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_inode.c

## Purpose
Provides Linux inode operation callbacks for ZFS files, directories, symlinks, and special nodes. It adapts lookup, create, mkdir, mknod, tmpfile, unlink, rmdir, rename, symlink, hardlink, getattr, setattr, ACL, and listxattr callbacks to ZFS vnode operations.

## Main APIs and Data
- `zpl_inode_operations`, `zpl_dir_inode_operations`, `zpl_symlink_inode_operations`, and `zpl_special_inode_operations` are exported operation tables.
- `zpl_lookup()` handles name lookup, longname policy, and case-insensitive dentry insertion.
- `zpl_vap_init()` prepares ZFS `vattr_t` creation attributes with idmap-aware UID/GID mapping and setgid inheritance.
- Creation paths include `zpl_create()`, `zpl_mknod()`, `zpl_tmpfile()`, `zpl_mkdir()`, and `zpl_symlink()`.
- Namespace mutation paths include `zpl_unlink()`, `zpl_rmdir()`, `zpl_rename2()`, and `zpl_link()`.
- Attribute paths include `zpl_getattr_impl()` and `zpl_setattr()`.

## Control Flow
Lookup enforces current longname settings: it rejects too-long create/rename targets while allowing access to existing long names when feature state permits. Case-insensitive datasets request the real name from `zfs_lookup()` and use `d_add_ci()` when the returned spelling differs.

Creation callbacks allocate `vattr_t`, initialize owner/group/mode, call the relevant ZFS create operation, then initialize security xattrs and POSIX ACLs. If post-create initialization fails, they remove the object, remove it from inode hash, and drop the inode. Tmpfile uses `zfs_tmpfile()` and wires the result into Linux’s tmpfile machinery.

Unlink/rmdir call ZFS remove operations and invalidate dentries on case-insensitive datasets to avoid negative dentry poisoning. Rename supports `RENAME_WHITEOUT` by creating a whiteout `vattr_t` for ZFS. Symlink creation mirrors file creation but omits ACL initialization. Hardlink checks `ZFS_LINK_MAX`, bumps ctime, grabs an inode ref, calls `zfs_link()`, and instantiates the new dentry.

Getattr uses `zfs_getattr_fast()` and conditionally populates Linux statx fields for birth time, NFS change cookie, direct-I/O alignment, and immutable/append/nodump attributes. Setattr validates with kernel helpers, converts idmapped UID/GID values, updates atime early when requested, calls `zfs_setattr()`, and adjusts POSIX ACLs after chmod.

## Integration Points
This is the central Linux VFS-to-ZFS namespace adapter. It depends on `zfs_vnops`, `zfs_znode`, ZFS idmap helpers, ACL/xattr initialization from `zpl_xattr.c`, SPL fstrans markers, Linux statx support, and kernel signature compatibility macros.

## Invariants and Edge Cases
- Longname constraints use both old `ZAP_MAXNAMELEN` and new `ZAP_MAXNAMELEN_NEW`.
- Case-insensitive filesystems avoid negative dentries after failed lookups and invalidated deletes.
- Setgid directories propagate group and setgid bit to subdirectories.
- Post-create security/ACL failure attempts to cleanly remove partially created objects.
- Symlink read rejects RCU path-walk by returning `-ECHILD` when no dentry is available.
- Change cookie combines ctime seconds and znode sequence to satisfy NFS monotonicity expectations.

## Risks and Testing Signals
Test longname feature toggles, case-insensitive lookup/delete/create, idmapped mounts, tmpfile behavior, security xattr and ACL failure cleanup, whiteout renames, statx change-cookie behavior under NFS, symlink reads, chmod ACL updates, and hardlink limit handling.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_super.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_super.c

## Purpose
Implements Linux superblock, filesystem type, fs_context, mount/remount, statfs, sync, inode lifecycle, dentry-cache, and mount-option behavior for ZFS.

## Main APIs and Data
- Tunables `zfs_delete_inode` and `zfs_delete_dentry` control inode/dentry cache retention.
- `zpl_super_operations` provides inode allocation/destruction, dirtying, drop/evict, unmount, sync, statfs, and mount display callbacks.
- `zpl_fs_context_operations` provides option parsing, mount tree creation, reconfigure, duplicate, and free callbacks.
- `zpl_fs_type` registers the ZFS filesystem type.
- `zpl_param_spec[]` defines accepted mount options.

## Control Flow
Inode allocation delegates to `zfs_inode_alloc()` and initializes i_version. Dirty inode callback pushes Linux inode changes into ZFS system attributes. Drop inode either uses normal generic caching or immediate deletion based on tunable. Eviction truncates pages, clears inode state, and calls `zfs_inactive()`.

Unmount calls `zfs_umount()` through `put_super`; `kill_sb` performs `zfs_preumount()` then `kill_anon_super()`. Sync wraps `zfs_sync()` and contains compatibility handling for older kernels where `syncfs()` ignored `sync_fs()` errors, using `s_wb_err` or waiting for TXG sync as needed. Statfs adapts `zfs_statvfs()` and scales block/file counts for 32-bit callers.

Mount option parsing handles Linux common options, ZFS-specific temporary options, SELinux passthrough, sloppy unknown-option behavior, snapshot mountpoint data, and legacy strings produced by mount tools. For kernels with forbidden sb flags in monolithic parsing, `zpl_parse_monolithic()` splits options itself so ZFS can still see options like `atime`, `dev`, `exec`, and `suid`.

`zpl_get_tree()` holds the named objset, uses `sget()` with `zpl_test_super()` to avoid duplicate mounts, rechecks the objset under ZFS enter locks, calls `zfs_domount()` for new superblocks, and rejects incompatible ro/rw multimounts for non-snapshots. Remount delegates to `zfs_remount()` and transfers ownership of parsed `vfs_t` options on success.

## Integration Points
This file is the kernel mount lifecycle bridge into `zfs_vfsops`, `zfs_znode`, DMU objset holding, DSL dataset long holds, Linux fs_context parsing, Linux superblock shrink/prune behavior, and mount option presentation in `/proc/self/mounts`.

## Invariants and Edge Cases
- DSL pool lock is released before `sget()` to avoid deadlocks with superblock teardown.
- Existing superblocks are revalidated against current `z_os` because rollback/unmount can race.
- Snapshot mounts are always effectively readonly and bypass one ro/rw conflict check.
- Mount options are deliberately permissive to preserve OpenZFS mount helper compatibility.
- Unknown options emit kernel notices rather than hard failure.
- `fc->fs_private` ownership transfers to `zfsvfs` on successful mount/remount.
- Dentry deletion tunable trades lookup overhead for lower inode/dbuf/ARC pinning.

## Risks and Testing Signals
Test mount/remount option compatibility across old/new kernels, duplicate mounts, rollback races, snapshot automount options, syncfs error reporting on older kernels, 32-bit statfs scaling, immediate inode/dentry deletion tunables, idmapped mount flags, and cleanup of fs_context allocation/dup/free paths.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_super.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_xattr.c -->
# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_xattr.c

## Purpose
Implements Linux extended attribute and POSIX ACL support for ZFS. It bridges Linux name/value xattrs to either ZFS directory-based xattrs or SA/spill-block xattrs, handles namespace-specific permissions, initializes security labels, stores POSIX ACLs as xattrs, and provides compatibility behavior for legacy unprefixed user attributes.

## Main APIs and Data
- `zpl_xattr_handlers[]` exports security, trusted, user, and optional POSIX ACL handlers.
- `zpl_xattr_list()` lists visible xattrs from SA storage and xattr directories.
- `zpl_xattr_get()` and `zpl_xattr_set()` are shared internal get/set engines.
- Directory storage helpers: `zpl_xattr_list_dir()`, `zpl_xattr_get_dir()`, `zpl_xattr_set_dir()`.
- SA storage helpers: `zpl_xattr_list_sa()`, `zpl_xattr_get_sa()`, `zpl_xattr_set_sa()`.
- POSIX ACL entry points include `zpl_set_acl()`, `zpl_get_acl()`, `zpl_init_acl()`, and `zpl_chmod_acl()`.
- Tunable `zfs_xattr_compat` controls whether new user xattrs are written in legacy unprefixed format.

## Control Flow
Listing creates an `xattr_filldir_t`, enters the zfsvfs/znode, takes `z_xattr_lock`, lists SA xattrs first when enabled, then lists xattr-directory entries. Each candidate name is filtered by `zpl_xattr_permission()`, which dispatches to namespace handlers and maps unknown non-FreeBSD names into the Linux `user.` namespace for compatibility.

Get first tries SA storage when dataset/znode state allows it. If the name is absent there, it falls back to the xattr directory. Directory get looks up the hidden xattr directory, then the attribute object, checks size, and reads with `zfs_read()`. SA get loads cached nvlist data with `zfs_sa_get_xattr()` and returns byte-array values.

Set takes the writer xattr lock and first determines whether the name exists in SA, directory, both, or neither so `XATTR_CREATE`/`XATTR_REPLACE` semantics are honored. It prefers SA when configured and possible, removes stale duplicates from the other backend after successful writes, and falls back to directory storage when SA size limits are exceeded or unsupported. Directory set creates/removes/truncates hidden xattr files and updates parent ctime/dirty state. SA set mutates the cached nvlist and persists through `zfs_sa_set_xattr()`, dropping the cache on error.

Namespace handlers apply Linux xattr rules:
- `user.*` requires dataset xattr support and rejects forbidden namespace forms; get tries prefixed then unprefixed for compatibility; set clears the alternate representation before writing the configured representation.
- `trusted.*` requires `CAP_SYS_ADMIN`.
- `security.*` is available for LSMs and file capabilities; security initialization stores labels from `security_inode_init_security()`.
- POSIX ACL handlers convert between Linux ACL xattr format and `struct posix_acl`, validate ownership/capability, and update inode mode where ACL equivalence requires it.

## Integration Points
This file connects Linux xattr/ACL VFS hooks to ZFS SA, hidden xattr directories, nvlist encoding, security modules, idmapped owner checks, inode dirtying, and create/chmod paths in `zpl_inode.c`.

## Invariants and Edge Cases
- SA xattrs are limited by `DXATTR_MAX_ENTRY_SIZE` and `DXATTR_MAX_SA_SIZE`.
- A warning is emitted if the same xattr exists in both SA and directory backends.
- Directory xattrs may create real hidden inodes not referenced by dentries.
- FreeBSD system namespace xattrs are hidden from Linux listing.
- Unknown namespace names are exposed as `user.*` for cross-platform compatibility.
- Symlinks cannot receive POSIX ACLs.
- Default ACLs only apply to directories.
- ACL freeing is delayed through a lockless multi-producer/single-consumer queue to avoid RCU/lifetime issues with kernel ACL caching.

## Risks and Testing Signals
Test SA and directory xattr get/set/list/remove, backend fallback and duplicate cleanup, `XATTR_CREATE`/`XATTR_REPLACE`, `xattr=off`, legacy `zfs_xattr_compat`, FreeBSD namespace hiding, trusted/security permission rules, SELinux label initialization, POSIX ACL inheritance/chmod/default ACLs, large xattr limits, and cache invalidation after SA persistence errors.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/os/linux/zfs/zpl_xattr.c -->