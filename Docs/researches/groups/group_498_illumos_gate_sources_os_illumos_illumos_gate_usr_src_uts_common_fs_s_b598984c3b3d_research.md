# Group Research: group_498_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_s_b598984c3b3d

Scope checked against `Docs/research_subset_a.md`; all thirteen listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dfs.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dfs.c

## Role

Implements SMB DFS referral handling for the kernel SMB server, including SMB2 DFS FSCTL dispatch and shared referral response encoding used by SMB1 transaction callers.

## Major Responsibilities

- Handles `FILE_DEVICE_DFS` FSCTL requests on IPC tree connections.
- Enforces SMB2 DFS capability checks and returns protocol-specific DFS errors.
- Decodes `FSCTL_DFS_GET_REFERRALS` and `FSCTL_DFS_GET_REFERRALS_EX` request bodies.
- Classifies referral paths as domain, DC, SYSVOL, root, link, or invalid.
- Calls user space over the SMB door interface to obtain configured DFS referral data.
- Encodes DFS referral response headers and referral entries for versions 1, 2, 3, and 4.
- Handles output buffer limits by returning overflow when no target fits and silently dropping later targets that do not fit.

## Key Functions

- `smb_dfs_fsctl()` validates IPC/DFS capability state and dispatches DFS FSCTL control codes.
- `smb_dfs_get_referrals()` decodes classic referral requests and writes encoded referrals to the FSCTL output mbuf chain.
- `smb_dfs_get_referrals_ex()` decodes the extended referral request fixed and variable parts, ignoring site data.
- `smb_dfs_get_reftype()` parses UNC paths and determines the DFS referral type.
- `smb_dfs_referrals_get()` uses `smb_kdoor_upcall()` with `SMB_DR_DFS_GET_REFERRALS` to query user-space DFS configuration.
- `smb_dfs_encode_hdr()` writes `PathConsumed`, target count, and response flags.
- `smb_dfs_encode_refv1()`, `smb_dfs_encode_refv2()`, and `smb_dfs_encode_refv3x()` encode version-specific referral entries.
- `smb_dfs_encode_targets()` appends DFS path, alternate path, and target UNC strings.
- `smb_dfs_referrals_free()` releases XDR-allocated referral response data.
- `smb_dfs_referrals_unclen()` computes encoded Unicode target UNC lengths.

## Research Notes

The kernel owns protocol decoding and referral packet layout, while actual DFS namespace knowledge comes from user space. Non-DC root behavior is explicit: domain/DC referral requests are rejected as invalid and SYSVOL referrals return no such device.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_directory.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_directory.c

## Role

Implements SMB1 directory create, delete, and check-directory commands, plus the common create-directory helper used by Trans2 create-directory handling.

## Major Responsibilities

- Decodes directory path operands for SMB1 directory operations.
- Rejects inappropriate operations on non-disk or IPC shares.
- Validates SMB pathnames and directory-name syntax.
- Creates directories with Windows-compatible DOS attributes.
- Deletes empty directories while enforcing DFS/root/read-only/delete-access rules.
- Verifies that a path exists, is a directory, and is traversable.
- Handles DFS link behavior for clients that set DFS flags.

## Key Functions

- `smb_pre_create_directory()` and `smb_post_create_directory()` decode and trace SMB create-directory requests.
- `smb_com_create_directory()` validates tree type/pathname and calls `smb_common_create_directory()`.
- `smb_common_create_directory()` reduces the path, checks nonexistence, enforces `FILE_ADD_SUBDIRECTORY`, sets directory attributes, calls `smb_fsop_mkdir()`, and releases nodes.
- `smb_pre_delete_directory()` and `smb_post_delete_directory()` decode and trace delete-directory requests.
- `smb_com_delete_directory()` resolves the target, rejects share roots and DFS links, requires a directory, checks DOS readonly and delete access, and calls `smb_fsop_rmdir()`.
- `smb_pre_check_directory()` and `smb_post_check_directory()` decode and trace check-directory requests.
- `smb_com_check_directory()` handles empty paths, resolves the directory, rejects non-directories, returns `PATH_NOT_COVERED` for DFS links under DFS requests, and checks `FILE_TRAVERSE`.

## Research Notes

