# sources/distributed-fs/lustre-release/lustre/llite/namei.c

## Purpose

`namei.c` implements Lustre llite directory and name operations. It is the bridge between Linux VFS inode operations and Lustre metadata server RPCs. The file handles inode instantiation from MDS metadata, lookup and open intent locks, atomic open/create, mknod/create/symlink/link/mkdir/rmdir/unlink/rename, dentry alias management, metadata LDLM blocking callbacks, supplementary-group retry for access checks, encryption/security context propagation, striped-directory behavior, and metadata-operation statistics.

The core design is intent-driven. For lookup/open/create, llite prepares `md_op_data`, sends an intent lock to the metadata export, receives metadata and locks in a `ptlrpc_request`, instantiates or updates Linux inodes/dentries, attaches lock data to inodes, and revalidates dentries when the returned lock covers lookup state.

## Important APIs, types, and functions

Inode lookup and instantiation:

- `ll_test_inode()` and `ll_set_inode()` are `iget5_locked()` callbacks keyed by Lustre FID. They validate `OBD_MD_FLID` and `OBD_MD_FLTYPE`, set `lli_fid`, initialize llite inode-private state with `ll_lli_init()`, and set the inode type bits.
- `ll_iget(struct super_block *sb, ino_t hash, struct lustre_md *md)` gets or creates an inode by hash/FID, calls `ll_read_inode2()` for new inodes, initializes regular-file CL objects with `cl_file_inode_init()`, updates existing inodes with `ll_update_inode()`, and handles bad/stale inode cases.
- `ll_test_inode_by_fid()` supports `ilookup5_nowait()` when invalidating striped-directory master inodes.

LDLM metadata lock callbacks and invalidation:

- `ll_md_blocking_ast()` handles `LDLM_CB_BLOCKING` by attempting lock conversion through `ldlm_cli_convert()` and falling back to cancel; it handles `LDLM_CB_CANCELING` by passing canceled inodebits to `ll_lock_cancel_bits()`.
- `ll_md_need_convert()` decides whether a granted metadata lock can keep remaining bits, primarily for DOM-related conversion, based on connection support, cancel bits, existing compatible locks, mode, and dirty-age limits.
- `ll_lock_cancel_bits()` maps canceled inodebits to local invalidation: empties xattr cache, closes open modes, flushes DoM data, invalidates layouts, marks update-atime, truncates directory page cache, increments directory i_version, prunes negative children, prunes aliases, and clears cached ACLs.
- `ll_dom_lock_cancel()` flushes Data-on-MDT object data with `cl_object_flush()` before DOM lock cancellation.
- `ll_prune_negative_children()` marks negative children invalid and drops unused negative dentries under locking.

Dentry alias handling:

- `ll_find_alias()` searches an inode's aliases for an invalid same-name alias or disconnected directory alias.
- `ll_splice_alias()` reuses a Lustre-invalid alias when possible or adds the new dentry. It also marks some foreign symlink directories with `DCACHE_SYMLINK_TYPE` so VFS treats them as symlink-like entries.

Intent lookup/open:

- `ll_i2suppgid()` and `ll_i2gids()` derive up to two supplementary GIDs to send to the MDS.
- `get_acl_from_req()`, `accmode_from_openflags()`, `get_uc_group_from_acl()`, and `failed_it_can_retry()` support retrying metadata intents after `-EACCES` with a better supplementary group from the returned inode GID or ACL.
- `ll_intent_lock()` wraps `md_intent_lock()`, logs the operation, and optionally retries once with a better supplementary GID after access failure.
- `obf_mod_fixup()` recognizes open-by-FID style names, rewrites `op_fid2`, clears the name, sets `MDS_FID_OP`, and adjusts open/getattr flags.
- `ll_lookup_it()` is the main lookup/open path. It validates name length, handles statahead revalidation, checks read-only write opens, prepares encrypted names through `ll_prepare_lookup()`, prepares `md_op_data`, applies open-by-FID and directory-read-on-open behavior, handles umask enforcement, prepares encryption/security/PCC data for creates, requests security context names, sends `ll_intent_lock()`, finalizes PCC precreation, calls `ll_lookup_it_finish()`, and handles open-create completion with `ll_create_it()`.
- `ll_lookup_it_finish()` consumes the metadata reply, prepares the child inode with `ll_prep_inode()`, caches returned encryption/security context, binds returned locks with `ll_set_lock_data()`, finishes DoM or directory open data, splices the dentry, revalidates dentries when lock coverage permits, handles negative lookup revalidation via parent update locks, and accounts create latency.
- `ll_lookup_nd()` is the VFS `.lookup` method. It avoids unnecessary lookup for create-without-open when parent permissions allow `.create` to handle the race; otherwise it calls `ll_lookup_it()`.
- `ll_atomic_open()` is the VFS `.atomic_open` method for negative dentries. It builds an `IT_OPEN` intent, handles `O_CREAT`, optional PCC dataset selection, open-cache lock requests, calls `ll_lookup_it()`, finalizes PCC create attach, finishes opening regular/directories/foreign openable entries, and releases or transfers intent state.

