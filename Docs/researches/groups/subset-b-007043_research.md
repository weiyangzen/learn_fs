# Research Group: subset-b-007043

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcCommand.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/ProcCommand.hh

## Purpose

`ProcCommand.hh` declares the legacy proc-command implementation used by EOS MGM for `/proc/user` and `/proc/admin` CGI-style commands. It also declares the `IFilter` interface used by archive/backup tree scans. The `ProcCommand` class is the old command surface behind `IProcCommand`: it opens a proc command, stores stdout/stderr/return code and optional temporary file results, streams results through `read()`/`stat()`, and exposes many user/admin command entry points implemented across `mgm/proc/user` and `mgm/proc/admin`.

## Important APIs, Types, and Functions

- `IFilter::FilterOutFile()` and `IFilter::FilterOutDir()` define a reusable exclusion contract for archive and backup traversal.
- `ProcCommand::open()`, `read()`, `stat()`, and `close()` implement the XRootD file-like command lifecycle.
- `ProcessRequest()` returns an empty `ReplyProto` by default, making legacy raw commands compatible with the protobuf-oriented `IProcCommand` interface.
- `AddOutput()`, `MakeResult()`, `KeyValToHttpTable()`, `CallJsonFormatter()`, and output getters assemble or expose command output.
- `OpenTemporaryOutputFiles()` and `GetResultFn()` support commands such as `find` that avoid keeping large output in memory.
- Public command methods include user commands such as `Archive`, `Backup`, `Find`, `Fileinfo`, `Rm`, `UserQuota`, and admin commands such as `Access`, `AdminQuota`, `Ns`, `Vid`, `Fusex`, `GeoSched`, and `Rtlog`.
- Archive/backup helpers include `ArchiveExecuteCmd`, `ArchDirStatus`, `ArchiveCreate`, `ArchiveAddEntries`, immutable subtree helpers, ACL checks, archive listing formatting, and `BackupCreate`.

## Control Flow

Callers obtain an `IProcCommand` through `ProcInterface`, then legacy commands run through `ProcCommand::open()`. The class parses CGI keys from `pOpaque`, selects a user or admin command, fills `stdOut`, `stdErr`, `stdJson`, `retc`, and finally builds a result stream. Later reads stream `mResultStream` or a temporary result file to the client. `close()` finalizes the command and frees/records transient command state.

The header also defines the call surface for archive and backup flows. Archive/backup commands gather namespace entries through `ArchiveAddEntries`, optionally filter them with `IFilter`, create local metadata files, and communicate with external archive machinery through `ArchiveExecuteCmd`.

## State and Persistence Behavior

`ProcCommand` itself is per-request state. It owns parsed command strings (`mCmd`, `mSubCmd`, `mArgs`, `mPath`), output buffers, format flags, the input `XrdOucEnv`, caller identity pointer `pVid`, temporary file names/handles, and the result stream. It does not persist command state directly; individual command implementations may mutate MGM configuration, namespace metadata, access-control config, archive metadata, or backup files. The `mClosed` guard makes `GetResult()` return no stream after close.

Temporary output files are runtime artifacts for large outputs. The archive/backup helpers can create local temporary files and copy generated metadata into EOS/remote destinations, while state changes are delegated to other subsystems.

## Dependencies and Integration Points

The class depends on `IProcCommand`, `VirtualIdentity`, `XrdOucEnv`, XRootD error/file offset types, namespace metadata interfaces, JSON, and many command implementation files. It is integrated by `ProcInterface` as the fallback for non-protobuf requests and as the base for older proc admin/user commands. Archive and backup helpers integrate with namespace views, archive daemon JSON commands, ACL/immutability behavior, and XRootD copy machinery in implementation files.

## Risks and Edge Cases

- The legacy command surface is broad and command selection is distributed across many implementation files, so adding/removing a command requires updates outside this header.
- `pVid`, `pOpaque`, `mError`, and temporary file handles are raw pointers/handles; lifecycle errors can cause leaks or stale access if open/close paths diverge.
- Large outputs split between memory streams and temporary files; tests need to cover both paths.
- Format flags (`mFuseFormat`, `mJsonFormat`, `mHttpFormat`, `mSendRetc`) affect client-visible output and can regress compatibility.
- `IFilter` is generic but currently tied to archive/backup, with a comment noting it should move to archive-specific code.

## Test Signals

Useful signals include legacy proc command integration tests for `open/read/stat/close`, result formatting with stdout/stderr/retc/json/http, temporary-file streaming for large `find`-style output, archive/backup filter behavior, and command dispatch coverage for admin/user commands. Regression tests should verify no result is returned after `mClosed`, that `GetCmd()` handles missing `mgm.cmd`, and that archive/backup failures set `retc`/`stdErr` consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcCommand.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcInterface.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/ProcInterface.cc

## Purpose

`ProcInterface.cc` implements the MGM proc-command factory, protobuf dispatcher, async command parking map, write-access classifier, and authorization predicates. It is the bridge between XRootD `/proc/...` access and either legacy `ProcCommand` objects or newer protobuf command handler classes such as `FsCmd`, `AccessCmd`, `ConvertCmd`, and `FileRegisterCmd`.

## Important APIs, Types, and Functions

- Static state includes `mMutexCmds`, `mMapCmds`, `mCmdToDel`, thread-local `tlLogId`, and `sProcThreads`.
- `GetProcCommand()` returns a previously submitted async command, a protobuf handler, or a legacy `ProcCommand`.
- `GetSubmittedCmd()`, `SaveSubmittedCmd()`, and `DropSubmittedCmd()` manage per-client async commands by `tident`.
- `HandleProtobufRequest(const char*, vid)` base64-decodes and deserializes `mgm.cmd.proto`, then delegates to `HandleProtobufRequest(RequestProto&, vid)`.
- `HandleProtobufRequest(RequestProto&, vid)` logs the request, enforces admin gating for admin-only command cases, and constructs the concrete handler class.
- `ProtoIsWriteAccess()` parses a protobuf request and classifies whether it modifies MGM/namespace state.
- `IsProcAccess()`, `IsWriteAccess()`, `Authorize()`, `VidIsAdmin()`, and `IsAdminCmd()` implement path detection, write classification, and access control.

## Control Flow

`GetProcCommand()` first installs a thread-local log id for the current user and connection. It then checks `mMapCmds` for a completed/stalled async command belonging to the same `tident`. If no command exists and the caller lacks a path or opaque string, it returns a legacy `ProcCommand`. Otherwise it parses the opaque CGI environment; if `mgm.cmd.proto` exists, it dispatches to protobuf handling, otherwise it also returns legacy `ProcCommand`.

