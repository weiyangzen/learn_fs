# subset-b-007041 Research

Grouped research for EOS MGM OFS command and fsctl sources. Each section preserves the source path in its title and is wrapped for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Remdir.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Remdir.inc

Purpose: implements directory deletion for `XrdMgmOfs`. The public `remdir()` entrypoint maps the XRootD security entity into a `VirtualIdentity`, performs namespace mapping, token scope checks, authorization for `AOP_Delete`, write access mode, stall/redirect checks, and delegates to `_remdir()`.

Important APIs and types: `XrdMgmOfs::remdir`, `XrdMgmOfs::_remdir`, `eos::common::VirtualIdentity`, `eos::common::Path`, `eos::IContainerMD`, `Acl`, `Quota`, `ProcCommand`, `RWMutexWriteLock`, and FuseX broadcast helpers. `_remdir()` supports a `simulate` parameter used by callers that need permission/existence validation without mutation.

Control flow: `_remdir()` rejects quota-node paths first, then takes the EOS view write lock, resolves the target container and its parent, builds the ACL path from the symlink-free parent URI, and returns `ENOENT` if the container is missing. If `mgm.option=r` is passed, it releases the namespace lock and runs the recursive `/proc/user` `rm -r` command instead of doing direct container removal. Non-recursive deletion evaluates immutable ACLs, public-access restrictions, explicit ACL delete/write denies, POSIX parent `W_OK|X_OK`, token-based UNIX-permission bypass, and sticky-bit ownership rules before mutating metadata.

State and persistence behavior: successful deletion updates parent directory mtime, notifies the directory service, persists the parent container, removes the child container from the view, releases the namespace lock, and broadcasts FuseX deletion/refresh events. It emits an audit `RMDIR` event with a trailing slash for directory paths when audit is enabled and `AllowAuditModification()` permits it.

Dependencies and integration points: integrates with quota-node checks (`Quota::Exists` and `QUOTA_NODE_FLAG`), ACL evaluation, public-access policy, the `/proc/user` command interface for recursive deletion, MGM stats/timing, EOS namespace services, and FuseX client cache invalidation. It is called directly from the XRootD `rmdir` API and indirectly by rename overwrite handling for empty target directories.

Risks: the expression `(dh->getFlags() && eos::QUOTA_NODE_FLAG)` is logical rather than bitwise and will treat any nonzero flags as a quota-node match for non-root users. Recursive mode releases the view lock before invoking `ProcCommand`, so state can change between permission checks and recursive execution. Permission behavior differs between ACL, sticky-bit, and token cases and should be regression-tested around explicit `!d`/`!w` ACLs.

Test signals: cover non-empty directory deletion (`ENOTEMPTY`), quota-node rejection, immutable ACL denial, explicit ACL delete/write denial, sticky-bit owner-only deletion, token-authorized deletion bypassing UNIX mode checks, recursive `mgm.option=r` dispatch, parent mtime/FuseX notifications, and audit emission on successful deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Remdir.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Rename.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Rename.inc

Purpose: implements file and directory rename/move operations for the MGM namespace, including public XRootD API authorization, low-level metadata mutation, overwrite behavior, version-directory moves, quota accounting, container accounting, FuseX invalidation, and a special move-with-symlink variant.

Important APIs and types: `XrdMgmOfs::rename` public and internal overloads, `XrdMgmOfs::_rename`, `XrdMgmOfs::_rename_with_symlink`, `eos::common::Path`, `IFileMD`, `IContainerMD`, `Prefetcher`, `Quota`, `IQuotaNode`, `MDLocking::BulkMDWriteLock`, `FusexCastBatch`, `Recycle::gRecyclingPrefix`, and `eos::isSafeToRename`.

Control flow: the public `rename()` decodes `#space#`, rejects version-file paths, maps identity for `AOP_Update`, separately authorizes old path deletion and new path update, applies namespace mapping and access-mode macros, then delegates to the internal API. The internal checked overload re-runs mapping, checks write access on source and destination with `_access()`, then calls `_rename()`. `_rename()` handles null/same-name cases, prefetches source/target parents and items, determines whether source is a file or directory, forbids moving a directory under itself, rejects renaming quota-node directories, and resolves target conflicts. Existing target files may be deleted via `_rem()` when overwrite is allowed; target directories cause basename append and empty-directory removal through `_remdir()`.

File rename behavior: within a single container it locks the parent and file, calls `renameFile`, updates parent mtime, persists the container, and queues FuseX deletion/refresh events. Across containers it obtains quota nodes before taking bulk locks, removes the file from the old parent, updates both parent mtimes, changes file name/container id, optionally updates ctime, persists file/container metadata, adjusts quota nodes, and broadcasts both source and destination refreshes.

Directory rename behavior: for cross-quota-node directory moves, `_find()` builds a subtree file list for quota checking and quota-node adjustment. It validates available target quota per uid/gid when `checkQuota` is true. It performs two `isSafeToRename()` checks, one early and one just before mutation. Same-parent directory rename locks source child and parent, renames the container, updates ctime/parent mtime, persists metadata, and broadcasts. Cross-parent moves remove the child from the source parent, update source container accounting, rename and reparent the moved container, add its tree accounting to the target parent, update mtimes, persist all containers, and queue FuseX refresh/deletion events.

Version and symlink behavior: if a file has a version directory and the target is outside that directory and outside recycle, `_rename()` recursively renames the version directory after the main rename. `_rename_with_symlink()` moves a file into a destination directory while creating a symlink at the old storage path pointing to the new storage path. It rejects directories and files with versions, requires source/destination access, prevents same directory moves, creates the namespace link via `eosView->createLink()`, adjusts quota nodes, persists metadata, broadcasts, and audits as `RENAME`.

State and persistence behavior: mutates file names, container membership, parent ids, container tree accounting, quota-node file accounting, mtimes/ctimes, and persistent file/container stores. FuseX broadcasts are batched to run after lock-protected state transitions. Successful operations audit `RENAME` with old path as auxiliary data and append slashes for directory renames.

Dependencies and integration points: heavily depends on `_exists`, `_access`, `_rem`, `_remdir`, `_find`, quota APIs, `eosView`, directory/file services, `eosContainerAccounting`, `mAudit`, and XRootD error propagation. It is also used by versioning and commit de-atomization paths.

Risks: overwrite handling uses deletion before rename and must preserve version semantics through `keepversion`. Directory quota moves are not fully atomic with subtree scans, as comments note. Cross-parent directory moves must keep quota and container accounting consistent if a late safe-rename check fails. `_rename_with_symlink()` creates storage-level side effects while holding metadata locks, so filesystem errors can leave partial external state.

