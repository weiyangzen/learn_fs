# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.cc

## Purpose
`XrdMgmOfsFile.cc` implements the MGM-side XRootD file-open surface. For normal file IO, the MGM does not serve bytes directly; it authenticates, authorizes, resolves metadata, applies policy/quota/workflows, selects FST targets, signs a capability, and redirects the client. It also handles proc pseudo-files, zero-size MGM-served reads, copy-on-write clone bookkeeping, hard-link delete bookkeeping, local/TPC redirects, FUSE-specific behavior, RAIN/PIO reconstruction, and tape garbage collector notifications.

## Important APIs and functions
- Anonymous helpers `getFirstDiskLocation` and `EnforceRainMinFsidEntry` support tape-aware space lookup and deterministic RAIN entry-server selection.
- `emsg` is a static helper used by copy-on-write clone creation.
- `XrdMgmOfsFile::create_cow` creates copy-on-write, delete/rename, or hard-link clone metadata under `/proc/clone/<cloneId>/<parentId>/...`, preserving selected xattrs and locations depending on clone type.
- `handleHardlinkDelete` updates `SYS_NUM_LINK`/`SYS_HARD_LINK`, renames still-linked targets to `...eos.ino...<inode>`, deletes unreferenced hidden targets, and invokes COW deletion when needed.
- `GetClientApplicationName`, `GetPosixOpenFlags`, and `GetXrdAccessOperation` derive application identity, POSIX flags, and authorization operation from XRootD inputs.
- `setProxyFwEntrypoint` maps scheduler-provided firewall/proxy endpoints into redirection target host/port and `mgm.fsprefix` suffixes.
- `open(...)` is the dominant path. It covers identity mapping, namespace mapping, proc handling, ACL/permission checks, file creation/truncation, conversion policy, placement/access scheduling, capability creation, workflow hooks, tape hooks, and final redirect.
- `read`, `pgRead`, `close`, and `stat` serve proc-command results or zero-size files. Non-proc byte IO returns `EOPNOTSUPP`.
- `sync`, `sync(XrdSfsAio*)`, and `truncate` are unsupported.
- `Emsg`, `IsRainRetryWithExclusion`, `GetTriedrcErrno`, `RedirectTpcAccess`, `LogSchedulingInfo`, and `GetExcludedFsids` provide common error, retry, TPC, debug, and scheduling helpers.

## Control flow
`open` starts by deriving POSIX flags and read/write intent, mapping the user unless a `VirtualIdentity` is supplied, applying namespace bounce macros, rejecting directory paths for normal file opens, initializing many mode flags from opaque CGI, and logging masked open information. It sets access mode macros, handles HA read redirection/stalling macros, resolves `fid:`, `fxid:`, `ino:`, and `/.fxid:` access forms, creates `openOpaque`, and redirects eligible write TPC requests before further metadata work.

Application identity drives FUSE/touch/TPC behavior. Operator-only `eos.iopriority`, obfuscation keys, chunk upload UUIDs, tried lists, workflow name, versioning CGI, injection, repair, and PIO reconstruction flags are parsed from opaque tags. Non-FUSE writes resolve symlinks to real paths. PIO reconstruction validates `eos.pio.recfs` as numeric filesystem IDs.

Proc paths are handled early: external auth and `ProcInterface::Authorize` gate access, `GetProcCommand` constructs the command, `open` may return a stall, and submitted proto commands can be moved into the global submitted-command map. Normal files increment `Open`, run external authorization, set token scope, reject writes to recycle paths, optionally create missing parent directories for `SFS_O_MKPTH`, and detect shared/squashfs access.

Metadata fetch is optimized with prefetching. Under the namespace read lock, it finds the parent container, lists directory attributes, initializes workflows, resolves atomic upload names, finds file metadata, follows hard-link and symlink metadata, handles `O_EXCL`, captures layout/locations/container/size, and records directory owner. Missing parents may trigger `sys.redirect.enoent` redirection from level-2 or directory attributes.

ACL and permission logic then evaluates directory/file ACLs, `.fxid` restrictions, write-once/update permissions, immutable directories, public access restrictions, token-vs-POSIX checks, sticky-owner impersonation, and `sys.proc` file redirection. Versioning, atomic upload, injection, repair, RAIN retry-with-exclusion, and xattr lock decisions are made after metadata release. Read/update conversion policies may asynchronously start converter jobs and return `SFS_STARTED` or `SFS_STALL`.

For writes, existing RAIN updates are blocked for unprivileged users unless allowed. Truncation captures audit-before state, enforces write-once rules, versions or removes the old file, and may keep the fmd for chunked uploads. New file creation takes the namespace write lock, creates file metadata, attaches it to the parent, emits CREATE/TRUNCATE audit, sets obfuscation/encryption attributes, mode, inherited versioning xattrs, trace attrs, temporary atomic markers, replication tracker state, updates stores, and broadcasts FuseX refreshes.