The protobuf path decodes base64, parses `RequestProto`, logs the JSON representation, checks `IsAdminCmd(req.command_case()) && !VidIsAdmin(vid)`, and returns null on refusal. The dispatcher then switches over `RequestProto::CommandCase` and constructs the matching command object. User-callable commands include ACL/find/rm/df/token/evict/route/recycle/quota; admin-only commands include filesystem, namespace, space, node, group, config, access, IO, scheduler, devices, monit, record/register, fsck, debug, and convert.

Write detection has separate paths. Protobuf requests are parsed and classified by command/subcommand. Legacy CGI requests are classified by `mgm.cmd` and `mgm.subcmd` string lists. `Authorize()` gates legacy `/proc/admin/` by `VidIsAdmin()` and allows `/proc/user/`.

## State and Persistence Behavior

The interface stores live/completed async command objects in static containers protected by `mMutexCmds`. `DropSubmittedCmd()` tries to kill orphaned commands; commands that cannot be killed immediately move to `mCmdToDel` and are retried later. The thread pool is a static MGM-wide execution resource sized from hardware concurrency with minimum/maximum values.

No namespace or config state is persisted here. Persistence is delegated to handler classes. Security state is derived from `VirtualIdentity`, `XrdSecEntity`, and constants such as daemon/admin uid/gid.

## Dependencies and Integration Points

This file includes every protobuf command handler it can construct, user handlers (`AclCmd`, `DfCmd`, `NewfindCmd`, `RecycleCmd`, `RmCmd`, `RouteCmd`, `TokenCmd`), admin handlers (`FsCmd`, `NsCmd`, `SpaceCmd`, `AccessCmd`, `FileRegisterCmd`, etc.), `SymKey` base64 helpers, protobuf JSON conversion, XRootD CGI parsing, and common constants. It is called from proc filesystem access code and supplies the shared `sProcThreads` pool used by long-running commands.

## Risks and Edge Cases

- Admin security depends on `IsAdminCmd()` staying in sync with future `RequestProto` command cases. The default is closed, which is safe but may break newly added user commands until classified.
- `ProtoIsWriteAccess()` parses the same protobuf later parsed again by command dispatch, which is noted as a TODO and can create duplicated parse cost or inconsistent error handling.
- Legacy write classification is a manual string list and can miss newer state-changing CGI commands.
- `ProtoIsWriteAccess()` returns false for all access-control commands so global stalls/write bans can still be removed; that intentional exception is security-sensitive.
- `DropSubmittedCmd()` keeps non-killable commands in a cleanup list; handlers must implement `KillJob()` correctly to avoid accumulating dead commands.

## Test Signals

Tests should cover protobuf base64 parse failures, unknown command cases, admin refusal for admin-only protobuf commands from non-admin VIDs, allowance for user-callable commands, `VidIsAdmin()` protocol/entity combinations, legacy `/proc/admin` versus `/proc/user` authorization, legacy and protobuf write-detection matrices, async save/get/drop behavior, and no duplicate `tident` insertion. Security regression tests should add a new command case and verify default admin gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcInterface.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcInterface.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/ProcInterface.hh

## Purpose

`ProcInterface.hh` declares the static interface for identifying, authorizing, constructing, and tracking MGM proc commands. Its documentation explains the proc model: clients read `/proc/user` or `/proc/admin`, pass command arguments in CGI keys such as `mgm.cmd` and `mgm.subcmd`, and receive a stream containing stdout, stderr, and return code. It also documents the newer protobuf request path.

## Important APIs, Types, and Functions

- `GetProcCommand()` is the factory entry point for both old CGI commands and new protobuf commands.
- `IsProcAccess()` detects proc paths.
- `ProtoIsWriteAccess()` and `IsWriteAccess()` classify state-changing requests.
- `Authorize()` gates `/proc/admin/` and `/proc/user/` paths.
- `GetSubmittedCmd()`, `SaveSubmittedCmd()`, and `DropSubmittedCmd()` handle async command pickup and disconnection.
- `VidIsAdmin()` centralizes MGM admin privilege checks for legacy path authorization, protobuf dispatch, and defense-in-depth command handlers.
- `sProcThreads` exposes the shared async thread pool.
- Private `IsAdminCmd()` and `HandleProtobufRequest()` keep protobuf command classification and construction internal.

## Control Flow

Callers first use `IsProcAccess()` to detect `/proc/` paths and `Authorize()`/`IsWriteAccess()` to apply access policy. They then call `GetProcCommand()`, which may return a parked async command, a protobuf handler, or a legacy `ProcCommand`. Long-running protobuf handlers can be saved and later retrieved by `tident`.

The header makes `VidIsAdmin()` the single source of truth for admin checks. That is important because command handlers such as `FileRegisterCmd` perform extra checks but should match the central predicate.

## State and Persistence Behavior

The header declares static process state: an async command map, a list of running orphaned commands waiting for deletion, a mutex, a thread-local log id, and the thread pool. This state is runtime-only and protects command lifecycles. Persistent effects are performed by concrete command handlers and the legacy `ProcCommand`.

## Dependencies and Integration Points

The interface depends on `IProcCommand`, `Logging`, `Mapping`, `ThreadPool`, `proc_fs.hh`, `VirtualIdentity`, and `RequestProto` command cases. It is the integration point between the proc filesystem implementation and the command classes under `mgm/proc/user` and `mgm/proc/admin`.

## Risks and Edge Cases

- Static mutable state must remain protected by `mMutexCmds`.
- `VidIsAdmin()` has two protocol sources (`XrdSecEntity` preferred, `vid.prot` fallback), so callers with and without an entity must behave consistently.
- Future protobuf command cases require updates to `IsAdminCmd()` and dispatch construction.
- Async command ownership transfers by `unique_ptr`; incorrect use can drop or leak a command object.

## Test Signals

Compile-level tests should ensure every declared handler has a matching implementation. Runtime tests should cover path detection, authorization, admin predicate combinations, async command parking, protobuf dispatch, and write-access classification. Security tests should verify non-admin users cannot instantiate admin protobuf commands even if they reach the protobuf dispatcher through a user URL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcInterface.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Access.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/Access.cc

## Purpose

`Access.cc` implements the legacy CGI `/proc/admin access` command through `ProcCommand::Access()`. It manages access-control allow/ban lists, global redirection rules, stall/rate rules, and listing output by mutating or reading static state in `mgm/access/Access`.

## Important APIs, Types, and Functions

- `ProcCommand::Access()` is the only function in this file.
- Input CGI keys include `mgm.access.user`, `group`, `host`, `domain`, `option`, `redirect`, `stall`, and `type`.
- `mSubCmd` selects `ban`, `unban`, `allow`, `unallow`, `set`, `rm`, or `ls`.
- Shared state includes `Access::gBannedUsers`, `gBannedGroups`, `gBannedHosts`, `gBannedDomains`, allowed equivalents, `gRedirectionRules`, `gStallRules`, and `gStallComment`.
- Persistence is through `Access::StoreAccessConfig()`.

