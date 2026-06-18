# Research Report: subset-b-009832

Grouped research for Samba VFS modules under `sources/user-network-fs/samba/source3/modules`. Each file section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_not_implemented.c -->
# sources/user-network-fs/samba/source3/modules/vfs_not_implemented.c

## Purpose
`vfs_not_implemented.c` is the negative/default implementation table for Samba's VFS layer. It supplies exported fallback functions for every VFS hook that has no real implementation in a module, returning `ENOSYS`, `NT_STATUS_NOT_IMPLEMENTED`, `NT_STATUS_NOT_SUPPORTED`, or other SMB-compatible "not available" statuses. Its registration also asserts that the table covers every VFS function pointer, making it a coverage guard for VFS interface evolution.

## Important APIs, Types, And Functions
- Exports many `_PUBLIC_` functions named `vfs_not_implemented_*` spanning connection, disk, directory, file, DFS, snapshot, ACL, xattr, AIO, FSCTL, byte-range lock, durable handle, compression, and copy-offload hooks.
- Async placeholders such as `vfs_not_implemented_offload_read_send`, `vfs_not_implemented_offload_write_send`, `vfs_not_implemented_get_dos_attributes_send`, and `vfs_not_implemented_getxattrat_send` allocate `tevent_req` objects and complete them immediately with an NTSTATUS or Unix error.
- `struct vfs_fn_pointers vfs_not_implemented_fns` binds every hook to the matching fallback.
- `vfs_not_implemented_init()` calls `smb_vfs_assert_all_fns()` before `smb_register_vfs(..., "vfs_not_implemented", ...)`.

## Control Flow
Most synchronous hooks are single-exit stubs: set `errno`, zero outputs where necessary, and return a failure sentinel. NTSTATUS-oriented hooks return Samba protocol statuses directly. Async hooks create a request, mark it failed via `tevent_req_nterror()` or `tevent_req_error()`, post it to the event loop, and have receive functions propagate the stored status/error before `tevent_req_received()`.

## State And Persistence
The module owns no persistent external state. It may initialize output buffers to safe empty values, such as zero disk-space counters or zeroed `struct file_id`, and async helper structs hold only transient request state.

## Dependencies And Integration Points
It depends on Samba VFS structs, `tevent`, and NTSTATUS utilities. Other modules explicitly reference its functions for hooks they intentionally do not implement, for example `offline` and `posix_eadb` use the not-implemented async DOS/xattr hooks. The all-functions assertion makes this file sensitive to changes in `struct vfs_fn_pointers`.

## Risks
- Interface drift is the main risk: a new VFS hook must be added here or `smb_vfs_assert_all_fns()` should fail.
- Return semantics must match the hook family. A wrong `errno`, status, or async completion style can change upper-layer fallback behavior.
- Stubbed async receive functions must set `vfs_aio_state->error` consistently so callers do not treat an unsupported operation as transient I/O.

## Test Signals
- Build-time registration should pass `smb_vfs_assert_all_fns()`.
- Loading `vfs_not_implemented` should register successfully.
- Unsupported VFS calls should surface expected SMB errors, for example `NT_STATUS_NOT_IMPLEMENTED`, `NT_STATUS_NOT_SUPPORTED`, `NT_STATUS_INVALID_DEVICE_REQUEST`, or `ENOSYS`.
- Async stub callers should observe immediate completion with the correct error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_not_implemented.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_offline.c -->
# sources/user-network-fs/samba/source3/modules/vfs_offline.c

## Purpose
`vfs_offline.c` marks every file in a share as offline/remote-storage capable for SMB clients. It is a small metadata filter that does not alter file I/O; it reports the filesystem capability `FILE_SUPPORTS_REMOTE_STORAGE` and sets `FILE_ATTRIBUTE_OFFLINE` in DOS attributes.

## Important APIs, Types, And Functions
- `offline_fs_capabilities()` ORs `FILE_SUPPORTS_REMOTE_STORAGE` into the next module's capability result.
- `offline_fget_dos_attributes()` ORs `FILE_ATTRIBUTE_OFFLINE` into `*dosmode` and then delegates to `SMB_VFS_NEXT_FGET_DOS_ATTRIBUTES`.
- `offline_fns` registers `.fs_capabilities_fn`, `.fget_dos_attributes_fn`, and not-implemented async DOS attribute hooks.
- `vfs_offline_init()` registers the module name `offline`.

## Control Flow
Each hook is a pass-through wrapper. Capabilities are delegated first through `SMB_VFS_NEXT_FS_CAPABILITIES` and augmented. File DOS attributes are modified in-place before calling the next VFS layer, so downstream layers can still add or validate attributes.

