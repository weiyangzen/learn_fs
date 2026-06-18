# subset-b-007047 research

Grouped research report for EOS MGM user command handlers under `sources/distributed-fs/eos/mgm/proc/user`. Each source file section is delimited for reconciliation into its source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Find.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Find.cc

Purpose: implements the legacy `/proc/user` `find` handler as `ProcCommand::Find()`. It traverses namespace paths, optionally filters files and directories, formats results, calculates replica balance summaries, and can trigger version or atomic-file purge side effects.

Important APIs and types: reads request fields from `pOpaque` (`mgm.path`, `mgm.option`, `mgm.find.*`), maps paths through `NAMESPACEMAP`, enforces `PROC_BOUNCE_*` and `PROC_TOKEN_SCOPE`, writes via temporary output files, calls `gOFS->_exists`, `gOFS->_find`, `_stat`, `_rem`, `_attr_ls`, `_attr_get`, and `PurgeVersion`, and inspects metadata through `gOFS->eosView`, `IFileMD`, `IContainerMD`, `FsView`, `Acl`, `LayoutId`, and checksum helpers.

Control flow: after option parsing, shallow whole-namespace-like searches are marked as `deepquery` and serialized by a static mutex around a shared `globalfound` map. The handler checks target existence, runs `_find`, iterates directory map entries and their file sets, applies file filters such as zero size, mixed scheduling groups, replica count mismatch, age windows, and output options, then optionally prints counters or balance summaries. Directory results are handled in a second pass for ACL checks, child counts, attributes, version purge, and `fileinfo -m` delegation.

State and persistence: normal operation is read-only except statistics and output files. `--purge` can remove old version directories with `PurgeVersion`, and `purge=atomic` can delete atomic temporary files older than one day if the caller is root or owns the file. Balance maps are process-local, while `globalfound` is static and reused after clearing.

Dependencies and integration: tightly coupled to `XrdMgmOfs`, namespace metadata locking, `FsView` filesystem inventory, ACL validation, and legacy `ProcCommand` dispatch. It delegates rich file metadata output by opening another `/proc/user` command.

Risks: destructive options are embedded in a search command, deep searches serialize globally and use shared mutable state, and output formatting is hand-built. Filters and counters are interleaved, which makes behavior sensitive to option combinations. Metadata exceptions are mostly logged and skipped, so partial results may look successful. Test signals should cover path mapping and token scope, deep query locking, large output behavior, purge authorization and age thresholds, mixed scheduling groups, replica mismatch selection, ACL validation, balance output, and `fileinfo -m` delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Find.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Fuse.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Fuse.cc

Purpose: implements the legacy FUSE directory-listing proc command `ProcCommand::Fuse()`. It returns a compact inode directory listing consumed by FUSE clients, with optional per-entry stat payloads.

Important APIs and types: uses `pOpaque` fields `mgm.path`, `mgm.statentries`, and `eos.encodepath`, path mapping macros, `XrdMgmOfsDirectory`, `gOFS->newDir`, `eosView->getFile`, `eosView->getContainer`, `FileId::FidToInode`, `Path`, `_stat`, and fast integer-to-hex conversion for struct stat fields.

Control flow: the handler maps and validates the path, opens the directory through the MGM OFS layer, initializes `mResultStream` with either `inodirlist` or `inodirlist_pathencode`, then loops through directory entries. Names are escaped, `.` and `..` are inserted at fixed positions, file metadata is tried first to derive a file inode, and container metadata is tried as a fallback. If requested, `_stat` is called and selected stat fields are appended in a compact brace-delimited hex format.

State and persistence: this command is read-only apart from MGM statistics and result stream state. It allocates a directory object with `gOFS->newDir` and deletes it after closing.

Dependencies and integration: sits on the legacy FUSE wire contract and the MGM namespace cache. It relies on exact output ordering and encoding conventions understood by clients.

Risks: response construction uses mutable string insertion offsets for dot entries and fixed stack buffers. Missing metadata yields zero or omitted inode data rather than a hard failure for ordinary entries. Tests should validate path encoding modes, statentries binary-compatible field order, dot/dotdot ordering, file and directory inode conversion, permission failures, and cleanup of directory handles on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Fuse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/FuseX.cc -->
# sources/distributed-fs/eos/mgm/proc/user/FuseX.cc