The create path intentionally sets `FILE_ATTRIBUTE_DIRECTORY` without archive to match Windows server behavior. Delete is conservative around share roots, DFS links, readonly DOS attributes, and delete permissions.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_directory.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dispatch.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dispatch.c

## Role

Central SMB1 request dispatcher. It defines the SMB command table, handles request queueing, cancellation, SMB header decoding, UID/TID setup, AndX command chaining, reply construction/signing, error mapping, and SMB1 request statistics.

## Major Responsibilities

- Maps every SMB command byte to a name, pre-op, main handler, post-op, minimum dialect, and dispatch flags.
- Performs early SMB header peek in the reader thread for signing sequence handling and `SMB_COM_NT_CANCEL`.
- Dispatches most SMB1 requests to the server worker task queue.
- Executes cancellation in the reader thread when enabled.
- Decodes each SMB command block into VWV and data shadow chains.
- Handles SMB signing verification and reply signing.
- Looks up user and tree objects unless suppressed by command flags.
- Executes command pre/main/post hooks and cleans up transaction state.
- Implements AndX reply backpatching and chained-command continuation.
- Encodes normal and error replies and disconnects malformed clients when required.
- Tracks per-command received bytes, transmitted bytes, request count, and latency.

## Key Functions

- `smb1sr_newrq()` peeks the SMB header, maintains signing sequence numbers, handles fast cancel dispatch, and queues requests.
- `smb1_tq_work()` moves requests from wait queue to run queue and invokes SMB1 work.
- `smb1sr_work()` is the main SMB1 command execution loop, including header decode, signing check, command decode, UID/TID binding, command dispatch, AndX processing, and reply/error handling.
- `smbsr_cleanup()` releases transaction references and marks requests cleaned.
- `smbsr_encode_empty_result()` and `smbsr_encode_result()` encode handler replies.
- `smbsr_check_result()` validates encoded reply structure and patches variable byte counts.
- `smbsr_decode_vwv()` and `smbsr_decode_data()` decode command parameter/data chains with SMB error setup on failure.
- `smbsr_send_reply()` rewrites the SMB header, signs if enabled, and sends the reply.
- `smbsr_map_errno()`, `smbsr_errno()`, `smbsr_status()`, and `smbsr_set_error()` translate and install SMB1 error state.
- `smbsr_lookup_xa()`, `smbsr_lookup_file()`, and `smbsr_release_file()` manage common request-associated objects.
- `smb_com_invalid()` handles unsupported or invalid SMB commands.
- `smb_dispatch_stats_init()`, `smb_dispatch_stats_fini()`, and `smb_dispatch_stats_update()` manage SMB1 kstat data.

## Research Notes

This file is the SMB1 control plane. Its most important invariant is that every non-kept request is cleaned and freed exactly once, while malformed protocol state can force a session disconnect. AndX chaining is implemented by moving the request chain offset to the next command and backpatching the prior reply block.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_echo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_echo.c

## Role

Implements SMB1 Echo, used by clients to test server responsiveness without requiring a valid tree connection.

## Major Responsibilities

- Decodes requested echo count.
- Caps echo replies using `smb_max_echo`.
- Copies request data into request-scoped memory.
- Emits one SMB echo reply per requested iteration.
- Preserves request identity fields and signs replies when signing is enabled.
- Stops early if the request is cancelled.
- Returns `SDRC_NO_REPLY` because replies are sent manually.

## Key Functions

- `smb_pre_echo()` and `smb_post_echo()` provide DTrace start/done hooks.
- `smb_com_echo()` decodes the count and payload, builds each echo reply, signs as needed, sends it through the session, and delays between replies.

## Research Notes

Echo is explicitly cancellation-aware. It ignores TID semantics and manually constructs SMB headers because it may emit multiple replies for one request.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_echo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_errno.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_errno.c

## Role

Provides error translation helpers between illumos `errno`, NT status codes, and SMB1 DOS/Win32 error codes.

## Major Responsibilities

- Maps common Unix errors to NT status values.
- Converts NT status values to 16-bit Win32/DOS-style error codes suitable for SMB1 DOS error replies.
- Falls back to internal/general failure errors when no mapping exists.

## Key Functions