## State And Persistence
The module stores no per-handle or on-disk state. Its behavior is deterministic for every open file and every connection where the module is stacked.

## Dependencies And Integration Points
It depends on Samba's VFS operation chain and `FILE_SUPPORTS_REMOTE_STORAGE`/`FILE_ATTRIBUTE_OFFLINE` constants. It integrates with Windows Explorer and SMB clients that use offline file attributes or remote-storage capability bits.

## Risks
- Because all files are marked offline, clients may issue recall-oriented or remote-storage behavior even when the backend is ordinary local storage.
- Async DOS attribute hooks are explicitly unsupported through `vfs_not_implemented_*`; callers relying only on async path-based attributes may not see the offline bit.
- Attribute ordering in the VFS stack matters because this module mutates `dosmode` before delegating.

## Test Signals
- `fsctl`/capability queries should show remote storage support.
- DOS attribute queries on open files should include `FILE_ATTRIBUTE_OFFLINE`.
- Ordinary reads/writes should pass through unchanged.
- Async path DOS attribute calls should return the not-implemented path unless another stacked module supplies them.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_offline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_posix_eadb.c -->
# sources/user-network-fs/samba/source3/modules/vfs_posix_eadb.c

## Purpose
`vfs_posix_eadb.c` implements POSIX extended attributes using a TDB database instead of filesystem-native xattrs. It is for environments where Samba must preserve POSIX EA semantics but the backing filesystem cannot, or should not, store them directly.

## Important APIs, Types, And Functions
- `posix_eadb_getattr`, `posix_eadb_setattr`, `posix_eadb_listattr`, and `posix_eadb_removeattr` wrap raw TDB xattr helpers from `ntvfs/posix/posix_eadb.h`.
- File-facing hooks `posix_eadb_fgetxattr`, `posix_eadb_fsetxattr`, `posix_eadb_flistxattr`, and `posix_eadb_fremovexattr` fetch the per-handle `struct tdb_wrap` via `SMB_VFS_HANDLE_GET_DATA`.
- `posix_eadb_init()` opens the database from the `posix:eadb` share parameter as root with `tdb_wrap_open`.
- `posix_eadb_unlink_internal()` and `posix_eadb_rmdir_internal()` delete EA records transactionally when the backing file or directory is removed.
- `posix_eadb_connect()` opens the DB and toggles `ea support` based on availability.

## Control Flow
On connect, the module delegates to the next VFS connect, resolves the service number, opens the configured EA database, and stores the `tdb_wrap` as VFS handle data. Xattr hooks translate the `files_struct` name/fd to raw DB helper calls. On unlink, the module builds a full path, stats it, starts a TDB transaction for last-link deletion, removes the EA record, delegates the unlink, then commits or cancels the transaction. Directory removal follows a similar record-delete plus `AT_REMOVEDIR` unlink flow.

## State And Persistence
Persistent EA data lives in the configured TDB file. The VFS handle stores a `tdb_wrap` pointer with a destructor. The module modifies Samba service state by setting `ea support` true if DB initialization succeeds and false if it fails.

## Dependencies And Integration Points
It depends on TDB, Samba loadparm helpers, generated NDR xattr support, raw posix_eadb helpers, and VFS path construction/stat/unlink APIs. It integrates with Samba's f* xattr hooks, not path-based async xattr hooks, which are mapped to not-implemented stubs.

## Risks
- Correct cleanup depends on link count: EA records are only removed on unlink when `st_ex_nlink == 1`.
- Transaction handling is critical; failed unlink or failed TDB commit must not leave DB/filesystem state inconsistent.
- `posix:eadb` misconfiguration silently disables EA support for the service after logging.
- Full-path construction and POSIX path flags affect whether `STAT` or `LSTAT` is used before deletion.

## Test Signals
- Configure `posix:eadb`, set/list/get/remove xattrs through SMB, and verify persistence in the DB.
- Remove files with single and multiple hard links; EA records should survive until the last link disappears.
- Remove directories with EAs and verify records are deleted transactionally.
- Simulate missing or unwritable DB path and verify the share continues with `ea support = False`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_posix_eadb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_posixacl.c -->
# sources/user-network-fs/samba/source3/modules/vfs_posixacl.c

## Purpose
`vfs_posixacl.c` maps Samba's internal POSIX ACL representation to the platform POSIX ACL API. It implements fd/pathref ACL get, set, and default ACL delete hooks for systems exposing `acl_get_fd`, `acl_get_file`, `acl_set_fd`, `acl_set_file`, and `acl_delete_def_file`.