Purpose: implements `ProcCommand::FuseX()`, the newer eosxd metadata command for GET, LS, and GETCAP operations by path, inode, or child lookup.

Important APIs and types: consumes `mgm.inode`, `mgm.clock`, `mgm.path`, `mgm.child`, `mgm.op`, client ids, auth ids, and inline-response flags. It uses `Prefetcher`, `eosView`, directory and file metadata services, `fusex::md`, `gOFS->zMQ->gFuseServer.HandleMD`, `SymKey::Base64`, `XrdOucBuffer`, access macros, and timing/stat macros.

Control flow: path input is URL-decoded and resolved to an inode by trying file metadata then container metadata. Child lookup prefetches parent children and resolves a child file or container; for small directories it may return the parent listing instead of only the child entry. Operation flags set the `fusex::md` request type. If a client clock is supplied, the function attempts a metadata clock comparison and returns `EEXIST` when unchanged. It delegates metadata construction or capability generation to `HandleMD`, validates GETCAP client clock skew, and either returns raw result stream data or a base64 inline payload in `mError`.

State and persistence: read-only for metadata GET and LS. GETCAP may issue capability data through the fuse server layer. It updates timing and MGM stats.

Dependencies and integration: deeply integrated with eosxd protocol semantics, ZeroMQ fuse server handling, namespace services, prefetching, and the MGM error channel.

Risks: clock comparison code has a local `md_clock` shadow in the container branch, which can undermine the intended cache validation. Inline responses use the error channel with `EIDRM`, so client compatibility is sensitive. Child lookup has special small-directory behavior. Tests should cover path versus inode lookup, child lookup, unchanged clocks, inline payload size threshold, GETCAP clock skew, permission bounces, and ENOENT/non-ENOENT error mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/FuseX.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Ls.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Ls.cc

Purpose: implements legacy `ProcCommand::Ls()` for user namespace listing, including simple listing, long listing, globbing, backend status, checksums, inode printing, and optional directory-list cache.

Important APIs and types: uses `XrdMgmOfsDirectory`, `gOFS->_stat`, `_access`, `_readlink`, `common::Glob`, `Path`, `Timing::ToLsFormat`, `modeToBuffer`, `LayoutId`, UID/GID mapping, and an optional static `LRU::Cache` controlled by `EOS_MGM_LISTING_CACHE`.

Control flow: the handler decodes paths when requested, rejects too-long and too-deep paths, maps namespace aliases, applies token scope, parses options, detects globbing unless disabled, stats the target, resolves the URI, then either opens a directory or prepares a single-file listing from its parent. It iterates entries, applies hidden-file and glob filters, and formats either bare names or long records with mode, link count, owner/group, size, timestamp, symlink target, backend redundancy symbol, checksum, and inode fields.

State and persistence: read-only except `MgmStats` and the process-local LRU cache keyed by inode, mtime, and options. Cache hits are still gated by an access check.

Dependencies and integration: provides familiar `ls` semantics through the proc framework while relying on EOS namespace stat/readlink and identity mapping services.

Risks: output is capped at 1 GiB but built in memory, and formatting uses fixed buffers. Cache correctness depends on mtime/ino/options and does not include caller identity, though access is rechecked. Globbing returns `ENOENT` when no entries match. Tests should cover cache hit and invalidation behavior, glob and no-glob paths, file versus directory listing, symlink formatting, backend status mode, numeric IDs, hidden files, long output truncation, and token/path mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Ls.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Map.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Map.cc

Purpose: implements legacy path map administration through `ProcCommand::Map()`. It lists, adds, and removes namespace path mappings.

Important APIs and types: uses `mSubCmd`, `pOpaque` keys `mgm.map.src` and `mgm.map.dest`, `gOFS->PathMap`, `PathMapMutex`, and `mConfigEngine` `SetConfigValue`/`DeleteConfigValue`.

Control flow: `ls` takes a read lock and formats all mapping pairs. `link` checks root/admin identity, validates source and destination syntax, rejects duplicate sources, adds the map entry, and persists it to config. `unlink` checks root/admin identity, takes a write lock, validates existence, removes the map entry, and deletes the config value.

State and persistence: mutates in-memory `PathMap` and persistent config namespace `map`. Listing is read-only.