Test signals: same-name no-op, source missing, target existing file with and without overwrite, directory moved into own subtree, quota-node directory rejection, same-parent and cross-parent file moves, same-parent and cross-parent directory moves with container accounting, cross-quota-node quota failure, version-directory rename, recycle-excluded version behavior, symlink move validation and link creation, FuseX events, and audit records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Rename.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Rm.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Rm.inc

Purpose: implements file deletion for the MGM namespace, including public XRootD authorization, ACL and sticky-bit enforcement, direct deletion, recycle-bin deletion, delete workflows, hardlink/COW handling, quota updates, version purge, FuseX notifications, and audit logging.

Important APIs and types: `XrdMgmOfs::rem`, `XrdMgmOfs::_rem`, `XrdSfsFileExistence`, `IFileMD`, `IContainerMD`, `Acl`, `RecycleEntry`, `Workflow`, `Quota`, `XrdMgmOfsFile::create_cow`, `XrdMgmOfsFile::handleHardlinkDelete`, `WriteRmRecord`, `WriteRecycleRecord`, `PurgeVersion`, and `EOS_DTRACE_ATTR`.

Control flow: public `rem()` maps namespace and identity, checks token scope and delete authorization, applies write access mode/stall/redirect macros, then calls `_rem()`. `_rem()` verifies the path is an existing file, prefetches metadata, takes the view write lock, loads file and parent container, evaluates immutable ACL/public access/write-once/delete-deny/sticky-bit rules, and decides whether deletion should go through recycle or be immediate. Recycle is enabled when the recycler is globally enforced or the parent has the recycle attribute and the path is not already under the recycle prefix.

Direct deletion behavior: when not recycling and not simulating, it removes file quota from the parent quota node, optionally releases the namespace lock to trigger `sync::delete` workflow, creates COW state for delete, handles hardlink deletion, unlinks the file from the namespace, reloads the modified file record, drops tape unlinked location when needed, removes file metadata if no linked or unlinked locations remain, writes an rm record, updates parent mtime, persists parent metadata, releases the lock, and broadcasts FuseX deletion/refresh events.

Recycle behavior: releases the namespace lock, reads recycle directory/id from attributes, checks responsible quota and available recycle space unless disabled, creates a `RecycleEntry`, triggers `sync::recycle`, moves the file to garbage, creates COW unlink state, records recycle metadata, stamps delete trace attributes on the recycled path as root, optionally records the version directory inode on the garbage file, and purges versions unless `keepversion` is set.

State and persistence behavior: changes file/container namespace membership, unlinked-location state, quota accounting, file metadata removal, parent mtime, recycle metadata, workflow side effects, and audit/delete records. `simulate` performs permission and recycle decision checks without mutation. `keepversion`, `no_recycling`, `no_quota_enforcement`, `fusexcast`, and `no_workflow` allow callers to tune behavior.

Dependencies and integration points: integrates with recycler configuration, ACL/public access, workflow engine, quota manager, copy-on-write support, hardlink semantics, tape location constants, versioning, Io/audit record writers, FuseX, and MGM stats/timing. Rename overwrite and version purge paths call `_rem()`.

Risks: lock release around workflow and recycle operations allows concurrent namespace changes after validation. Recycle quota checks depend on the recycle path having responsible quota configured. Direct deletion has special tape/unlinked-location cleanup that can leak or prematurely remove metadata if location state is inconsistent. `fusexcast` is accepted but direct deletion always broadcasts in the shown path.