## Control Flow

The function parses CGI fields into local strings, derives `monitoring` from option `m`, and disables id-to-name translation when option `n` is present. For `ban` and `allow`, it converts usernames/groups to uid/gid and inserts entries into the appropriate sets; hosts and domains are inserted directly. For `unban` and `unallow`, it validates membership before erasing. Each mutation is protected by `Access::gAccessMutex` and immediately calls `StoreAccessConfig()`.

The `set` branch handles either redirection or stall/rate rules. Redirection supports global `*` plus `r`, `w`, `ENONET`, `ENOENT`, and `ENETUNREACH` keys. Stall supports those keys and `rate:user:`/`rate:group:` rules, validates the integer threshold, stores optional comments from `mComment`, and persists. The `rm` branch removes corresponding redirect or stall rules.

The `ls` branch takes a read lock and emits all non-empty lists. Output can be human-oriented with section headers and counters or monitoring-oriented with `key=value` lines. Numeric uid/gid or name translation is controlled by `translate`.

## State and Persistence Behavior

All meaningful state lives in `Access` static containers and is guarded by `Access::gAccessMutex`. Mutations call `Access::StoreAccessConfig()` while still under the write lock in this legacy implementation. The command writes result state into the `ProcCommand` fields `stdOut`, `stdErr`, and `retc`.

The file does not include token allow/ban handling or thread-limit key normalization present in the newer protobuf `AccessCmd` path.

## Dependencies and Integration Points

The implementation depends on `XrdOucEnv`, `XrdMgmOfs` for stats, `mgm/access/Access.hh` for global access state, `MgmStats`, and `Mapping` helpers for username/group conversion. It integrates with the legacy `ProcCommand` dispatcher and the stored access configuration consumed by runtime access checks elsewhere in MGM.

## Risks and Edge Cases

- `set` uses `atoi()` for stall/rate parsing, so malformed numeric strings can become zero; the protobuf path uses `std::stoi()` and is stricter.
- Every individual user/group/host/domain operation persists immediately, so a command with multiple fields can partly succeed before a later field fails.
- Rate rules are accepted only for `rate:user:` and `rate:group:`; old string handling does not normalize usernames to uid and may leave stale rule variants.
- Listing typo `"Allowd Users"` is client-visible legacy output.
- Holding the write lock while calling `StoreAccessConfig()` may increase contention or risk lock-order issues depending on storage internals.

## Test Signals

Regression tests should cover each subcommand with user/group/host/domain, missing users/groups, duplicate removals, redirect/stall/rate set and remove, monitoring output, numeric output option `n`, persistence failure handling, and compatibility with existing config files. Cross-plane tests should compare legacy behavior with `AccessCmd` for equivalent operations and document intentional differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Access.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.cc

## Purpose

`AccessCmd.cc` implements the protobuf access-control command. It is the newer replacement for legacy `ProcCommand::Access()`, providing structured `ls`, `set`, `rm`, `ban`, `unban`, `allow`, `unallow`, and `stallhosts` subcommands over `AccessProto`.

## Important APIs, Types, and Functions

- `ProcessRuleKey()` normalizes `threads:<target>` keys, converting username targets to uid strings while allowing `max` and `*`.
- `AccessCmd::ProcessRequest()` enforces access-admin privileges and dispatches by `AccessProto::subcmd_case()`.
- `LsSubcmd()` emits banned/allowed users/groups/hosts/domains/tokens, redirect rules, stall rules/comments, stall-host whitelist, and no-stall blacklist.
- `SetSubcmd()` sets redirect, stall, rate, or thread-limit rules.
- `RmSubcmd()` removes redirect, stall, rate, or thread-limit rules and cleans comments.
- `BanSubcmd()`, `UnbanSubcmd()`, `AllowSubcmd()`, and `UnallowSubcmd()` mutate corresponding sets.
- `StallhostsSubcmd()` manages mutually exclusive stall and no-stall host-pattern sets.
- `aux()` persists config and writes common success/error messages after set mutations.

## Control Flow

`ProcessRequest()` first allows only root, admin uid, admin gid, or sudoer identities. It then switches on the structured subcommand. Read-only listing takes a read lock and iterates every access-control collection. Mutating commands take a write lock, validate enum/input fields, mutate `Access` globals, release the write lock, then call `StoreAccessConfig()` through `aux()` or an inline read-lock block.

`SetSubcmd()` validates redirect keys against global/read/write/network-error keys. Stall and limit rules must parse as integer targets; zero is allowed only for `rate:` limits. For `rate:user:`, `rate:group:`, and `threads:` keys it stores the normalized `ProcessRuleKey()` output. Otherwise it stores global or key-suffixed rules like `r:*`.

`RmSubcmd()` mirrors `set` and removes both normalized and original `threads:` keys to cover an old bug. Ban/allow operations convert users/groups through `Mapping` before inserting uid/gid sets, while hosts/domains/tokens are strings. Unban/unallow verify membership before erasing.

## State and Persistence Behavior

State is stored in `Access` static sets/maps guarded by `Access::gAccessMutex`. Mutations are intended to persist through `Access::StoreAccessConfig()` after releasing the write lock and reacquiring a read lock. Rule comments are stored in `Access::gStallComment` using the request comment from `mReqProto.comment()`.

Token allow/ban sets and stall/no-stall host sets are covered in this protobuf path. Thread-limit normalization persists uid-based keys when possible and erases old username keys on removal.

## Dependencies and Integration Points

The file depends on `AccessCmd.hh`, `ProcInterface` for proc context, `XrdMgmOfs` for stats, `mgm/access/Access`, `MgmStats`, `Mapping`, `StringUtils::trim`, and common constants. It is constructed by `ProcInterface` for `RequestProto::kAccess`, which is centrally admin-gated before handler construction.

## Risks and Edge Cases

- `LsSubcmd()` appears to invert `id2name()` naming: when `id2name()` is true it prints `UidAsString()`/`GidAsString()`, otherwise it tries name lookup. Tests should lock in intended CLI semantics.
- Some `StallhostsSubcmd()` paths call `aux()` even after setting an error return, and the `NOSTALL` `ADD` branch calls `aux()` unconditionally after release; this can persist and report success wording alongside an error state if not carefully interpreted.
- `RmSubcmd()` accepts any non-empty stall key in the existence check, then erases computed variants; removing a non-existent arbitrary key can still persist and report success.
- The command has a defense-in-depth admin check, but central `ProcInterface` also gates `kAccess`; both predicates should remain consistent.
- Persistence failures after in-memory mutation leave changed runtime state even if config storage failed.

## Test Signals