Dependencies and integration: path mapping feeds the broader proc namespace mapping macros used by many handlers in this folder.

Risks: `link` writes `PathMap` without taking `PathMapMutex`, while `ls` and `unlink` lock, so concurrent mutation may race. Validation is string-based and intentionally strict about slashes, spaces, backslashes, and dot segments. Tests should cover admin authorization, invalid path forms, duplicate link, unlink missing path, persistence calls, and concurrent link/list behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Map.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Member.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Member.cc

Purpose: implements `ProcCommand::Member()`, a small inspection and refresh command for egroup membership.

Important APIs and types: reads `mgm.egroup` and `mgm.egroupupdate`, uses `gOFS->EgroupRefresh->refresh`, `DumpMember`, and `DumpMembers`, and references the caller through `vid.uid_string`.

Control flow: when a specific egroup is supplied, optional refresh is performed for the current user and that group, then the membership dump for that group is appended to stdout. Without a group, all known memberships are dumped.

State and persistence: optional refresh can update the egroup refresh subsystem's cache or backing state. Otherwise the command is read-only.

Dependencies and integration: depends on MGM egroup refresh services and virtual identity strings. It does not run the common path or token scope macros because it is not path based.

Risks: there is no explicit authorization barrier in this file; visibility is delegated to `EgroupRefresh`. Tests should verify refresh behavior, single-group and all-group output, empty group input, and error handling inside the egroup service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Member.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Mkdir.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Mkdir.cc

Purpose: implements legacy directory creation as `ProcCommand::Mkdir()`.

Important APIs and types: reads `mgm.path` and `mgm.option`, applies `NAMESPACEMAP`, illegal-name and permission bounce macros, `PROC_TOKEN_SCOPE`, and calls `gOFS->_mkdir` with `SFS_O_MKPTH` for option `p`.

Control flow: map and validate the input path, reject an empty path, translate `-p` into the recursive create flag, call the OFS mkdir helper, and return `errno` plus a generic error string on failure.

State and persistence: mutates namespace metadata by creating a directory or a path of directories. It also participates in the usual access/token policy.

Dependencies and integration: simple wrapper around the MGM OFS namespace creation operation.

Risks: error text is generic and relies on `errno` for detail. Tests should cover empty path, illegal names, token-scoped create, `-p` parent creation, existing directory behavior, permission denial, and namespace mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Mkdir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Motd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Motd.cc

Purpose: implements `ProcCommand::Motd()` for reading and, for admins, updating the MGM message-of-the-day file.

Important APIs and types: uses `mgm.motd`, `gOFS->MgmMetaLogDir`, `SymKey::Base64Decode`, POSIX `open`, `write`, `read`, and admin checks against root or admin UID/GID.

Control flow: builds the motd file path under the MGM meta log directory. If a base64 payload is supplied by root/admin, it decodes and writes it to the existing motd file. It then opens the motd file for reading and appends up to 64 KiB to stdout.

State and persistence: persists MOTD contents in the local file `${MgmMetaLogDir}/motd`. Reads are local filesystem reads.

Dependencies and integration: integrates with MGM stats and local deployment filesystem state rather than namespace metadata.

Risks: update opens with `O_WRONLY` only and does not create or truncate the file, so shorter updates may leave trailing content. It checks only zero bytes written, not partial writes. The read path sets `buffer[65535] = 0` regardless of bytes read and appends as a C string. Tests should cover admin-only update, invalid base64, missing motd file, shorter replacement content, partial-write handling, and maximum read length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Motd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.cc

Purpose: implements the protobuf-backed `NewfindCmd` command, replacing much of legacy `find` with structured request parsing, QDB namespace exploration, optional in-memory cache traversal, richer formatting, and optional gRPC streaming.

Important APIs and types: includes filter helpers for name regex, UID/GID, time, permissions, attributes, and faulty ACLs; output helpers for paths, replicas, checksums, `du`, formatted fields, and metadata IDs; `TraversalFilter`; `FindResult`; and `FindResultProvider`. It uses `NamespaceExplorer`, `QClient`, `QuarkFileMD`, `QuarkContainerMD`, `AccessChecker`, `BalanceCalculator`, `Prefetcher`, `gOFS->_find`, metadata views, `ProcCommand` delegation for `fileinfo` and file layout, and compile-time `EOS_GRPC`.

