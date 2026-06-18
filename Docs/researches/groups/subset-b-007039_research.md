# subset-b-007039 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsConfigure.cc -->
# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsConfigure.cc

## Purpose
`XrdMgmOfsConfigure.cc` is the MGM OFS plugin bootstrap path. It parses `xrd.cf.mgm` directives, initializes process-wide MGM state, connects the namespace to QuarkDB, creates required `/eos/<instance>/proc` namespace directories, starts background services, installs signal handlers, and seeds metrics. It is the file that turns a constructed `XrdMgmOfs` object into a running manager/redirector daemon.

## Important APIs and functions
- `xrdmgmofs_stack(int sig)` implements `SIGUSR1`/`SIGUSR2` stack dump handling. `SIGUSR1` snapshots tracked in-flight threads and signals each with `SIGUSR2`; `SIGUSR2` appends that thread's lock state and stack trace to `/var/eos/md/stacktrace.<time>`.
- `XrdMgmOfs::StartHeapProfiling`, `StopHeapProfiling`, and `DumpHeapProfile` are realtime-signal handlers for jemalloc profiling operations through `mJeMallocHandler`.
- `XrdMgmOfs::Configure(XrdSysError& Eroute)` is the main configuration routine. It sets XrdCl defaults, default MGM paths/URLs, parses config records, validates required QuarkDB and local directories, creates service objects, starts worker threads, and returns non-zero on startup failure.
- `XrdMgmOfs::InitStats()` pre-registers MGM counter names in `MgmStats`, including file, directory, HTTP, FUSEX, quota, redirect, tape REST, workflow, and scheduler counters.
- `XrdMgmOfs::SetupProcFiles()` creates or updates proc pseudo-files such as `whoami`, `who`, `quota`, `reconnect`, and `master`, with `sys.proc` attributes for command-backed reads where appropriate.

## Control flow
`Configure` begins with process defaults: it forces SSS for XRootD clients, enables TPC for zero-size files, initializes string lookup tables, applies environment overrides for archive URL/service class, configures jemalloc signal hooks, and cleans/creates `TmpStorePath`. It derives host, short host prefix, manager ID, manager IP, manager port, and HTTP port from XRootD environment and network APIs.

The config parser loops over `XrdOucStream::GetMyFirstWord()` records. It handles `all.role`, `ofs.tpc redirect`, `mgmofs.*` keys, `xrd.protocol`, and tape REST API keys. Parsed state includes filesystem root, broker URL, instance, namespace library path, QuarkDB cluster/password, qclient persistence directory/flusher settings, authorization plugin, tape enablement and tape GC spaces, prepare defaults, redirector mode, archive/metalog/auth/report directories, FST gateway, trace masks, auth thread/port/local binding, proto workflow options, JWT token path, HTTP port, and tape REST endpoint mappings. Invalid booleans, missing values, inaccessible files, malformed tape REST endpoint versions, and config stream errors set `NoGo`.

After parsing, startup hard-fails without QuarkDB members and password. It also validates broker URL shape, `MgmMetaLogDir`, and `MgmAuthDir`, optionally loads the namespace plugin, derives queue names, configures log fan-out files and aliases, kills/restarts optional `eos-tty-broadcast`, loads external authorization if enabled, sets XRootD redirector role state, creates `QuarkDBConfigEngine`, and opens comment/fuse trace logs.

Runtime services are then initialized: audit log directory and rotation, symmetric key generation from `/etc/eos.keytab`, tape garbage collector validation, HA master state through `QdbMaster`, QDB-backed `MessagingRealm`, optional ZMQ/FUSE serving, `GeoTreeEngine`, mapping, namespace boot, root and `/eos` directory checks, proc/recycle/conversion/devices/archive/clone/workflow/tracker/token/tape REST directories, proc files, bulk request cleaner, replication tracker, device tracker, archive endpoint, stats/archive/error/fs monitor threads, HTTP/gRPC/WNC/REST-gRPC servers, monitoring config, admin socket, tape REST manager config, converter engine, LRU/WFE/device/recycler daemons, FUSE server, IO stats, shutdown/crash/coverage/stack signal handlers, auth master/workers, geotree updater, and scheduler placement strategies.

## State and persistence behavior
This file mutates most long-lived `XrdMgmOfs` fields: names, aliases, ports, queue paths, QuarkDB contact details, auth settings, tape flags, proc paths, archive endpoint, redirector mode, audit flags, scheduler settings, and thread holders. It persists or touches local filesystem state under `/var/tmp/eos`, `/var/eos/ns-queue`, `/var/log/eos/mgm`, the configured XRootD log directory, the auth/metalog/report/archive directories, and `/etc/eos.keytab`. It also persists namespace metadata via `eosView` and service stores, creating system containers and proc pseudo-files when this node is master. QuarkDB-backed state is established through `QdbMaster`, `QuarkDBConfigEngine`, and `MessagingRealm`.