Tests should cover all enum variants, privilege refusal, monitoring versus normal listing, id/name output, token allow/ban, `threads:<username>` conversion and malformed usernames, set/rm redirect keys, rate limit zero/nonzero rules, stall comments, stale username thread-key cleanup, stall/no-stall mutual exclusion, and `StoreAccessConfig()` failure handling. Cross-tests with legacy `Access.cc` should cover expected compatibility and known differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.hh

## Purpose

`AccessCmd.hh` declares the protobuf access-control command handler and the `ProcessRuleKey()` helper. It defines the structured admin interface for managing MGM access bans, allows, redirections, stalls, limits, and stall-host patterns.

## Important APIs, Types, and Functions

- `ProcessRuleKey(const std::string&)` converts eligible `threads:` username keys to internal uid-based keys.
- `AccessCmd` derives from `IProcCommand` and stores a moved `RequestProto` plus caller `VirtualIdentity`.
- `ProcessRequest()` is the public command execution entry.
- Private subcommand methods cover `LsSubcmd`, `RmSubcmd`, `SetSubcmd`, `BanSubcmd`, `UnbanSubcmd`, `AllowSubcmd`, `UnallowSubcmd`, and `StallhostsSubcmd`.
- `aux()` centralizes persistence/result handling for several mutations.

## Control Flow

`ProcInterface` constructs `AccessCmd` for `RequestProto::kAccess`. The command then validates access-admin privileges and dispatches to a private method matching the oneof subcommand in `AccessProto`. Most private methods mutate `Access` global state and call `aux()` or `StoreAccessConfig()`.

## State and Persistence Behavior

The header declares no state of its own beyond inherited `IProcCommand` request/identity data. Runtime and persisted state are external in `mgm/access/Access`. The constructor passes `false` as the third `IProcCommand` argument, so this handler is not flagged as the special long-running behavior used by some commands.

## Dependencies and Integration Points

It includes `proto/Access.pb.h` and `mgm/proc/ProcCommand.hh` for `IProcCommand`/proc definitions. It is tightly paired with `AccessCmd.cc` and constructed by `ProcInterface`.

## Risks and Edge Cases

- Any new `AccessProto` subcommand requires a new private method and switch update in the implementation.
- `ProcessRuleKey()` is declared globally in the MGM namespace, so other code may start depending on its current normalization semantics.
- The header comment says "config commands", which is stale and can confuse maintainers.

## Test Signals

Compile tests should verify generated `Access.pb.h` enum names and all declared subcommands match implementation signatures. Behavioral tests belong in `AccessCmd.cc` coverage, especially privilege checks and persistence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/AccessCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Backup.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/Backup.cc

## Purpose

`Backup.cc` implements legacy backup command support and the `TwindowFilter` used to restrict backup contents by `ctime` or `mtime`. The command builds a backup metadata file from namespace archive-entry scans, copies it into the source EOS tree under the backup file prefix, then asks the archive subsystem to copy that backup file to the destination.

## Important APIs, Types, and Functions

- `TwindowFilter::FilterOutFile()` filters version files and files older than the configured time window, while recording directories that must be retained.
- `TwindowFilter::FilterOutDir()` filters directories not needed by retained files.
- `ProcCommand::Backup()` parses `mgm.backup.*` CGI keys, validates URLs/time-window config, queues a backup job or performs creation, and triggers archive execution.
- `ProcCommand::BackupCreate()` creates temporary files, uses `ArchiveAddEntries()` for files and directories, writes the final backup header plus entries, copies it to EOS, and cleans temporary files.

## Control Flow

`Backup()` reads source and destination SURLs, ensures trailing slash, validates `XrdCl::URL`s, translates `file:` URLs to local MGM `root://<ManagerId>/...` URLs, validates the time-window type, parses comma-separated excluded xattrs, and either submits a queued backup job or performs immediate creation if `mgm.backup.create` is present.

`BackupCreate()` creates `/tmp/eos.mgm/backup.<threadid>` files, owns the temp directory as daemon uid/gid, scans file entries first with `ArchiveAddEntries(..., true, filter)`, then directory entries with the same filter, writes a JSON header that swaps src/dst because backups are treated as archive get operations from tape to disk, appends directory and file entries, and copies the local file to `<src>/EOS_COMMON_PATH_BACKUP_FILE_PREFIX/backup.file` as root. On success, `Backup()` builds an archive JSON command for that backup file and calls `ArchiveExecuteCmd()`.

## State and Persistence Behavior

The backup command itself persists no MGM config. It creates transient local temp files and a backup metadata file in EOS. Queued jobs are stored through `gOFS->SubmitBackupJob(job_spec)`. The final backup metadata includes source/destination URLs, metadata field lists, excluded xattrs, uid/gid, time-window values, timestamp, and entry counts.

The filter keeps `mSetDirs` in memory while scanning, so file scanning must happen before directory scanning; otherwise directory filtering would not know which ancestor directories to keep.

## Dependencies and Integration Points

This file depends on `common/Path`, `Backup.hh`, `XrdMgmOfs`, `XrdCl::CopyProcess`, `XrdCl::URL`, `ArchiveAddEntries()`, `ArchiveExecuteCmd()`, EOS backup path constants, and XRootD CGI parsing. It integrates with the legacy proc command path and the archive daemon protocol.

## Risks and Edge Cases

- `Backup()` dereferences `src_surl.rbegin()` and `dst_surl.rbegin()` before checking empty strings; empty inputs can be undefined behavior.
- `TwindowFilter::FilterOutFile()` assumes `entry_info["file"]` exists and uses `strtof()` without validating conversion errors.
- Temporary files under `/tmp/eos.mgm` are named only by thread id; concurrent reuse or stale files should be considered.
- Some error paths rely on cleanup of only files created so far; coverage should verify no leaked temp files.
- Copying as root with `eos.ruid=0&eos.rgid=0` is powerful and must stay constrained to generated backup-file paths.

## Test Signals

Tests should cover URL validation, `file:` URL conversion, empty URL handling, invalid time-window type, excluded xattr serialization, queued duplicate backup jobs, immediate backup creation, no-file backup behavior, temp-file creation/open failures, copy prepare/run failures, archive command construction, time-window filtering for files/directories, and filtering of `.sys.v#.` version files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Backup.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Backup.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/Backup.hh

## Purpose

`Backup.hh` declares `TwindowFilter`, an `IFilter` implementation used by backup creation to exclude version files, files outside a time window, and directories that no retained files require.

## Important APIs, Types, and Functions

- `TwindowFilter(const std::string& twindow_type, const std::string& twindow_val)` stores the filter dimension and threshold.
- `FilterOutFile(const std::map<std::string,std::string>& entry_info)` decides whether a file archive-entry should be skipped.
- `FilterOutDir(const std::string& path)` decides whether a directory archive-entry should be skipped.
- Private state includes `mTwindowType`, `mTwindowVal`, and `mSetDirs`.

## Control Flow