Control flow: `ProcessRequest()` validates regex and path existence, resolves real paths, enforces tree-token scope, opens temporary output files, parses purge options, selects either in-memory `_find` or QDB `NamespaceExplorer`, then iterates DFS results. Directory results are expansion-permission checked, converted to metadata, filtered unless treecount is active, counted, optionally purged, or printed. File results are converted, optionally accounted for balance, filtered for size/mixed groups/stripe mismatch, counted, optionally purged or layout-modified, and printed. The gRPC overload mirrors much of the logic but batches output every 100 records through `ServerWriter`.

State and persistence: ordinary find is read-only except stats and temporary output files. Purge modes can delete atomic files or purge versions. `ModifyLayoutStripes` invokes a nested file layout command that mutates file layout. QDB traversal reads directly from the namespace backend, while cache mode uses the in-memory view.

Dependencies and integration: bridges console protobufs, QDB namespace exploration, MGM auth/access checks, EOS metadata types, legacy proc commands, and optional gRPC service output.

Risks: non-gRPC and gRPC implementations duplicate logic and differ in details. In the gRPC cache branch `findResultProvider` is dereferenced before initialization. Some gRPC printing helpers write to `mOfsOutStream` instead of the local response stream. `hasStripeDiff` returns true for nominal layout but is used as an exclusion for `stripediff`, suggesting inverted semantics or confusing naming. Tests should cover QDB and cache modes, invalid regex, tree token denial, expansion permission errors, count/treecount, balance, custom format tokens, symlinks, purge and layout mutations, result limits, gRPC batching, and parity between gRPC and non-gRPC output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.hh

Purpose: declares `NewfindCmd`, the asynchronous protobuf-backed find command.

Important APIs and types: derives from `IProcCommand`, takes `eos::console::RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, optionally exposes a gRPC `ProcessRequest(ServerWriter<ReplyProto>*)`, and declares helpers `PrintFileInfoMinusM`, `ModifyLayoutStripes`, `ProcessAtomicFilePurge`, and `PurgeVersions`. It forward-declares `FindResult` and `eos::IFileMD`.

Control flow: the header establishes that normal command execution returns a `ReplyProto`, while streaming execution is compiled only under `EOS_GRPC`. Helper overloads route default output to `mOfsOutStream` or accept an explicit stream.

State and persistence: no state is declared beyond the inherited request, identity, and output streams. Mutating behavior is implemented in the `.cc` helpers for purge and layout changes.

Dependencies and integration: ties console protobuf requests to MGM command dispatch through `IProcCommand`, and conditionally to the WNC gRPC protobuf service.

Risks: templated private helpers are implemented in the `.cc`, which works because they are only instantiated there but limits reuse. Tests compile both `EOS_GRPC` and non-gRPC builds to catch signature drift, and should exercise helper call paths through public command requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/NewfindCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Quota.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Quota.cc

Purpose: implements legacy user quota operations in `ProcCommand::UserQuota()`: listing the caller's quotas, admin listing, setting, and removing quota limits.

Important APIs and types: uses `Quota::PrintOut`, `SetQuotaTypeForId`, `RmQuotaForId`, `RmQuotaTypeForId`, `GetResponsibleSpaceQuotaPath`, `Acl::CanSetQuota`, `Mapping` user/group translation, `StringConversion` size parsing, and `gOFS->_stat`.

Control flow: optional quota space is normalized to a directory path when it exists. `lsuser` prints current user's UID and GID quota views. For other subcommands, root/admin users are authorized directly; non-admin users must pass ACL quota-admin checks on the responsible quota node. `ls` prints selected UID/GID quota entries. `set` validates space, exactly one uid/gid, parses byte and inode limits, and updates quota records. `rm` similarly validates identity and removes all or selected quota types, with an extra guard against non-local storage-node `sss` authentication.

State and persistence: `set` and `rm` mutate quota state managed by `Quota`; listing is read-only. Stats are incremented.

Dependencies and integration: quota state is linked to namespace paths, ACLs, identity mapping, and the MGM quota subsystem.

Risks: the `set` branch has an `else` attached to `if (mSubCmd == "set")`, which assigns an EPERM storage-node message for non-set subcommands before `rm` handling can run; this can leave confusing transient state. Parsing uses global `errno` after conversion helpers, so tests should reset and assert error paths. Test signals include ACL quota admin, admin override, UID/GID translation failure, volume/inode parsing, `sss` local versus remote behavior, unknown quota type, monitor format, numeric ID printing, and responsible-space resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Quota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.cc

Purpose: implements protobuf-backed recycle-bin commands for listing, purging, restoring, configuring recycle policies, and setting recycle project IDs.

Important APIs and types: dispatches on `RecycleProto::SubcmdCase`, calls `Recycle::Print`, `Purge`, `Restore`, `Config`, `RecycleIdSetup`, uses `Quota::SetQuotaTypeForId` for recycle-bin quota limits, reads `gOFS->mRecycler->Dump()`, and fills `ReplyProto`.

Control flow: `ls` maps enum type to `uid`, `all`, or `rid` and calls `Recycle::Print`. `purge` and `restore` translate options into recycle subsystem calls and route output to stdout or stderr based on return code. `config` requires root and handles add/remove bin, lifetime, ratio, size, inode, collection/remove interval, dry-run, enforce, enable, and dump operations. `project` is intended to require root before calling `RecycleIdSetup`.

State and persistence: purge, restore, config, project setup, and recycle quota changes mutate recycle subsystem state, namespace state, or quota state. Listing is read-only.

Dependencies and integration: integrates recycle command protobufs with MGM recycle services and quota enforcement for the global recycle prefix/project ID.

Risks: in the `project` branch, after setting EPERM for non-root, the code does not return before calling `RecycleIdSetup`, so unauthorized callers may still trigger setup depending on downstream checks. Config size and inode both use `config.size()`. Tests should cover every config op, non-root config and project denial, `ls` vector-output overload, purge/restore success and failure routing, type enum mapping, quota failures, and recycler dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.hh

Purpose: declares `RecycleCmd`, the protobuf-backed recycle command handler.

Important APIs and types: derives from `IProcCommand`, includes `proto/Recycle.pb.h` and `ProcCommand.hh`, constructs with `RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, and overloads `ProcessRequest(std::vector<std::map<std::string, std::string>>*)` for callers that need structured listing rows.