## Important APIs, Types, And Functions
- Public hooks: `posixacl_sys_acl_get_fd`, `posixacl_sys_acl_set_fd`, and `posixacl_sys_acl_delete_def_fd`.
- Conversion helpers: `smb_ace_to_internal`, `smb_acl_to_internal`, `smb_acl_set_mode`, and `smb_acl_to_posix`.
- Uses Samba types `SMB_ACL_T`, `SMB_ACL_TYPE_T`, `struct smb_acl_t`, and `struct smb_acl_entry`.
- `posixacl_fns` also wires `.sys_acl_blob_get_fd_fn = posix_sys_acl_blob_get_fd`.

## Control Flow
Get maps Samba ACL type to `ACL_TYPE_ACCESS` or `ACL_TYPE_DEFAULT`, chooses fd-based access ACL retrieval when possible, uses `/proc/fd` path support for pathrefs, or falls back to filename-based ACL calls. Retrieved platform ACL entries are iterated and converted into Samba entries. Set converts Samba entries into a platform ACL, validates it with `acl_valid`, and writes via fd, proc-fd path, or pathname. Default ACL delete uses proc-fd if available and pathname otherwise.

## State And Persistence
The module stores no private state. ACL state persists in the filesystem's ACL metadata. Temporary ACL objects are freed with `acl_free`; Samba ACL arrays are allocated on the caller's `TALLOC_CTX`.

## Dependencies And Integration Points
It depends on system POSIX ACL headers/APIs and Samba's ACL abstractions. It is a VFS module named `posixacl` and can be stacked where Samba needs direct POSIX ACL pass-through. It recognizes platform-specific `HAVE_ACL_GET_PERM_NP` and explicitly rejects `ACL_EVERYONE` with guidance to use `zfsacl`.

## Risks
- Pathname fallback is no longer truly handle-based and can be vulnerable to races compared with fd/proc-fd paths.
- Unsupported ACL tags fail conversion; FreeBSD/ZFS `ACL_EVERYONE` is intentionally not handled.
- ACL qualifier ownership and permission bit mapping must be exact to avoid access-control changes.
- `acl_valid` failures are logged with textual ACL output and must prevent invalid ACL persistence.

## Test Signals
- Round-trip user, group, owner, group object, mask, and other ACL entries through SMB and compare with native `getfacl`.
- Exercise pathref handles with and without proc-fd support.
- Attempt invalid Samba ACLs and verify `acl_valid` failure prevents write.
- Test default ACL deletion on directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_posixacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_posixacl.h -->
# sources/user-network-fs/samba/source3/modules/vfs_posixacl.h

## Purpose
`vfs_posixacl.h` declares the public hook functions implemented by `vfs_posixacl.c`. It allows other Samba source files or module registration code to reference the POSIX ACL operations without exposing helper internals.

## Important APIs, Types, And Functions
- Declares `posixacl_sys_acl_get_fd`.
- Declares `posixacl_sys_acl_set_fd`.
- Declares `posixacl_sys_acl_delete_def_fd`.
- Uses Samba VFS and ACL types including `vfs_handle_struct`, `files_struct`, `SMB_ACL_TYPE_T`, `SMB_ACL_T`, and `TALLOC_CTX`.

## Control Flow
The header has no runtime control flow. It provides prototypes guarded by `__VFS_POSIXACL_H__`.

## State And Persistence
No state is defined here. Persistence behavior belongs to the implementation and the filesystem ACL layer.

## Dependencies And Integration Points
The header assumes including translation units already have the relevant Samba type definitions available through `includes.h` or module includes. It is included by `vfs_posixacl.c`.

## Risks
- Prototype drift between this header and `vfs_posixacl.c` would cause build failures or ABI mismatches.
- Because only public functions are declared, helper reuse requires editing the implementation or adding new declarations deliberately.

## Test Signals
- Full Samba/module build should validate prototypes.
- Any caller including the header should compile without duplicate or missing symbol warnings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_posixacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_prealloc.c -->
# sources/user-network-fs/samba/source3/modules/vfs_prealloc.c

## Purpose
`vfs_prealloc.c` preallocates disk extents for newly created or truncated files based on filename extension. It targets XFS-style reservation APIs so large expected files can be laid out more efficiently without immediately changing logical file size.

## Important APIs, Types, And Functions
- `preallocate_space()` issues `XFS_IOC_RESVSP64`, `F_RESVSP64`, or fails with `ENOSYS` depending on platform support.
- `prealloc_connect()` loads `prealloc:debug`.
- `prealloc_openat()` checks `O_CREAT`/`O_TRUNC`, extracts a lowercase extension up to nine characters, reads `prealloc:<ext>`, opens the file, stores the requested size as an FSP extension, and preallocates.
- `prealloc_ftruncate()` delegates truncate then reapplies the saved preallocation.