Test signals: file-vs-directory errors, missing file errors, immutable/write-once/`!d` ACL denial, sticky-bit owner/container-owner permission, token permission behavior, direct delete with hardlinks and tape location, workflow failure propagation, recycle quota full and no-quota errors, enforced vs attribute-based recycling, version purge and keepversion, DTrace xattr stamping, parent mtime/FuseX updates, and audit `DELETE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Rm.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/SharedPath.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/SharedPath.inc

Purpose: creates and verifies signed share URLs for EOS files. It binds a path, expiry timestamp, MGM instance name, and file identifier into a symmetric-key signature so shared links become invalid when the file id changes or the link expires.

Important APIs and types: `XrdMgmOfs::CreateSharePath`, `XrdMgmOfs::VerifySharePath`, `XrdOucEnv`, `VirtualIdentity`, `SymKey`, `gSymKeyStore`, `FileId::Fid2Hex`, `_access`, `_exists`, and `_stat`.

Control flow: `CreateSharePath()` namespace-maps the input path, requires read access, verifies the object exists and is a file, stats it as root to retrieve the inode/file id, builds query parameters `eos.share.expires`, `eos.share.fxid`, and `eos.share.signature`, fetches the current symmetric key, encrypts the canonical string `expires + path + expires + instance + fxid`, strips newlines, and returns `path?...signature=...`. `VerifySharePath()` rejects missing signature, missing/zero expiry, missing fid, stat failures, changed file ids, expired timestamps, missing symmetric key, and signature mismatches.

State and persistence behavior: no namespace mutation. Verification does a live stat, so it depends on current file id and path state. The signature uses only the current key, not key id/version data.

Dependencies and integration points: used by share-link authorization paths around XRootD opaque data. Depends on EOS symmetric-key distribution, the MGM instance name, file id stability, path canonicalization from namespace mapping, and current wall-clock time.

Risks: key rotation can invalidate all existing share URLs if only the current key is accepted. The canonical string includes `expires` twice, which must remain stable between producer and verifier. Verification stats the current path, so a replaced file with a different fid invalidates the share as intended, while a moved file likely invalidates the original path. Error logging can include opaque query strings.

Test signals: create link for readable file, reject unreadable path, reject directory, missing key creation failure, verify valid link, reject expired link, reject changed fid, reject modified signature, reject missing fields, and confirm newline stripping makes produced and verified signatures comparable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/SharedPath.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRedirect.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRedirect.inc

Purpose: decides whether a request should be redirected to another MGM endpoint based on configured access redirection rules and the request access mode.

Important APIs and types: `XrdMgmOfs::ShouldRedirect`, `Access::gAccessMutex`, `Access::gRedirectionRules`, access-mode macros such as `IS_ACCESSMODE_R`, `IS_ACCESSMODE_W`, `IS_ACCESSMODE_R_MASTER`, `VirtualIdentity`, and `MgmStats`.

Control flow: localhost and root are exempt when this MGM is master or the request is read-only. With redirection rules present, the function checks global `*`, write `w:*`, read `r:*`, and read-master fallback to `w:*` in precedence order. It tokenizes the selected `host[:port[:delay_ms]]` value, applies default port `1094` for host-only rules, optionally sleeps for a configured delay, records stats by rule type, sets `collapse=true`, and returns true. If no matching rule exists it returns false.

State and persistence behavior: no persistent state changes. It reads global redirection config under the access mutex and records stats counters. The optional delay intentionally blocks the request thread before returning redirect.

Dependencies and integration points: invoked through `MAYREDIRECT` macros in command handlers. Depends on administrator-managed `Access` static state and XRootD redirect response construction by the caller.

Risks: malformed token lists larger than three are silently ignored after setting `collapse=true` and returning true, potentially leaving host/port unchanged. Port parsing uses `strtol` without range validation. Delay is performed while holding the access read lock, which can block config writers and other readers depending on RW lock implementation.

Test signals: localhost/root exemptions, global/read/write/read-master rule selection, host-only default port, host/port parsing, delay handling, empty/malformed rule token behavior, stats counter names, and `collapse` output state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRedirect.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRoute.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRoute.inc

Purpose: delegates path-based request routing decisions to the MGM routing subsystem, supporting reroute and stall responses.

Important APIs and types: `XrdMgmOfs::ShouldRoute`, `PathRouting::Reroute`, `PathRouting::Status::{REROUTE,STALL}`, `VirtualIdentity`, and `MgmStats`.

Control flow: root and localhost clients are never routed. If `mRouting` is null, which can happen during shutdown, the request is not routed. Otherwise `mRouting->Reroute()` receives path, opaque info, identity, and output host/port/stat string. `REROUTE` records the returned stat counter and returns true; `STALL` sets `stall_timeout=5` seconds and returns true; all other statuses return false.

State and persistence behavior: no persistence. It reads routing configuration through `mRouting` and increments stats when reroute occurs.

Dependencies and integration points: used by MGM request front-door logic around path routing. Caller must interpret true plus host/port as reroute or true plus `stall_timeout` as stall. It is separate from static access redirection rules in `ShouldRedirect.inc`.

Risks: a `STALL` result returns true without setting host/port, so callers must branch on `stall_timeout`. Stall duration is hardcoded to 5 seconds. Routing is disabled for privileged/local identities even if rules would otherwise match.

Test signals: root/localhost bypass, null-routing bypass during shutdown, reroute host/port propagation and stat increment, stall timeout behavior, and no-route fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ShouldRoute.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ShouldStall.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/ShouldStall.inc

Purpose: enforces request stalls or delays for banned identities, global/read/write stall rules, per-user/per-group rate rules, and thread-pool saturation.

Important APIs and types: `XrdMgmOfs::ShouldStall`, `Access::gBannedUsers`, `gBannedGroups`, `gBannedHosts`, `gBannedDomains`, `gBannedTokens`, `gStallRules`, `gStallComment`, `gStallGlobal`, `gStallRead`, `gStallWrite`, `gStallUserGroup`, `MgmStats`, `mTracker.ShouldStall`, and `VirtualIdentity`.

Control flow: initially stalling is enabled, then disabled for booted FST daemon SSS clients and for HTTPS unless `EOS_MGM_ALLOW_HTTP_STALL` is set. Under `Access::gAccessMutex`, non-root users above uid 3 and non-stat/non-no-stall-app requests first check per-uid thread saturation, then banned user/group/host/domain/token lists, then global/read/write stall rules, then user/group rate rules. Rate rules match exact and wildcard user/group prefixes and optionally fine-grained Eosxd command names. If a hard stall applies, it adds a random 0-5 second offset unless the stall is rate-limit delay mode, builds a user message, records stats, and returns true. If a rate limit has a finite cutoff but is not a hard saturation, it releases the access lock, sleeps for a computed millisecond delay capped at 40s, records delay stats, and returns false.

State and persistence behavior: no persistent mutation. It reads access policy state, MgmStats moving averages, environment variables, and thread tracker state. It records stall/delay counters and may sleep the current request thread.

Dependencies and integration points: called by `MAYSTALL` macros in most MGM operations. FUSE clients receive immediate true/error-style responses for banned user/group cases instead of long stalls. Localhost root/admin can still be affected by global boot/write stall semantics.

Risks: sleeping request threads can affect thread-pool pressure; the code caps delay but hard stalls may still be long. Several branches depend on string prefixes such as `fuse` and `Eosxd`. The read lock is manually released before delay sleep, so changes after rule evaluation do not cancel the delay. The stat command and a configured FUSE no-stall app bypass many user-level rules.

Test signals: FST daemon bypass, HTTPS bypass and environment override, banned user/group/host/domain/token, FUSE banned behavior, global/read/write stalls, user/group exact and wildcard rate rules, Eosxd command-specific matching, saturated thread stalls with random offset, delay-mode cap at 40s, and localhost/root global stall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ShouldStall.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Shutdown.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Shutdown.inc

Purpose: signal handler for orderly MGM shutdown.

Important APIs and types: `xrdmgmofs_shutdown`, POSIX `signal`, global `gOFS`, `XrdMgmOfs::Shutdown`, `OrderlyShutdown`, logging, and `std::quick_exit`.

Control flow: ignores `SIGINT`, `SIGTERM`, and `SIGQUIT`, logs shutdown start, returns immediately if shutdown is already in progress, sets `gOFS->Shutdown`, calls `gOFS->OrderlyShutdown()`, logs completion, and exits the process with status 0 via `quick_exit`.

State and persistence behavior: mutates the in-memory shutdown flag and delegates all persistent/service cleanup to `OrderlyShutdown()`. It intentionally exits without normal stack unwinding.

Dependencies and integration points: registered as a process signal handler by the MGM process. Commented design indicates `OrderlyShutdown()` handles namespace follower and sub-service shutdown depending on role.

Risks: the handler calls logging and complex shutdown code from a signal context, which is generally not async-signal-safe. `quick_exit` bypasses normal destructors. If `gOFS` is invalid during signal delivery, the handler has no guard.

Test signals: idempotent second signal return, signal ignore setup, `Shutdown` flag set before cleanup, `OrderlyShutdown()` called once, and process exit behavior in integration tests rather than unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Shutdown.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Stacktrace.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Stacktrace.inc

Purpose: signal handler that prints diagnostic stack traces and optionally generates a core file before process termination or signal re-raise.

Important APIs and types: `xrdmgmofs_stacktrace`, `backtrace`, `backtrace_symbols_fd`, `eos::common::StackTrace::GdbTrace`, environment variables `EOS_CORE_DUMP` and `EOS_RAISE_SIGNAL_AFTER_SIGV`, `kill`, and `std::quick_exit`.

Control flow: ignores common termination signals, captures up to ten stack frames, prints the received signal and frame symbols to stderr, asks gdb for `thread apply all bt`, optionally asks gdb to `generate-core-file`, then either restores the default handler and re-sends the original signal or exits with `128 + sig`.

State and persistence behavior: normally no namespace state. It can create a core file when configured and always writes diagnostics to stderr. It exits without normal destructor unwinding unless configured to re-raise.

Dependencies and integration points: registered for crash diagnostics in the MGM process and depends on gdb availability/permissions through `StackTrace::GdbTrace`.

Risks: stack tracing, gdb invocation, environment checks, and stdio are not async-signal-safe. Capturing only ten direct frames may be less useful than the gdb all-thread trace. Core-file generation can be large, which the code avoids by default.

Test signals: handler prints frame information, gdb trace command invocation under normal mode, `EOS_CORE_DUMP` triggers core command, `EOS_RAISE_SIGNAL_AFTER_SIGV` re-raises with default handler, and default path exits with `128 + sig`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Stacktrace.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Stat.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Stat.inc

Purpose: implements stat/lstat and checksum retrieval for files and containers, translating EOS namespace metadata into POSIX `struct stat` plus XRootD-specific tape/offline flags.

Important APIs and types: public `XrdMgmOfs::stat` overloads, `_stat`, `_stat_set_flags`, `_getchecksum`, `lstat`, `eos::Resolver::retrieveFileIdentifier`, `Prefetcher`, `IFileMD`, `IContainerMD`, `LayoutId`, `Quota::MapSizeCB`, `calculateEtag`, and `appendChecksumOnStringAsHex`.

Control flow: public `stat()` namespace-maps and authorizes `AOP_Stat`, maps identity in stat mode, applies read access/stall and redirect except for the master proc path, calls `_stat()`, sets tape/offline flags on success, and may attempt ENOENT redirect/stall handling on missing paths. `_stat()` handles the master proc path only on a master MGM, enforces public access policy, prefetches the item, takes a read lock, and first attempts file lookup. It supports `/.fxid:` inode addressing, rejects a file stat with trailing slash as `EISDIR`, optionally returns URI and checksum, then fills POSIX fields from file metadata. If no file is found, it attempts container lookup and fills directory stat fields.

File metadata behavior: file stat sets device, inode derived from fid, mode from metadata, nlink from layout redundancy and disk/tape locations, size, uid/gid, block size, quota-mapped block count, ctime/mtime/atime including nanoseconds, optional etag, and optional checksum. Tape mode sets `XRDSFS_HASBKUP`, and files with no disk copies but nonzero size set `XRDSFS_OFFLINE`.

Directory metadata behavior: directory stat sets inode from container id, mode, uid/gid, tree size, `st_blksize` as child count, ctime/mtime, and atime as tree-modification time when sync-time accounting is enabled. Etag is calculated from container metadata and checksum is returned empty for directories.

State and persistence behavior: read-only except stats counters and prefetch/cache effects. It does not perform normal ACL checks for stat for performance, but does enforce public-access restrictions.

Dependencies and integration points: used by XRootD stat/lstat, share-path validation, versioning, and checksum queries. Integrates with namespace resolver, metadata services, quota size mapping, layout encoding, tape constants, and redirect/stall macros.

Risks: stat intentionally bypasses ACL checks, making public-access policy the main read guard here. `/.fxid:` lookup bypasses path traversal and must remain restricted by public-access and caller context. File trailing slash detection uses `std::string(path).back()` and assumes non-empty path. `lstat()` behaves like `stat()` and follows the same implementation.

Test signals: regular file stat, symlink/follow behavior, directory stat, missing path, `/.fxid:` lookup, file path with trailing slash, master proc path on non-master, tape-only/offline flags, etag for hardlink attribute, checksum output, public-access denial, and platform-specific nanosecond fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Stat.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Stripes.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Stripes.inc

Purpose: implements low-level replica/stripe maintenance helpers: verifying stripes on FSTs, dropping individual or all stripes, and scheduling stripe copy/move jobs through the drain engine.

Important APIs and types: `_verifystripe` by path and fid, `_dropstripe`, `_dropallstripes`, `_movestripe`, `_copystripe`, `_replicatestripe` by path and by `IFileMD`, `IFileMD`, `IContainerMD`, `FsView`, `FileSystem`, `DrainTransferJob`, `mFidTracker`, `mDrainEngine`, and `SendQuery`.

Control flow: `_verifystripe(path)` resolves fid then calls fid variant. The fid variant reads file metadata for cid/layout, validates parent-container permissions or root-only detached handling, collects parent attributes, looks up target filesystem in `FsView`, constructs an FST query opaque with fid, manager id, access mode, fsid, optional user tag, cid, sealed namespace path, layout id, and options, then sends `/?fst.pcmd=verify` to the FST host/port. `_dropstripe()` resolves file/cid, checks parent write/execute permission or root-only detached drop, write-locks file metadata, records `sys.fs.tracking`, unlinks and optionally removes the location, persists metadata, and for force removal erases inconsistent fsview entries outside the file lock. `_dropallstripes()` requires parent write/execute permission, skips tape-only files, and unlinks/removes every non-tape location.

Replication behavior: `_movestripe()` and `_copystripe()` call `_replicatestripe()` with `dropsource` true/false. The path overload checks parent permissions and source/target location presence. The metadata overload creates a `DrainTransferJob`, registers the fid in `mFidTracker` as a drain operation to avoid duplicate work, and pushes the job to the drain engine thread pool.

State and persistence behavior: verification sends external FST commands but does not mutate namespace metadata. Drop operations mutate file location/unlinked-location lists, `sys.fs.tracking`, file store, optional fsview entries, and sometimes all disk locations. Replication scheduling mutates tracker state and later asynchronous jobs mutate replicas.

Dependencies and integration points: integrates with FST query protocol, FsView id view, layout id/checksum metadata, directory xattrs (`user.tag`), namespace permissions, quota indirectly through file metadata, drain transfer engine, and MGM stats/timing.

Risks: `_verifystripe` condition `cmd && (vid.token || !access)` appears to deny token-authenticated users even if otherwise privileged. `_dropallstripes()` iterates locations while mutating the same file object, which depends on metadata container semantics. Asynchronous replication returns success once scheduled, not once copied/moved. Force removal can erase fsview entries for rare inconsistency cases and needs careful audit.

Test signals: verify by path and fid, missing file/parent/filesystem, permission denial, sealed path in FST query, options propagation, drop linked vs force removal, detached root-only drop, drop-all preserving tape-only files and skipping tape fsid, source missing or target already exists in replication, duplicate fid tracker rejection, and drain job submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Stripes.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Touch.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Touch.inc

Purpose: creates or updates a namespace file entry without necessarily writing data. It supports normal layout-backed creation, no-layout metadata creation, truncation/size preset, external-file registration via hardlink/symlink/absorb, checksum stamping, quota updates, birth-time attributes, and FuseX notifications.

Important APIs and types: `XrdMgmOfs::_touch`, `XrdMgmOfsFile::open`, `attr::checkDirOwner`, `IFileMD`, `IContainerMD`, `FsView`, `LayoutId`, checksum conversion utilities, xattr APIs (`lgetxattr`, `lsetxattr`), POSIX `stat/access/link/symlink/rename`, `IQuotaNode`, and FuseX broadcast helpers.

Control flow: `_touch()` first checks write access, prefetches file metadata, optionally takes the namespace write lock, rejects paths that are directories, detects existing files, validates incompatible options (`absorb` with truncate/no-layout, linkpath without layout) and root-only external registration, then validates the external `linkpath` if supplied. If the file does not exist and `useLayout` is true, it releases the lock and opens the file through `XrdMgmOfsFile` with `SFS_O_CREAT` and `eos.bookingsize=0&eos.app=touch`, expecting a redirect-style successful booking. If `useLayout` is false, it applies `sys.owner.auth` sticky ownership behavior and creates file metadata directly.

External registration behavior: for each nonzero non-tape location, it maps the fid to the local FST path. Absorb mode renames the provided external file into the FST tree. Non-absorb mode tries a hardlink and falls back to symlink on `EXDEV`. Successful hardlink registration stamps `user.eos.lfn` on the source path; checksum registration can stamp `user.eos.checksumtype` and `user.eos.checksum` on the link path and update the EOS file checksum.

State and persistence behavior: sets owner/group, ctime, mtime, size, optional `sys.eos.btime`, external registration attributes (`sys.hardlink.path`, `sys.symlink.path`, `sys.absorbed.path`), checksum, and parent mtime. It persists file and parent container metadata, updates quota for direct no-layout creations, releases the lock, broadcasts FuseX metadata and parent refresh, and optionally triggers verify-stripe calls for registered locations.

Dependencies and integration points: used by higher-level create/touch commands and proc flows. It depends on access checks, namespace services, layout/open machinery, filesystem view snapshots, xattr compatibility layer, checksum plugins, quota manager, and FuseX.

Risks: external registration performs local filesystem operations from the MGM host and can leave partial state if metadata persistence fails after link/rename. `linkpath` root-only checks are essential because hardlink/symlink/absorb affects arbitrary local paths. The expected `SFS_REDIRECT` result from `open()` is a subtle success path. Error appending to `errmsg` assumes it is non-null in one checksum branch after a `linkpath` test.

Test signals: existing file touch updates timestamps, directory path returns `EISDIR`, layout-backed creation path, no-layout direct creation and quota add, `sys.owner.auth` ownership rewrite, invalid option combinations, non-root external registration denial, hardlink registration and xattr stamping, symlink fallback on `EXDEV`, absorb rename, checksum parse/store, truncate vs preset size, birth-time attribute, FuseX broadcasts, and verify-stripe invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Touch.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Utimes.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Utimes.inc

Purpose: sets modification/change times for files and directories.

Important APIs and types: public `XrdMgmOfs::utimes`, internal `_utimes`, `VirtualIdentity`, `IContainerMD`, `IFileMD`, `RWMutexWriteLock`, `_access`, and metadata store update methods.

Control flow: public `utimes()` maps identity for `AOP_Update`, namespace-maps path, authorizes update, applies write mode, stall, and redirect, then calls `_utimes()`. `_utimes()` increments stats, takes the namespace write lock, checks write access, first attempts to treat the path as a container, sets directory mtime from `tvp[1]`, notifies directory service, and persists the container. If no container was found, it attempts file lookup, sets ctime from `tvp[0]` only when nonzero, sets mtime from `tvp[1]`, and persists file metadata.

State and persistence behavior: updates directory mtime or file ctime/mtime in metadata stores. It does not broadcast FuseX refreshes in this file, so cache coherency may be handled elsewhere or could be a gap.

Dependencies and integration points: standard XRootD utimes path through auth/mapping macros. Depends on `_access` and EOS namespace services.

Risks: `_utimes()` returns `SFS_OK` unconditionally after attempts, even if both container and file lookup failed and `errno` was set. The write lock is held while `_access()` runs, which may have its own lock behavior. Lack of explicit FuseX notification may make timestamp changes less visible to clients.

Test signals: file mtime/ctime update, ctime skipped for zero `tvp[0]`, directory mtime update and notification, write access denial, missing path behavior, namespace/auth macro behavior, and cache notification expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Utimes.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Version.inc -->
## sources/distributed-fs/eos/mgm/ofs/cmds/Version.inc

Purpose: implements file version creation and version retention purge. Versions are stored under hidden `.sys.v#.<name>/` directories with filenames derived from ctime and fid.