Control flow: the header defines the public command entry points only; subcommand dispatch is implemented in the `.cc`.

State and persistence: no direct state beyond inherited command data. Mutations are performed by recycle subsystem calls in the implementation.

Dependencies and integration: connects console recycle protobufs to the MGM asynchronous command framework and exposes a structured-listing integration point.

Risks: the vector overload is only meaningful for `ls` and falls back to the normal method otherwise, so tests should validate both call forms. Header includes `ProcCommand.hh` rather than only `IProcCommand` because `IProcCommand` is made available there; compile tests should catch include fragility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RecycleCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Rm.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Rm.cc

Purpose: implements legacy removal command `ProcCommand::Rm()` for file deletion, wildcard deletion, recursive directory deletion, recycle-bin moves, and forced removal by root.

Important APIs and types: accepts `mgm.path`, `mgm.file.id`, `mgm.container.id`, `mgm.option`, and `mgm.deletion`; uses `GetPathFromFid`, `GetPathFromCid`, path mapping and token macros, POSIX regex for wildcard deletion, `XrdMgmOfsDirectory`, `gOFS->_exists`, `_find`, `_rem`, `_remdir`, `_attr_get`, `_stat`, `RecycleEntry`, and recycle constants.

Control flow: the command resolves file/container IDs or a path, maps and validates it, strips force for non-root, expands wildcard deletion by listing and regex matching, and checks existence. Non-recursive deletes call `_rem` for each target. Recursive deletes require a confirmation marker for shallow paths, collect the subtree with `_find`, then either simulate deletes and move the root into recycle garbage when recycle attributes are configured, or delete files and directories deepest-first.

State and persistence: mutates namespace metadata and possibly recycle-bin metadata. With recycle configured it preserves deleted trees through `RecycleEntry::ToGarbage`; with force or no recycle it deletes directly.

Dependencies and integration: legacy wrapper around the MGM OFS delete, recursive find, recycle, and quota-related deletion accounting paths.