- `smb_errno2status()` returns an NT status for an `errno`, with explicit mappings for access, path, handle, quota, disk-full, stale-handle, invalid-name, and lock-conflict cases.
- `smb_status2doserr()` searches `smb_status2winerr_map` and returns only Win32 errors that fit below `0xFFFF`, otherwise `ERROR_GEN_FAILURE`.

## Research Notes

This file is intentionally small but central to consistent SMB1 error behavior. `ERANGE` is specially used for byte-range lock conflicts and maps to `NT_STATUS_FILE_LOCK_CONFLICT`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_errno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fem.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fem.c

## Role

Installs and implements FEM vnode monitors used by SMB for file change notification and oplock breaking when non-SMB filesystem activity touches watched SMB nodes.

## Major Responsibilities

- Creates FEM operation vectors for file-change-notification and oplock monitors.
- Installs/uninstalls notification hooks on directory nodes.
- Installs/uninstalls oplock hooks on file nodes with SMB node reference callbacks.
- Emits directory change notifications for non-SMB creates, removes, renames, mkdir/rmdir, links, and symlinks.
- Breaks SMB oplocks before non-SMB open, read, write, truncation, allocation changes, remove, and rename operations.
- Honors caller contexts so SMB-originated VOP calls do not recursively notify or break oplocks.
- Provides bounded oplock wait behavior, including `CC_DONTBLOCK` handling.

## Key Functions

- `smb_fem_init()` creates `smb_fcn_ops` and `smb_oplock_ops`.
- `smb_fem_fini()` frees FEM operation vectors.
- `smb_fem_fcn_install()` and `smb_fem_fcn_uninstall()` manage notification hooks.
- `smb_fem_oplock_install()` and `smb_fem_oplock_uninstall()` manage oplock hooks.
- `smb_fem_fcn_create()`, `smb_fem_fcn_remove()`, `smb_fem_fcn_rename()`, `smb_fem_fcn_mkdir()`, `smb_fem_fcn_rmdir()`, `smb_fem_fcn_link()`, and `smb_fem_fcn_symlink()` call through to `vnext_*()` and notify successful non-SMB namespace changes.
- `smb_fem_oplock_open()`, `smb_fem_oplock_read()`, `smb_fem_oplock_write()`, `smb_fem_oplock_setattr()`, `smb_fem_oplock_space()`, and `smb_fem_oplock_vnevent()` initiate the correct oplock break type before passing through.
- `smb_fem_oplock_wait()` waits for oplock break completion or returns `EAGAIN` for nonblocking contexts.

## Research Notes

The FCN hooks focus on namespace changes, not every metadata change, because broad metadata FEM coverage would be costly. Oplock hooks are specifically for NFS/local/non-SMB callers; SMB paths break oplocks at higher layers before VFS.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_find.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_find.c

## Role

Implements legacy SMB1 directory search commands that use 8.3 names and resume keys: `SMB_COM_SEARCH`, `SMB_COM_FIND`, `SMB_COM_FIND_CLOSE`, and `SMB_COM_FIND_UNIQUE`.

## Major Responsibilities

- Decodes old search/find request formats, including search attributes and resume keys.
- Opens and reuses `smb_odir_t` directory search objects.
- Handles first-search and resume-search flows.
- Encodes legacy directory entries with 21-byte resume keys and 8.3 filenames.
- Supports special volume-label-only search responses.
- Caps returned entries at `SMB_MAX_SEARCH`.
- Saves directory cookies for indexed resume.
- Explicitly closes find handles for `SMB_COM_FIND_CLOSE`.
- Opens, returns, and closes a one-shot search for `SMB_COM_FIND_UNIQUE`.

## Key Functions

- `smb_com_search()` implements core search, disables long-name semantics, handles volume-label requests, manages resume keys, reads directory entries, and optionally uppercases short names for older clients.
- `smb_com_find()` implements the LANMAN find protocol with similar resume-key handling but different error behavior.
- `smb_com_find_close()` extracts the open directory id from the resume key and closes the associated `smb_odir_t`.
- `smb_com_find_unique()` performs a one-shot search and closes the directory before returning.
- `smb_name83()` converts a short filename into the 11-byte base/ext resume-key form.
- `smb_pre_*()` and `smb_post_*()` functions provide DTrace hooks for each command.

## Research Notes