Create/new-node flow:

- `ll_create_node()` consumes the create reference from an intent-open reply, prepares the inode, and binds the returned lock to the new inode.
- `ll_create_it()` finishes intent create: checks server open-create error, calls `ll_create_node()`, applies security context before dentry instantiation, instantiates the dentry, applies encryption flags, initializes security if the server did not provide secctx, and revalidates the dentry when lookup lock bits were returned.
- `ll_update_times()` updates parent inode mtime/ctime from an MDS reply when server timestamps are newer.
- `ll_qos_mkdir_prep()` computes inherited directory depth and marks QoS/round-robin mkdir flags when root default LMV policy should apply.
- `ll_new_node_prepare()` prepares common mknod/mkdir/symlink create state: allocates `md_op_data`, packs default LMV for directory inheritance, initializes security context, prepares fscrypt state, inherits encryption context, and encrypts symlink targets using a temporary fake inode when needed.
- `ll_new_node_finish()` updates parent times, prepares the new inode, applies security context before `d_instantiate()`, applies encryption flags, caches plaintext encrypted symlink target opportunistically, and initializes local security if needed.
- `ll_new_node()` wraps non-atomic create RPCs through `md_create()`, including legacy retry logic that fetches default LMV after `-EREMOTE`, then calls the finish path and releases request/op-data/LUM resources.

VFS inode operations:

- `ll_mknod()` validates mode, applies umask when server umask support or POSIX ACLs are absent, and calls `ll_new_node()` for regular/device/fifo/socket nodes.
- `ll_create_nd()` implements plain `.create` through `ll_mknod()` and tallies create latency.
- `ll_symlink()` prepares an encrypted symlink target with `llcrypt_prepare_symlink()`, calls `ll_new_node()`, frees allocated target buffers, and tallies.
- `ll_link()` validates fscrypt link constraints, sends `md_link()`, updates parent times, and tallies.
- `do_mkdir()` applies mode/umask, chooses either plain `ll_new_node()` or intent mkdir based on `ll_intent_mkdir_enabled`, finalizes returned inode and lock, and tallies.
- `ll_mkdir()` adapts `do_mkdir()` to kernel API variants.
- `ll_rmdir()` rejects mountpoints and non-removable foreign entries, sends `md_unlink()` for directories, updates parent times and child nlink from the reply, and tallies.
- `ll_rmdir_entry()` removes a directory entry by name with `CLI_RM_ENTRY`, used for specialized internal removal.
- `ll_unlink()` rejects mountpoints and non-removable foreign entries, flags dirty regular-file data with `CLI_DIRTY_DATA`, sends `md_unlink()`, updates child nlink and parent times, and tallies.
- `ll_rename()` rejects unsupported flags and mountpoints, performs fscrypt rename preparation, prevents encrypted-to-unencrypted-directory moves, handles subdir-mounted `.fscrypt` root fixup, prepares source/target FIDs and encrypted disk names, sends `md_rename()`, updates source/target times, moves the dentry locally, and tallies.
- `ll_dir_inode_operations` publishes the directory inode operations table, integrating name operations with setattr/getattr/permission/xattr/ACL/fileattr handlers from other llite files.
- `ll_special_inode_operations` provides non-directory special inode operations.

## Control flow

The common lookup flow starts in VFS `.lookup` or `.atomic_open`. `ll_lookup_nd()` either defers create races to `.create` or calls `ll_lookup_it()` with a GETATTR intent. `ll_atomic_open()` allocates a lookup intent, sets `IT_OPEN` and optionally `IT_CREAT`, prepares open flags/mode, optionally selects a PCC dataset for new regular files, and delegates to `ll_lookup_it()`.

`ll_lookup_it()` prepares the request context. It checks name length and read-only write opens, resolves encrypted disk names and FID/namehash information through `ll_prepare_lookup()`, allocates `md_op_data`, applies open-by-FID rewrite when the parent is an OBF directory, disables directory read-on-open when configured, applies umask locally when necessary, prepares encryption context inheritance for encrypted creates, initializes requested security context buffers, packs PCC create data when applicable, and adds read access for GETATTR intents. It then calls `ll_intent_lock()` against the metadata export.