Important APIs and types: `XrdMgmOfs::Version`, `XrdMgmOfs::PurgeVersion`, `VirtualIdentity`, `IFileMD`, `XrdMgmOfsDirectory`, `Path::DecodeAtomicPath`, `_stat`, `_mkdir`, `_chmod`, `_rename`, `_attr_ls`, `_rem`, `ProcCommand`, and root identity.

Control flow for version creation: `Version()` loads file metadata under read lock, translates fid to path, decodes atomic paths, uses the file owner identity for versioning, captures file ctime, and rejects non-root callers who are not the file owner. It builds `.sys.v#.<basename>/<ctime>.<fidhex>`, optionally returns that path, creates the version directory if missing, ensures owner write permission by chmod as root, then renames the current file into the version path unless `simulate` is true. If `max_versions > 0`, it purges according to policy.

Control flow for purge: `PurgeVersion()` accepts explicit `max_versions`, reads `sys.versioning` from the parent when negative, and returns if no policy exists. If `max_versions == 0`, it recursively removes the whole version directory via `/proc/user` `rm -r` as root to preserve recycle semantics. Otherwise it lists version entries, computes age from the timestamp prefix, keeps at most one oldest entry per age bin, and removes older entries beyond the requested count with `_rem()`.

State and persistence behavior: creates hidden version directories, changes permissions, renames live files into version storage, removes old version files/directories, and may invoke recycle-aware delete paths. `simulate` validates/builds version naming without performing the main rename.

