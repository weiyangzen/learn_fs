# subset-b-007042 Research

Grouped source research for EOS MGM fsctl handlers, path routing, placement scheduling, policy resolution, and proc command dispatch. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Event.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Event.cc

Source read size: 234 lines, 8604 bytes.

## Purpose

Implements `XrdMgmOfs::Event`, the fsctl endpoint used to trigger EOS workflow events from FUSE or other MGM control clients. It reconstructs a workflow identity from opaque environment fields, checks the caller can perform the requested event on the target path, loads file/container metadata and attributes, and calls `Workflow::Trigger`.

## Important APIs, Types, and Functions

The exported function is `XrdMgmOfs::Event(const char*, const char*, XrdOucEnv&, XrdOucErrInfo&, VirtualIdentity&, const XrdSecEntity*)`. Important inputs are `mgm.ruid`, `mgm.rgid`, `mgm.sec`, `mgm.logid`, `mgm.path`, `mgm.fid`, `mgm.event`, `mgm.workflow`, and optional base64 `mgm.errmsg`. It uses `VirtualIdentity`, `SecEntity::KeyToMap`, `Mapping::*To*Name`, `Workflow`, `IFileMD`, `IContainerMD`, and attribute maps.

## Control Flow

The function builds a local identity from env overrides, sets the thread log id if present, chooses `P_OK` for prepare-like events and `W_OK` otherwise, and runs `_access` unless the caller uses `sss`. After write-mode access, stall, and redirect macros, it validates required env fields. It resolves metadata by fid or path under `FsView::gFsView.ViewMutex`, copies parent container attributes, optionally overlays attributes from `sys.attr.link`, initializes the workflow with attributes/path/fid, decodes a synchronous error message, and triggers the requested event/workflow. Missing workflows, internal errors, and nonzero workflow return codes are translated to `Emsg`; success returns `SFS_DATA` with `OK`.

## State and Persistence Behavior

No persistent state is owned here. It reads namespace metadata and xattrs under read locks, temporarily mutates local variables for template workflows beginning with `eos.`, and delegates durable side effects to workflow handlers. Thread-local logging state may be updated through `tlLogId`.

## Dependencies and Integration Points

Integrates fsctl request handling with `XrdMgmOfs`, MGM access macros, `FsView`, namespace services, workflow configuration under `MgmProcWorkflowPath`, xattr inheritance, base64 decoding, stats (`MgmStats.Add("Event")`), and `Workflow::Trigger`.

## Risks and Edge Cases

`spath` is used for access before the required-field block, so malformed calls without `mgm.path` depend on `_access` behavior. The prepare test is substring-based. Attribute-link failures are logged but do not abort, which may hide misconfiguration. Template workflows rewrite `spath` and reset fid, so callers must understand that metadata lookup changes. Base64 decode failure clears the synchronous error message.

## Test Signals

Exercise successful prepare and write events, permission failures for non-`sss` identities, fid and path lookup, `eos.*` template workflows, missing workflow `ENOKEY`, sync and async workflow failure handling, `sys.attr.link` inheritance, malformed env calls, and base64 `mgm.errmsg` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Event.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Fusex.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Fusex.cc

Source read size: 84 lines, 3432 bytes.

## Purpose

Implements the write-side eosxd/FUSE protocol fsctl entry point `XrdMgmOfs::Fusex`. It accepts a serialized `eos::fusex::md` protobuf request, dispatches it to the in-process FuseX server, and returns a base64-encoded protobuf response.

## Important APIs, Types, and Functions

The main API is `XrdMgmOfs::Fusex(...)`. It parses `eos::fusex::md`, derives `vid.app` from `gOFS->zMQ->gFuseServer.Client().client2app(md.clientid())`, records `Eosxd::prot::SET` stats, and calls `gFuseServer.HandleMD(id, md, vid, &resultstream, 0)`.

## Control Flow

The handler enters write mode, allows master redirection, starts timing, parses the protobuf string, maps the client id to an app name, applies stall handling, and invokes the FuseX metadata server with a synchronous id based on `vid.tident`. Nonparseable input, handler errors, and empty responses become `Emsg`; successful responses are base64 encoded and returned as `Fusex:<encoded>`.

## State and Persistence Behavior

This file owns no state. Persistent namespace/cache changes are performed inside the FuseX server. It mutates the request identity's app field for accounting and downstream authorization/audit.

## Dependencies and Integration Points

Depends on `mgm/zmq/ZMQ.hh`, FuseX protobuf definitions, `XrdMgmOfs`, access/redirect/stall macros, `MgmStats`, and `SymKey::Base64`. It is the fsctl bridge from eosxd clients into `gFuseServer.HandleMD`.

## Risks and Edge Cases

Large protobufs are only logged by length; malformed input is rejected early. Empty FuseX responses are treated as illegal even if the handler returned success. The app is trusted from client id mapping, so stale FuseX client registration affects accounting. Error text is generic (`handle request`) and may hide detailed handler diagnostics.

## Test Signals

Cover parse failure, valid metadata mutation returning nonempty output, empty handler response, handler nonzero rc, app mapping from client id, redirect/stall behavior on followers, and base64 round-trip of the result stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Fusex.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/GetFusex.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/GetFusex.cc

Source read size: 76 lines, 3114 bytes.

## Purpose

Implements the read-side eosxd/FUSE metadata-stat fsctl entry point `XrdMgmOfs::GetFusex`. It proxies `/proc/user/` requests to the legacy `ProcCommand` path and returns the command result as an `XrdOucBuffer`.

## Important APIs, Types, and Functions

The exported function is `XrdMgmOfs::GetFusex(...)`. It uses `ProcCommand::open("/proc/user/", ininfo, vid, &error)`, `ProcCommand::GetResult(size_t&)`, and returns data through `XrdOucErrInfo::setErrInfo(len, XrdOucBuffer*)`.

## Control Flow

The function enters read mode, applies stall and redirect handling, records `Eosxd::prot::STAT`, validates that the fsctl path is exactly `/proc/user/`, opens a proc command, copies the returned result into malloc-owned memory, wraps it in an `XrdOucBuffer`, and returns `SFS_DATA`. Invalid paths, proc open errors, or allocation failures are reported through `Emsg`.

## State and Persistence Behavior

No durable state is owned. It allocates a buffer that is handed to XRootD error-info ownership. Command side effects depend on the proc command described by `ininfo`.

## Dependencies and Integration Points

Integrates fsctl FUSE stat requests with `ProcCommand`, MGM stats, XRootD buffers, and normal MGM read redirection/stall macros.

## Risks and Edge Cases

The path must include the trailing slash. Result copying uses `malloc(len)` without adding a terminator, which is correct for explicit-length buffers but dangerous if downstream code treats it as C string data. `ProcCommand::GetResult` is virtual/legacy and must provide a stable pointer for the copy.

## Test Signals