These commands cannot return Unicode or long filenames. The implementation skips names needing mangling when no shortname is available, and it treats zero matches on an initial search as `NO_MORE_FILES`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_find.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_flush.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_flush.c

## Role

Implements SMB1 Flush, synchronously pushing cached file data and allocation information to stable storage.

## Major Responsibilities

- Decodes the target FID.
- Short-circuits when global flush enforcement is disabled.
- Flushes one open file when the FID is valid.
- Flushes all open files on the tree when FID is `0xFFFF`.
- Protects the tree open-file list while iterating.
- Encodes an empty SMB success response.

## Key Functions

- `smb_pre_flush()` decodes `sr->smb_fid` and emits DTrace start.
- `smb_post_flush()` emits DTrace done.
- `smb_com_flush()` validates the FID or iterates the tree open-file list and calls `smb_ofile_flush()`.

## Research Notes

The all-files path enters the tree open-file AVL as a reader and locks each `smb_ofile_t` around flushing because the flush may block.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_flush.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsinfo.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsinfo.c

## Role

Implements SMB1 disk/filesystem information queries and filesystem control-info setting, including quota-aware capacity reporting.

## Major Responsibilities

- Handles legacy `SMB_COM_QUERY_INFORMATION_DISK`.
- Handles Trans2 query filesystem information levels for allocation, volume, size, device, attributes, control, and full-size information.
- Reports filesystem capabilities based on SMB tree features.
- Formats volume labels and filesystem names for Unicode and non-Unicode clients.
- Computes caller-visible capacity and free space using filesystem stats and optional per-user quota data.
- Handles Trans2 set filesystem control information for quota enforcement defaults.

## Key Functions

- `smb_com_query_information_disk()` returns old 16-bit disk capacity fields, scaling block/unit values to fit legacy clients.
- `smb_com_trans2_query_fs_information()` decodes the information level and encodes the requested FS structure.
- `smb_fssize()` calls `smb_fsop_statfs()`, normalizes block geometry, computes total/free units, and applies user quota limits when supported.
- `smb_com_trans2_set_fs_information()` dispatches supported set-info levels.
- `smb_trans2_set_fs_ctrl_info()` permits only administrators to set quota control info and only supports enforced quotas with unlimited defaults.

## Research Notes

The server reports the filesystem name as `NTFS` for compatibility while deriving feature flags from the share/tree state. Quota reporting affects caller-visible units but leaves volume-visible units available for full-size information.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsops.c

## Role

CIFS-aware filesystem operation layer. It sits above `smb_vop_*` and below SMB command handlers, adding SMB semantics for access checks, share boundaries, streams, short-name mangling, ACL/security descriptor handling, byte-range/share locks, notifications, and read/write behavior.

## Major Responsibilities

- Converts SMB access masks to VOP open modes.
- Wraps VFS open/close/create/mkdir/remove/rmdir/link/rename/getattr/setattr/read/write/statfs/commit operations.
- Enforces tree containment, share access masks, readonly shares, ACE permissions, and open-file granted access.
- Handles named streams using extended-attribute vnode operations and unnamed-stream authorization.
- Blocks restricted stream names for non-kernel credentials.
- Handles mangled 8.3 names and exact case-sensitive follow-up operations.
- Applies Windows security descriptor inheritance for ZFS/ACE ACL targets.
- Reads, writes, merges, and inherits owner/group/DACL/SACL security data.
- Issues file-change notifications after namespace, stream, ACL, and create/remove operations.
- Checks SMB byte-range lock conflicts before read/write.
- Preserves pending mtime semantics after writes through handles with manually set mtime.
- Provides zero-copy buffer request/return wrappers and sparse-range helpers.
- Implements share reservations and byte-range lock VOP translations.

## Key Functions