Dependencies and integration points: used by write/commit atomic upload paths and `_rem()` version purge cleanup. Depends on hidden path conventions, root identity for metadata management, existing rename/delete semantics, and directory attribute policy `sys.versioning`.

Risks: version filenames depend on ctime seconds plus fid; collision handling is not in this file but appears in commit helper. Purge ordering uses directory iteration order for `versions` while age keep-set is computed separately, so deletion order may not be strictly chronological unless directory listing is stable. Recursive delete through proc releases control to command infrastructure.

Test signals: owner vs non-owner version permission, version directory creation and chmod, simulate mode, successful rename to `.sys.v#`, max-version purge, `max_versions=0` recursive delete, negative policy read from parent attr, missing policy no-op, age-bin retention, and integration with atomic commit versioning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Version.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Access.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/Access.cc

Purpose: FUSE/fsctl handler for access checks. It converts a request containing `mode` into a call to the normal MGM `access()` API and returns a text response through `XrdOucErrInfo`.

Important APIs and types: `XrdMgmOfs::Access`, `XrdOucEnv`, `XrdOucErrInfo`, `VirtualIdentity`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: marks the operation read-only, applies stall/redirect behavior, increments `Fuse-Access`, reads `mode` from the environment, calls `access(path, newmode, error, client, 0)` if present, maps failures to `error.getErrInfo()`, otherwise uses `EINVAL`, and returns `SFS_DATA` with `access: retc=<code>`.