Exercise valid `/proc/user/` stat requests, invalid path rejection, command open failure, zero-length and large results, allocation failure injection, and ownership cleanup of the returned `XrdOucBuffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/GetFusex.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Getfmd.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Getfmd.cc

Source read size: 127 lines, 4961 bytes.

## Purpose

Implements `XrdMgmOfs::Getfmd`, an fsctl endpoint that returns file metadata for a decimal file id in EOS env-string form. It is used by clients that need compact metadata without a full proc command.

## Important APIs, Types, and Functions

The endpoint reads `mgm.getfmd.fid`, prefetches metadata with `Prefetcher::prefetchFileMDWithParentsAndWait`, resolves `IFileMD` and full URI, calls `IFileMD::getEnv(fmdEnv, true)`, patches container/name fields, and may allocate a response buffer from `mXrdBuffPool`.

## Control Flow

After write-mode access, stall, redirect, and stats, the handler parses the fid. For nonzero fid it prefetches the file and parents, takes `eosViewRWMutex`, loads file metadata and URI, serializes metadata to an env string, releases the lock, appends the parent container path, patches empty checksum values to `none`, and seals names containing ampersands. Missing or invalid fid returns a `getfmd: retc=<errno>` response. Responses larger than 2 KiB are copied into an aligned XRootD buffer pool allocation.

## State and Persistence Behavior

The function is read-only with respect to namespace state. It uses the metadata prefetch cache and the shared XRootD buffer pool for large transient responses.

## Dependencies and Integration Points

Depends on namespace view/file services, `Path`, `StringConversion`, `BufferManager`, `Prefetcher`, and `mXrdBuffPool`. It returns wire-format env strings compatible with XRootD opaque parsing.

## Risks and Edge Cases

Only decimal fid is accepted. `XrdOucEnv` cannot represent empty checksum values, so the response deliberately rewrites `checksum=` to `checksum=none`; clients must know this sentinel. Names and parent paths with `&` require sealing. Very large metadata depends on buffer-pool max size and failure handling.

## Test Signals

Test existing fid, nonexistent fid, missing fid, metadata with empty checksum, names and parent paths containing `&`, responses above and below 2 KiB, and buffer-pool allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Getfmd.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Mkdir.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Mkdir.cc

Source read size: 104 lines, 4232 bytes.

## Purpose

Implements the FUSE fsctl mkdir operation. It creates a directory using MGM namespace APIs and returns a POSIX-style stat tuple for the created entry.

## Important APIs, Types, and Functions

The endpoint is `XrdMgmOfs::Mkdir(...)`. It reads `mode`, calls `_mkdir(path, mode, error, vid, 0)`, then `lstat(path, &buf, error, client, 0)` and formats `struct stat` fields into a `mkdir:` response.

## Control Flow

Write access, stall, redirect, and `Fuse-Mkdir` stats happen first. If `mode` is present, it creates the directory and stats it. Success returns `SFS_DATA` with device, inode, mode, ownership, size/block, and timestamp seconds/nanoseconds. Failure returns `mkdir: retc=<errno>`.

## State and Persistence Behavior

The durable side effect is namespace container creation through `_mkdir`. The stat response is transient.

## Dependencies and Integration Points

Integrates fsctl mkdir requests with the main `XrdMgmOfs::_mkdir` implementation, `lstat`, `MgmStats`, XRootD env parsing, and platform-specific stat timestamp fields.

## Risks and Edge Cases

`atoi` accepts malformed mode prefixes. The fixed 16 KiB stack buffer is much larger than the formatted response but still uses `sprintf`. If mkdir succeeds and stat fails, callers only receive the stat error code, not a rollback.

## Test Signals

Cover valid mode creation, missing/malformed mode, permission failure, redirect to master, mkdir success with lstat failure, and Linux/macOS timestamp formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Mkdir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Open.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Open.cc

Source read size: 72 lines, 2891 bytes.

## Purpose

Implements an fsctl endpoint for parallel I/O layout opens. It opens the file through `XrdMgmOfsFile` with an opaque marker requesting PIO access and returns the redirect data as payload.

## Important APIs, Types, and Functions

The exported function is `XrdMgmOfs::Open(...)`. It allocates `XrdMgmOfsFile(client->tident)`, appends `eos.cli.access=pio` to the opaque info, calls `file->open(path, SFS_O_RDONLY, 0, client, opaque.c_str())`, and copies `file->error` into the fsctl error object.

## Control Flow

The handler uses read access, stall, redirect, and `OpenLayout` stats. A successful PIO layout request is expected to return `SFS_REDIRECT`; in that case the error code is replaced with the length of the redirect text and the endpoint returns `SFS_DATA`. Allocation failure returns `SFS_ERROR` with `ENOMEM`.

## State and Persistence Behavior

No persistent state is owned. It opens a temporary `XrdMgmOfsFile` object and immediately deletes it after extracting redirect information.

## Dependencies and Integration Points

Depends on `XrdMgmOfsFile::open`, open-layout redirect semantics, access macros, and XRootD error-info encoding.

## Risks and Edge Cases

Only redirect success is converted to data; non-redirect successful opens would still return `SFS_ERROR`. `client` and `client->tident` are assumed non-null. Opaque concatenation assumes `ininfo` already has compatible separator syntax.

## Test Signals

Test normal read redirect, allocation failure, non-redirect open return paths, opaque construction with existing query parameters, and malformed/null client handling if supported by the surrounding interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Open.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Readlink.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Readlink.cc

Source read size: 68 lines, 2700 bytes.

## Purpose

Implements the FUSE fsctl readlink operation, returning the symlink target in a compact `readlink:` response.

## Important APIs, Types, and Functions

The endpoint is `XrdMgmOfs::Readlink(...)`. It calls `readlink(path, error, link, client)`, optionally URL-escapes the target when `eos.encodepath` is set, and writes the return code plus target into `XrdOucErrInfo`.

## Control Flow

The handler performs read access, stall, redirect, and stats. It calls the underlying MGM readlink implementation, maps errors from `error.getErrInfo()` or `-1`, and returns `readlink: retc=<retc> [target]`.

## State and Persistence Behavior

Read-only. All state is local to the request.

## Dependencies and Integration Points

Depends on `XrdMgmOfs::readlink`, `StringConversion::curl_escaped`, XRootD env fields, and normal MGM read redirection.

## Risks and Edge Cases

Targets containing spaces or `&` are only escaped when the caller asks for `eos.encodepath`; unencoded callers must handle raw target text. An underlying error with no errno becomes `-1`.

## Test Signals

Cover existing symlink, missing path, permission failure, encoded and raw targets with reserved characters, redirect behavior, and error propagation when `readlink` sets no errno.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Readlink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Redirect.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Redirect.cc

Source read size: 111 lines, 4031 bytes.

## Purpose

Implements an fsctl helper that returns the open redirect URL for a path without performing data transfer. It is used by clients that need to discover the target FST for read or write/open-create operations.

## Important APIs, Types, and Functions

The function is `XrdMgmOfs::Redirect(...)`. It parses `eos.client.openflags` and `eos.client.openmode`, constructs XRootD `SFS_O_*` flags, applies read or write access macros, opens through `XrdMgmOfsFile`, and rewrites the redirect URL with `:<port>/<path>?`.

## Control Flow

The handler records `OpenRedirect`, builds a file object, maps textual flags (`wo`, `rw`, `cr`, `tr`) to open bits, chooses write access when create/rw/truncate is requested and read access otherwise, calls `file->open`, and returns `SFS_DATA` only for `SFS_REDIRECT`. Redirect text is patched to include `file->error.getErrInfo()` and the requested path; failures return the file error text and code.

## State and Persistence Behavior

Potential durable side effects depend on open flags: create and truncate can mutate namespace/file state through `XrdMgmOfsFile::open`. The local file object is temporary.

## Dependencies and Integration Points

Depends on `XrdMgmOfsFile`, access/stall/redirect macros, XRootD open flag semantics, and client opaque fields.

## Risks and Edge Cases

`eos.client.openmode` is read when `eos.client.openflags` exists; a missing mode yields octal parse of an empty string. The string replacement assumes the redirect text contains `?`; if not, `emsg.find("?")` can produce an invalid replace position. Flag substring matching can misinterpret unexpected flag text.

## Test Signals

Test read-only redirect, create/write/truncate redirects, missing or malformed open mode, failed opens, redirect text without `?`, permission failures, and path strings needing URL escaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Redirect.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Stat.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Stat.cc

Source read size: 92 lines, 4112 bytes.

## Purpose

Implements `XrdMgmOfs::FuseStat`, the FUSE stat fsctl endpoint. It returns an `lstat` result as a fixed field list in an XRootD buffer.

## Important APIs, Types, and Functions

The endpoint calls `lstat(path, &buf, error, client, ininfo)`, formats `struct stat` fields into `stat: ...`, wraps malloc-owned memory in `XrdOucBuffer`, and returns it through `error.setErrInfo`.

## Control Flow

The function uses `ACCESSMODE_R_MASTER`, stall and redirect handling, records `Fuse-Stat`, executes lstat, and on success formats device, inode, mode, link count, uid/gid, rdev, size, block size/count, and timestamp seconds/nanoseconds. On failure it returns `stat: retc=<errno>`.

## State and Persistence Behavior

Read-only. The response buffer is transferred to XRootD ownership.

## Dependencies and Integration Points

Depends on the MGM stat/lstat implementation, XRootD buffer ownership, and platform-specific timestamp fields.

## Risks and Edge Cases

The success path uses `malloc(16384)` and `sprintf` without checking allocation before formatting. The endpoint forces read-master access, so follower behavior differs from normal read-only stat. The buffer length passed to `XrdOucBuffer` is `strlen(statinfo)`, while `setErrInfo` uses `BuffSize()`.

## Test Signals

Cover file, directory, symlink, missing path, permission failure, null allocation injection, timestamp formatting, and master redirection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Stat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Statvfs.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Statvfs.cc

Source read size: 138 lines, 4974 bytes.

## Purpose

Implements the FUSE statvfs fsctl endpoint. It returns space-wide or quota-specific availability and capacity counters for a requested EOS space/path.

## Important APIs, Types, and Functions

The function reads `path` from the env, optionally URL-decodes it, uses `FsView::gFsView.mSpaceView["default"]` aggregate statfs counters for shallow/default requests, or calls `Quota::GetIndividualQuota` for deeper quota paths. It returns `f_avail_bytes`, `f_avail_files`, `f_max_bytes`, and `f_max_files`.

## Control Flow

After read access, stall, redirect, and stats, the handler decodes the requested space/path and counts slash depth. Unless `EOS_MGM_STATVFS_ONLY_QUOTA` is set, shallow paths or `EOS_MGM_STATVFS_ONLY_SPACE` use a static cached default-space aggregate guarded by `statvfsmutex`; the cache refreshes after a randomized 5-15 second interval. Other paths call the quota subsystem. Empty path returns `EINVAL`.

## State and Persistence Behavior

The file owns static process-local cache state for statvfs counters and last refresh time. It does not persist to disk.

## Dependencies and Integration Points

Integrates FUSE statvfs with `FsView`, space statfs counters, quota lookup, random cache jitter, env-controlled behavior, and XRootD response formatting.

## Risks and Edge Cases

Only the `default` space is used for aggregate statfs, regardless of the decoded path. Environment variables change semantics globally. Cached values can be stale for up to the randomized interval. Slash-depth heuristic determines whether quota is consulted.

## Test Signals

Test empty path, encoded path, shallow aggregate path, deep quota path, env overrides, missing default space, cache refresh timing, and quota values for users with and without limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Statvfs.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Symlink.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Symlink.cc

Source read size: 70 lines, 2781 bytes.

## Purpose

Implements the FUSE fsctl symlink operation, creating an EOS symlink and returning a compact return-code response.

## Important APIs, Types, and Functions

The endpoint reads env `target`, decodes it with `curl_unescaped` when `eos.encodepath` is set or `UnsealXrdPath` otherwise, and calls `symlink(path, target.c_str(), error, client, 0, 0)`.

## Control Flow

Write access, stall, redirect, and `Fuse-Symlink` stats are applied first. If `target` exists, the target is decoded and passed to the underlying symlink implementation; errors are copied from `error.getErrInfo()`. Missing target returns `EINVAL`. The response is always `symlink: retc=<retc>` with `SFS_DATA`.

## State and Persistence Behavior

The durable side effect is namespace symlink creation. No local persistent state is owned.

## Dependencies and Integration Points

Depends on `XrdMgmOfs::symlink`, XRootD env encoding conventions, and path conversion helpers.

## Risks and Edge Cases

The order of `path` and `target` follows the local `symlink` wrapper signature, not necessarily POSIX naming expectations. Target decoding differs between encoded and sealed modes; callers must set `eos.encodepath` consistently. Existing target/path conflicts are delegated to the underlying implementation.

## Test Signals

Cover encoded and sealed targets, missing target, relative and absolute target strings, existing link path, permission failure, and master redirect handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Symlink.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Utimes.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Utimes.cc

Source read size: 73 lines, 2907 bytes.

## Purpose

Implements the FUSE fsctl endpoint for updating file timestamps.

## Important APIs, Types, and Functions

The function reads `tv1_sec`, `tv1_nsec`, `tv2_sec`, and `tv2_nsec`, fills a two-element `timespec` array, and calls `_utimes(path, tvp, error, vid, ininfo)`.

## Control Flow

The handler uses write access, stall, redirect, and `Fuse-Utimes` stats. When all timestamp fields are present, it parses them as base-10 integers, calls `_utimes`, and returns `utimes: retc=<retc>`. Missing fields return `EINVAL`.

## State and Persistence Behavior

The durable side effect is namespace metadata timestamp mutation. No local state persists.

## Dependencies and Integration Points

Depends on `XrdMgmOfs::_utimes`, XRootD env fields, and MGM permission/redirect macros.

## Risks and Edge Cases

Fields are parsed with `strtol` without range or trailing-character validation. Comments label the first element as ctime, although POSIX `utimens`-style arrays are usually atime and mtime; correctness depends on `_utimes`' expected convention. Nanosecond bounds are not checked locally.

## Test Signals

Test valid timestamp updates, missing fields, malformed values, nanosecond overflow/negative values, permission failure, and timestamp ordering expected by `_utimes`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Utimes.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Version.cc -->
# sources/distributed-fs/eos/mgm/ofs/fsctl/Version.cc

Source read size: 77 lines, 2872 bytes.

## Purpose

Implements an fsctl endpoint that returns EOS version and optional feature information using the existing proc command implementation.

## Important APIs, Types, and Functions

The endpoint is `XrdMgmOfs::Version(...)`. It checks `mgm.version.features`, opens `ProcCommand` on `/proc/user` with `mgm.cmd=version` and optional `mgm.option=f`, then streams the proc output into a `version: retc=<retc>` response.

## Control Flow

The handler applies read access, stall, redirect, and records `Version`. It opens the proc command, sets `retc=EINVAL` on open failure, and on success repeatedly reads 4095-byte chunks until EOF or a short read. The final response is returned through `XrdOucErrInfo`.

## State and Persistence Behavior

Read-only. It allocates no persistent state and uses a stack buffer for streaming.

## Dependencies and Integration Points

Depends on `ProcCommand`, the user `version` proc command, XRootD env flags, and normal MGM read routing.

## Risks and Edge Cases

Proc open errors are collapsed to `EINVAL`. The read loop stops on the first short read, assuming normal stream semantics. Large version output is accumulated in memory in an `XrdOucString`.

## Test Signals

Cover normal version output, features output, proc open failure, chunked output larger than 4095 bytes, empty output, and HTTP/FUSE clients consuming the prefixed response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/fsctl/Version.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.cc -->
# sources/distributed-fs/eos/mgm/pathrouting/PathRouting.cc

Source read size: 307 lines, 9396 bytes.

## Purpose

Implements the runtime behavior of `PathRouting`, an in-memory MGM route table that maps EOS path prefixes to one or more remote MGM endpoints and chooses a reachable master endpoint for client redirection.

## Important APIs, Types, and Functions

Key methods are `Clear`, `Add`, `Remove`, `Reroute`, `GetListing`, and the background `UpdateEndpointsStatus(ThreadAssistant&)`. It stores `std::map<std::string, std::list<RouteEndpoint>> mPathRoute` guarded by `mPathRouteMutex`, uses `RouteEndpoint::UpdateStatus`, and returns `Status::{REROUTE,NOROUTING,STALL}`.

## Control Flow

`Add` inserts a path-to-endpoint mapping while rejecting duplicate endpoint objects for an existing path. `Reroute` parses `inpath` plus `ininfo` through `XrdCl::URL`, prefers CGI tags `eos.route`, `mgm.path`, then `mgm.quota.space`, URL-decodes and normalizes the path, appends a trailing slash, finds an exact route or longest parent subpath, picks an online master endpoint or the first endpoint, stalls if the selected endpoint is offline, and fills host/port/stat-info for HTTP(S) or XRootD redirect. `GetListing` emits all or one route with `_` for offline and `*` for master endpoints. `UpdateEndpointsStatus` periodically refreshes endpoint online/master state and marks a route offline if two or more online masters are seen.

## State and Persistence Behavior

Routes and endpoint status live only in memory. A background assisted thread is started when the update timeout is nonzero; the destructor joins it. Endpoint online/master flags are atomic fields owned by `RouteEndpoint`.

## Dependencies and Integration Points

Depends on `RouteEndpoint`, `common::Path`, URL decoding, `XrdCl::URL`, logging, and `AssistedThread`. It is used by MGM redirect/proc routing to direct clients to the correct remote MGM.

## Risks and Edge Cases

The destructor unconditionally joins the assisted thread, so construction with zero timeout depends on `AssistedThread::join` being safe. `Reroute` assumes `path.back()` after empty checks and normalized path handling. Multiple masters force all endpoints offline, deliberately stalling clients. Longest-prefix search starts below the full path, so exact matches must be normalized with trailing slash.

## Test Signals

Test exact and longest-prefix routes, CGI tag priority, URL-encoded paths, HTTP/HTTPS versus XRootD ports, offline endpoint stall, multiple-master detection, duplicate add rejection, remove/clear/listing behavior, and background refresh termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.hh -->
# sources/distributed-fs/eos/mgm/pathrouting/PathRouting.hh

Source read size: 135 lines, 5803 bytes.

## Purpose

Declares the `PathRouting` class and its public contract for path-prefix based MGM redirection.

## Important APIs, Types, and Functions

The header defines `PathRouting::Status`, constructor with update interval, destructor, `Reroute`, `Add`, `Remove`, `Clear`, `GetListing`, and private `UpdateEndpointsStatus`. Main fields are `mPathRoute`, `mPathRouteMutex`, `mThread`, and `mTimeout`.

## Control Flow

The constructor stores the update timeout and starts the assisted status-update thread if the timeout is nonzero. Public methods are implemented in the `.cc`: route-table mutation takes write locks, routing/listing take read locks, and the private thread method polls endpoint status until termination is requested.

## State and Persistence Behavior

The route table is process-local memory. There is no serialization in this header; persistence, if any, is handled by higher-level configuration code that calls `Add` and `Remove`.

## Dependencies and Integration Points

Includes MGM namespace/logging, `Mapping`, `AssistedThread`, and `RouteEndpoint`. Consumers include MGM redirect decisions and admin route listing/configuration commands.

## Risks and Edge Cases

Callers must normalize route keys consistently with `Reroute`'s trailing-slash logic. Thread lifetime is tied to the object. `RouteEndpoint` equality determines duplicate detection semantics.

## Test Signals

Compile tests for route consumers, construction with zero and nonzero timeout, route-table concurrent add/list/reroute coverage, and endpoint status update tests using controlled `RouteEndpoint` responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/pathrouting/PathRouting.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterDataTypes.hh -->
# sources/distributed-fs/eos/mgm/placement/ClusterDataTypes.hh

Source read size: 440 lines, 13005 bytes.

## Purpose

Defines compact placement data structures used by the new EOS MGM filesystem scheduler: disks, hierarchical buckets, cluster snapshots, geotag hash storage, and formatted diagnostics.

## Important APIs, Types, and Functions

Important types are `fsid_t`, `item_id_t`, `epoch_id_t`, `Disk`, `Bucket`, `ClusterData`, and `StdBucketType`. Helpers include `getActiveStatus`, `GroupIDtoBucketID`, `BucketIDtoGroupID`, `BucketTypeToStr`, `FormatItemList`, `ClusterData::setDiskStatus`, `setDiskWeight`, `getDisksAsString`, `getBucketsAsString`, and `isValidBucketId`.

## Control Flow

There is no scheduler control loop here; methods perform atomic field updates and diagnostic table generation. `getActiveStatus` maps an online filesystem that is not booted to offline. Group ids are represented as negative bucket ids. `ClusterData` indexes disks by `fsid - 1` and buckets by `-bucket_id`.

## State and Persistence Behavior

`ClusterData` is an in-memory snapshot. Disk config/active status, weight, and percent used are atomics to allow live updates without rebuilding the full snapshot. Geotag hashes and string maps are diagnostic/topology state within the snapshot.

## Dependencies and Integration Points

Depends on `common::FileSystem` status enums, table formatter classes, atomics, vectors, and unordered maps. It is consumed by `ClusterMap`, `FlatScheduler`, and placement strategies.

## Risks and Edge Cases

Indexing assumes positive disk ids start at 1 and negative bucket ids fit the bucket vector. `setDiskStatus` checks `id > disks.size()` but not `id == 0`, so id 0 would index before the vector. The `Disk` size static assertion is ABI/performance-sensitive. `isValidBucketId` returns true for valid bucket ids; callers must not invert its meaning.

## Test Signals

Cover group/bucket id round trips, active status mapping with boot states, atomic status/weight updates, table formatting color thresholds, geotag display, invalid id handling including id 0, and `sizeof(Disk) == 8` compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterDataTypes.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.cc -->
# sources/distributed-fs/eos/mgm/placement/ClusterMap.cc

Source read size: 240 lines, 7003 bytes.

## Purpose

Implements RCU-managed cluster snapshot publication and `StorageHandler`, the builder used to construct placement data from EOS filesystem views.

## Important APIs, Types, and Functions

Key methods are `ClusterMgr::getStorageHandler`, `getClusterData`, `addClusterData`, `setDiskStatus`, `setDiskWeight`, `getStorageHandlerWithData`, `getStateStr`, and `StorageHandler::{addBucket,addDisk,addDiskSequential,addGeoTag,getUniqueHash}`.

## Control Flow

`StorageHandler` accumulates buckets, disks, weights, and geotags in a local `ClusterData`. Its destructor publishes the completed snapshot through `ClusterMgr::addClusterData`, which swaps an atomic unique pointer under the RCU mutex and increments the epoch. Disk status updates acquire RCU read locks and mutate atomics in the current snapshot. Geotags are split on `::`, each segment is hashed with XXH3, and rare hash collisions are resolved by appending a nonce before rehashing.

## State and Persistence Behavior

All state is in memory. `ClusterMgr` owns the current snapshot pointer and epoch. `StorageHandler` publishes on destruction, making object lifetime part of the commit protocol.

## Dependencies and Integration Points

Depends on `ClusterDataTypes`, `RCULite`, `AtomicUniquePtr`, and xxhash. It is fed by `EosClusterMgrHandler` in `FsScheduler` and read by `FlatScheduler` and placement strategies.

## Risks and Edge Cases

Publishing in the `StorageHandler` destructor is convenient but risky if a partially built handler exits early. `addBucket` uses `parent_index != bucket_id`, comparing an index to an id, so root special-case logic is subtle. Nonsequential disk insertion resizes vectors and may leave default disk slots. `addGeoTag` currently omits the final segment after the last `::`.

## Test Signals

Test snapshot publication and epoch increments, RCU readers during swap, sequential and sparse disk insertion, bucket parent item lists and total weights, hash collision fallback, geotag parsing including single/no-delimiter tags, and diagnostic state strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.hh -->
# sources/distributed-fs/eos/mgm/placement/ClusterMap.hh

Source read size: 125 lines, 4228 bytes.

## Purpose

Declares the placement cluster snapshot manager and builder API.

## Important APIs, Types, and Functions

Defines `RCUMutexT`, `ClusterMgr`, nested `ClusterDataPtr`, and `StorageHandler`. Public operations include snapshot builders, RCU-protected snapshot access, live disk status/weight updates, state string generation, bucket/disk addition, and geotag helpers.

## Control Flow

`ClusterDataPtr` acquires an RCU read lock in its constructor and exposes pointer-like access to the snapshot until destruction. `StorageHandler` initializes a bucket vector, accumulates changes, and publishes by calling `ClusterMgr::addClusterData` from its destructor.

## State and Persistence Behavior

State is process-local and RCU-protected. The epoch counter tracks snapshot/weight changes for strategy caches and diagnostics; no disk persistence is performed here.

## Dependencies and Integration Points

Used by `FsScheduler`, `FlatScheduler`, and all placement strategies. Depends on common RCU primitives, atomic unique pointers, and the data types from `ClusterDataTypes.hh`.

## Risks and Edge Cases

The builder destructor has side effects, so copies/moves and early returns must be controlled. `ClusterDataPtr` assumes the raw pointer remains valid while its read lock is held. `setDiskWeight` increments epoch, but config/active status updates do not.

## Test Signals

Compile and unit coverage for snapshot lifetime, RCU lock scope, builder publication on destructor, mutable disk updates, and state string calls with empty and populated snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ClusterMap.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.cc -->
# sources/distributed-fs/eos/mgm/placement/FlatScheduler.cc

Source read size: 189 lines, 5818 bytes.

## Purpose

Implements `FlatScheduler`, the strategy-dispatching placement engine that walks cluster buckets and selects disks or sub-buckets for replicas.

## Important APIs, Types, and Functions

Important functions are `makePlacementStrategy`, constructors, `schedule`, `scheduleDefault`, `access`, and `accessStategyIndex`. It instantiates round-robin, weighted-random, and weighted-round-robin strategies in `mPlacementStrategy`.

## Control Flow

`schedule` validates replica count and strategy, then either calls `scheduleDefault` or performs a BFS over buckets according to selection rules. Each bucket level delegates to the chosen `PlacementStrategy::placeFiles`; returned negative ids are queued as child buckets and positive ids become final disk ids. `scheduleDefault` descends one bucket at a time until it reaches a valid disk placement, selecting all replicas at group level and optionally honoring `forced_group_index`. `access` maps several strategy names to an access strategy implementation and delegates replica read selection.

## State and Persistence Behavior

`FlatScheduler` owns strategy objects and their in-memory seeds/caches. It does not persist placements.

## Dependencies and Integration Points

Depends on `ClusterData`, `PlacementStrategy`, `RoundRobinPlacement`, `WeightedRandomPlacement`, and `WeightedRoundRobinPlacement`. It is owned by `FSScheduler`.

## Risks and Edge Cases

The early bucket check appears inverted: it returns "Bucket id out of range" when `isValidBucketId(args.bucket_id, cluster_data)` is true. The BFS branch shadows `result` inside the loop and returns the outer result, so non-default scheduling may drop successful ids. Rule indexing by `bucket.bucket_type` assumes valid type below `MAX_PLACEMENT_HEIGHT`. `accessStategyIndex` maps weighted round robin to weighted random for access.

## Test Signals

Test default placement through root/group/disk, forced group success/failure, non-default BFS rule traversal, invalid bucket ids, zero replicas, invalid strategy fallback, and access strategy mapping for all strategy enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.hh -->
# sources/distributed-fs/eos/mgm/placement/FlatScheduler.hh

Source read size: 62 lines, 2562 bytes.

## Purpose

Declares the flat placement scheduler facade used by EOS MGM scheduling code.

## Important APIs, Types, and Functions

Defines `makePlacementStrategy` and class `FlatScheduler` with constructors, `schedule`, `access`, `accessStategyIndex`, private `scheduleDefault`, `mPlacementStrategy`, and `mDefaultStrategy`.

## Control Flow

The header establishes that all placement calls pass immutable `ClusterData` plus `PlacementArguments`, while access calls pass mutable `AccessArguments`. Strategy implementations are hidden behind `PlacementStrategy` pointers.

## State and Persistence Behavior

Scheduler state is the array of strategy instances plus a default strategy enum. Strategy internals may hold seed/cached weight state; the scheduler itself has no persistence.

## Dependencies and Integration Points

Depends on cluster data and placement strategy abstractions. It is constructed by `FSScheduler` and used for both file placement and replica access choice.

## Risks and Edge Cases

The strategy array is indexed directly by enum ordinals, so enum changes must keep `TOTAL_PLACEMENT_STRATEGIES` and factory behavior aligned. A constructor that creates only one strategy leaves other slots null.

## Test Signals

Compile coverage for every enum strategy, constructor coverage for all-strategy and single-strategy modes, null-strategy error handling, and ABI checks for callers using `accessStategyIndex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FlatScheduler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.cc -->
# sources/distributed-fs/eos/mgm/placement/FsScheduler.cc