## Control Flow
Only create/truncate-oriented opens are eligible. The extension is parsed from `smb_fname->base_name`, converted to lowercase, and used as a loadparm key. If no configured positive size exists, open passes through. If configured, the file is opened first, an FSP extension stores the size, and the reservation call runs. Truncate reuses that extension to restore the reserved allocation after logical size changes.

## State And Persistence
The module has global `module_debug` and per-open FSP extension state containing the reservation size. Reservations are filesystem allocation state, not Samba metadata; `RESVSP` is chosen so reservation should not inflate `st_size`.

## Dependencies And Integration Points
It depends on Samba VFS open/truncate hooks, loadparm parsing, and platform XFS/fcntl reservation APIs. It registers as `prealloc` and is configured with keys like `prealloc:mpeg = 500M`.

## Risks
- There is a suspicious `if (!ok); goto normal_open;` pattern after `strlower_m(fext)` that makes normal-open flow unconditional in that block; this should be treated as a bug signal when reviewing behavior.
- Platform support is conditional; unsupported builds silently fail reservation with debug logging.
- Extension length is capped at `sizeof(fext) - 1`.
- Reservation failures remove the FSP extension, so later truncate will not retry.

## Test Signals
- Configure a matching extension and verify reservation syscall occurs on create/truncate opens.
- Verify nonmatching, long-extension, and read-only opens bypass preallocation.
- Test truncate after preallocated open and confirm reservation is reissued.
- Build/test on platforms with and without XFS reservation support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_prealloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_preopen.c -->
# sources/user-network-fs/samba/source3/modules/vfs_preopen.c

## Purpose
`vfs_preopen.c` improves sequential numbered-file access by forking helper processes that open and read the first bytes of likely upcoming files. It is a cache-warming module driven by filename patterns and numeric sequences.

## Important APIs, Types, And Functions
- `struct preopen_state` stores helper pool, queue limits, logging levels, matching state, filename template, digit position/count, and queued numeric range.
- `struct preopen_helper` tracks child pid, socket fd, tevent fd, and busy status.
- Helper lifecycle: `preopen_init_helper`, `preopen_helper`, `preopen_helper_open_one`, `preopen_helper_readable`, `preopen_helper_destroy`, and `preopen_helpers_destructor`.
- Queue logic: `preopen_queue_run`, `preopen_parse_fname`, `num_digits_max_value`.
- `preopen_state_get()` lazily initializes state from `preopen:*` parameters and creates wildcard or POSIX basic regex matchers.
- `preopen_openat()` is the only VFS hook.

## Control Flow
On each open, the module lazily creates helpers if `preopen:names` is configured, delegates the real open first, then only continues for successful read-only file opens. It requires an absolute directory path and relative non-dot basename. The basename is matched against configured patterns. If matched, the module constructs an absolute template, discovers a numeric field, detects sequence resets when the pattern, digit offset, digit count, prefix, or suffix changes, advances sent counters, computes a bounded queue end, and pushes future filenames over idle helper sockets. Helpers read a NUL-terminated pathname, open it read-only, read `num_bytes`, and signal completion with one byte.

## State And Persistence
Per-handle state persists for the VFS handle lifetime and owns child processes. Child helpers are killed and waited in the destructor. No on-disk state is changed; effects are kernel page-cache warming only.

## Dependencies And Integration Points
It depends on `tevent`, socketpairs, fork, `sys_rw`, Samba path matching helpers, global event context, and VFS open hooks. Configuration includes `preopen:names`, `preopen:num_bytes`, `preopen:helpers`, `preopen:queuelen`, `preopen:posix-basic-regex`, and log-level knobs.

## Risks
- Forked helper management must avoid leaking children or descriptors; destructor correctness is important.
- Helpers use raw POSIX `open()` on constructed absolute paths, bypassing parts of Samba VFS policy for the speculative read path.
- Numeric parsing assumes useful sequences have at least three adjacent digits unless regex replacement hints provide exact positions.
- Aggressive queues can create extra backend I/O for users who skip around in a sequence.

## Test Signals
- Configure wildcard and regex `preopen:names`; open `file001` and observe helper opens for subsequent numbers.
- Verify reset behavior when moving to a different pattern, digit width, prefix, or suffix.
- Confirm write opens, relative directories, dot names, and absolute basenames bypass preopen.
- Run under process/fd leak checks and verify helpers terminate when the VFS handle is destroyed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_preopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_readahead.c -->
# sources/user-network-fs/samba/source3/modules/vfs_readahead.c