`ll_intent_lock()` sends `md_intent_lock()`. If the server denies access and retry is enabled, it inspects the reply body and ACL for a supplementary group that current credentials actually hold, resets `op_fid2` when not open-by-FID, updates `op_suppgids[1]`, releases the failed request/intent state, and retries once. This moves some server-side credential ambiguity into a bounded client retry.

After a successful intent reply, `ll_lookup_it_finish()` prepares the returned inode unless the lookup is negative, installs server-returned encryption/security contexts, associates LDLM lock data with the inode, finishes DoM or directory open content when matching lock bits were returned, splices/reuses the dentry, and revalidates the dentry if the lookup lock is held. Negative lookups can also be revalidated if the parent update lock proves the directory state. For open-create dispositions, `ll_lookup_it()` calls `ll_create_it()`, which consumes the create reference, instantiates the new inode/dentry, sets security/encryption state, and revalidates on lookup lock coverage. Finally open locks are finished and non-openable special files release open handles.

Non-atomic creates use `ll_new_node()`. Preparation builds `md_op_data`, inherited LMV/default directory layout, security context, encryption context, and encrypted symlink data. The create RPC is `md_create()`. On success `ll_new_node_finish()` updates parent times, instantiates the child, and applies security/encryption. On old-server `-EREMOTE` around default LMV inheritance, the code fetches default LMV from the directory, updates the parent inode metadata, and retries preparation and create.

Metadata lock cancellation is asynchronous. `ll_md_blocking_ast()` receives LDLM callbacks. Blocking callbacks try to convert locks and preserve non-conflicting bits; canceling callbacks invoke `ll_lock_cancel_bits()`. That function translates canceled metadata bits into local state changes: xattr and ACL invalidation, real close for open locks, DoM flushing, layout invalidation, directory page-cache truncation, i_version bump, negative dentry pruning for master or slave striped directories, and alias pruning for lookup/permission invalidation.

Unlink/rmdir/rename/link paths are more direct. They prepare operation data with source/target FIDs and encrypted disk names, call the relevant MDC operation (`md_unlink`, `md_rename`, `md_link`), update local timestamps and link counts from replies, update dentries where needed, and increment lprocfs counters through `ll_stats_ops_tally()`.

## State and persistence behavior

This file mutates in-memory VFS, llite, and cache state as a reflection of authoritative MDS state:

- Inodes are keyed by Lustre FID in `lli_fid`; new inode state is initialized with MDS body data and `ll_read_inode2()`, then updated later through `ll_update_inode()`.
- Dentries are added, moved, invalidated, revalidated, or pruned. Lustre-specific dentry validity is driven by LDLM lookup/update/permission locks and helpers like `d_lustre_revalidate()` and `set_lld_invalid()`.
- Metadata locks are associated with inodes through `ll_set_lock_data()` so future LDLM callbacks can find and invalidate the correct inode.
- Directory page cache and i_version are updated on metadata lock cancellation to maintain NFS/export and readdir consistency after remote changes.
- ACL and xattr caches are explicitly dropped on lock cancellation. Security contexts returned by the MDS are applied before `d_instantiate()` to avoid recursive getxattr/deadlock behavior in security hooks.
- Encryption context is inherited or returned by the server, cached in xattr cache, and applied to new/lookup inodes through `ll_set_encflags()`. Encrypted symlink plaintext may be cached in `lli_symlink_name` after create, but failure to cache it is nonfatal.
- Parent mtime/ctime and child nlink are updated from MDS replies after create/link/unlink/rmdir/rename.
- PCC create attach state is prepared before the MDS create/open and finalized only if the server actually created the file.

Persistent namespace and metadata changes are committed by MDS RPCs (`md_create`, `md_link`, `md_unlink`, `md_rename`, and intent opens/creates). The local changes in this file are cache coherency and VFS state updates around those persistent server-side operations.

## Dependencies and integration points

Kernel/VFS dependencies include `iget5_locked`, dentry alias and locking APIs, inode operations, POSIX ACL helpers, user namespace UID/GID conversion, mountpoint checks, `finish_open`, `finish_no_open`, and fscrypt/llcrypt hooks.

Lustre dependencies include:

- MDC metadata APIs: `md_intent_lock`, `md_create`, `md_link`, `md_unlink`, `md_rename`, `md_revalidate_lock`, `md_get_fid_from_lsm`.
- RPC capsule parsing: `ptlrpc_request`, `req_capsule_server_get`, `req_capsule_get_size`, `RMF_MDT_BODY`, `RMF_FILE_ENCCTX`, `RMF_FILE_SECCTX`, and `RMF_ACL`.
- Metadata operation data helpers: `ll_prep_md_op_data`, `ll_finish_md_op_data`, `ll_unlock_md_op_lsm`, `ll_prepare_lookup`, `ll_setup_filename`.
- LDLM APIs: lock conversion/cancel, inodebits, lock modes, lock handles, and callbacks.
- llite helpers from other files: inode read/update, security initialization, xattr cache, directory layout/LMV, statahead, foreign symlink/file rules, PCC, open cleanup, open handle release, layout invalidation, DoM open finish, and metadata stats.
- CL/object layer integration for regular files and DoM data through `cl_file_inode_init()`, `cl_env_get/put()`, and `cl_object_flush()`.

The file also directly integrates with `lproc_llite.c` through `ll_stats_ops_tally()` for operation latency counters and with runtime tunables from `ll_sb_info`, including `ll_namelen`, `ll_dir_open_read`, `ll_intent_mkdir_enabled`, open-cache thresholds, PCC superblock state, encryption support flags, and foreign symlink policy.

## Risks and edge cases

- Intent/open/create flows are resource-heavy and have many ownership transfers: `ptlrpc_request`, `lookup_intent`, `md_op_data`, `llcrypt_name`, `lov_user_md`, PCC dataset/dentry, security buffers, and encryption buffers. Error paths must avoid leaks and double releases.
- Security and encryption contexts must be applied before `d_instantiate()` to avoid security hook recursion and deadlocks. Reordering this is risky.
- Supplementary-group retry trusts hints from MDS replies but must verify current process group membership and ACL permissions. Incorrect retry logic could cause false denial or overbroad access.
- LDLM cancellation runs concurrently with normal VFS operations. Pruning aliases or negative children while other threads look up names requires the exact dentry and inode locking used here.
- `ll_md_need_convert()` only allows limited conversion cases. Incorrect conversion can retain stale metadata locks or cause unnecessary cancels that hurt performance.
- Striped-directory invalidation has special slave/master handling and intentionally uses `ilookup5_nowait()` to avoid deadlocks with inodes in `I_NEW`.
- Open-by-FID parsing in `obf_mod_fixup()` rewrites operation names and FIDs. Malformed bracketed FIDs, unsupported FID classes, and name ownership flags must be handled exactly.
- Encrypted volatile file handling allows a narrow no-key create path only with ciphertext and direct I/O constraints; relaxing this can break fscrypt semantics.
- Default LMV inheritance compatibility code retries after `-EREMOTE` for older servers. It mutates parent default stripe metadata and must release intermediate requests and metadata correctly.
- `ll_rename()` rejects all nonzero flags; newer VFS flags such as exchange/noreplace are not supported by this implementation.
- Local `d_move()` after successful rename assumes the server completed the namespace change. Any missed invalidation around target aliases can produce stale local dentries.

## Test signals

Useful validation should cover:

- Lookup of positive, negative, stale, disconnected, and invalid aliases, including dentry reuse by `ll_splice_alias()`.
- Atomic open with and without `O_CREAT`, with existing files, newly created files, special files, directories, read-only mounts, open-cache lock threshold enabled, and PCC create attach.
- Plain `create`, `mknod`, `symlink`, `link`, `mkdir`, `rmdir`, `unlink`, and `rename`, verifying MDS RPC arguments, local dentry/inode state, timestamps, nlink updates, and lprocfs counters.
- Encrypted directory lookup/create/symlink/rename paths with key present, key absent, volatile ciphertext direct-I/O create, encrypted-to-unencrypted rename rejection, and server-returned encryption contexts.
- Security context propagation with `LL_SBI_FILE_SECCTX` both enabled and disabled; verify no extra getxattr deadlocks during instantiation.
- Access retry cases where initial intent returns `-EACCES` and MDS body/ACL hints provide a valid or invalid supplementary group.
- LDLM blocking/cancel callbacks for LOOKUP, UPDATE, LAYOUT, PERM, OPEN, XATTR, and DOM bits; verify xattr/ACL cache invalidation, layout invalidation, DoM flush, dentry pruning, and directory page-cache truncation.
- Striped-directory invalidation where a slave lock cancellation prunes negative children on a loaded master inode without deadlocking on `I_NEW`.
- Default LMV/QoS mkdir behavior, including root default LMV inheritance and old-server `-EREMOTE` retry.
- Fault-injection points such as `OBD_FAIL_LLITE_CREATE_FILE_PAUSE`, `OBD_FAIL_LLITE_CREATE_NODE_PAUSE`, `OBD_FAIL_LLITE_NEWNODE_PAUSE`, and `OBD_FAIL_LDLM_REPLAY_PAUSE` to exercise races and cleanup paths.