Source read size: 351 lines, 11385 bytes.

## Purpose

Implements `FSScheduler`, the EOS-facing placement scheduler that rebuilds cluster data from `FsView`, exposes scheduling/access operations by space, and applies default or per-space strategy configuration.

## Important APIs, Types, and Functions

Key methods are `EosClusterMgrHandler::make_cluster_mgr`, `FSScheduler::updateClusterData`, `schedule`, `access`, `setDiskStatus`, `setDiskWeight`, `setPlacementStrategy`, `getPlacementStrategy`, `getStateStr`, and `isRunning`.

## Control Flow

The cluster handler reads `FsView::gFsView.mSpaceGroupView` under the view mutex, creates one `ClusterMgr` per space, adds a root bucket, adds group buckets from group indexes, and inserts each filesystem as a disk with config status, active status adjusted for boot state, capacity-derived weight, percent used, and geotag. `updateClusterData` publishes the new space map with an RCU write and marks the scheduler running. `schedule` resolves invalid strategy to the space/default strategy, reads the cluster map under RCU, gets the space snapshot, and retries placement up to ten times. `access` delegates read selection. Disk status/weight setters mutate the live cluster manager for a space. Per-space strategy updates copy and republish the strategy map under RCU.

## State and Persistence Behavior

The scheduler owns an RCU-protected map of spaces to cluster managers, an atomic default strategy, an optional RCU-protected per-space strategy map, and a running flag. Cluster state is rebuilt from `FsView`; it is not persisted here.