State and persistence behavior: no namespace mutation. It may update stats and trigger redirect/stall side effects before the access call.

Dependencies and integration points: FUSE clients depend on the exact response string. The actual authorization and permission semantics live in `XrdMgmOfs::access`.

Risks: `ininfo` and `ininfo`-derived opaque data are not passed to `access()` here, so mode checks may not see caller opaque options. `atoi()` accepts malformed `mode` as zero. A successful access returns retc 0 inside an `SFS_DATA` response rather than `SFS_OK`.

Test signals: missing mode, malformed mode, allowed/denied access modes, stall/redirect behavior, response string format, and stats increment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Access.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/AdjustReplica.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/AdjustReplica.cc

Purpose: fsctl repair-on-close handler from FST/FUSE paths that dispatches replica adjustment through the user proc command interface.

Important APIs and types: `XrdMgmOfs::AdjustReplica`, `REQUIRE_SSS_OR_LOCAL_AUTH`, `ProcCommand`, root `VirtualIdentity`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: requires SSS or local authentication, marks write access, applies stall/redirect, switches identity to root, reads `mgm.path` from the environment, constructs `mgm.cmd=file&mgm.subcmd=adjustreplica&mgm.path=<path>&mgm.format=fuse`, opens and closes `/proc/user`, records stats, returns an `EIO` message if the proc command failed or path was missing, otherwise responds `OK` as `SFS_DATA`.

State and persistence behavior: the handler itself only changes the local `vid` to root and invokes proc infrastructure. Actual replica repair state changes happen in the file adjustreplica command.

Dependencies and integration points: intended for trusted local/SSS callers, likely FST repair-on-close flows. Depends on `/proc/user` command parsing and implementation of `file adjustreplica`.

Risks: root identity means the proc command bypasses caller permissions after authentication gate. The original `path` argument is used only for redirect macros; actual target comes from `mgm.path`. Error code is collapsed to `EIO` for proc failures, losing details.

Test signals: auth rejection for non-SSS/non-local, missing `mgm.path`, proc success response, proc failure mapped to `EIO`, root identity use, and command string format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/AdjustReplica.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Checksum.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/Checksum.cc

Purpose: fsctl handler that returns a file checksum for FUSE clients or other MGM fsctl callers.

Important APIs and types: `XrdMgmOfs::Checksum`, `eos::Resolver::retrieveFileIdentifier`, `IFileMD`, `LayoutId`, `appendChecksumOnStringAsHex`, `RWMutexReadLock`, and access-mode/stall/redirect macros.

Control flow: marks read-master access, applies stall/redirect, increments `Fuse-Checksum`, detects `mgm.option=fuse` to use the layout-specific checksum length, takes the namespace read lock, resolves path as fid when possible or as normal file path otherwise, appends checksum bytes as hex into the response string, catches metadata exceptions into `retc`, and returns `checksum: <hex> retc=<code>` as `SFS_DATA`.

State and persistence behavior: read-only except stats and potential prefetch/cache effects from metadata service access.

Dependencies and integration points: supports fid-addressed checksum lookups and FUSE-readable shortened checksum output. Uses SHA256 length as default output width.

Risks: no explicit `_access` check is performed in this handler; it relies on trusted fsctl context, access-mode macros, and routing/auth wrappers. `mgm.option` parsing is strict string equality with `fuse`. Empty checksum with retc 0 is possible for metadata without checksum bytes.

Test signals: path lookup, fid lookup, missing file retc, FUSE layout-length output, default SHA256-length output, response format, and read-master redirect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Checksum.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Chmod.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/Chmod.cc

Purpose: fsctl wrapper around internal chmod for FUSE-style callers.

Important APIs and types: `XrdMgmOfs::Chmod`, `_chmod`, `XrdOucEnv`, `XrdSfsMode`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: marks write access, applies stall/redirect, increments `Fuse-Chmod`, reads `mode`, converts with `atoi`, calls `_chmod(path, newmode, error, vid)`, maps errors to `retc`, returns `EINVAL` when mode is missing, and writes `chmod: retc=<code>` to `error` while returning `SFS_DATA`.

State and persistence behavior: actual mode changes are performed by `_chmod`; this file only parses request and returns fsctl-formatted response.

Dependencies and integration points: FUSE clients depend on this response contract. Authorization and metadata persistence are delegated to `_chmod`.

Risks: malformed modes parse as zero. The `client` and `ininfo` parameters are unused after macros, so all semantic checks depend on the supplied `vid` and `_chmod`.

Test signals: valid mode change, missing mode, malformed mode, permission denial from `_chmod`, response format, and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Chmod.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Chown.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/Chown.cc

Purpose: fsctl wrapper around internal chown for file or directory ownership changes.

Important APIs and types: `XrdMgmOfs::Chown`, `_chown`, `XrdOucEnv`, `uid_t`, access-mode/stall/redirect macros, and `MgmStats`.

Control flow: marks write access, applies stall/redirect, increments `Fuse-Chown`, reads `uid` and `gid`, converts both with `atoi`, calls `_chown(path, uid, gid, error, vid)`, maps failures to `retc`, returns `EINVAL` if either parameter is missing, and responds `chown: retc=<code>` as `SFS_DATA`.

State and persistence behavior: actual metadata ownership changes are delegated to `_chown`.