Risks: the container-id branch calls `spath.c_str()` instead of assigning the resolved path, which appears to drop CID resolution. Wildcard handling only looks for `*` and uses regex after ad hoc conversion. Recursive shallow-path protection depends on `mgm.deletion=deep`. Tests should cover file ID and container ID deletion, force stripping, wildcard match/no-match behavior, recursive confirmation, recycle simulation failure, version directory exclusion, direct deepest-first deletion, ENOENT handling, and token-scoped removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Rm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RmCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/RmCmd.cc

Purpose: implements protobuf-backed removal as `RmCmd::ProcessRequest()`, covering path, file ID, container ID, detached metadata cleanup, globbing, recursive deletion, recycle-bin moves, and workflow bypass.

Important APIs and types: uses `RmProto`, `ReplyProto`, `NamespaceMap`, `PROC_MVID_TOKEN_SCOPE`, `IsOperationForbidden`, `Glob`, `XrdMgmOfsDirectory`, `gOFS->_exists`, `_find`, `_rem`, `_remdir`, `_attr_get`, `_stat`, `RemoveDetached`, `RecycleEntry`, and recursive stall macros.

Control flow: it first resolves path or ID. If an ID has no path and caller is root, it attempts `RemoveDetached`; non-root is denied. It maps namespace aliases, applies operation-forbidden checks, strips bypass-recycle force from non-root, optionally expands globbing, validates existence, clears recursive for files and globbed directory contents, and then either recursively collects a subtree or deletes direct targets. Recursive recycle mode performs simulated file and directory removals before moving the root to garbage; direct mode deletes files then directories deepest-first and passes `noworkflow` to file removal.

State and persistence: mutates namespace and possibly recycle metadata. `noworkflow` and `bypassrecycle` alter side effects in lower layers. Detached removal can delete namespace objects not reachable by path.

Dependencies and integration: this is the modern console command path for deletion, integrating with access policy, token scope, recycle, and namespace service edge cases.

Risks: recursive `_find` is requested with `E2BIG` failure behavior and can reject large trees. `ret_c |= errno` can produce combined error values for multiple direct failures. Globbing disables recursive deletion for matched entries. Tests should cover detached root-only cleanup, path mapping, operation forbidden errors, no-globbing, empty glob returning ENOENT, recycle simulation, direct recursive delete with `noworkflow`, force stripping, file versus directory recursive flags, and E2BIG tree limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RmCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RmCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/RmCmd.hh

Purpose: declares the protobuf-backed `RmCmd` command.

Important APIs and types: derives from `IProcCommand`, includes `ConsoleRequest.pb.h`, constructs with `RequestProto&&` and `VirtualIdentity&`, and overrides `ProcessRequest() noexcept`.

Control flow: the header only defines construction and dispatch shape. All removal behavior is implemented in `RmCmd.cc`.

State and persistence: no direct state beyond inherited command request, identity, and async execution metadata. The implementation performs namespace mutations.

Dependencies and integration: part of the modern command framework, replacing or paralleling legacy `ProcCommand::Rm()`.

Risks: compile-time compatibility depends on `IProcCommand` and protobuf request schema. Tests should instantiate the command with representative `RmProto` requests and verify the implementation contract through `ReplyProto`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RmCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Rmdir.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Rmdir.cc

Purpose: implements legacy empty-directory removal as `ProcCommand::Rmdir()`.

Important APIs and types: reads `mgm.path`, applies `NAMESPACEMAP`, `NAMESPACE_NO_TRAILING_SLASH`, illegal-name and permission bounces, token scope, and calls `gOFS->_remdir`.

Control flow: path is mapped and normalized without trailing slash, empty paths are rejected, and `_remdir` is invoked. Failures return a quoted path and `errno`.

State and persistence: mutates namespace metadata by removing a directory when lower-layer checks allow it.

Dependencies and integration: simple proc wrapper over MGM OFS directory removal.

Risks: behavior for non-empty directories and recycle policies is delegated entirely to `_remdir`; callers needing recursive or recycle-aware behavior should use rm. Tests should cover trailing slash normalization, empty path, token scope, illegal names, non-empty directory failure, missing path, and permission denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Rmdir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RouteCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/RouteCmd.cc

Purpose: implements protobuf-backed route table management for path-based redirection endpoints.

Important APIs and types: dispatches `RouteProto` subcommands to `ListSubcmd`, `LinkSubcmd`, and `UnlinkSubcmd`; uses `RouteEndpoint`, `gOFS->mRouting`, and `mConfigEngine` `SetConfigValue`/`DeleteConfigValue`.