## Dependencies and Integration Points

Integrates placement with `FsView` space/group/filesystem views, `FlatScheduler`, `ClusterMgr`, filesystem status/config/geometry attributes, common RCU helpers, and EOS logging.

## Risks and Edge Cases

`make_cluster_mgr(const std::string&)` adds group buckets without passing parent id, relying on default parent `0`; root handling must be valid. Capacity-to-uint8 weight can truncate very large capacities. `schedule` retries without changing args, so repeated failure may not improve unless strategy state advances. `get_cluster_mgr` requires initialized `cluster_mgr_map`.

## Test Signals

Use fake `ClusterMgrHandler`/`FsView` data to test cluster rebuilds, multiple spaces, empty spaces, status and boot mapping, capacity weights, geotags, strategy fallback and per-space overrides, scheduling before initialization, and RCU map replacement under readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.hh -->
# sources/distributed-fs/eos/mgm/placement/FsScheduler.hh

Source read size: 99 lines, 4129 bytes.

## Purpose

Declares the EOS filesystem scheduler facade and its cluster-manager provider interface.

## Important APIs, Types, and Functions

Defines `ClusterMapT`, abstract `ClusterMgrHandler`, concrete `EosClusterMgrHandler`, and `FSScheduler` with scheduling, access, cluster update, disk status/weight mutation, strategy configuration, state dump, and running-state APIs.