For reads, missing files can redirect/stall. Existing files may trigger read conversion and always update access stats and replication tracker access. The path then checks FUSE flush synchronization, builds an unsigned capability with tape flag, access mode, clone/COW data, obfuscation/encryption keys, layout/space policy output, optional local `file://localhost` redirect, IO priority/schedule/type, atime updates, placement policy, external ctime/mtime/etag/user xattrs, and creation/truncation metadata updates.

Scheduling either places new/no-location/injection files through `Quota::FilePlacement` or accesses existing locations through `Scheduler::FileAccess`. It handles offline replicas, unavailable filesystems, repair/recreation placement, triedrc error mapping, ENONET redirects/stalls, remote-master redirects, quota cleanup of newly created namespace entries, and client-booking early location commits for zero-size/chunked/RAIN creations. FUSE update opens bias the selected replica toward the highest suitable fsid/geotag. RAIN entry selection can be round-robin by fid or forced to the minimum fsid by behavior config.

The final redirection target is built from the selected filesystem snapshot, alias host/port, proxy/firewall entrypoints, PIO URL lists, replacement filesystem details, RAIN reconstruction additions, alternate checksum settings, and a signed `SymKey` capability. It appends log id, checksum/mtime/etag/id/replica index metadata, create workflow CGI, close workflow CGI, tape-GC notifications, clientinfo, and then calls `SetRedirectionInfo`; HTTP(S) clients use the selected FST HTTP port, other clients use the XRootD port. Successful reads may emit audit READ.

## State and persistence behavior
The file mutates both per-object and namespace state. Per-object fields include mapped `vid`, `openOpaque`, `mProcCmd`, `mFid`, `mIsZeroSize`, obfuscation settings, `fileName`, `oh`, log identifiers, and error state. Namespace mutations include file creation/removal, layout changes, timestamps, atime, checksums, locations, `sys.fs.tracking`, clone attributes, hard-link attributes, versioning and atomic-upload temporary attributes, `sys.utrace`/`sys.vtrace`, user xattrs from upload opaque data, quota node file accounting, parent mtimes, store updates, and FuseX broadcasts. It also schedules conversion and workflow jobs, updates replication tracker access/create state, emits audit records, and notifies tape garbage collection.

## Dependencies and integration points
This implementation is tightly integrated with EOS common utilities (`Mapping`, `FileId`, `LayoutId`, `Path`, `SecEntity`, `StringTokenizer`, `StringConversion`, `SymKey`, `BehaviourConfig`), MGM services (`Access`, `Acl`, `Policy`, `Quota`, `Workflow`, `ProcInterface`, `Recycle`, `ConverterEngine`, `ReplicationTracker`, `FsScheduler`, `FsView`, `MultiSpaceTapeGc`, `AttrHelper`, `XattrLock`, audit helpers), namespace services (`IFileMD`, `IContainerMD`, `Prefetcher`, `Resolver`), XRootD SFS/Ouc/Sec/Oss/Pgrw APIs, global `gOFS`, and macros from `XrdMgmOfsSecurity.hh`/`Macros.hh`.

## Risks and edge cases
- `open` is extremely large and stateful; small ordering changes can break auth, namespace consistency, workflow semantics, or redirection capability contents.
- Multiple branches release locks before store updates or workflow actions; correctness depends on metadata service concurrency guarantees and repeated existence checks.
- New-file cleanup after quota/scheduling failure deliberately avoids deleting entries that acquired locations during a retry; this is critical for data-loss avoidance.
- Copy-on-write and hard-link handling manipulate hidden proc clone trees and link counters; malformed attributes or partial update failures can corrupt reference state.
- Atomic uploads, chunk UUIDs, versioning, truncation, and FUSE lazy-open paths share file creation/update code and need careful regression coverage.
- Capability strings are manually assembled; missing escaping or unexpected opaque values can affect FST interpretation, though path sealing and tag masking are used in key places.
- RAIN/PIO reconstruction has many computed stripe and replacement cases, including fsid `0` sentinel handling and replacement shortages.
- Tape GC notification exceptions are swallowed, so operational observability must come from tape GC logs/metrics rather than open failure.
- The helper marks unavailable replica hosts with `__offline_` but then overwrites `replicahost` from the filesystem snapshot in the same loop, which is worth reviewing if offline masking is intended to survive.

## Test signals
High-value coverage includes open-by-path and open-by-fid/fxid/ino, proc command opens/stalls, external authorization failures, ACL allow/deny/read/write/update/write-once cases, token permission behavior, immutable/public-access restrictions, symlink resolution on writes, missing parent and `SFS_O_MKPTH`, `sys.redirect.enoent` and `sys.redirect.enonet`, read/update conversion async/stall paths, truncation with versioning and audit, atomic upload and chunk UUID flows, injection into existing stubs, quota ENOSPC/EDQUOT cleanup races, zero-size MGM reads, local redirects, TPC delegated/undelegated redirects, proxy/firewall redirection suffixes, FUSE update replica selection, RAIN unprivileged update denial, PIO and PIO reconstruct replacement scheduling, signed capability contents, alternate checksum tags, HTTP(S) etag/port behavior, create/close workflow CGI, tape-file read/write notifications, unsupported `sync`/`truncate`, and `triedrc` error mapping.