- `smb_fsop_amask_to_omode()` maps SMB desired access to `FREAD`, `FWRITE`, and `FAPPEND`.
- `smb_fsop_create()` handles regular file and stream creates, including share containment, readonly checks, CATIA/ABE/case flags, and mangled-name collision checks.
- `smb_fsop_create_file_with_stream()` creates a base file if needed, then creates a named stream, removing the base file on stream-create failure.
- `smb_fsop_create_stream()` creates a named stream and aligns UID/GID with the unnamed stream.
- `smb_fsop_create_file()` creates regular files, applying incoming or inherited security descriptors when available.
- `smb_fsop_mkdir()` creates directories with analogous ACL inheritance/security descriptor behavior.
- `smb_fsop_remove()` removes files or streams, including stream parsing, restricted stream checks, mangled-name fallback, and notifications.
- `smb_fsop_remove_streams()` enumerates and removes all streams from a file.
- `smb_fsop_rmdir()` removes directories with mangled-name fallback and notifications.
- `smb_fsop_getattr()` checks tree/open access, handles named-stream unnamed vnode context, and marks DFS links as directories.
- `smb_fsop_link()` creates hard links after tree and readonly checks.
- `smb_fsop_rename()` validates source/destination permissions, rejects mount points and reparse points, checks open-handle delete access, performs rename, updates node cache naming, and emits rename/remove/add notifications.
- `smb_fsop_setattr()` checks write permissions by attribute class and calls `smb_vop_setattr()`.
- `smb_fsop_freesp()` supports valid-data-length zeroing/free-space operations via `VOP_SPACE`.
- `smb_fsop_read()` and `smb_fsop_write()` enforce tree/open access, stream credentials, mandatory lock conflicts, critical regions, and VOP I/O.
- `smb_fsop_next_alloc_range()` uses `_FIO_SEEK_DATA` and `_FIO_SEEK_HOLE`.
- `smb_fsop_statfs()` wraps filesystem statfs.
- `smb_fsop_access()` implements SMB access checks, including readonly denial, reparse delete denial, stream behavior, `ACCESS_SYSTEM_SECURITY`, share mask filtering, and ACE/POSIX access translation.
- `smb_fsop_lookup_name()`, `smb_fsop_lookup_file()`, `smb_fsop_lookup_stream()`, and `smb_fsop_lookup()` implement file/stream lookup, path containment, symlink following, traversal checks, CATIA/ABE/case flags, and short-name unmangling.
- `smb_fsop_aclread()` and `smb_fsop_aclwrite()` translate ACLs between filesystem and SMB expectations.
- `smb_fsop_sdread()`, `smb_fsop_sdmerge()`, `smb_fsop_sdwrite()`, and `smb_fsop_sdinherit()` handle security descriptor read/write/merge/inheritance.
- `smb_fsop_eaccess()` computes effective SMB-style access from filesystem access.
- `smb_fsop_shrlock()` and `smb_fsop_unshrlock()` manage share reservations.
- `smb_fsop_frlock()` maps SMB byte-range locks to `flock64_t` remote locks while skipping zero-length and wraparound ranges.

## Research Notes

This is the main semantic boundary between SMB protocol rules and illumos VFS. Command handlers should call `smb_fsop_*` rather than raw `smb_vop_*` so tree policy, stream rules, Windows ACL behavior, notifications, and open-handle semantics remain consistent.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_fsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_idmap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_idmap.c

## Role

Kernel SMB interface to illumos ID mapping, translating between Unix UID/GID values and Windows SIDs through `kidmap`.

## Major Responsibilities

- Maps UID/GID to binary SMB SIDs.
- Maps binary SMB SIDs to UID/GID or unknown principal type.
- Provides batch mapping contexts for groups of ID/SID conversions.
- Handles special SMB identities such as Everyone, current owner, and current group.
- Converts returned domain SID strings plus RIDs into binary SID objects.
- Frees batch-allocated SID/domain state correctly for each mapping direction.

## Key Functions

- `smb_idmap_getsid()` maps one UID/GID/special ID to an SMB SID using `kidmap_getsidbyuid()` or `kidmap_getsidbygid()`.
- `smb_idmap_getid()` splits a SID into domain SID and RID and maps it to UID, GID, or principal type.
- `smb_idmap_batch_create()` initializes a `kidmap` batch handle and allocates map entries.
- `smb_idmap_batch_destroy()` destroys the batch handle and frees direction-specific allocations.
- `smb_idmap_batch_getid()` queues SID-to-ID lookups.
- `smb_idmap_batch_getsid()` queues ID-to-SID lookups and handles special SID constants.
- `smb_idmap_batch_getmappings()` runs queued mappings, counts/report errors, optionally skips errors, and converts SID/RID pairs to binary SIDs.
- `smb_idmap_batch_binsid()` builds binary SIDs for ID-to-SID batch results.