Control flow: `ProcessRequest()` switches on the route subcommand. `list` calls `mRouting->GetListing` and returns ENOENT on no match. `link` requires root or admin UID/GID, converts each endpoint proto to `RouteEndpoint`, adds it to routing for the path, and persists the string endpoint representation. `unlink` requires root/admin, removes routing for the path, and deletes persistent config.

State and persistence: `link` and `unlink` mutate in-memory routing and persistent `route` config entries. Listing is read-only.

Dependencies and integration: integrates console route protobufs with the MGM path-routing subsystem and config engine.

Risks: multiple endpoints for one path call `SetConfigValue` with the same key repeatedly, so persistence semantics depend on config engine support for repeated values or overwrite behavior. Success replies are mostly empty. Tests should cover authorization, list no-match, duplicate endpoint add, multiple endpoint persistence, unlink missing path, and config rollback expectations when add/remove partially fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RouteCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RouteCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/RouteCmd.hh

Purpose: declares `RouteCmd`, the protobuf-backed route management command.

Important APIs and types: derives from `IProcCommand`, includes `Route.pb.h`, `ProcCommand.hh`, `IContainerMD.hh`, and `<list>`, constructs with `RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, and declares private subcommand helpers for list, link, and unlink.

Control flow: public dispatch is through `ProcessRequest`; helper signatures show each subcommand mutates a shared `ReplyProto`.

State and persistence: no direct data fields are declared. Implementation mutates routing and config state.

Dependencies and integration: command is not marked in the constructor as needing the same async/path behavior as some other commands (`IProcCommand(..., false)`), which is relevant to routing commands that are not ordinary namespace operations.

Risks: unused includes may hide tighter coupling than needed. Tests should compile command registration and exercise each helper through protobuf requests rather than direct private calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/RouteCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/TokenCmd.cc -->
# sources/distributed-fs/eos/mgm/proc/user/TokenCmd.cc

Purpose: implements protobuf-backed token creation and token decoding in `TokenCmd`, including authorization checks, token key loading, origin restrictions, and voucher persistence.

Important APIs and types: uses `TokenProto`, `EosTok`, `SymKeyStore`, optional `EOS_MGM_TOKEN_KEYFILE`, `gOFS->_access`, `_stat`, `_mkdir`, `_chown`, `eosView->getFile`, `createFile`, and file extended attribute `sys.token`. Helper methods are `GetTokenPrefix()` and `StoreToken()`.

Control flow: `ProcessRequest()` first requires token generation to be enabled and denies token-authenticated callers. For creation, non-root users are limited to `rwx d ! +` style permissions, one-year lifetime, current owner/group, and access-checked paths; file tokens force `allowtree=false`. It loads the signing key from the current symmetric key or a daemon-owned 0400 key file. It then builds an `EosTok`, verifies origin regexes, writes the encoded token to stdout, warns if approval is required, and stores a dumped token by voucher ID. For decoding, it reads with expiry and generation enforcement, verifies origin before dumping claims, and returns errors otherwise.

State and persistence: created token dumps are persisted as EOS namespace files under `MgmProcTokenPath/uid:<uid>/YYYY/MM/DD/<voucherid>` with `sys.token` xattr and caller ownership. Directory prefixes are created as root and chowned to the user/group.

Dependencies and integration: integrates token generation, namespace access checks, symmetric key management, audit logging, allowed-token approval policy, and namespace metadata persistence.

Risks: `StoreToken()` manipulates namespace metadata through `eosView` without an explicit local lock in this function. Permission parsing allows `!` although the error message mentions `[+1]`. Multi-path tokenization on `://:` is unusual and should be tested carefully. Tests should cover disabled generation, token-authenticated denial, root versus user creation, path access for files and tree directories, lifetime cap, keyfile ownership/mode, origin regex errors, approval warning, duplicate voucher storage, decode of expired/wrong-generation tokens, and origin mismatch without claim leakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/TokenCmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/TokenCmd.hh -->
# sources/distributed-fs/eos/mgm/proc/user/TokenCmd.hh

Purpose: declares `TokenCmd`, the protobuf-backed token command.