## Control Flow

The header fixes the dependency-injection point: tests or alternate providers can supply a custom `ClusterMgrHandler`, while the default constructor uses `EosClusterMgrHandler`. The private `get_cluster_mgr` looks up space-specific state from the RCU map.

## State and Persistence Behavior

State fields are `mIsRunning`, `scheduler`, `cluster_handler`, RCU-protected `cluster_mgr_map`, atomic `placement_strategy`, RCU-protected `space_strategy_map`, and `cluster_rcu_mutex`.

## Dependencies and Integration Points

Used by MGM file placement/open paths and admin diagnostics. Depends on `ClusterMap` and `FlatScheduler`.

## Risks and Edge Cases

The API allows scheduling before `updateClusterData`, which returns empty/error results. Strategy reads and map reads share the same RCU mutex, so writers must avoid long critical sections.

## Test Signals

Mock handler tests for constructor injection, cluster update, scheduling/access before and after initialization, disk mutation APIs, strategy override visibility, and state string behavior for missing spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/FsScheduler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/PlacementStrategy.cc

Source read size: 131 lines, 5218 bytes.

## Purpose

Implements shared geolocation-aware helper logic for placement strategies.

## Important APIs, Types, and Functions

Defines `PlacementStrategy::calculateMaxGeoOverlap` and `PlacementStrategy::placeWithGeoFilter`. These operate on `ClusterData::disk_tags`, current `PlacementResult`, and a pre-sorted candidate list.

## Control Flow

`calculateMaxGeoOverlap` rejects non-disk or missing topology candidates, compares the candidate geotag hash vector with every already selected disk, and returns the maximum common prefix depth. `placeWithGeoFilter` walks sorted candidates, skips non-disk and duplicate entries, computes overlap, and skips overlapping candidates only when there are more than twice as many remaining candidates as needed. It fills result ids until the requested replica count or returns `ENOSPC`.

## State and Persistence Behavior

No state is stored. The functions are pure with respect to cluster input and result output.

## Dependencies and Integration Points

Used by placement strategies that want topology spreading after candidate ranking. Depends on `PlacementStrategy.hh` and geotag vectors populated by `StorageHandler::addGeoTag`.

## Risks and Edge Cases

If a candidate id is beyond `disk_tags`, overlap is treated as `max`, which encourages skipping when possible. Candidates without tags get zero overlap. The buffer factor heuristic is intentionally approximate and may still place replicas in the same topology when capacity is tight.

## Test Signals

Unit-test overlap depth for shared site/room/rack prefixes, missing tags, invalid ids, duplicate candidates, insufficient candidates, and cases where the skip heuristic should or should not preserve enough candidates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/PlacementStrategy.hh

Source read size: 387 lines, 12482 bytes.

## Purpose

Declares the common placement strategy interface, placement/access argument structures, result structure, strategy enum/string mapping, validation helpers, and deterministic hash ranking primitives.

## Important APIs, Types, and Functions

Important items are `PlacementResult`, `PlacementStrategyT`, `PlacementArguments`, `AccessArguments`, abstract `PlacementStrategy::placeFiles` and `access`, `validateArgs`, `validDiskPlct`, `calculateMaxGeoOverlap`, `placeWithGeoFilter`, `hashFid`, and `RankedItem`.

## Control Flow

Concrete strategies call `validateArgs` before selecting. `validDiskPlct` rejects non-disk ids, excluded filesystems, offline disks, and disks below the requested config status. Strategy string conversion maps unknown strings to `kGeoScheduler`. `hashFid` hashes fid/fsid/salt in little-endian order for cross-platform deterministic ranking.

## State and Persistence Behavior

The header defines data passed through scheduler calls; no persistence is owned. `PlacementResult` contains a fixed array of 32 ids, return code, replica count, and optional error text.

## Dependencies and Integration Points