## Purpose
`vfs_readahead.c` issues kernel readahead hints for reads at configured boundaries. It targets clients that issue large sequential reads, especially Vista-era AIO patterns, so later reads may hit warm cache.

## Important APIs, Types, And Functions
- `struct readahead_data` stores `off_bound`, `len`, and a once-only warning flag.
- `readahead_sendfile()` and `readahead_pread()` trigger Linux `readahead()` or `posix_fadvise(POSIX_FADV_WILLNEED)` when `offset % off_bound == 0`.
- `readahead_connect()` allocates per-handle data and reads `readahead:offset` and `readahead:length`.
- `free_readahead_data()` frees the heap allocation.

## Control Flow
On connect, defaults are established: offset boundary defaults to `0x80000`, and length defaults to the boundary. Sendfile and pread wrappers inspect offsets and issue the platform hint only at exact boundaries before delegating to the next VFS operation. Unsupported platforms log one warning per connection path.

## State And Persistence
State is per VFS handle and freed on disconnect. The module changes no files; it only influences kernel cache behavior.

## Dependencies And Integration Points
It depends on Linux `readahead` or POSIX fadvise availability, Samba VFS `pread`/`sendfile`, and loadparm size parsing. It registers as `readahead`.

## Risks
- If `readahead:offset` resolves to zero after parsing but before defaulting incorrectly, modulo-by-zero would be dangerous; current code defaults zero to `0x80000`.
- Workloads with random boundary-aligned reads may cause wasted I/O.
- The module assumes `handle->data` is initialized by connect before read hooks are called.

## Test Signals
- With Linux support, trace `readahead(fd, offset, len)` at configured boundaries.
- With fadvise-only support, trace `posix_fadvise`.
- Verify no hint occurs for non-boundary offsets.
- Verify unsupported builds log the warning only once per handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_readahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_readonly.c -->
# sources/user-network-fs/samba/source3/modules/vfs_readonly.c

## Purpose
`vfs_readonly.c` makes a share read-only during a configured date/time window. It is a connection-time policy module that parses human-readable date expressions using `get_date()`.

## Important APIs, Types, And Functions
- `readonly_connect()` reads `readonly:period`, delegates connect, parses begin/end times, sets `conn->read_only`, and clears the VUID cache.
- `vfs_readonly_fns` registers only `.connect_fn`.
- Default period is `"today 0:0:0","tomorrow 0:0:0"`, which effectively makes the share read-only for the current day if no parameter is supplied.

## Control Flow
After successful downstream connect, the module obtains a two-element period list from the module parameter namespace, with `handle->param` override support. It compares `time(NULL)` to parsed begin/end values. If current time is within the interval, it sets `handle->conn->read_only = True` and invalidates cached VUID entries so later access decisions re-evaluate read-only state.

## State And Persistence
State is per connection in `connection_struct`. It does not persist to disk. VUID cache entries are cleared in memory to avoid stale write permissions.

## Dependencies And Integration Points
It depends on Samba loadparm list parsing, `getdate.h`, connection read-only enforcement, and Samba's VUID cache layout. It registers as `readonly`.

## Risks
- Date parsing failures are not explicitly checked; invalid expressions may produce unexpected `time_t` values.
- The default period can surprise administrators by making the share read-only unless overridden.
- The policy is evaluated only at connect time; long-lived connections do not automatically flip when the time window starts or ends.

## Test Signals
- Connect inside and outside a configured period and verify write access decisions.
- Verify VUID cache entries are invalidated after enabling read-only.
- Test invalid, missing, and single-element `readonly:period` lists.
- Test multiple stacked instances using different `handle->param` names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_readonly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_recycle.c -->
# sources/user-network-fs/samba/source3/modules/vfs_recycle.c

## Purpose
`vfs_recycle.c` implements a Samba recycle bin. Instead of deleting regular files, it moves them into a configured repository, optionally preserving directory structure, versioning duplicate names, and touching timestamps.

## Important APIs, Types, And Functions
- `struct recycle_config_data` stores repository, `keeptree`, `versions`, touch flags, exclude lists, version-exclusion list, directory modes, and size limits.
- `vfs_recycle_connect()` reads configuration, performs Samba substitutions in the repository path, and stores config as handle data.
- Helpers include `recycle_directory_exist`, `recycle_file_exist`, `recycle_get_file_size`, `recycle_create_dir`, `matchdirparam`, `matchparam`, and `recycle_do_touch`.
- `recycle_unlink_internal()` performs the recycle-or-purge decision and rename.
- `recycle_unlinkat()` bypasses directories and recycles regular unlink calls.