Important APIs and types: derives from `IProcCommand`, includes `ConsoleRequest.pb.h`, constructs from `RequestProto&&` and `VirtualIdentity&`, overrides `ProcessRequest()`, and exposes helper methods `StoreToken()` and `GetTokenPrefix()`.

Control flow: public helpers show that token persistence is part of the command contract, not hidden entirely inside `ProcessRequest`.

State and persistence: no direct member fields are declared. Helper signatures reveal persisted token path generation and storage are keyed by token string, voucher ID, UID, and GID.

Dependencies and integration: command participates in the async proc framework and relies on implementation-level integration with `EosTok`, key stores, and namespace metadata.

Risks: helper methods are public, so other code can store tokens without going through `ProcessRequest()` authorization unless call sites are controlled. Tests should prefer end-to-end `ProcessRequest` coverage and include direct helper tests for prefix creation, ownership correction, and duplicate voucher behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/TokenCmd.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Version.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Version.cc

Purpose: implements `ProcCommand::Version()`, reporting EOS instance name, server version/release, XRootD version, and feature flags.

Important APIs and types: uses `XrdVERSIONINFOREF/XrdVERSIONINFOVAR`, compile-time `VERSION` and `RELEASE`, `gOFS->MgmOfsInstanceName`, `Features::sMap`, `mgm.option`, and MGM stats.

Control flow: with option `m`, it emits one-line monitoring key/value output including parsed XRootD version and all feature map entries. Otherwise it emits human-readable lines for instance and server version, and with option `f` appends feature entries.

State and persistence: read-only except stats.

Dependencies and integration: exposes deployment/runtime metadata to users and monitoring systems.

Risks: output ordering of features depends on `Features::sMap` iteration. XRootD version parsing assumes a space-delimited component prefix. Tests should cover monitoring format, feature format, absent or unusual XRootD version strings, and stable presence of instance/version/release fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Version.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Who.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Who.cc

Purpose: implements `ProcCommand::Who()`, reporting active client sessions grouped by user, authentication protocol, and optionally individual clients.

Important APIs and types: reads `mgm.option` and `mgm.format`, uses `Mapping::ActiveTidentsSharded`, `StringConversion::Tokenize`, `Mapping::UidToUserName`, JsonCpp `Json::Value` and stream writer, and writes to `stdOut` or `stdJson`.

Control flow: parses flags for monitoring, clients, auth summary, all, summary-only, and numeric IDs. It snapshots active tident shards into an unordered map, counts users and auth protocols, then emits selected auth counts, user counts, client records, and total client summary in monitoring, JSON, or human-readable format.

State and persistence: read-only except stats. It copies active session entries before detailed output, reducing time spent reading sharded state.

Dependencies and integration: consumes global active identity/session tracking and name mapping services.

Risks: tident parsing assumes caret-delimited tokens with at least uid, client, auth, and gateway fields; malformed entries can index missing tokens. JSON output is an array of heterogeneous objects, not a structured object with named sections. Tests should cover numeric and translated IDs, monitoring and JSON formats, malformed/short tident strings, showclients/showall/showsummary combinations, auth summaries, and idle time calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Who.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Whoami.cc -->
# sources/distributed-fs/eos/mgm/proc/user/Whoami.cc

Purpose: implements `ProcCommand::Whoami()`, returning the caller's virtual identity in monitoring or human-readable form.

Important APIs and types: reads `mgm.option`, uses fields from `pVid` such as uid/gid, allowed UID/GID sets, auth protocol, sudo flag, host, domain, geolocation, key, fullname, federation, email, and optional token dump.

Control flow: option `m` emits compact key/value fields for UID, allowed UIDs, GID, allowed GIDs, authz, and sudo. Default output formats identity details, host/domain, auth key redaction for non-sss protocols, optional profile fields, and token dump if present.

State and persistence: read-only except stats.

Dependencies and integration: exposes the resolved identity object used by all other proc commands, making it a diagnostic integration point for auth mapping and token scope.

Risks: monitoring output intentionally omits host/geolocation, while human output may reveal PII such as fullname and email. Token dumps are included in default output with secret suppression controlled by `Dump(true, false)`. Tests should cover empty allowed UID/GID sets, sudo flag, sss versus oauth key redaction, optional PII fields, token-authenticated identities, and monitoring output grammar.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/user/Whoami.cc -->