Consumed by all placement strategies, `FlatScheduler`, and `FSScheduler`. Depends on cluster data, `RRSeed`, xxhash, and EOS status enums.

## Risks and Edge Cases

`PlacementResult::contains` searches up to `n_replicas`, not the number already filled, so default zeros can matter if used before all slots are set. The result array caps placements at 32 replicas. `validateArgs` compares bucket vector size to replica count, not the selected bucket's item count only. Unknown strategy strings silently become geoscheduler.

## Test Signals

Test enum/string round trips, unknown strategy defaulting, validation errors, exclude/status filtering, result validity for positive/negative ids, hash determinism across endian platforms, and max-replica boundary behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/PlacementStrategy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RRSeed.hh -->
# sources/distributed-fs/eos/mgm/placement/RRSeed.hh

Source read size: 77 lines, 3347 bytes.

## Purpose

Defines a small atomic round-robin seed generator used by placement strategies to advance per-bucket selection offsets.

## Important APIs, Types, and Functions

The header defines `AtomicWrapper<T>` and template class `RRSeed<T>`. `RRSeed::get(index, n_items)` atomically fetch-adds the seed at an index, and `getNumSeeds()` reports the seed vector size.

## Control Flow

Construction initializes a vector of copyable atomic wrappers. Each `get` call reserves a range by adding `n_items`, letting callers select consecutive bucket items without a global scheduler lock.

## State and Persistence Behavior

State is process-local atomic counters. It is not a synchronization primitive for other data and is not persisted.

## Dependencies and Integration Points

Used by `GlobalRRSeeder` in `RoundRobinPlacementStrategy.hh`. Depends on atomics and vectors.

## Risks and Edge Cases

Only unsigned integral types are allowed because wraparound is expected. `get` uses `at`, so out-of-range indexes throw. Copying atomics is intentionally only for initialization/storage, not live synchronization.

## Test Signals

Test monotonic increments per index, multi-thread fetch-add behavior, wraparound for unsigned types if feasible, out-of-range exceptions, and construction with zero seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RRSeed.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.cc

Source read size: 91 lines, 2656 bytes.

## Purpose

Implements unweighted placement strategies: global round robin, thread-local round robin, random, and fid-derived random seeding.

## Important APIs, Types, and Functions

Key functions are `makeRRSeeder`, `RoundRobinPlacement::placeFiles`, and `RoundRobinPlacement::access`. The strategy uses `RRSeeder` implementations, `pickIndexRR`, `validDiskPlct`, and `MAX_PLACEMENT_ATTEMPTS`.

## Control Flow

`makeRRSeeder` selects a seeder based on `PlacementStrategyT`. `placeFiles` validates arguments, checks the bucket count fits the seed pool, obtains a seed for the bucket, then tries up to `MAX_PLACEMENT_ATTEMPTS` positions in the bucket item list. It skips duplicate selections and unusable disks, allows child buckets through, and succeeds only when the requested replica count is filled. `access` currently chooses a random selected filesystem index.

## State and Persistence Behavior

State is held in the seeder object or thread-local seed vector. There is no persistent placement record.

## Dependencies and Integration Points

Depends on cluster data, common random/container utilities, `RRSeed`, and `ThreadLocalRRSeed`. It is instantiated by `FlatScheduler`.

## Risks and Edge Cases

Random seeding may duplicate candidates and exhaust attempts. `RandomSeeder::get` returns a seed based on `mMaxBuckets`, not the selected bucket size. Access ignores disk health and geolocation and assumes `selectedfs` is nonempty. Bucket count greater than seed count is rejected.

## Test Signals

Cover each seeder type, duplicate avoidance, excluded/offline/status-filtered disks, child bucket selection, insufficient capacity, seed pool overflow, and access with empty and nonempty replica vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.hh

Source read size: 140 lines, 4113 bytes.

## Purpose

Declares the unweighted placement strategy and seed-provider abstraction.

## Important APIs, Types, and Functions

Defines `RRSeeder`, `GlobalRRSeeder`, `ThreadLocalRRSeeder`, `RandomSeeder`, `FidSeeder`, `makeRRSeeder`, and `RoundRobinPlacement`.

## Control Flow

Concrete seeders return a starting offset for a bucket. Global seeders use atomic counters, thread-local seeders use per-thread vectors, random seeders use `getRandom`, and fid seeders derive a deterministic seed from bucket index, replica count, and fid. `RoundRobinPlacement` delegates placement and access to the `.cc` implementation.

## State and Persistence Behavior

Seeder state is in memory. Thread-local seeds are initialized when a thread-local strategy object is constructed.

## Dependencies and Integration Points

Used by `FlatScheduler` and the round-robin strategy implementation. Depends on logging, cluster data, placement interfaces, `RRSeed`, `ThreadLocalRRSeed`, and random utilities.

## Risks and Edge Cases

The trailing namespace comment has a typo, harmless to compilation but a maintenance signal. `RandomSeeder::get` handles `index > mMaxBuckets`, not `>=`, and logs before returning an adjusted value. Fid seeding is deterministic but simple xor may collide heavily for related ids.

## Test Signals

Compile each seeder path, test thread-local initialization in multiple threads, deterministic fid seeding, random range bounds, and strategy construction for all accepted unweighted enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/RoundRobinPlacementStrategy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.cc -->
# sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.cc

Source read size: 46 lines, 1038 bytes.

## Purpose

Implements the thread-local round-robin seed vector used by thread-local placement strategy mode.

## Important APIs, Types, and Functions

Defines `thread_local std::vector<uint64_t> ThreadLocalRRSeed::gRRSeeds`, plus `init`, `resize`, and `get`.

## Control Flow

`init` resizes the thread-local vector and optionally fills every seed with a random initial value. `resize` preserves existing seeds and optionally randomizes newly added entries. `get` returns the current seed for an index and advances it by `n_items`, logging a critical error and returning zero when the index is out of range.

## State and Persistence Behavior

State is per-thread memory only. It is not shared across threads and is reset when a thread exits or reinitializes the vector.

## Dependencies and Integration Points

Used by `ThreadLocalRRSeeder` in the round-robin placement strategy. Depends on EOS logging and random utilities.

## Risks and Edge Cases

Thread-local state means scheduling fairness is per worker thread, not global. Calling `init` can reset existing seeds in the current thread. Out-of-range access returns zero, which biases selection instead of failing the placement.

## Test Signals

Test independent seed sequences across threads, randomized initialization bounds, resize preserving old values, out-of-range handling, and repeated `get` increments by replica count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.hh -->
# sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.hh

Source read size: 32 lines, 760 bytes.

## Purpose

Declares the thread-local round-robin seed holder for placement scheduling.

## Important APIs, Types, and Functions

Defines `kDefaultMaxRRSeeds` and struct `ThreadLocalRRSeed` with static `get`, `init`, `resize`, `getNumSeeds`, and thread-local `gRRSeeds`.

## Control Flow

The header exposes only static functions; concrete behavior is implemented in the `.cc` file and consumed through `ThreadLocalRRSeeder`.

## State and Persistence Behavior

The only state is a thread-local vector of `uint64_t` seeds. It is process memory with per-thread lifetime.

## Dependencies and Integration Points

Included by `RoundRobinPlacementStrategy.hh` and used by the thread-local round-robin strategy.

## Risks and Edge Cases

Users must call `init` or rely on the default 1024-entry vector before requesting indexes. Different threads may produce different placement sequences for identical workloads.

## Test Signals

Compile coverage, default seed count, explicit init/resize behavior, and integration with `RoundRobinPlacement` using `kThreadLocalRoundRobin`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/ThreadLocalRRSeed.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.cc

Source read size: 168 lines, 4627 bytes.

## Purpose

Implements weighted-random placement and a weighted access-selection path. Disk and bucket weights are derived from cluster snapshot weights.

## Important APIs, Types, and Functions

Important pieces are `WeightedRandomPlacement::Impl`, `populateWeights`, `Impl::placeFiles`, public `placeFiles`, `access`, and destructor. It uses `std::discrete_distribution`, a shared mutex, thread-local `std::mt19937`, `hashFid`, and `validDiskPlct`.

## Control Flow

Weights are populated lazily the first time placement is requested: one distribution for buckets and one per bucket's item list. Placement samples item indexes from the distribution for `args.bucket_id`, skips duplicates and unusable disks, and fills requested replicas up to `MAX_PLACEMENT_ATTEMPTS`. Access walks the already selected fs ids, filters invalid/unavailable/read-disallowed disks, computes `hashFid(inode, fsid) / weight`, and selects the lowest score.