The intended flow is two-pass backup creation. First, file entries are scanned through `FilterOutFile()`, and accepted files populate `mSetDirs` with their ancestor directories. Second, directory entries are scanned through `FilterOutDir()`, which keeps only paths found in `mSetDirs`. If no time-window fields are configured, both methods keep everything.

## State and Persistence Behavior

The filter is purely in-memory and per-backup. It does not persist state. `mSetDirs` is an execution cache built by file filtering and consumed by directory filtering.

## Dependencies and Integration Points

It includes `ProcCommand.hh` for `IFilter` and logging base definitions, plus `<set>`. It is constructed in `Backup.cc` and passed to `ProcCommand::ArchiveAddEntries()`.

## Risks and Edge Cases

- Directory filtering only works if the same filter object sees the file pass before the directory pass.
- The header does not constrain `mTwindowType`; validation is done by `Backup()`.
- `FilterOutFile()` implementation depends on expected archive-entry keys such as `file`, `ctime`, or `mtime`.

## Test Signals

Tests should instantiate the filter with empty and non-empty time-window settings, feed file entries with older/newer times, verify version-file exclusion, verify ancestor directory retention, and verify directory filtering after and before file-pass population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/Backup.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.cc

## Purpose

`ConfigCmd.cc` implements the protobuf admin command for listing, dumping, resetting, saving, loading, and tailing MGM configuration through `gOFS->mConfigEngine`.

## Important APIs, Types, and Functions

- `ConfigCmd::ProcessRequest()` enforces root-only execution and dispatches by `ConfigProto::subcmd_case()`.
- `LsSubcmd()` calls `IConfigEngine::ListConfigs()`.
- `DumpSubcmd()` calls `DumpConfig()`.
- `ResetSubcmd()` calls `ResetConfig()`.
- `ExportSubcmd()` rejects deprecated export use.
- `SaveSubcmd()` calls `SaveConfig(file, force, comment, std_err)`.
- `LoadSubcmd()` constructs `ConfigResetMonitor` and calls `LoadConfig()`.
- `ChangelogSubcmd()` tails the config-engine changelog.

## Control Flow

On execution, non-root callers get `EPERM`. Root requests are copied from `mReqProto.config()` and dispatched. Listing and dumping return text produced by the config engine. Reset mutates in-memory/current config and returns success. Save/load log their proto debug strings, call the config engine, propagate `errno` on failure, and return success messages on success. Export is intentionally deprecated and always `EINVAL`.

## State and Persistence Behavior

All state is in `gOFS->mConfigEngine`. Save persists current configuration to a named config file, optionally forced. Load replaces current configuration from a named file and uses `ConfigResetMonitor`, likely to coordinate fsview/config reset side effects. Reset cleans current config. Changelog reads engine-maintained history.

## Dependencies and Integration Points

The command depends on `ConfigCmd.hh`, `ProcInterface`, `XrdMgmOfs`, `FsView` for `ConfigResetMonitor`, and `IConfigEngine`. It is constructed by `ProcInterface` for admin-only `RequestProto::kConfig`.

## Risks and Edge Cases

- `ProcessRequest()` requires `uid == 0`, stricter than central admin gating; admins/sudoers who pass `VidIsAdmin()` still cannot run it.
- Failures use global `errno`, which may not be reliably set by every config-engine method.
- `ResetSubcmd()` does not set an explicit `retc`; success relies on protobuf default zero.
- `ExportSubcmd()` remains in the proto surface but is deprecated.

## Test Signals

Tests should cover root/non-root behavior, list with and without backups, dump missing config, save force/no-force, load errors and reset-monitor side effects, changelog line counts, deprecated export failure, and config-engine failure propagation through `std_err` and `retc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.hh

## Purpose

`ConfigCmd.hh` declares the protobuf MGM configuration command handler. It exposes a root-only administrative surface for config list, dump, reset, export, save, load, and changelog operations.

## Important APIs, Types, and Functions

- `ConfigCmd` derives from `IProcCommand`.
- The constructor moves `RequestProto` and stores the caller identity.
- `ProcessRequest()` is the execution entry point.
- Private methods correspond to `ConfigProto` subcommands: `LsSubcmd`, `DumpSubcmd`, `ResetSubcmd`, `ExportSubcmd`, `SaveSubcmd`, `LoadSubcmd`, and `ChangelogSubcmd`.

## Control Flow

`ProcInterface` constructs this class for `RequestProto::kConfig`. The implementation then checks root privileges and dispatches to private methods based on the config proto oneof.

## State and Persistence Behavior

The class declares no member state beyond inherited request/identity data. Configuration state and persistence are delegated to `gOFS->mConfigEngine`.

## Dependencies and Integration Points

The header includes `proto/Config.pb.h` and `ProcCommand.hh`. It is paired with `ConfigCmd.cc` and participates in central protobuf admin dispatch.

## Risks and Edge Cases

- Proto evolution requires adding private methods and implementation switch cases.
- The header exposes export even though the implementation rejects it as deprecated.
- The comment spacing and extra blank lines are harmless but reflect an older generated/manual style.

## Test Signals

Compile tests should verify generated config proto symbols match declarations. Runtime behavior is covered in `ConfigCmd.cc` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConfigCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.cc

## Purpose

`ConvertCmd.cc` implements the protobuf command for configuring the converter engine, scheduling file layout conversions, listing pending conversion jobs, and clearing pending jobs.

## Important APIs, Types, and Functions

- `ConvertCmd::ProcessRequest()` validates converter-engine availability, selects JSON output when requested, and dispatches `config`, `file`, `list`, and `clear`.
- `ConfigList()` reports converter threadpool/config/running/pending/failed state in text or JSON.
- `ConfigSubcmd()` lists or sets converter engine configuration.
- `FileSubcmd()` resolves an identifier to a file path, validates metadata, computes target space/checksum/layout, builds a conversion id, and schedules a job.
- `ListSubcmd()` formats pending jobs as JSON or a table.
- `ClearSubcmd()` clears pending jobs; it is additionally root/admin/sudoer gated.
- `PathFromIdentifierProto()` supports path, file id, and container id identifiers.
- `CheckConversionProto()` validates layout, replica count, checksum, and placement policy.
- Static `CheckValidPath()` validates namespace existence and type.
- Static `BuildConversionId()` constructs the converter engine job string.

## Control Flow

Execution starts by requiring `gOFS->mConverterEngine`. Config list/set delegates directly to the engine. File conversion resolves the target path, checks it is a file through `_exists`, reads file metadata and first replica location under namespace locks, validates requested conversion parameters, infers the target space from the replica filesystem if not specified, chooses the requested or existing checksum, builds a conversion id of the form `<fid>:<space>#<layoutid>[~placement]`, and calls `ScheduleJob()`. Listing reads pending jobs and formats them. Clearing is allowed only for root, sudoer, admin uid, or admin gid.