## Research Notes

Unlike user-level SMB idmap helpers, this kernel implementation calls `kidmap_*` directly and treats returned domain SID strings as shared state except where SID-to-ID batching duplicates strings for later cleanup.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_init.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_init.c

## Role

Kernel module and pseudo-device entry point for the illumos SMB server driver.

## Major Responsibilities

- Defines global tunables for buffer size, flush behavior, symlink handling, signing debug, audit flags, advisory locks, thresholds, timeouts, and server thread priorities.
- Registers the SMB server pseudo-device driver module.
- Creates minor nodes for the control device and library-access device.
- Enforces privileged exclusive control opens for `smbd`.
- Creates and destroys `smb_server_t` instances through control-device open/close.
- Supports clone opens for library access.
- Validates ioctl headers, lengths, and CRCs.
- Enforces ioctl access policy by command class and opened device.
- Dispatches server configuration, lifecycle, share, event, enumeration, close, and spool-document ioctls.
- Copies ioctl results back for query-style operations.

## Key Functions

- `_init()` initializes global SMB server state and installs the module.
- `_info()` returns module info.
- `_fini()` refuses unload while servers exist, removes the module, and finalizes global state.
- `smb_drv_open()` routes opens by minor number.
- `smb_drv_open_ctl()` checks `secpolicy_smb()`, allocates a clone minor, and creates the SMB server instance.
- `smb_drv_open_lib()` allocates a clone minor for non-control library access.
- `smb_drv_close()` deletes the server when the control device closes and frees the clone minor.
- `smb_drv_ioctl()` validates/copies the ioctl payload, looks up the server, checks permissions, dispatches the ioctl command, and copies out results when needed.
- `smb_drv_attach()` creates `smbsrv` and `smbsrv1` minor nodes and initializes minor id space.
- `smb_drv_detach()` destroys minor id space and removes minor nodes.
- `smb_drv_getinfo()` maps device numbers to devinfo or instance values.

## Research Notes

The control minor is reserved for `smbd` and gates most mutating operations, while the library minor allows selected non-mutating or separately privileged operations. The ioctl path allocates at least the full union size to protect type-specific handlers from undersized user lengths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_init.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kdoor.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kdoor.c

## Role

Implements kernel-to-user-space SMB door upcalls used by the SMB server for operations such as DFS referral queries.

## Major Responsibilities

- Maintains the server door handle, door id, active call count, mutex, and close condition variable.
- Opens and closes kernel door handles safely.
- Prevents door close while upcalls are active.
- Encodes request headers and request bodies with XDR.
- Supports synchronous upcalls and asynchronous request/response upcall pairs.
- Retries door upcalls on transient `EAGAIN`/`EINTR`.
- Validates response headers, magic, opcode, transaction id, and door return code.
- Frees request and response buffers, including doorfs-grown result buffers.

## Key Functions

- `smb_kdoor_init()` and `smb_kdoor_fini()` initialize and destroy door synchronization state.
- `smb_kdoor_open()` closes any existing handle and looks up the new door id.
- `smb_kdoor_close()` waits for active calls to drain, releases the door handle, and resets state.
- `smb_kdoor_upcall()` prepares an `smb_doorarg_t`, creates an event, accounts for active calls, and runs synchronous or async call flow.
- `smb_kdoor_send()` sends the request half of an async door operation.
- `smb_kdoor_receive()` requests the async response using `SMB_DR_ASYNC_RESPONSE`.
- `smb_kdoor_upcall_private()` performs the limited kernel door upcall with retry and stopping checks.
- `smb_kdoor_encode()` computes XDR size, builds the SMB door header, and encodes request payload.
- `smb_kdoor_decode()` decodes and validates the response header and response payload.
- `smb_kdoor_sethdr()` fills SMB door header fields.
- `smb_kdoor_chkhdr()` validates response identity and door return status.
- `smb_kdoor_free()` frees both argument and result buffers.

## Research Notes

The function copies `door_arg_t` before upcall because doorfs may replace `data_ptr`; response data is therefore consumed via `rbuf`/`rsize`. Async upcalls are modeled as send plus later receive, keyed by the SMB event transaction id.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_kdoor.c -->