Dependencies and integration points: used by FUSE/fsctl ownership changes. Relies on `_chown` for authorization, ownership semantics, quota or accounting side effects, and persistence.

Risks: `gid` is stored in a `uid_t` local rather than `gid_t`; this may be harmless on common platforms but is type-inaccurate. `atoi()` makes malformed values zero. Missing opaque/client use after macros may reduce contextual checks to the passed `vid`.

Test signals: valid chown, missing uid/gid, malformed values, permission denial, uid/gid type boundaries, response format, and stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Chown.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Commit.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/Commit.cc

Purpose: trusted fsctl handler for committing completed writes, replicas, reconstruction results, OC chunks, checksum updates, atomic uploads, and versioning side effects into MGM file metadata.

Important APIs and types: `XrdMgmOfs::Commit`, `CommitHelper`, `IFileMD`, `IContainerMD`, `Prefetcher`, `ReplicationTracker`, `eos::Buffer`, `LayoutId`, `VirtualIdentity`, `FuseXCastRefresh`, audit helpers, and `REQUIRE_SSS_OR_LOCAL_AUTH`.

Control flow: requires SSS/local auth, marks write access, applies stall/redirect, extracts CGI fields through `CommitHelper::grab_cgi`, optionally initializes thread log id, initializes OC parameters and option flags, normalizes reconstruction commits by clearing verification/commit flags, converts checksum hex to binary, then selects either the full commit path, alternative-checksum-only path, or parameter-error path.

Full commit behavior: after validating required fields (`size`, `fid`, `path`, `fsid`, `mtime`, `mtimensec`), it parses numeric values, logs request data, checks that the committing filesystem is operational, builds a checksum buffer, prefetches file metadata, and takes the namespace write lock. It loads the file by fid, rejects missing/unlinked/wrong-fid files, rejects FUSEX recovery commits for unlinked or absent fsid, validates replication size/checksum for replica layouts, logs verification mismatches, updates location/tracking/dropfsid state, commits alt checksums, records FUSEX state attributes, handles OC chunk counters, commits checksum, detects atomic-path naming and disables atomic/versioning for commitverify, optionally captures audit before-state, updates mtime for content-changing non-atomic or OC commits, calls `CommitHelper::commit_fmd()` to persist file/container metadata and parent mtime, releases the namespace lock, broadcasts FuseX refreshes, and emits WRITE audit with before/after stats.

Atomic/versioning behavior: after the lock-protected metadata update, it uses root identity to handle de-atomization. If a commit-size operation changes an atomic temporary name into the final name and is not an incomplete OC chunk, it may simulate version creation for the previous final-path fid, then calls `CommitHelper::handle_versioning()` to move previous target to version storage, rename the atomic upload to final name, and identify a temporary delete path. It commits the fid to `mReplicationTracker`, removes leftover atomic files with `_rem()`, and reports `EREMCHG` when overlapping atomic upload handling set abort.

Alternative checksum path: when `mgm.commit.altxs` plus `mgm.altxs` or `mgm.altxs.delete` and fid are present, it loads the file under write lock, clears/adds/removes alt checksum entries, and persists through `commit_fmd()` without changing size.

State and persistence behavior: mutates file size, mtime, checksum, alt checksums, location lists, unlinked locations, `sys.fs.tracking`, FUSEX state, OC chunk flags, temp etags, parent mtime/ctime, atomic names, version directories/files, replication tracker state, FuseX caches, and audit logs.

Dependencies and integration points: central endpoint for FST/FUSE close/commit messages. Depends on trusted SSS/local auth, filesystem view config, namespace locks, commit helper functions, replication scheduler/tracker, audit subsystem, versioning and delete helpers, OC chunk parsing, and layout semantics.

Risks: this is a high-concurrency state transition; the code intentionally releases the namespace lock before atomic/version cleanup, so overlapping commits are handled by tags and abort paths. Reconstruct commits disable verification flags, which must match caller trust assumptions. Parameter parsing with `std::stoull/stoul` can throw for malformed full-commit fields after `check_commit_params()` only checks presence. `fmd` is used for replication tracker after a prior scope; shared ownership keeps it alive but concurrency assumptions are delicate.

Test signals: missing params, bad fid/fsid/size parse, non-operational filesystem, missing file/unlinked fid, wrong fid, FUSEX recovery rejection, replication size/checksum failures with cleanup behavior, dropfsid tracking, alt checksum add/delete, OC chunk progression and finalization, checksum commit/update mtime, atomic upload rename, versioning simulation and conflict handling, overlapping atomic abort, parent/FuseX broadcasts, WRITE audit before/after, and `OK` response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Commit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.cc

Purpose: helper implementation for `Commit.cc`, isolating CGI extraction, option normalization, validation, checksum/location/OC handling, persistent metadata commit, and atomic/versioning rename mechanics.

Important APIs and types: `CommitHelper` static methods, thread-local `LogId`, `FsView`, `FileSystem`, `OwnCloud::GetChunkInfo`, `LayoutId`, `IFileMD`, `IContainerMD`, `IQuotaNode`, `FusexCastBatch`, `Prefetcher`, and EOS namespace services.

Control flow and functions: `IncrementTsForVersionFn()` increments the timestamp prefix in `<ctime>.<fxid>` names for collision avoidance. `hex2bin_checksum()` converts hex checksum text to a 32-byte buffer. `check_filesystem()` verifies the fsid exists and has config status at least drain. `grab_cgi()` copies known `mgm.*` environment keys into a string map. `set_options()` derives booleans for verification, commit, replication, reconstruction, FUSEX, atomic, versioning, OC, and abort state. `init_oc()` parses OwnCloud chunk state. `is_reconstruction()` disables normal verification and commit flags for reconstruction commits. `check_commit_params()` and `check_altchecksums_commit_params()` validate presence of required fields.

Validation behavior: `remove_scheduler()` removes fid tracking. `validate_size()` compares committed size to existing metadata and, for FUSEX, unlinks/removes the offending location and persists metadata on mismatch. `validate_checksum()` compares layout checksum bytes and, for non-FUSEX, removes the bad replica. `log_verifychecksum()` reports post-verification checksum differences without rejecting.

Metadata update behavior: `handle_location()` loads the parent container, removes old quota accounting, records new fsid in `sys.fs.tracking`, adds the committed location, removes it again if unlinked locations exist, processes comma-separated `dropfsid`, reduces tracking strings, marks `option["update"]` when committed size or modified flag changes content, updates file size, and re-adds quota. `handle_occhunk()` stores chunk progress in file flags and marks `ocdone` on the final chunk. `handle_checksum()` marks updates when checksum differs and persists the committed checksum. `commit_fmd()` removes temporary etags when appropriate, persists file metadata, updates parent mtime/ctime and temp etag on content updates, persists the parent, notifies mtime changes, and returns the parent identifier.