## State and Persistence Behavior

Persistent conversion state is owned by `mConverterEngine` and namespace metadata. This command schedules jobs by file id and conversion id; it does not directly mutate file metadata. It reads namespace metadata under `gOFS->eosViewRWMutex` and filesystem scheduling data under `FsView::gFsView.ViewMutex`.

## Dependencies and Integration Points

The file depends on `XrdMgmOfs`, scheduler placement policy parsing, `FsView`, `ConverterEngine`, namespace view/file/container interfaces, table formatting, layout/file-id helpers, common constants, and JSON. It is centrally admin-gated by `ProcInterface` for `RequestProto::kConvert`, with an extra privilege check for clearing.

## Risks and Edge Cases

- `CheckValidPath()` error text says "path must point to a <actual type>" when `enforce_type` mismatches; that wording may be reversed from what users need.
- `FileSubcmd()` uses the first replica location and rejects files without replicas; conversion of tape-only or empty-location files is unsupported.
- `PathFromIdentifierProto()` accepts container id but `FileSubcmd()` later enforces file existence, so container identifiers lead to type errors.
- `ConfigSubcmd(SET)` has no visible success message, only `retc=0`.
- `ClearSubcmd()` ignores fields in the clear proto and clears all pending jobs.

## Test Signals

Tests should cover missing converter engine, config list text/JSON, config set failures, identifier resolution by path/fid/cid, non-existent paths, directory input, files without replicas, invalid layout/replica/checksum/placement, inferred space from fsview, explicit space, conversion id formatting, schedule failure with engine message, pending list formatting, and clear authorization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.hh

## Purpose

`ConvertCmd.hh` declares the protobuf converter command handler used to inspect/configure the converter engine, schedule file conversions, list jobs, and clear jobs.

## Important APIs, Types, and Functions

- `ConvertCmd` derives from `IProcCommand`.
- `ProcessRequest()` executes the command.
- `ConfigList(bool json)` formats current converter state.
- `ConfigSubcmd()`, `FileSubcmd()`, `ListSubcmd()`, and `ClearSubcmd()` implement the proto subcommands.
- `PathFromIdentifierProto()` resolves proto identifiers into namespace paths.
- `CheckConversionProto()` validates conversion parameters.

## Control Flow

`ProcInterface` constructs this handler for `RequestProto::kConvert`. The implementation dispatches the `ConvertProto` oneof to the private helper matching the requested operation, using `RequestProto::JSON` to select JSON formatting.

## State and Persistence Behavior

The class has no declared mutable state beyond inherited request/identity. Converter configuration and job queues live in `gOFS->mConverterEngine`; namespace metadata is accessed externally.

## Dependencies and Integration Points

The header includes `proto/Convert.pb.h`, MGM namespace definitions, and `IProcCommand`. It is paired with `ConvertCmd.cc` and central protobuf dispatch.

## Risks and Edge Cases

- Private validation helpers define the command contract; proto additions need matching declaration/implementation changes.
- The comment typo "jons" and "represetation" is cosmetic but can obscure generated docs.
- Clearing jobs is declared without indicating its stronger privilege check, so readers must inspect implementation.

## Test Signals

Compile tests should ensure `Convert.pb.h` generated nested proto names remain compatible. Behavioral tests are covered by implementation tests for config/file/list/clear flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.cc

## Purpose

`DebugCmd.cc` implements the protobuf admin command for reading and setting MGM/FST debug log levels and filters.

## Important APIs, Types, and Functions

- `DebugCmd::ProcessRequest()` dispatches `get` and `set`.
- `GetSubcmd()` reports local MGM log priority and node debug states from `FsView`.
- `PrepareMsg()` builds the legacy `mgm.cmd=debug` message body string.
- `PrepareQuery()` builds FST query parameters for debug level/filter.
- `SetSubcmd()` validates root privilege, log level, wildcard use, updates local logging, and broadcasts to selected endpoints.

## Control Flow

`get` takes a read lock on `FsView::gFsView.ViewMutex`, reads the global logging priority, lowercases it, prints the local MGM endpoint, then iterates node view entries and prints each node's `debug.state`.

`set` requires `mVid.uid == 0`. It validates the requested debug level through `Logging::GetPriorityByString()`, rejects node patterns with more than one wildcard, prepares legacy body/query strings, and updates local MGM logging when the target is `*`, empty, the MGM queue, or `/eos/*/mgm`. For an all-MGM target or empty target it returns after local update. Otherwise it resolves endpoints through `FsView::gFsView.CollectEndpoints()` and sends `gOFS->BroadcastQuery()` to FSTs/nodes.

## State and Persistence Behavior

The command mutates runtime logging priority and optional log-id filter in `eos::common::Logging`. It can also mutate remote FST/node debug state via broadcast query. These are runtime operational settings, not persisted config in this file.

## Dependencies and Integration Points

Dependencies include `DebugCmd.hh`, `ProcInterface`, `XrdMgmOfs`, `FsView`, `MessagingRealm`, and common logging. It integrates with node endpoint discovery and `BroadcastQuery()`.

## Risks and Edge Cases

- Only uid 0 can set debug, stricter than central admin gating.
- For local-only `/eos/*/mgm` or empty node target, `SetSubcmd()` sets `retc` and returns without setting stdout, even though it built a success message.
- `PrepareMsg()` builds a body string that is not used by the current broadcast path; it may be leftover compatibility code.
- Wildcard validation only counts `*`; it does not validate other pattern forms before endpoint collection.
- `GetSubcmd()` copies `mNodeView` then indexes back into the global map, so concurrent changes are protected by the read lock but the pattern is slightly redundant.

## Test Signals

Tests should cover get output with local priority and node states, non-root set refusal, invalid log levels, multiple wildcard rejection, local MGM-only update, filter update, endpoint-not-found failure, broadcast success/failure, and expected stdout behavior for local-only targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.hh

## Purpose

`DebugCmd.hh` declares the protobuf debug command handler for getting and setting MGM/FST debug logging state.

## Important APIs, Types, and Functions

- `DebugCmd` derives from `IProcCommand`.
- `ProcessRequest()` executes the command.
- `GetSubcmd()` is static and handles read-only debug state reporting.
- `SetSubcmd()` handles runtime log-level/filter changes.

## Control Flow

The handler is constructed by `ProcInterface` for admin-only `RequestProto::kDebug`. The implementation dispatches the debug proto oneof to `get` or `set`; set requires root.

## State and Persistence Behavior

No handler-specific state is declared. Runtime logging state is external in `Logging` and remote nodes.

## Dependencies and Integration Points

The header includes `proto/Debug.pb.h` and `ProcCommand.hh`, and is paired with `DebugCmd.cc`.

## Risks and Edge Cases

- `GetSubcmd()` is static because it does not need identity; `SetSubcmd()` is non-static because it checks `mVid`.
- Future debug subcommands require updates to both header and implementation.