## Dependencies and integration points
The file integrates XRootD config/error/logging/network APIs, EOS common logging/mapping/audit/password/plugin utilities, QuarkDB config and shared-manager messaging, namespace interfaces, FsView/Scheduler/Quota/GeoTree/Converter/Drainer/LRU/Recycler/WFE/ReplicationTracker subsystems, ZMQ and FUSEX serving, HTTP/gRPC services, tape REST/gc components, admin socket, and proc command infrastructure. It also depends on macros and global `gOFS` for cross-component access.

## Risks and edge cases
- `system("rm -rf ...")`, `mkdir -p`, `chown -R`, and `pkill` calls are string-built and operationally sensitive; path validation depends on config trust.
- Several startup checks require local files and writable directories (`/etc/eos.keytab`, logbook files, auth/metalog/report dirs); missing ownership or permissions prevent boot.
- `Configure` is a monolithic sequence with partial side effects before later failure, so failed startup can leave directories, namespace objects, logs, or spawned helper processes behind.
- Tape mode requires `EOS_HA_REDIRECT_READS`; misconfiguration hard-fails after many prior initialization steps.
- Master-only namespace creation means redirectors or slaves depend on already initialized root/proc namespace state.
- Signal handlers perform filesystem and logging work; the design favors debug utility but should be reviewed carefully for async-signal-safety assumptions.
- Config parser booleans often log errors without consistently setting `NoGo`, so invalid optional directives may not uniformly fail startup.

## Test signals
Useful tests include config parser coverage for every directive family, invalid boolean/missing value/malformed tape REST version cases, broker URL and QuarkDB password hard-fail cases, redirector-vs-manager startup differences, proc directory/file creation on master, non-master behavior when root permissions are unset, audit environment combinations, tape enabled/disabled and tape GC space combinations, auth plugin load failures, and signal-driven stack/jemalloc actions in an integration environment. Runtime smoke tests should assert expected `MgmStats` keys, started service threads, REST/gRPC activation flags, scheduler placement strategy loading, and generated proc pseudo-files with correct `sys.proc` attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsConfigure.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.cc -->
# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.cc

## Purpose
`XrdMgmOfsDirectory.cc` implements the XRootD `XrdSfsDirectory` surface for EOS MGM directory listings. It maps and authorizes callers, resolves namespace paths, loads container metadata and child names, optionally caches listing snapshots, returns entries through `nextEntry()`, and emits audit/listing metrics.

## Important APIs and functions
- `XrdMgmOfsDirectory::XrdMgmOfsDirectory` initializes the object with an empty path and `VirtualIdentity::Nobody()`.
- `getCacheName(id, mtime_sec, mtime_nsec, nofiles, nodirs)` builds an LRU key from container identity, mtime, and listing filter flags.
- `open(const char*, const XrdSecEntity*, const char*)` is the authenticated XRootD entry point. It runs namespace mapping, illegal-name checks, external authorization, identity mapping, access-mode routing macros, and delegates to `_open`.
- `open(const char*, VirtualIdentity&, const char*)` is the already-mapped identity variant, used by internal callers.
- `_open` does the actual metadata fetch, permission/ACL/public-access check, listing construction, optional cache lookup/insert, stats, and audit emission.
- `nextEntry()` returns the current cached string pointer and advances the iterator.
- `close()` drops the shared listing.
- `Emsg()` formats errors into `XrdOucErrInfo`, logging `ENOENT` as debug and other failures as errors.

## Control flow
The public `open` path first applies `NAMESPACEMAP`, `BOUNCE_ILLEGAL_NAMES`, `AUTHORIZE`, `Mapping::IdMap`, `BOUNCE_NOT_ALLOWED`, `ACCESSMODE_R`, `MAYSTALL`, and `MAYREDIRECT`. `_open` records the token validation scope as the directory path with a trailing slash, logs non-conversion listings, increments `OpenDir`, parses opaque filters, and prefetches the target container plus children.

Under `eosViewRWMutex`, `_open` retrieves the `IContainerMD`, obtains mtime for the cache key, releases the namespace lock, evaluates POSIX `R_OK | X_OK` access for non-token identities, then evaluates ACL browse permissions. If browsing is allowed, it locks `mDirLsMutex`, tries `dirCache` when `EOS_MGM_LISTING_CACHE` enabled it, and otherwise builds a `std::set<std::string>` from `FileMapIterator` and `ContainerMapIterator`. The opaque flags `ls.skip.files` and `ls.skip.directories` suppress file or directory entries. Directory listings include `.` and include `..` except for root. The iterator is initialized to `begin`, and the listing is stored in the static LRU cache when enabled.

Failures to fetch metadata become `errno` from `MDException` and return `Emsg`. After metadata success, `_open` rejects failed permission checks with `EPERM` and rejects paths failing global public access restrictions with `EACCES`. On success it stores `dirName`, ends timing, and optionally emits an audit `LIST` event depending on global audit mode or per-directory `sys.audit`.