## Control Flow
Connect skips IPC/print shares, allocates config, expands `recycle:repository`, trims trailing slash, reads booleans/lists/modes/sizes, and stores the result. On file unlink, the module builds the full path, avoids recycling anything already inside the repository, enforces min/max file-size policy, splits parent/base, applies filename and directory exclude patterns, creates the target repository/tree, builds a destination `smb_filename`, handles existing destination by deleting or generating `Copy #N of ...`, then delegates `SMB_VFS_NEXT_RENAMEAT`. If setup or rename fails, it falls back to actual unlink. Touch options update atime/mtime using a synthetic pathref.

## State And Persistence
Configuration is per connection. Persistent state is the repository directory and moved files. Versioning state is implicit in existing destination filenames. The module does not maintain an index.

## Dependencies And Integration Points
It depends on Samba substitutions, VFS stat/mkdir/rename/unlink/fntimes hooks, wildcard matching, connection/session user data, and debug class registration. It integrates at `unlinkat_fn`, leaving directory removal untouched.

## Risks
- Recycling is implemented as rename; cross-filesystem repository paths can fail and cause purge fallback.
- Repository path prefix checks are string-based and can be sensitive to normalization.
- Size max logic applies to individual file size, not total recycle-bin usage; a FIXME notes this.
- Version loop can be expensive in directories with many duplicate copies.
- Failure paths often purge the file to preserve unlink semantics.

## Test Signals
- Delete files with default and custom repositories; verify rename target and optional tree preservation.
- Test `exclude`, `exclude_dir`, `noversions`, `versions`, `minsize`, and `maxsize`.
- Delete a file already in the recycle repository and verify it is purged.
- Test duplicate names and `Copy #N` generation.
- Verify touch/touch_mtime behavior after recycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_recycle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_shadow_copy.c -->
# sources/user-network-fs/samba/source3/modules/vfs_shadow_copy.c

## Purpose
`vfs_shadow_copy.c` is the older shadow-copy module that exposes snapshot directories named exactly like `@GMT-YYYY.MM.DD-HH.MM.SS` at the share root while hiding those directories from normal listings.

## Important APIs, Types, And Functions
- `shadow_copy_match_name()` recognizes fixed-length `@GMT-` labels.
- `shadow_copy_fdopendir()` reads the real directory, filters out `@GMT` entries, copies remaining `struct dirent` values into a private `shadow_copy_Dir`, closes the real DIR/fd, and returns the private object as `DIR *`.
- `shadow_copy_readdir`, `shadow_copy_rewinddir`, and `shadow_copy_closedir` operate on the private directory buffer.
- `shadow_copy_get_shadow_copy_data()` opens the share root and enumerates `@GMT` labels for Windows shadow-copy queries.

## Control Flow
Directory open delegates to the next VFS layer, consumes all entries immediately, hides snapshot labels, and substitutes an in-memory directory iterator. Shadow-copy data enumeration independently opens `conn->connectpath` through Samba directory APIs and counts or copies labels depending on the `labels` flag.

## State And Persistence
The module stores transient directory-list buffers only. Snapshot persistence is external: directories must already exist at the share root with correct `@GMT` names.

## Dependencies And Integration Points
It depends on Samba directory APIs (`OpenDir`, `ReadDirName`), VFS directory hooks, `ntioctl` shadow-copy data types, and a debug class named `shadow_copy`. It registers as `shadow_copy`.

## Risks
- Snapshot labels must exactly match the sample length and prefix; no timestamp validation beyond string shape.
- `shadow_copy_fdopendir()` closes the real DIR and fd after snapshotting entries, so directory changes after open are not reflected.
- Copying raw `struct dirent` into a realloc array assumes the platform struct contains enough fixed storage for names as used by Samba.
- The module only discovers snapshots at the share root.

## Test Signals
- Create root-level `@GMT-YYYY.MM.DD-HH.MM.SS` directories and verify shadow-copy enumeration returns them.
- Normal directory listings should hide those `@GMT` directories.
- Rewind and close on the synthetic DIR should behave correctly.
- Malformed `@GMT`-prefixed names should be ignored.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_shadow_copy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_shadow_copy2.c -->
# sources/user-network-fs/samba/source3/modules/vfs_shadow_copy2.c

## Purpose
`vfs_shadow_copy2.c` is the richer shadow-copy implementation. It exposes filesystem snapshots as Windows Previous Versions by translating SMB `@GMT` timestamp references (`smb_filename->twrp`) into snapshot filesystem paths, enumerating snapshots from configurable snapshot directories, and blocking writes into snapshots.