## Test Signals

Compile tests should ensure generated debug proto nested types match signatures. Behavior tests should focus on implementation paths for get/set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DebugCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.cc

## Purpose

`DevicesCmd.cc` implements the protobuf devices listing command. It reports disk/device SMART metadata collected by `gOFS->mDeviceTracker`, grouped by EOS space, in table, monitoring, or JSON-oriented formats.

## Important APIs, Types, and Functions

- `DevicesCmd::ProcessRequest()` dispatches the `ls` subcommand.
- `LsSubcmd()` optionally refreshes the tracker extraction, reads extraction timestamps, iterates spaces and devices, parses smartctl JSON, builds per-device rows, model statistics, SMART-status counts, and cost matrix values.
- It uses `TableFormatterBase` for human/monitoring output and `Json::Value` for JSON output.

## Control Flow

`ProcessRequest()` accepts only `DevicesProto::kLs`. `LsSubcmd()` maps default output to monitoring when the request wants JSON. If `ls.refresh()` is true, it calls `mDeviceTracker->Extract()`. It then fetches extraction time, device JSON map, fsid-to-space map, and SMART-status map. If tracker data is not yet available it returns `EAGAIN`.

For each space in `FsView::gFsView.mSpaceView`, it builds a device table. It iterates all extracted device JSON entries, skips fsids not mapped to the current space, parses fields such as model, serial, device type, capacity, rotation rate, power-on hours, temperature, interface speed, read lookahead, and write cache, and updates per-model counters. It then emits detail rows, per-model aggregate rows, and a cost matrix based on TB-years and assumed cloud cost. If JSON is requested, it serializes the accumulated `gjson`.

## State and Persistence Behavior

The command is read-mostly. It can trigger a fresh runtime extraction via `mDeviceTracker->Extract()`, but it does not persist configuration or namespace metadata. State is sourced from `mDeviceTracker` and `FsView::gFsView`.

## Dependencies and Integration Points

Dependencies include `DevicesCmd.hh`, `ProcInterface`, TGC constants, `XrdMgmOfs`, `mgm/devices/Devices`, `common/Path`, config engine, common constants/tokenizers/string utilities/symkeys, table formatting, and JSON helpers. It integrates with the MGM device tracker and filesystem-space view.

## Risks and Edge Cases

- `sminfo` is used without a null check even though `jinfo` and `spinfo` are checked; tracker implementations should guarantee it.
- In the SMART status loop, `sm->second` is used after checking `sm != end`; if no SMART entry exists, care is needed to avoid dereferencing end. The code sets `smartstatus` but still uses `sm->second` inside the model block.
- JSON output is selected by `WantsJsonOutput()` but the output format enum is also adjusted to monitoring; table generation still happens internally.
- The cost model uses hard-coded cloud-dollar assumptions (`250` per TB-year and fixed divisors).
- JSON parse exceptions add a fatal line and continue; malformed device JSON can partially omit rows.

## Test Signals

Tests should cover unavailable tracker data (`EAGAIN` text and JSON error), refresh invocation, listing/monitoring/JSON formats, devices with missing optional JSON fields, malformed JSON, missing space mappings, missing SMART entries, model aggregation, SMART status mapping, cost matrix calculations, and multi-space separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.hh

## Purpose

`DevicesCmd.hh` declares the protobuf devices command handler for listing device/SMART information.

## Important APIs, Types, and Functions

- `DevicesCmd` derives from `IProcCommand`.
- `ProcessRequest()` is the execution entry point.
- Private `LsSubcmd()` implements `DevicesProto_LsProto`.

## Control Flow

`ProcInterface` constructs this handler for admin-only `RequestProto::kDevices`. The implementation supports only the `ls` subcommand and rejects others.

## State and Persistence Behavior

No command-specific state is declared. Device state comes from `gOFS->mDeviceTracker`.

## Dependencies and Integration Points

The header includes `proto/Devices.pb.h` and `ProcCommand.hh`, and is paired with `DevicesCmd.cc`.

## Risks and Edge Cases

- Adding subcommands requires header and implementation changes.
- The constructor formatting is slightly misaligned but behaviorally irrelevant.

## Test Signals

Compile coverage should verify generated `Devices.pb.h` types. Runtime tests should cover the `ls` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/DevicesCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.cc

## Purpose

`EvictCmd.cc` implements the protobuf tape-eviction command. It removes disk replicas for files that have tape replicas, optionally respecting an eviction counter and optionally targeting a single filesystem id.

## Important APIs, Types, and Functions

- `EvictCmd::ProcessRequest()` is the complete command implementation.
- It consumes `EvictProto` fields including repeated `file`, `ignoreevictcounter`, `evictsinglereplica().fsid()`, and `ignoreremovalonfst`.
- It uses `_access`, `_exists`, `_stat`, `_dropstripe`, and `_dropallstripes` on `gOFS`.
- It reads/writes namespace metadata attributes `RETRIEVE_EVICT_COUNTER_NAME`, `RETRIEVE_REQID_ATTR_NAME`, and `RETRIEVE_REQTIME_ATTR_NAME`.
- `EosCtaReporterEvict` logs CTA/tape eviction audit parameters.

## Control Flow

The command validates option combinations: `fsid` requires `ignore-evict-counter`, and `ignore-removal-on-fst` requires `fsid`. It then iterates each file identifier, resolving path or fid to a path. For each file, it checks `p` ACL permission on the parent path, validates that the path exists and is a file, stats it, and requires tape mode (`EOS_TAPE_MODE_T`).

It counts disk replicas by reading file metadata and ignoring `TAPE_FS_ID`. If a target fsid is present, it verifies that replica exists. With single-fsid eviction, it calls `_dropstripe()` as root, optionally skipping FST removal. Without fsid, it optionally decrements the eviction counter under a metadata write lock and skips removal if the counter remains positive; otherwise it calls `_dropallstripes()`.

When all disk replicas are removed, it resets retrieve request id/time and eviction-counter attributes. It accumulates success/error counts and emits a summary.

## State and Persistence Behavior

The command mutates namespace metadata by decrementing/removing retrieve eviction counters and clearing retrieve request attributes. It removes disk replica locations through MGM drop operations. It uses root virtual identity for the actual drop calls after validating the caller has parent `p` ACL permission.

CTA reporter objects are per-file runtime audit records. Summary counters are per-request.

## Dependencies and Integration Points

Dependencies include path utilities, timing, `XrdMgmOfs`, `EosCtaReporter`, common constants/definitions, namespace `IView`, and optional. It integrates with CTA/tape workflows, retrieve/evict metadata conventions, EOS ACL checking, and low-level replica removal.

## Risks and Edge Cases