## State and persistence behavior
The object stores `dirName`, `vid`, a shared pointer to immutable-ish listing content, and an iterator into that listing. `dirCache` is static process-wide LRU state; enabling and sizing it is controlled by `EOS_MGM_LISTING_CACHE` at first `_open` execution. No namespace state is modified by directory listing, but stats counters and audit logs are emitted. Prefetching may populate metadata caches outside this class.

## Dependencies and integration points
The implementation depends on XRootD SFS and auth types, `XrdOucEnv` opaque parsing, EOS security macros, `Mapping`, `Acl`, `Access`, `Path`, `Prefetcher`, namespace `IView`/`IContainerMD`, file/container child iterators, global `gOFS`, `MgmStats`, `allow_public_access`, and `common::Audit`. The class is declared in `XrdMgmOfsDirectory.hh` and used as the MGM directory plugin object returned to XRootD.

## Risks and edge cases
- Listing cache invalidation relies on container id plus mtime and filter flags. If child changes do not reliably update mtime with nanosecond precision, stale listings are possible.
- The cache stores complete `std::set` listings, so large directories can consume memory even with LRU bounds.
- `nextEntry()` returns `c_str()` from strings owned by `dh_list`; callers must not use returned pointers after `nextEntry`, `close`, or object destruction assumptions change.
- `vid.scope.back()` assumes non-empty `dir_path` after `dir_path` truthiness; empty string input could be unsafe.
- ACL construction receives an empty `attrmap` in this file; correctness depends on `Acl` fetching or interpreting attributes through other mechanisms.
- Token identities skip POSIX access by setting `permok` false initially and rely on ACL browse permissions or other auth layers.

## Test signals
Tests should cover successful listings with files/directories, root `..` omission, `ls.skip.files`, `ls.skip.directories`, cache enable/disable and mtime invalidation, ACL allow/deny browse overriding POSIX mode, token and non-token identities, public access restriction rejection, missing container errors, `nextEntry()` EOF behavior, `close()` idempotence, and audit `LIST` emission in global and attribute-only modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.hh -->
# sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.hh

## Purpose
`XrdMgmOfsDirectory.hh` declares the EOS MGM directory object used by XRootD OFS. It defines the directory-open, iteration, close, and error-reporting interface plus the state used to cache a resolved namespace listing.

## Important APIs and types
- `class XrdMgmOfsDirectory : public XrdSfsDirectory, public eos::common::LogId` is the concrete SFS directory implementation.
- `open(const char* dirName, const XrdSecClientName* client = 0, const char* opaque = 0)` declares the client-authenticated entry point. The implementation uses the corresponding XRootD security entity type.
- `open(const char* dirName, eos::common::VirtualIdentity& vid, const char* opaque = 0)` supports internal callers with a precomputed EOS identity.
- `_open(...)` is the low-level implementation after mapping, bounce, access mode, stall, and redirect decisions.
- `nextEntry()` returns a null-terminated name pointer or null at EOF/error.
- `Emsg(...)` writes error text and code into an `XrdOucErrInfo`.
- `close()` releases listing state.
- `FName()` exposes the currently opened directory path.
- `listing_t` is `std::set<std::string>`, giving sorted, unique entries.
- `dirCache` is a static `eos::common::LRU::Cache<std::string, std::shared_ptr<listing_t>, std::mutex>`.

## Control flow and state shape
The header shows a two-layer open model: public overloads receive either XRootD auth data or a `VirtualIdentity`; both normalize and authorize before `_open` fills `dh_list` and `dh_it`. Iteration is stateful: `nextEntry()` advances `dh_it`, while `close()` clears `dh_list`. `getCacheName` is private and exists to couple cache keys to namespace metadata timestamps and listing filters.

The instance state is intentionally small: `dirName` for diagnostics, `vid` for the mapped caller, `dh_list`/`dh_it` for the materialized result, and `mDirLsMutex` to serialize access to that result. The cache is shared across all directory objects.

## Dependencies and integration points
The declaration pulls in EOS logging, mapping, LRU cache support, XRootD error/security/SFS interfaces, POSIX `dirent`, and STL containers/mutexes. It forward-declares `eos::IContainerMD`, matching the implementation's namespace metadata dependency while keeping the header relatively light.

## Risks and edge cases
- The declaration names `XrdSecClientName` while the implementation uses `XrdSecEntity`; this may depend on typedef compatibility or may be a stale declaration risk worth checking against the active XRootD headers.
- Returning raw `const char*` from `nextEntry()` exposes lifetime coupling to `dh_list`.
- `listing_t` as `std::set` sorts entries and removes duplicates, which may differ from physical namespace order but gives deterministic XRootD responses.
- Static cache state has process-wide memory and coherency implications.

## Test signals
Header-level regression signals include compile coverage against the active XRootD SFS signature, construction/destruction through `XrdSfsDirectory` pointers, concurrent `nextEntry`/`close` access, cache type instantiation, and ABI compatibility for plugin loading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsDirectory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.cc -->