## State and Persistence Behavior

The strategy caches distributions inside `Impl` for the process lifetime. It does not currently track cluster epochs, so cached distributions can become stale after weights or topology change.

## Dependencies and Integration Points

Instantiated by `FlatScheduler` for weighted-random strategy and also used as the access strategy for weighted modes. Depends on C++ random facilities, cluster data, logging, and placement helpers.

## Risks and Edge Cases

`populateWeights` iterates default bucket slots too, so bucket id/index validity matters. Placement sets `ret_code=0` even if fewer than requested replicas were added. Access stores `best_index = fsid` but `selectedIndex` convention may expect an index into `selectedfs`; the final `best_index <= args.selectedfs.size()` check is suspicious for fs ids greater than the vector length. Division by zero is possible if disk weight is zero.

## Test Signals

Test distribution population for sparse buckets, duplicate/filtered candidates, stale cache after weight changes, insufficient replicas, zero weights, weighted access index semantics, unavailable/excluded replicas, and deterministic hash ranking for a fixed inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.hh

Source read size: 44 lines, 2192 bytes.

## Purpose

Declares the weighted-random placement strategy.

## Important APIs, Types, and Functions

Defines class `WeightedRandomPlacement : PlacementStrategy` with constructor, `placeFiles`, `access`, destructor, and private PIMPL `Impl`.

## Control Flow

The public methods delegate to `Impl` in the `.cc` file after base validation. PIMPL hides the random distribution cache and locking.

## State and Persistence Behavior

Strategy state is in-memory distribution data owned by `Impl`. No persistence is done.

## Dependencies and Integration Points

Included by `FlatScheduler` and used for both placement and weighted access choices.

## Risks and Edge Cases

The header comment says weighted random based on disk sizes; if future weights include utilization or admin overrides, documentation and tests need updating. PIMPL lifetime must remain stable for strategy array storage.

## Test Signals

Compile construction/destruction, virtual dispatch through `PlacementStrategy`, and integration tests through `FlatScheduler` for weighted-random placement and access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRandomStrategy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.cc -->
# sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.cc

Source read size: 150 lines, 4596 bytes.

## Purpose

Implements an approximate weighted round-robin placement strategy using decrementing per-item weight budgets.

## Important APIs, Types, and Functions

Important methods are `WeightedRoundRobinPlacement::Impl::fill_weights`, `Impl::placeFiles`, public `placeFiles`, `access`, and destructor. State includes `mItemWeights`, `mBucketIndex`, `total_wt`, `total_disk_wt`, and `wt_mtx`.

## Control Flow

`placeFiles` locks the weight state, refills weights when total remaining weight is below the requested replica count, takes and increments a per-bucket round-robin index, then scans bucket items with `pickIndexRR`. Disk candidates are skipped when weight is exhausted, excluded, unknown, offline, or below requested config status; accepted disks decrement item, bucket, and total weights. Child buckets are accepted only if their remaining weight can satisfy the requested replicas. Success requires all replicas to be filled.

## State and Persistence Behavior

Weight budgets and bucket indexes persist in the strategy object between calls. They are not tied to cluster epochs except by refill decisions, so topology/weight changes may be reflected only on refill.

## Dependencies and Integration Points

Instantiated by `FlatScheduler` for `kWeightedRoundRobin`. Depends on cluster data, common round-robin picking, logging, and placement validation.

## Risks and Edge Cases

The strategy serializes placement with one mutex. `mCurrentEpoch` is declared but not used. Weight maps include default bucket slots and can be stale. `access` is unimplemented and returns `EINVAL`; `FlatScheduler` maps weighted round-robin access to weighted random instead.

## Test Signals

Test weight refill, proportional placement over repeated calls, excluded/offline/status-filtered disks, child bucket weights, insufficient capacity, topology changes between refills, and access fallback through `FlatScheduler`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.hh -->
# sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.hh

Source read size: 44 lines, 2215 bytes.

## Purpose

Declares the weighted round-robin placement strategy.

## Important APIs, Types, and Functions

Defines class `WeightedRoundRobinPlacement : PlacementStrategy` with constructor, `placeFiles`, `access`, destructor, and private PIMPL `Impl`.

## Control Flow

Public methods dispatch to the `.cc` implementation. `access` is part of the virtual interface but currently returns an error in the implementation.

## State and Persistence Behavior

In-memory state lives in the PIMPL and tracks weight counters across placement calls.

## Dependencies and Integration Points

Included by `FlatScheduler`; selected through `PlacementStrategyT::kWeightedRoundRobin`.

## Risks and Edge Cases

The class comment repeats weighted-random wording, which can confuse maintainers. Because access is not supported directly, callers must rely on scheduler-level remapping or handle `EINVAL`.

## Test Signals

Compile and virtual dispatch coverage, construction/destruction, strategy selection through `makePlacementStrategy`, and scheduler access fallback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/placement/WeightedRoundRobinStrategy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.cc -->
# sources/distributed-fs/eos/mgm/policy/Policy.cc

Source read size: 846 lines, 30722 bytes.

## Purpose

Implements EOS MGM policy resolution for layout, space, forced placement, local redirect, conversion, read/write QoS fields, and proc policy command stubs.

## Important APIs, Types, and Functions

Key functions are `GetDefaultSizeFactor`, `GetSpacePolicyLayout`, `GetLayoutAndSpace`, `GetPlctPolicy`, `RedirectLocal`, `HasUpdConversion`, `HasReadConversion`, `UpdateConversion`, `ReadConversion`, `Set`, `Ls`, `Rm`, `Get`, `IsProcConversion`, `GetRWValue`, `GetRWConfigKeys`, and `RWParams::getKeys`. Static key lists define base policy and read/write policy names.

## Control Flow

`GetLayoutAndSpace` starts from explicit env layout/checksum/stripe/block settings, loads default and selected-space policies from `FsView`, applies read/write policy overrides by app/user/group/default priority, injects nonempty space policies into missing `sys.forced.*` attributes, processes explicit/forced space and group choices, optionally moves writes to the first under-nominal alternative space, applies sys forced layout/checksum/block/stripe/QoS/schedule settings, then applies user forced settings unless disabled. It outputs the final layout id, space, forced fs/group, bandwidth, schedule, I/O priority/type, atime age, and alternate checksums. `GetPlctPolicy` resolves scattered/hybrid/gathered placement and target geotag. Conversion helpers parse `space:layout` targets and return async/none/fail. Redirect logic returns never/always/optional based on xattrs, env override, and layout type.

## State and Persistence Behavior

The functions are mostly read-only, but `GetLayoutAndSpace` mutates the provided attribute map by injecting policy-derived `sys.forced.*` entries. Policy values are read from `FsView` space configuration; no persistent writes are implemented here (`Set` is effectively a stub).

## Dependencies and Integration Points

Integrates `LayoutId`, `FsView`, quota/nominal-space checks, namespace xattrs, `VirtualIdentity`, XRootD env parsing, conversion proc paths, alt checksum policy, and scheduler placement policy enums.

## Risks and Edge Cases

The policy precedence chain is complex: env, default space config, selected/alternative space config, sys forced xattrs, and user forced xattrs interact. Alternative-space selection only runs on writes. `std::stoi` for conversion layout can throw if malformed. `Set`, `Ls`, and `Get` are stubs/empty, so proc policy management may not do what callers expect. Logging format for layout id appears to pass layout/layoutId in reversed order.

## Test Signals

Use table-driven tests for policy precedence, noforce flags, root overrides, default/nondefault/alternative space policies, forced group/fsid, checksum noforce, alt checksum computation, read/write QoS keys by app/user/group, local redirect modes, placement policy geotag sanitation, conversion parsing and quota suppression, and malformed policy values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.hh -->
# sources/distributed-fs/eos/mgm/policy/Policy.hh

Source read size: 163 lines, 6887 bytes.

## Purpose

Declares the static MGM policy utility class that resolves storage layout, space, placement, conversion, local redirect, and policy proc command behavior.

## Important APIs, Types, and Functions

Important declarations include `GetLayoutAndSpace`, `GetPlctPolicy`, `RedirectStatus`, `RedirectLocal`, `ConversionPolicy`, `HasUpdConversion`, `HasReadConversion`, `UpdateConversion`, `ReadConversion`, `GetSpacePolicyLayout`, `Set/Ls/Rm/Get`, `IsProcConversion`, static policy key vectors, `GetDefaultSizeFactor`, and nested `RWParams`.

## Control Flow

The class is a namespace-like collection of static functions. `RWParams` derives app/user/group/read-write policy keys and orders key lookup from app-specific to user, group, and generic read/write keys.