- `allReplicasRemoved` is declared outside the file loop and is not reset per file; after one file removes all replicas, later files can enter the cleanup block even if their own removal did not remove all replicas.
- Error messages accumulate in one stream across files, so later per-file errors can produce long combined stderr.
- `_exists` failure returns `errno`, but the actual `XrdOucErrInfo` code may be more precise.
- Direct `gOFS->eosView->getFile()` calls are not consistently protected by `eosViewRWMutex` in replica-count sections.
- Single-replica eviction uses root identity after only parent `p` ACL validation; ACL semantics must be correct for this destructive operation.

## Test Signals

Tests should cover invalid option combinations, path and fid resolution, empty paths, missing files, directory input, missing parent `p` permission, non-tape files, files with no disk replicas, fsid not present, single-replica drop success/failure, drop-all success/failure, eviction-counter decrement/skip/remove, retrieve attribute cleanup, multi-file mixed success/errors, and the `allReplicasRemoved` per-file behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.hh

## Purpose

`EvictCmd.hh` declares the protobuf tape-eviction command handler used to remove disk replicas for tape-backed files.

## Important APIs, Types, and Functions

- `EvictCmd` derives from `IProcCommand`.
- The constructor passes `true` as the third `IProcCommand` argument, marking it differently from most admin handlers, likely as a long-running/asynchronous command.
- `ProcessRequest()` executes the eviction logic.

## Control Flow

`ProcInterface` constructs this handler for `RequestProto::kEvict`, which is classified as user-callable rather than admin-only. The implementation performs per-file permission checks before destructive replica removal.

## State and Persistence Behavior

No state is declared in the header. State mutations are implemented in `EvictCmd.cc` through namespace metadata and replica drop operations.

## Dependencies and Integration Points

The header includes `IProcCommand`, MGM namespace definitions, and `ConsoleRequest.pb.h`. It is paired with `EvictCmd.cc`.

## Risks and Edge Cases

- The command is user-callable but destructive; permission checks in the implementation are the primary protection.
- The special `IProcCommand(..., true)` constructor flag should be understood before changing async behavior.

## Test Signals

Compile tests should verify proto types and constructor signatures. Behavioral tests should focus on permission and replica-removal paths in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/EvictCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.cc -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.cc

## Purpose

`FileRegisterCmd.cc` implements a protobuf admin command for creating or updating namespace file metadata directly from caller-supplied registration data. It can set owner, mode, checksum, timestamps, birth time, locations, extended attributes, layout id, and size/quota accounting.

## Important APIs, Types, and Functions

- `FileRegisterCmd::ProcessRequest()` is the complete implementation.
- It performs a defense-in-depth `ProcInterface::VidIsAdmin(mVid)` check.
- It consumes `FileRegisterProto` from `mReqProto.record()`.
- It uses `Prefetcher::prefetchContainerMDAndWait()`, `eosView->getContainer()`, `createFile()`, `updateFileStore()`, `updateContainerStore()`, and quota-node APIs.
- It uses `Policy::GetLayoutAndSpace()` to derive a layout id when none is supplied.

## Control Flow

The command refuses non-admin callers even though `ProcInterface` also gates `kRecord`. It resolves the parent path, prefetches the parent container, and takes the namespace read lock. It fetches the parent directory and current attributes, checks whether the target file/container exists, and either creates a new file or updates an existing file depending on `reg.update()`.

Owner uid/gid come from numeric fields and can be overridden by username/groupname lookup. The command then applies mode, SHA-256 checksum, ctime, mtime, atime (optionally only if newer), btime (or current time if absent), replica locations, arbitrary xattrs, and layout id. If no layout id is supplied, it asks policy for a layout/space using parent attributes and the request identity. Size is applied with quota accounting when a quota node exists. Finally it updates the file store, updates parent mtime/store, releases the lock, and notifies directory mtime change.

## State and Persistence Behavior

This command directly persists namespace metadata. It can create new file metadata or update existing file metadata, including caller-supplied locations and xattrs. It updates quota accounting by adding new files or removing old quota contribution before changing size for updates. It also mutates parent directory mtime and notifies directory services.

The read lock name is surprising because the code performs writes while holding `RWMutexReadLock`; correctness depends on underlying EOS namespace locking conventions.

## Dependencies and Integration Points

Dependencies include `QuotaCmd.hh` naming in the file header, `ProcInterface`, `XrdMgmOfs`, policy layout selection, `common/Path`, constants, namespace prefetcher, quota interface, and `FileRegisterCmd.hh`. It is constructed for admin-only `RequestProto::kRecord`.

## Risks and Edge Cases

- The source file banner says `QuotaCmd.cc`, which is misleading.
- Username/groupname lookup ignores `errc`; failed lookup can leave uid/gid at prior values without an explicit error.
- SHA-256 checksum conversion assumes valid hex and fixed digest length; malformed checksum behavior depends on `Hex2BinDataChar()`.
- Locations allow values up to and including `TAPE_FS_ID`; validation of real filesystem existence is not shown.
- Arbitrary xattrs from the request are accepted, so admin misuse can set sensitive metadata.
- The update path for quota removes the old file from quota then sets size, but does not visibly re-add in the shown code; quota semantics need careful tests.
- The typo `"no suche file"` is client-visible.

## Test Signals

Tests should cover non-admin refusal, create versus update, existing file/container conflicts, update missing file, uid/gid by numeric and name, failed name lookup, mode/checksum/timestamps/btime, `atimeifnewer`, location validation, xattr setting, explicit layout id versus policy-derived layout, quota-node present/absent behavior, metadata-store exceptions, parent mtime notification, and malformed checksum input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.hh -->
# Research: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.hh

## Purpose

`FileRegisterCmd.hh` declares the protobuf file-registration command handler for direct namespace metadata creation/update.

## Important APIs, Types, and Functions

- `FileRegisterCmd` derives from `IProcCommand`.
- The constructor moves `RequestProto` and stores caller identity.
- `ProcessRequest()` executes registration.

## Control Flow

`ProcInterface` constructs this handler for `RequestProto::kRecord`, an admin-only protobuf command. The implementation re-checks admin privileges before writing namespace metadata.

## State and Persistence Behavior

The header declares no extra state. All persistent effects happen in `FileRegisterCmd.cc` through namespace metadata operations.

## Dependencies and Integration Points

The header includes `proto/File.pb.h` and `ProcCommand.hh`, and is paired with `FileRegisterCmd.cc`.

## Risks and Edge Cases

- The command name is more specific than the included proto (`File.pb.h`), so proto schema changes can affect it indirectly.
- No private helper declarations exist; all implementation logic is concentrated in one method, making future extension harder to split cleanly.

## Test Signals

Compile coverage should ensure `FileRegisterProto` remains available through `File.pb.h`. Runtime tests should focus on the implementation's namespace mutation and admin checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/admin/FileRegisterCmd.hh -->