## Important APIs, Types, And Functions
- `struct shadow_copy2_config` stores `shadow:*` parameters: timestamp format, sscanf/localtime mode, snapdir, delimiter, snapdirseverywhere, crossmountpoints, fixinodes, sort order, mount point, relative connect path, and snapshot base path.
- `struct shadow_copy2_private` stores config, cached regex snaplist, `shadow_cwd`, and connectpath state.
- Path conversion helpers: `shadow_copy2_strip_snapshot_internal`, `check_for_converted_path`, `shadow_copy2_do_convert`, `shadow_copy2_convert`, `shadow_copy2_insert_string`, `shadow_copy2_snapshot_path`, and `make_path_absolute`.
- Snapshot enumeration helpers: `shadow_copy2_find_snapdir`, `shadow_copy2_snapshot_to_gmt`, `shadow_copy2_get_shadow_copy_data`, and sorting helpers.
- VFS wrappers cover stat/lstat/fstat/fstatat/open/readlink/realpath/disk_free/quota/DFS/parent_pathname and deny rename/link/symlink/unlink/mkdir/mknod/chmod/chflags/fsetxattr/fntimes into snapshots.
- `shadow_copy2_connect()` parses and validates configuration and registers private state.

## Control Flow
Connect delegates first, allocates private state, reads `shadow:*` parameters, validates incompatible combinations, discovers or validates mountpoint/basedir/snapsharepath, computes `snapshot_basepath`, trims path strings, and stores handle data. For reads and metadata, wrappers inspect `twrp` or already-converted paths. If no timestamp is present, they delegate and optionally adjust inode values for converted snapshot paths. If a timestamp exists, they strip the SMB-layer snapshot marker, convert the requested path to a backend snapshot path, delegate using the converted name, and then restore caller-visible objects. Mutating operations detect timestamp or converted snapshot paths and fail with `EROFS` or `EXDEV`. Enumeration opens the discovered snapshot directory, verifies list permission, converts backend snapshot names to `@GMT` labels, optionally caches regex-based names, and sorts labels.

## State And Persistence
Per-connection state holds configuration, current shadow CWD, and a cached snapshot list for regex mapping. Persistent snapshots are external filesystem directories. The module can alter returned inode numbers when `shadow:fixinodes = yes` by hashing the snapshot path into high inode bits, but it does not modify files.

## Dependencies And Integration Points
It depends on Samba VFS path, open, stat, directory, DFS, quota, and parent-pathname APIs; `ntioctl` shadow-copy structures; TDB Jenkins hash for inode adjustment; POSIX regex; and loadparm. It is intended for stacking where snapshot directories are visible in the local filesystem and registers as `shadow_copy2`.

## Risks
- Path conversion is complex and highly configuration-sensitive; absolute snapdir, snapdirseverywhere, basedir, mountpoint, and snapsharepath interactions can produce surprising paths.
- Snapshot write protection relies on all mutating hooks being covered; missing hooks could allow writes through a snapshot path.
- Cached regex snapshot names must refresh when requested timestamp is newer than fetch time.
- The code sometimes maps conversion failures to `ENOMEM` even when the underlying condition is not memory-related.
- `fixinodes` reduces but does not eliminate inode collision risk.

## Test Signals
- Enumerate snapshots with `shadow:format`, `shadow:snapdir`, sorting, regex prefix/delimiter, and labels/no-labels calls.
- Open/stat/read files through SMB Previous Versions and verify backend path conversion for classic and `snapdirseverywhere` layouts.
- Attempt writes, renames, xattrs, mkdir, DFS create, and unlink through `@GMT` paths and verify `EROFS`/write-protected behavior.
- Test absolute snapdir, mountpoint, basedir, snapsharepath, and crossmountpoints combinations.
- Verify `fixinodes` changes returned inode values only for snapshot paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_shadow_copy2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_shell_snap.c -->
# sources/user-network-fs/samba/source3/modules/vfs_shell_snap.c

## Purpose
`vfs_shell_snap.c` implements Samba snapshot-management hooks by invoking administrator-configured shell commands. It does not implement snapshot I/O; it provides check/create/delete plumbing for external snapshot tooling.

## Important APIs, Types, And Functions
- `shell_snap_check_path()` runs `shell_snap:check path command <service_path>` and returns the service path as the base volume on success.
- `shell_snap_create()` runs `shell_snap:create command <base_volume>`, reads stdout, and expects a single snapshot path line.
- `shell_snap_delete()` runs `shell_snap:delete command <base_path> <snap_path>`.
- `shell_snap_fns` registers snap check/create/delete hooks.

## Control Flow
Each hook reads its configured command from the service parameters. Missing commands return `NT_STATUS_NOT_SUPPORTED`. Create uses `smbrun` with stdout captured to an fd, reads bounded lines via `fd_lines_load`, and copies base/snapshot paths to caller memory. Delete and check use command exit status only.