## State and Persistence Behavior

The header declares static key lists but no mutable state. Policy state lives in EOS space config and namespace attributes read by the implementation.

## Dependencies and Integration Points

Depends on mapping, MGM scheduler placement enums, namespace container metadata, and XRootD env/string types. Used by open/create/read paths and proc/admin policy surfaces.

## Risks and Edge Cases

Because all APIs are static and accept mutable attr/env references, callers must document whether the view lock is already held and whether attrmap mutation is acceptable. The policy command management API is declared even though much of it is not implemented in the `.cc`.

## Test Signals

Compile consumers of every static API, unit-test `RWParams::getKeys`, and integration-test `GetLayoutAndSpace` with controlled env/attr/space configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/policy/Policy.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.cc -->
# sources/distributed-fs/eos/mgm/proc/IProcCommand.cc

Source read size: 633 lines, 21528 bytes.

## Purpose

Implements the asynchronous protobuf-based proc command base class for MGM commands. It manages command execution slots, thread-pool dispatch, streaming responses, temporary output files, JSON formatting, path/id resolution, routing redirects, and comment logging.

## Important APIs, Types, and Functions

Key methods are `open`, `read`, `LaunchJob`, `KillJob`, `OpenTemporaryOutputFiles`, `CloseTemporaryOutputFiles`, `ConvertOutputToJsonFormat`, `ResponseToJsonString`, `GetPathFromFid`, `GetPathFromCid`, `IsOperationForbidden`, `ShouldRoute`, `HasSlot`, and `ResolveIdentifierToPath`. Static state includes `uuid`, `mMapCmdsMutex`, and `mCmdsExecuting`.

## Control Flow

`open` launches `ProcessRequest` once a per-command slot is available, either via `ProcInterface::sProcThreads` or synchronously through a ready promise. It waits up to five seconds; not-ready jobs stall the client, slot exhaustion stalls for a shorter delay, and ready jobs are converted to redirect/stall, file-backed streams, or an in-memory `mgm.proc.*` response. It logs privileged comments with the protobuf request serialized to JSON. `read` drains stdout, stderr, and return-code streams in order for file-backed output, or slices `mTmpResp` by offset. JSON conversion parses key/value lines into nested JSON with compatibility rewrites for known flat status keys. Identifier helpers resolve fid/fxid/cid/cxid to namespace paths.

## State and Persistence Behavior

Each command object owns future state, request identity, routing info, temp filenames/streams, and result buffers. Static command counters enforce up to 50 queued/running commands per command type and are decremented in the destructor. Temporary files are created under `/var/tmp/eos/mgm/` and unlinked by close/destruction. Comments can persist through `gOFS->mCommentLog`.

## Dependencies and Integration Points

Depends on protobuf request/reply types, `ProcInterface` thread pool, XRootD SFS interfaces, MGM redirect/stall, namespace services, JSONCPP, protobuf JSON conversion, `ProcBounce*` validation, and `CommentLog`.

## Risks and Edge Cases

The slot counter relies on destructor cleanup; leaked command objects leak capacity. Async jobs capture `this`, so object lifetime must be controlled by `KillJob` and caller ownership. `ConvertOutputToJsonFormat` advances `jep` twice per token level, which deserves scrutiny. File output uses fixed `/var/tmp/eos/mgm/` rather than `TmpStorePath`. Identifier resolution does not take an explicit namespace view lock in `ResolveIdentifierToPath`.

## Test Signals

Test async ready/stall/slot-exhaustion paths, redirect and route-stall replies, file-backed and memory-backed reads with offsets, comment logging authorization, JSON conversion of nested and conflicting keys, fid/fxid/cid/cxid resolution success/failure, forbidden path checks, destructor cleanup, and command counter decrementing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.hh -->
# sources/distributed-fs/eos/mgm/proc/IProcCommand.hh

Source read size: 389 lines, 15417 bytes.

## Purpose

Declares `IProcCommand`, the abstract base class for protobuf-backed MGM proc commands.

## Important APIs, Types, and Functions

The class provides constructors, destructor, virtual `open/read/stat/close/GetCmd/ProcessRequest/GetResult/SetError`, final `LaunchJob` and `KillJob`, temporary-file helpers, path/id resolution helpers, JSON response helpers, operation-forbidden and routing helpers, slot accounting, `RoutingInfo`, and many stream/result fields.

## Control Flow

Subclasses implement `ProcessRequest`. The base `open` method handles launching and response conversion, while `read/stat/close` expose the result to XRootD. The destructor marks `mForceKill`, closes/unlinks temp files, and decrements command slot counters when held.

## State and Persistence Behavior

Per-object state includes request proto, future, async flags, force-kill flag, virtual identity, timestamp/comment, routing info, temp files, response buffers, and stream read-phase booleans. Static state tracks command concurrency.

## Dependencies and Integration Points

Depends on MGM namespace/logging/mapping, console protobufs, XRootD SFS interfaces, futures, streams, JSONCPP forward declarations, and proc command subclasses.

## Risks and Edge Cases

The default `GetResult` returns placeholder text, so callers must use concrete subclasses for real result access. `stat` computes sizes from current stream positions and assumes stream state is seekable. Subclasses must honor `mForceKill` for cancellation to be effective.

## Test Signals

Subclass-based tests for virtual dispatch, async cancellation, stat/read sequencing for file and memory results, destructor cleanup, slot accounting, and JSON formatting exposure through `CallJsonFormatter`-style wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/IProcCommand.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcCommand.cc -->
# sources/distributed-fs/eos/mgm/proc/ProcCommand.cc

Source read size: 723 lines, 21270 bytes.

## Purpose

Implements the legacy string/CGI-based MGM proc command dispatcher. It parses `/proc/admin` and `/proc/user` requests, invokes command-specific member functions, and formats stdout/stderr/return-code results for normal, FUSE, JSON, JSONP, and HTTP clients.

## Important APIs, Types, and Functions

Key methods are constructors/destructor, `OpenTemporaryOutputFiles`, `open`, `read`, `stat`, `close`, `MakeResult`, `KeyValToHttpTable`, and `CallJsonFormatter`. Dispatch targets include admin commands such as `archive`, `backup`, `geosched`, `monit`, `fusex`, `vid`, `rtlog`, `access`, `quota`, and user commands such as `accounting`, `archive`, `motd`, `version`, `who`, `fuse`, `fuseX`, `file`, `fileinfo`, `mkdir`, `rmdir`, `cd`, `chown`, `ls`, `rm`, `whoami`, `find`, `map`, `member`, `attr`, `chmod`, and `quota`.

## Control Flow

`open` stores request identity/path/info, identifies admin or user proc path, protects literal ampersands in opaque values, builds an `XrdOucEnv`, extracts command/subcommand/output-format/depth/selection/comment/callback/retc flags, resets output state, and dispatches to the appropriate command function. Unknown commands set `EINVAL` or `ENOTSUP`. Some commands return directly for special streaming behavior; otherwise `MakeResult` builds the response. `read` serves either file-backed result streams or in-memory `mResultStream` slices. `close` records privileged comments. `MakeResult` sorts stdout unless disabled, seals key/value output for default format, emits raw stdout for FUSE, renders simple HTTP/HTML output, or builds JSON/JSONP. File-backed results are spooled from temp stdout/stderr into a combined result stream.

## State and Persistence Behavior

Per-command state includes opaque env ownership, stdout/stderr/json strings, return code, temp files under `gOFS->TmpStorePath`, command flags, selection/depth/comment, and result length. Temporary files are removed in destructor or after spooling. Comments can persist in the MGM comment log for root/daemon/sudoer users.

## Dependencies and Integration Points

Depends on `XrdMgmOfs`, `XrdOucEnv`/tokenizer, `CommentLog`, namespace view/services, JSONCPP, command-specific member implementations in other files, and formatting helpers from `StringConversion`.

## Risks and Edge Cases

The ampersand repair heuristic depends on known prefixes and can still misparse unusual opaque values. Dispatch is a long string chain, making command names and format behavior easy to drift. HTTP output emits hand-built HTML and only sets a restrictive CSP when stderr is present. `read` assumes offsets fit `mLen`; file-backed reads rely on `FILE*` seek state. Destructor cleanup must match all early-return paths.

## Test Signals

Test admin/user command dispatch and unknown commands, literal ampersand handling, default/FUSE/HTTP/JSON/JSONP formatting, stdout sorting toggles, file-backed find-style output, `mgm.retc` open behavior, comment logging authorization, `read` offsets and EOF, and temp-file cleanup on success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/proc/ProcCommand.cc -->