Atomic/versioning behavior: `get_version_fid()` locates the existing final-path file id for versioning. `handle_versioning()` takes the namespace write lock, finds the parent directory, final file, version directory, and previous final file, avoids handling if the current file is already final, moves the previous final file into the version directory with timestamp-collision retries, copies ownership/mode/xattrs from old final file to new file except selected temporary/tracking tags, handles previous target swap/delete naming, aborts stale overlapping atomic uploads, renames the committed file to final name, releases the lock, and lets `FusexCastBatch` send deletion/refresh events.

State and persistence behavior: mutates file location/checksum/size/flags/xattrs, quota accounting, parent timestamps, version directory contents, file names/container ids, temporary etags, and tracking attributes. It may remove bad replica locations during validation before the caller returns an error.

Dependencies and integration points: exclusively supports `Commit.cc` but reaches many MGM subsystems: filesystem config view, quota, namespace metadata stores, OwnCloud chunk parser, FUSEX cache broadcasts, and atomic upload conventions (`sys.tmp.atomic`, `.delete`, version path).

Risks: `hex2bin_checksum()` assumes even-length input and indexes `i+1` without bounds checking. `handle_location()` removes and re-adds quota around size changes, so failures between these steps could skew accounting. `handle_versioning()` catches metadata exceptions but often continues with `errno` set rather than returning a status, leaving caller to infer via `delete_path`/abort. Collision retry is capped at five timestamp increments.

Test signals: checksum hex odd/invalid input, filesystem config thresholds, CGI extraction defaults, reconstruction option clearing, FUSEX vs non-FUSEX bad replica cleanup, location add/drop tracking strings, quota remove/add around size changes, OC chunk flags and final chunk reset, tmp etag removal rules, parent mtime update, version fid discovery, timestamp collision retries, xattr copy skip list, overlapping atomic abort, and FuseX batch events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.hh -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.hh

Purpose: declaration for the `CommitHelper` utility class used by the fsctl commit path.

Important APIs and types: `CommitHelper`, thread-local `eos::common::LogId tlLogId`, typedefs `cgi_t`, `option_t`, `param_t`, `path_t`, and static helper methods for checksum conversion, filesystem checks, CGI parsing, option setup, OC initialization, reconstruction detection, parameter checks, scheduler removal, size/checksum validation, location/checksum/OC handling, metadata commit, version fid lookup, versioning handling, and timestamp collision adjustment.

Control flow role: the header defines the functional decomposition used by `Commit.cc`. Public static methods split commit handling into parse, validate, mutate metadata, and version/atomic phases. `IncrementTsForVersionFn()` is private in production but exposed under `IN_TEST_HARNESS`, indicating it has or should have unit coverage.

State and persistence behavior: no implementation here, but the API surface shows helper methods mutate global MGM state through `gOFS`, file metadata, quota, scheduler/tracker state, and path maps. The `option_t` map is a mutable control-plane object shared between helper calls and the main commit function.

Dependencies and integration points: includes logging, path, mapping, namespace, and `IFileMD` interfaces. The header is included by `Commit.cc` and `CommitHelper.cc`.

Risks: option and parameter maps use string keys rather than typed structs, so missing or misspelled keys silently default through `operator[]` in the implementation. `path_t` stores `eos::common::Path` objects and relies on specific keys such as `atomic`, `version`, and `versiondir`.

Test signals: compile-time interface consistency with `Commit.cc`, test-harness access to `IncrementTsForVersionFn`, typed expectations around all string-map keys, and ABI/namespace macro correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/CommitHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Drop.cc -->
## sources/distributed-fs/eos/mgm/ofs/fsctl/Drop.cc

Purpose: trusted fsctl handler for dropping a committed or failed replica from file metadata and filesystem views, including delete-on-close `dropall` behavior and optional I/O deletion reports.

Important APIs and types: `XrdMgmOfs::Drop`, `REQUIRE_SSS_OR_LOCAL_AUTH`, `Prefetcher`, `IFileMD`, `IContainerMD`, `IQuotaNode`, `IFsView`, `SymKey::ZDeBase64`, `Iostat`, FuseX refresh, and access-mode/stall/redirect macros.

Control flow: requires SSS/local authentication, marks write access, applies stall/redirect, logs the full environment, requires `mgm.fid` and `mgm.fsid`, converts fid from hex and fsid from decimal, prefetches filesystem file list and file-with-parents metadata, and takes the namespace write lock. If file metadata is already gone, it releases the lock and erases the fsview entry. If metadata exists, it loads `sys.fs.tracking`, parent container, and quota node, builds a list containing either the requested fsid or all locations when `mgm.dropall` is present, and processes each id.

Drop behavior: for each selected fsid, it unlinks linked locations and appends `-fsid` to tracking, removes unlinked locations and appends `/fsid`, optionally sends `DeleteExternal()` for `dropall`, persists tracking/file metadata and reloads the file, or erases stale fsview entries when metadata did not contain the fsid. If no linked or unlinked locations remain and this was a real update/dropall, it removes quota accounting, removes file metadata, updates parent mtime, persists parent, notifies directory service, releases the lock, and broadcasts parent FuseX refresh.

Report behavior: if `mgm.report` is supplied, it base64/zlib-decodes the report and writes it through `mIoStats`; decode failures are logged but do not fail the drop.

State and persistence behavior: mutates file location and unlinked-location lists, `sys.fs.tracking`, file store, fsview entries, quota accounting, file metadata deletion, parent mtime, directory notifications, FuseX cache state, and optional IoStat records.

Dependencies and integration points: called by FST/FUSE close/delete flows to reconcile failed writes or deleted replicas. Relies on trusted auth, filesystem view consistency, metadata services, quota manager, external deletion helper, and I/O report encoding.

Risks: many metadata operations are inside broad `catch (...)` blocks, which can hide partial failures. The handler logs full opaque environment, potentially including large reports. `dropall` iterates over current locations and then mutates/reloads the file; correctness depends on stable metadata semantics. Removal of file metadata occurs only when there was an update or dropall to avoid unlinking namespace files after secondary replica failures.

Test signals: missing fid/fsid error, missing metadata erases fsview entry, single-fsid linked drop, unlinked removal, stale fsview cleanup, `dropall` all-location removal and external deletes, final metadata removal with quota update, parent mtime/FuseX refresh, report decode/write, report decode failure, and auth gate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Drop.cc -->