## State And Persistence
The module stores no state. Persistent effects are entirely produced by external commands.

## Dependencies And Integration Points
It depends on `smbrun`, Samba parameter lookup, `fd_lines_load`, and snapshot-management VFS hooks. It registers as `shell_snap`.

## Risks
- Command strings are concatenated with paths without shell escaping in this file; safe configuration and trusted paths are critical.
- Create assumes the first output line is the snapshot path and ignores extra semantics.
- Exit-code-only check/delete may not distinguish unsupported, permission denied, and transient failures.

## Test Signals
- Configure harmless scripts for check/create/delete and verify hook statuses and returned paths.
- Test missing command parameters and nonzero exits.
- Test snapshot path output with empty, long, and multiple-line stdout.
- Validate behavior with service paths containing spaces or shell metacharacters in a controlled environment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_shell_snap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_snapper.c -->
# sources/user-network-fs/samba/source3/modules/vfs_snapper.c

## Purpose
`vfs_snapper.c` integrates Samba with Snapper over system DBus. It exposes Snapper snapshots as shadow copies, supports snapshot create/delete management hooks, and translates SMB `@GMT` timestamped paths into Snapper snapshot paths while denying writes into snapshots.

## Important APIs, Types, And Functions
- DBus model types: `struct snapper_dict`, `struct snapper_snap`, and `struct snapper_conf`.
- DBus utility functions: `snapper_dbus_str_encode`, `snapper_dbus_str_decode`, `snapper_dbus_conn_create`, `snapper_dbus_msg_xchng`, `snapper_type_check`, and unpack/pack helpers for configs, snapshots, create, delete, and list-at-time.
- Snapper management hooks: `snapper_snap_check_path`, `snapper_snap_create`, `snapper_snap_delete`, and `snapper_get_shadow_copy_data`.
- Path translation helpers: `snapper_gmt_strip_snapshot`, `snapper_get_snap_at_time_call`, `snapper_snap_path_expand`, and `snapper_gmt_convert`.
- VFS wrappers mirror `shadow_copy2` coverage for stat/lstat/fstatat/open/readlink/realpath/chdir/disk_free/quota/get_real_filename and mutating-operation denial.

## Control Flow
DBus calls are synchronous: create a private system-bus connection, pack a method call, send and block for a reply, validate the reply type and signature, unpack typed arrays/structs/dictionaries, then unref messages and close the connection. Config discovery calls Snapper `ListConfigs` and requires the share path to exactly match a Snapper mount. Shadow-copy listing calls `ListSnapshots`, skips the current snapshot entry, and formats labels in descending order. GMT path access converts `smb_fname->twrp` to Unix time, asks Snapper for snapshots at that exact time, builds `base/.snapshots/<id>/snapshot`, appends the requested path, and delegates the VFS operation on that converted path. Mutating wrappers return `EROFS`, `EXDEV`, or media-write-protected NTSTATUS when the source or target has a timestamp.

## State And Persistence
The module stores no long-lived VFS private state. Each operation opens a new private DBus connection so Snapper sees the correct effective UID. Persistent state is owned by Snapper and the filesystem under `.snapshots`.

## Dependencies And Integration Points
It depends on libdbus, Snapper's `org.opensuse.Snapper` DBus API, Samba VFS hooks, NTSTATUS utilities, and SMB timestamp handling. It registers as `snapper` and participates both in shadow-copy enumeration and snapshot management (`FSCTL_SRV_REQUEST_RESUME_KEY`/shadow-copy style operations via Samba hooks).

## Risks
- DBus operations are blocking and can add latency to metadata and snapshot path access.
- `snapper_get_conf_call()` only supports exact share-root to Snapper-config mount matches.
- The code maps only `error.no_permissions` explicitly; other DBus errors collapse to `NT_STATUS_UNSUCCESSFUL`.
- Timestamp lookup uses exact lower/upper time equality; snapshots with nearby but not exact times will not match.
- Path construction assumes Snapper's `.snapshots/<id>/snapshot` layout.
- Some error paths use `abort()` on allocation failure inside unpack loops.

## Test Signals
- With Snapper configured for the share root, list Previous Versions and verify labels exclude the current snapshot.
- Create and delete snapshots through Samba snapshot hooks and verify Snapper IDs/paths.
- Open/stat/read files through `@GMT` labels and verify conversion to `.snapshots/<id>/snapshot`.
- Attempt mutating operations through snapshot paths and verify read-only failures.
- Test DBus permission errors, missing Snapper service, no matching config, and no snapshot at exact time.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/modules/vfs_snapper.c -->
