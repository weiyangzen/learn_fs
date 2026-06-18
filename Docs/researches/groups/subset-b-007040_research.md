# Research Group: subset-b-007040

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.hh -->
# Research: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.hh

## Purpose

`XrdMgmOfsFile.hh` declares the EOS MGM implementation of the XRootD `XrdSfsFile` interface. It is the file-handle object used by the MGM for file opens, metadata-only proc command reads, close/stat/truncate/sync handling, page-read support, redirection scheduling, copy-on-write support, and per-open state such as identity, opaque CGI parameters, namespace file id, encryption key, and proc command result streaming.

## Important APIs, Types, and Functions

- `XrdMgmOfsFile` derives from `XrdSfsFile` and `eos::common::LogId`.
- `open(...)`, `close()`, `sync()`, `stat()`, `truncate()`, `read(offset,buff,len)`, and `pgRead(...)` are the main supported XRootD file operations.
- `write(...)`, async read/write, `pgWrite(...)`, async page I/O, and mmap are explicitly unsupported or no-op, which reflects that ordinary EOS data I/O is redirected to FSTs rather than served by the MGM.
- `handleHardlinkDelete()` and `create_cow()` are static helpers for hard-link deletion and copy-on-write clone behavior. `cowUpdate`, `cowDelete`, and `cowUnlink` define the supported clone modes.
- `targetParams` plus `setProxyFwEntrypoint()` model scheduled target host/port/http-port plus proxy/firewall redirection suffixes.
- Test-harness-visible helpers include `IsRainRetryWithExclusion()`, `GetTriedrcErrno()`, `RedirectTpcAccess()`, `LogSchedulingInfo()`, `GetExcludedFsids()`, `GetClientApplicationName()`, `GetPosixOpenFlags()`, and `GetXrdAccessOperation()`.

## Control Flow

The header exposes the intended file-control flow. Construction initializes the per-handle `VirtualIdentity` to `Nobody`. External XRootD open calls delegate to the overload that can also accept a precomputed `VirtualIdentity`; implementation code is expected to parse CGI opaque values, map identity, perform authorization, consult namespace metadata, and either return errors, proc-command data, or redirection details. Normal file data reads are not MGM-served except for proc command output, so `read(offset,buff,len)` is reserved for streaming command results while real files are usually redirected at open.

Unsupported write and async methods call `Emsg()` with `EOPNOTSUPP`, keeping the MGM file object a control-plane endpoint rather than a data-plane endpoint. The private scheduling helpers imply open-time logic that can exclude prior failed fsids, interpret `triedrc`, redirect third-party-copy access, and select proxy/firewall entrypoints.

## State and Persistence Behavior

The class stores transient per-open state: `oh`, `fileName`, `openOpaque`, `mFid`, `mProcCmd`, `fmd`, `vid`, `mEosKey`, `mEosObfuscate`, and `mIsZeroSize`. It does not itself persist metadata in the declaration, but its implementation is expected to mutate or read namespace state through `IFileMD`, `IContainerMD`, copy-on-write helpers, and close/truncate/stat code. `openOpaque` ownership and `mProcCmd` lifetime are important resource-management details because the file object can survive between auth-plugin RPC calls until close.

## Dependencies and Integration Points

This header depends on EOS identity mapping, logging, proc command interfaces, XRootD `XrdOucErrInfo`, `XrdSfsInterface`, `XrdSecEntity`, and namespace metadata interfaces. It integrates with XRootD by overriding `XrdSfsFile`, with MGM scheduling/redirection code through target parameters and access-operation mapping, with proc commands through `IProcCommand`, and with namespace hard-link/COW behavior through `IFileMD` and `IContainerMD`.

## Risks and Edge Cases

- The MGM intentionally does not serve normal file writes, so callers must handle redirects or `EOPNOTSUPP`; any path that accidentally expects direct MGM writes will fail.
- `openOpaque` is a raw pointer, so construction, open failure, and destruction paths need strict ownership discipline.
- Retry parsing and fsid exclusion logic can influence data placement and must distinguish legitimate retry from client-side exclusion.
- TPC redirection, firewall entrypoints, proxy endpoints, and port validation are security-sensitive because they populate redirect responses.
- Copy-on-write and hard-link deletion helpers can mutate namespace topology and must be lock-safe in their implementation.

## Test Signals

Useful tests should cover open-mode to POSIX flag conversion, access-operation mapping, unsupported write/async/page-write errors, proc-command read offsets, redirection target validation, retry opaque parsing with and without `triedrc`, excluded fsid extraction, TPC redirection, COW update/delete/unlink behavior, close/stat/truncate side effects, and destructor cleanup of opaque/proc state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsSecurity.hh -->
# Research: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsSecurity.hh

## Purpose

`XrdMgmOfsSecurity.hh` centralizes small authorization and identity-environment macros used by the MGM OFS command implementations. It adapts XRootD authorization callbacks to EOS-style early returns and provides a helper for putting authenticated user/host information into `XrdOucEnv`.

## Important APIs, Types, and Functions

- `AUTHORIZE(usr, env, optype, action, pathp, edata)` calls `gOFS->mExtAuthz->Access()` when a client and external authorizer exist; on denial it writes an EOS error with `EACCES` and returns `SFS_ERROR`.
- `AUTHORIZE2(...)` applies `AUTHORIZE` to two path/env/operation tuples, used by two-path operations.
- `OOIDENTENV(usr, env)` stores `SEC_USER` and `SEC_HOST` in an `XrdOucEnv` when available.

## Control Flow

The macros are meant to be invoked early in high-level XRootD command wrappers, before the lower-level EOS operation runs. `AUTHORIZE` is an inline guard: success falls through, while failure returns immediately from the containing function. Because it is a macro, it depends on local variables such as `epname` and the caller's return type.

## State and Persistence Behavior

This file stores no state and performs no persistence. Its only side effect is to call the configured external authorizer and populate `XrdOucErrInfo` on denial. `OOIDENTENV` mutates an environment object with authentication details.

## Dependencies and Integration Points

The macros depend on `XrdAccAuthorize.hh`, global `gOFS`, `mExtAuthz`, XRootD access-operation constants such as `AOP_Stat`, and `XrdOucErrInfo`. They are used throughout command `.inc` files before identity mapping, namespace access checks, or metadata mutation.

## Risks and Edge Cases

- Macro early returns are easy to misuse in functions that do not return `int`/`SFS_ERROR`.
- Authorization operation types must match the real operation. Passing `AOP_Stat` for a mutation would weaken external authorization.
- `env` may be null depending on caller construction; authorizer implementations must tolerate the pointer contracts used here.
- Because the macro checks only external authorization, callers still need EOS ACL/POSIX/token checks.

## Test Signals

Tests should exercise allow/deny external authorizer paths for representative read, update, create, delete, chmod, and two-path operations; verify `EACCES` text is set on denial; and confirm operations still apply internal EOS ACL checks after external authorization succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsSecurity.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsTrace.hh -->
# Research: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsTrace.hh

## Purpose

`XrdMgmOfsTrace.hh` defines compile-time-controlled tracing macros and trace-bit constants for the MGM OFS plugin. It provides consistent trace gates for common XRootD/OFS operations and maps groups such as directory, I/O, authorization, mapping, role, attribute, and prepare handling to bit masks.

## Important APIs, Types, and Functions

- `GTRACE(act)` checks `gMgmOfsTrace.What` against `TRACE_<act>`.
- `TRACES(x)` emits a trace message through `gMgmOfsTrace.Beg(epname,tident)`, `std::cerr`, and `End()`.
- `FTRACE`, `XTRACE`, `ZTRACE`, and `DEBUG` add common file-name or target context.
- `EPNAME(x)` declares a static endpoint name when debugging is enabled.
- `TRACE_*` constants enumerate operation categories, including `TRACE_open`, `TRACE_read`, `TRACE_write`, `TRACE_redirect`, `TRACE_fsctl`, `TRACE_authorize`, `TRACE_map`, `TRACE_attributes`, `TRACE_stager`, and `TRACE_prepare`.

## Control Flow

When `NODEBUG` is not defined, trace macros evaluate their bit guard and emit to the global trace object. When `NODEBUG` is defined, most macros compile to empty statements and `GTRACE` to zero. Command handlers can therefore leave trace calls inline without runtime logging cost in nodebug builds.

## State and Persistence Behavior

The file persists no state. It reads global trace flags and writes trace output. The trace flags influence observability only; they do not affect namespace metadata or request outcomes.

## Dependencies and Integration Points

It includes `mgm/ofs/XrdMgmOfs.hh`, uses the global `gMgmOfsTrace`, and assumes local variables such as `epname`, `tident`, and sometimes `oh`. It integrates with command handlers and file/directory methods as a conditional diagnostic layer.

## Risks and Edge Cases

- Macros that assume local names (`epname`, `tident`, `oh`) can fail or log misleading data if used in the wrong scope.
- Some trace constants share bits or are aliases (`TRACE_closedir`, `TRACE_close`, `TRACE_chmod`), which is useful for grouping but can surprise fine-grained filtering.
- Trace output uses `std::cerr`; high-volume tracing can affect performance or interleave messages.

## Test Signals

Compile both debug and `NODEBUG` builds, enable individual trace bits, and verify representative command paths emit expected operation names without changing behavior. Tests should also ensure trace macros remain syntactically safe in functions with no file handle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Access.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Access.inc

## Purpose

`Access.inc` implements access checking and access-right derivation for EOS MGM paths. It handles the public XRootD `access()` entry point, lower-level `_access()` checks against namespace metadata, ACL/POSIX permission interpretation, token-issuer permission, OC-style access string generation, anonymous/public access restrictions, squashfs special access, and a coarse `GetXrdAccPrivs()` bridge for XRootD authorization.

## Important APIs, Types, and Functions

- `XrdMgmOfs::access()` performs namespace mapping, external authorization, identity mapping, token/access-mode guards, stall/redirect handling, and delegates to `_access()`.
- `XrdMgmOfs::_access()` checks file or directory existence, parent-directory fallback for files and non-existing entries, `sys.owner.auth`, `Acl`, `AccessChecker::checkContainer()`, `AccessChecker::checkFile()`, token-issuer permission via `T_OK`, root/daemon override, and public access restrictions.
- `XrdMgmOfs::acc_access()` returns an OC permission string such as `R`, `WCKNV`, and `D` based on POSIX bits plus ACLs.
- `is_squashfs_access()` and `allow_public_access()` implement `eosnobody`/squashfs and anonymous-depth restrictions.
- `GetXrdAccPrivs()` performs basic mapping and currently returns `XrdAccPriv_All` after coarse checks.

## Control Flow

The high-level entry point maps `inpath` through `NAMESPACEMAP`, checks illegal names and external authorization, maps the client to `VirtualIdentity`, enforces global access restrictions, and invokes `_access`. `_access` first prefetches the requested item, tries file and container lookups, and if it is a file or non-existing child, switches the authorization object to the parent directory while optionally carrying file xattrs into the ACL.

The main permission path evaluates `sys.owner.auth` before ACL/POSIX checks, constructs `Acl`, locks the container to read mode and ownership, rejects token issuance for non-owners unless ACL allows it, then checks container and file permission. Deletion has a special path where `!d` can be overridden for a file owner. If metadata is missing, it returns `ENOENT`; if the directory exists but permission fails, it returns `EACCES`.

`acc_access()` uses similar metadata discovery but computes boolean capabilities for read, write/create, execute/browse, and delete, merging secondary groups when configured and applying ACL mutable/delete/write-once semantics.

## State and Persistence Behavior

The file does not modify namespace metadata. It reads file/container attributes, ownership, mode bits, secondary-group mappings, public-access config, and static cached `eosnobody` uid. It increments `MgmStats` counters for identity mapping, access, and redirect decisions. Permission decisions are transient, but they are consumed by mutating operations throughout OFS.

## Dependencies and Integration Points

Dependencies include `Mapping::IdMap`, `Acl`, `AccessChecker`, `eos::Prefetcher`, `eosView`, namespace metadata locks, `XrdMgmOfsSecurity.hh` macros, token-scope/access-mode macros, public access mapping, and XRootD `XrdAccPrivs`. It is a core integration point for mkdir, symlink, find, FUSE/FSctl paths, token issuance, and any command that calls `_access()`.

## Risks and Edge Cases

- File permission checks use parent directory ACLs plus file attributes. Ordering around `sys.owner.auth` is security-sensitive and intentionally mirrors open/mkdir behavior.
- `_access` allows root all access and daemon read-only access; regression here would affect internal services.
- `F_OK` succeeds if the directory metadata object exists, even when `permok` is false.
- Public access restrictions are checked only in some terminal paths; callers relying on `_access` need to understand when anonymous depth limits apply.
- `GetXrdAccPrivs()` currently returns all privileges after basic checks, so it should not be mistaken for a fine-grained authorization decision.

## Test Signals

Tests should cover file versus directory checks, missing child parent checks, ACL read/write/write-once/browse/delete/chmod/token combinations, `sys.owner.auth` keyed and sticky cases, file-owner delete despite `!d`, root and daemon behavior, anonymous public-depth denial, `eosnobody` squashfs allow/deny, secondary groups, token identity, and OC permission string output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Access.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Attr.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Attr.inc

## Purpose

`Attr.inc` implements EOS namespace extended-attribute listing, reading, setting, removing, space-attribute merging, and common attribute helper templates. It is the backing implementation for both command-level attribute operations and the XRootD FAttr adapter.

## Important APIs, Types, and Functions

- `attr_ls()` / `_attr_ls()` list attributes for files or directories and hide `eos::kAttrObfuscateKey`.
- `attr_get()` / `_attr_get()` fetch one attribute from path, file metadata, container metadata, or `FileOrContainerMD`, with optional base64 output encoding.
- `attr_set()` / `_attr_set(path,...)` validate input, decode base64 values, validate/convert ACL values, lock metadata for writes, delegate to `_attr_set(item,...)`, and audit changes.
- `_attr_set(FileOrContainerMD&,...)` enforces owner/ACL xattr update rules, exclusive set, application-lock conflicts, ctime updates, store updates, and FUSE refresh registration.
- `attr_rem()` / `_attr_rem()` remove attributes with owner/ACL checks, store updates, FUSE refresh, and audit.
- `mergeSpaceAttributes()`, `listAttributes(...)`, and `getAttribute<T>()` merge configured space attributes into namespace attributes.

## Control Flow

High-level methods map identity with operation-specific access types, perform namespace mapping and external authorization, then call low-level functions. Listing and getting prefetch the item and lock only around metadata reads. Getting always tries to decode base64-stored values and can re-encode when `eos.attr.val.encoding=base64` is present.

Setting validates missing key/value, ignores forced attributes on version directories, decodes `base64:` inputs, validates ACL syntax and numeric id conversion, prefetches the target, captures previous value for audit, write-locks the item, and calls the item-level setter. The item-level setter builds an ACL from existing attrs, rejects unauthorized updates, handles exclusive collision and foreign app-lock collision, updates file/container metadata store, and schedules FUSE refresh after lock release through `FusexCastBatch`.

Removal similarly prefetches, write-locks file or container, enforces owner/ACL permissions, removes the key, updates the backing store, releases the lock before refresh, and audits old/new values.

Space attribute merging reads `mSpaceAttributes` for the selected `sys.forced.space` or `default`, applies special ACL merge operators (`>`, `<`, `|`), optional prefixing, and overwrite/default rules.

## State and Persistence Behavior

Set/remove operations persist changes through `eosView->updateFileStore()` or `updateContainerStore()`, update ctime except for temporary etag keys, emit audit records for xattr and ACL changes, and notify FUSE clients. Space attributes are read from `gOFS->mSpaceAttributes` under `mSpaceAttributesMutex` and are overlaid on reads; they are not written into the target metadata unless explicitly set elsewhere.

## Dependencies and Integration Points

The file depends on `Acl`, `XattrLock`, `SymKey` base64 helpers, `Prefetcher`, metadata locks, `eos::listAttributes`/`eos::getAttribute`, audit helpers, FUSE xcast, MGM stats, token authorization, and external authorization macros. It is used by access checks, find filters, mkdir/chown permission evaluation, FAttr, and command interfaces that expose ACL/attribute management.

## Risks and Edge Cases

- Attribute updates are security-sensitive because ACLs, forced placement, ownership, obfuscation, and app locks are all xattrs.
- Space attribute merging can make reads return values not physically present on the metadata object, so callers must distinguish effective from stored attributes.
- The obfuscate key is intentionally hidden on list/get; tests must prevent leakage.
- ACL value conversion changes user/group names to numeric form; failures must be surfaced as `EINVAL`.
- Removal permission differs for files and containers and token identities are denied on container removal.
- Audit and FUSE refresh happen after metadata updates; failures there are not represented as operation failures in this file.

## Test Signals

Tests should cover list/get/set/remove on files and directories, hidden obfuscation key, base64 input/output, invalid ACL syntax, ACL id conversion failure, owner versus ACL-authorized xattr updates, exclusive set collisions, foreign app-lock `EBUSY`, temp etag ctime exception, audit records for ACL/xattr changes, FUSE refresh emission, version-directory forced-attribute ignore, and space attribute merge operators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Attr.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Auth.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Auth.inc

## Purpose

`Auth.inc` implements the MGM authentication-plugin RPC bridge. It runs a ZeroMQ ROUTER/DEALER frontend/backend proxy, worker threads that receive protobuf requests from EOS auth plugins, validates HMACs, dispatches requests into normal `gOFS` XRootD/OFS methods, tracks open directory and file objects by UUID, serializes responses, and collects per-operation latency statistics.

## Important APIs, Types, and Functions

- `StartAuthWorkerThread()` is a pthread-style trampoline into `AuthWorkerThread()`.
- `AuthMasterThread()` binds the frontend TCP socket and inproc backend, then runs `zmq::proxy`.
- `ConnectToBackend()` creates/recreates a `ZMQ_REP` worker socket and retries connection to `inproc://authbackend`.
- `AuthWorkerThread()` is the main request loop and dispatcher for stat, fsctl, chmod, checksum, exists, mkdir, remdir, rem, rename, prepare, truncate, directory operations, and file open/stat/name/read/write/close.
- `ValidAuthRequest()` verifies request integrity by clearing the hmac field, serializing the protobuf, computing `SymKey::HmacSha256`, base64 encoding, and comparing with `CRYPTO_memcmp`.
- `AuthCollectInfo()`, `AuthComputeStats()`, `AuthUpdateAggregate()`, and `AuthPrintStatistics()` maintain and log latency aggregates.

## Control Flow

The master binds a client-facing ROUTER socket and a DEALER backend and proxies messages until ZeroMQ termination. Each worker connects to the backend and loops receiving a protobuf request. After parsing, it rejects invalid HMACs or switches on `RequestProto_OperationType`.

Stateless operations reconstruct `XrdOucErrInfo` and `XrdSecEntity` from protobuf helpers, call the matching `gOFS` method, and copy any binary result into the response. Stateful directory and file operations use UUID maps guarded by `mMutexDirs` or `mMutexFiles`. Open creates `XrdMgmOfsDirectory` or `XrdMgmOfsFile`, stores it on success, and deletes it on failure. Subsequent read/stat/name/write/close operations find the object, call the corresponding method, and close erases and deletes it.

After each request, the worker deletes reconstructed security entities, converts the error object if present, serializes `ResponseProto`, sends it nonblocking with retries, reconnects the socket on send failure, and records latency.

## State and Persistence Behavior

The bridge persists no namespace state directly but invokes operations that do. It owns runtime socket state, file/directory object maps, auth sample/aggregate maps, mutexes, and per-request reconstructed objects. File and directory handles can hold MGM-side state across multiple auth-plugin RPCs, so map cleanup on close and failure is critical. HMAC verification depends on the shared symmetric key store.

## Dependencies and Integration Points

Dependencies include ZeroMQ, protobuf auth messages, `auth_plugin/ProtoUtils.hh`, OpenSSL `CRYPTO_memcmp`, `XrdMgmOfsFile`, `XrdMgmOfsDirectory`, XRootD error/security types, and most `gOFS` command methods. It integrates external auth-plugin clients with the normal in-process MGM OFS implementation.

## Risks and Edge Cases

- HMAC validation must remain constant-time and must restore no trusted state from unauthenticated input.
- The large switch manually manages memory for reconstructed XRootD objects; missed deletes or double deletes are possible around FSctl/prepare/client handling.
- UUID map entries can leak if clients open and never close or if close requests are lost.
- `FILEWRITE` delegates to `XrdMgmOfsFile::write()`, which is unsupported for normal MGM files; clients must expect errors.
- Socket reconnect after failed send can drop an already executed request response, making idempotency of callers important.
- Directory `nextEntry()` uses `SFS_ERROR` for end-of-stream, which may be indistinguishable from some failures unless callers inspect context.

## Test Signals

Tests should cover HMAC mismatch rejection, each operation type serialization/deserialization, file and directory UUID lifecycle, duplicate open idempotence, missing UUID errors, send retry/reconnect behavior, ETERM shutdown, binary stat/read response sizes, memory cleanup for FSctl/prepare/client objects, and latency aggregation output after minute boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Auth.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Chksum.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Chksum.inc

## Purpose

`Chksum.inc` implements XRootD checksum queries for EOS files. It supports the XRootD checksum size probe and checksum get/calc operations, returning the checksum type and hex digest derived from EOS file layout metadata.

## Important APIs, Types, and Functions

- `XrdMgmOfs::chksum(csFunc Func, const char* csName, const char* inpath, XrdOucErrInfo&, const XrdSecEntity*, const char* ininfo)` is the only exported function.
- `csSize` returns a fixed maximum checksum length of 20 bytes.
- `csGet` and `csCalc` both return the existing namespace checksum rather than causing data-plane recalculation.
- `LayoutId::GetChecksumStringReal()`, `GetChecksumLen()`, and `IFileMD::getChecksum()` define the returned checksum type and digest bytes.

## Control Flow

The function handles `csSize` before path mapping and authorization. Other operations perform namespace mapping, identity mapping with `AOP_Stat`, external authorization, access-mode/stall/redirect checks, and file metadata prefetch. It then takes a read lock on `eosViewRWMutex`, fetches the file metadata, detects missing replicas, and may redirect `ENONET` to a remote master if this MGM is not master and the remote master is alive.

For valid `csCalc` or `csGet`, it formats a response as `!<type> <hex-digest>` using the file's layout id and stored checksum bytes, sets that in `XrdOucErrInfo`, and returns `SFS_OK`.

## State and Persistence Behavior

This is read-only against namespace metadata. It increments `IdMap`, `Checksum`, and possible `RedirectENONET` stats. It does not recalculate or persist checksum values, so returned data reflects metadata already stored with the file.

## Dependencies and Integration Points

Dependencies include identity mapping, external authorization, namespace prefetch, `eosView`, master/remote-master routing, `LayoutId`, and XRootD checksum function enums. It integrates with clients that call XRootD checksum APIs and with master/slave redirect behavior for replica-less metadata.

## Risks and Edge Cases

- `csSize` returns 20 unconditionally; clients expecting name-specific support may not get strict validation.
- Missing path returns `EINVAL`; missing file returns `ENOENT` and may trigger stall/redirect macros.
- Files with no committed replicas can redirect to a remote master; remote master id parsing failure is surfaced as an EOS error.
- `csCalc` does not calculate from bytes; it returns stored metadata checksum.
- Buffer formatting relies on fixed `MAXPATHLEN + 8` storage and checksum lengths from layout metadata.

## Test Signals

Tests should cover `csSize`, `csGet`, `csCalc`, invalid function, missing path, missing file, zero-location redirect on slave, checksum type/length per layout, empty checksum formatting, authorization denial, and stats counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Chksum.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Chmod.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Chmod.inc

## Purpose

`Chmod.inc` implements mode changes for EOS directories and files. It exposes the XRootD `chmod` wrapper and the internal `_chmod` mutation that applies ACL/owner/admin rules, updates metadata stores, emits audit records, and broadcasts FUSE refreshes.

## Important APIs, Types, and Functions

- `XrdMgmOfs::chmod()` maps identity with `AOP_Chmod`, performs namespace mapping, external authorization, global access checks, and delegates to `_chmod`.
- `XrdMgmOfs::_chmod()` performs the actual metadata mutation for containers or files.
- For containers, it masks requested mode, strips regular-file and setuid bits, sets `S_IFDIR`, updates ctime and container store.
- For files, it stores only the nine rwx bits in file flags and updates the file store.
- Audit helpers build before/after `eos::audit::Stat` objects for `CHMOD`.

## Control Flow

The low-level function prefetches possible container and file metadata, takes a write lock on `eosViewRWMutex`, and tries directory lookup first, then file lookup. For either object, it resolves the URI to the parent container, constructs an ACL for the parent path, and checks mutability plus ownership/admin/ACL `CanChmod()`.

On success, it updates the parent store, mutates the target directory or file, captures identifiers, releases the namespace lock, and sends FUSE refreshes for the parent, target directory, or target file. It returns `SFS_OK` for either successful directory or file update; otherwise it emits `Emsg`.

## State and Persistence Behavior

The operation persists mode changes through `updateContainerStore()` or `updateFileStore()`, updates ctime for directories, updates parent container store, emits audit records when enabled and allowed, and sends FUSE refresh notifications. File mode is represented in file flags, while directory mode is represented as mode bits with `S_IFDIR`.

## Dependencies and Integration Points

Dependencies include `Acl`, `Prefetcher`, `eosViewRWMutex`, metadata services, audit helpers, FUSE xcast, external authorization, identity mapping, and global access-mode/stall/redirect macros. It is called both directly via XRootD and indirectly through auth-plugin/FSctl command dispatch.

## Risks and Edge Cases

- Permission depends on parent ACL, not only target ownership; this is important for file chmod semantics.
- Immutable ACL state blocks non-root changes.
- File chmod stores only nine permission bits, while directory chmod strips unsupported bits; callers expecting full POSIX mode preservation can be surprised.
- The function updates parent container store before target updates; partial failure paths need careful auditing in implementation changes.
- Audit construction occurs while metadata is live; before/after capture must remain aligned with persisted mutation.

## Test Signals

Tests should cover owner, root, admin uid/gid, ACL `CanChmod`, ACL `CanNotChmod`, immutable ACL, directory mode masking, file flag masking, nonexistent path, FUSE refresh targets, audit before/after records, and direct plus auth-plugin/FSctl invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Chmod.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Chown.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Chown.inc

## Purpose

`Chown.inc` implements internal owner/group changes for EOS directories and files. XRootD OFS has no public chown entry here, so `_chown` is used by EOS command paths and supports no-dereference behavior, ACL/admin permission checks, quota adjustment for files, metadata persistence, audit, and FUSE refresh.

## Important APIs, Types, and Functions

- `XrdMgmOfs::_chown(path, uid, gid, error, vid, ininfo, nodereference)` is the only function.
- Directory path: fetch container, list effective attrs, construct ACL, enforce root/admin/admin-group/`CanChown()` plus mutability, update `CUid`/`CGid`.
- File path: fetch parent, quota node, parent attrs, ACL, then file metadata, subtract/add quota accounting around owner/group changes.
- `0xffffffff` uid or gid means "do not change this field".
- Audit helpers build before/after `CHOWN` stats.

## Control Flow

The function takes a namespace write lock and first attempts to chown the target as a container. It computes effective attributes, removes `user.acl` from permission evaluation if the requested uid differs from the caller uid, and checks ACL/admin rules. On success it updates owner/group, ctime, store, releases lock, sends FUSE refresh, and audits.

If no container is found, it treats the target as a file. It resolves and optionally de-references the parent, gets quota node, evaluates parent ACL, fetches the file, removes the file from quota accounting, applies uid/gid changes according to privilege rules, re-adds the file to quota, updates ctime/store, releases lock, refreshes FUSE, and audits.

## State and Persistence Behavior

The operation persists owner/group and ctime changes to container or file stores. File chown also mutates quota accounting by removing and re-adding the file around metadata changes. It emits audit records and FUSE refreshes after successful mutations.

## Dependencies and Integration Points

Dependencies include `Acl`, `_attr_ls`, `listAttributes`, namespace locks, quota nodes, metadata stores, audit helpers, FUSE xcast, and identity roles (`ADM_UID`, `ADM_GID`, `sudoer`). It is integrated through FSctl command dispatch and internal EOS management paths.

## Risks and Edge Cases

- Directory and file permission rules differ: file ownership changes require root/admin/sudo/ACL, but group changes are more restricted.
- Quota accounting must be balanced even if future edits introduce exceptions between remove and add.
- `nodereference` changes lookup behavior for symlink-like paths; tests need both modes.
- Removing `user.acl` from permission evaluation when changing to another uid prevents self-granted ACL escalation.
- The function ends timing with `"Chmod"` rather than `"Chown"`, a diagnostic inconsistency.

## Test Signals

Tests should cover directory and file chown, root/admin/sudo/ACL permission cases, immutable denial, user ACL self-escalation prevention, `0xffffffff` skip semantics, gid change privilege limits, quota accounting updates, no-dereference lookup, audit records, and FUSE refresh identifiers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Chown.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Coverage.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Coverage.inc

## Purpose

`Coverage.inc` implements a signal-callable coverage flush hook for MGM/OFS builds. In coverage builds it dumps gcov data for the main binary and asks loaded plugins to dump their own coverage; in non-coverage builds it logs that coverage support is absent.

## Important APIs, Types, and Functions

- `xrdmgmofs_coverage(int sig)` is the exported coverage handler.
- Under `COVERAGE_BUILD`, it calls `__gcov_dump()`.
- It obtains loaded dynamic libraries from `eos::common::PluginManager::GetInstance().GetDynamicLibMap()`.
- For each dynamic library, it looks up `plugin_coverage` and calls it when present.

## Control Flow

The handler logs that coverage data is being printed, flushes gcov data for the main process, iterates the plugin manager's dynamic library map, and invokes optional plugin coverage functions. Without `COVERAGE_BUILD`, it only logs a notice.

## State and Persistence Behavior

The function writes coverage data through gcov runtime side effects and plugin-provided hooks. It does not mutate namespace state. Plugin coverage functions may write their own coverage files.

## Dependencies and Integration Points

Dependencies include gcov runtime symbols, EOS logging, `PluginManager`, and dynamic-library symbol lookup. It integrates with signal handlers or manual hooks used by coverage test runs.

## Risks and Edge Cases

- Running complex C++ code in a signal handler can be unsafe if actually called from asynchronous signal context.
- Plugin coverage functions are optional and unchecked beyond null testing; plugin failures are not handled.
- `__gcov_dump()` availability depends on compiler/runtime and `COVERAGE_BUILD`.

## Test Signals

Coverage builds should verify gcov files update for the MGM and plugins, missing plugin symbols are skipped, and non-coverage builds log the expected message without link errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Coverage.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/DeleteExternal.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/DeleteExternal.inc

## Purpose

`DeleteExternal.inc` sends an authenticated drop request from the MGM to an FST so the data server deletes a physical replica or stripe. It builds a short-lived capability containing delete access, manager id, fsid, and fid, then sends an HTTP-style query to the FST.

## Important APIs, Types, and Functions

- `XrdMgmOfs::DeleteExternal(fsid, fid, is_fsck)` is the only function.
- It looks up the filesystem in `FsView::gFsView.mIdView` under `ViewMutex`.
- It constructs capability parameters `mgm.access=delete`, `mgm.manager`, `mgm.fsid`, and `mgm.fids`.
- `SymKey::CreateCapability()` encrypts/signs capability data using the current key and `mCapabilityValidity`.
- `SendQuery(fst_host, fst_port, qreq, qresp)` sends `/?fst.pcmd=drop` plus optional `fst.drop.type=fsck`.

## Control Flow

The function reads the filesystem object, extracts queue, host, and port, and returns false if the fsid is unknown. It builds an `XrdOucEnv`, creates an output capability environment, appends it to the drop query, sends the query to the FST, logs send failure, deletes the allocated capability env, and returns success/failure.

## State and Persistence Behavior

This file does not update namespace metadata. It causes external state mutation on an FST when the query is accepted. It reads filesystem registry state and current symmetric key material.

## Dependencies and Integration Points

Dependencies include `FsView`, filesystem locator/core params, `FileId::Fid2Hex`, `SymKey` capability creation, key store, `SendQuery`, and MGM manager identity. It is used by `DropReplica()` and likely other replica-removal paths.

## Risks and Edge Cases

- Capability generation failure prevents physical deletion.
- Unknown fsid returns false without namespace cleanup.
- `SendQuery` return convention is inverted in this code path: nonzero indicates failure.
- FST-side acceptance is not strongly confirmed beyond query send result.
- Capability validity and key rotation affect whether FSTs accept the deletion.

## Test Signals

Tests should cover valid and missing fsid, generated query parameters, fsck drop type, capability creation failure, send failure, port extraction, key-store behavior, and integration with `DropReplica()` when FST deletion fails but namespace drop proceeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/DeleteExternal.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/DropReplica.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/DropReplica.inc

## Purpose

`DropReplica.inc` coordinates replica removal from an FST and from the EOS namespace. It is a small helper used when a specific file id and filesystem id must be dropped, such as fsck-driven cleanup.

## Important APIs, Types, and Functions

- `XrdMgmOfs::DropReplica(fid, fsid) const` is the only function.
- It treats `fsid == 0` as a no-op success.
- It calls `gOFS->DeleteExternal(fsid, fid, true)` to request physical deletion.
- It calls `gOFS->_dropstripe("", fid, err, Root(), fsid, true)` to remove the replica from namespace metadata.

## Control Flow

The function logs the target file/fsid, sends the FST unlink/drop request, records a false return if that send fails, then uses root virtual identity to drop the stripe from the namespace by file id. Namespace drop errors are logged but do not currently flip the returned boolean; the return value primarily reflects FST message success.

## State and Persistence Behavior

The helper can trigger both external FST deletion and namespace metadata mutation through `_dropstripe`. It does not itself lock or persist state; it delegates both state-changing operations.

## Dependencies and Integration Points

Dependencies include `DeleteExternal`, `_dropstripe`, `VirtualIdentity::Root`, and XRootD error objects. It integrates fsck/repair-like flows with data-server cleanup and namespace replica accounting.

## Risks and Edge Cases

- Return value does not reflect namespace drop failure, only FST deletion failure.
- If FST deletion succeeds and namespace drop fails, data and namespace can remain inconsistent.
- If FST deletion fails and namespace drop succeeds, metadata may forget a replica that still exists physically.
- Empty path plus root identity assumes `_dropstripe` can authorize by fid only.

## Test Signals

Tests should cover fsid zero no-op, FST deletion failure, namespace drop failure, combined success, root identity use, and consistency checks after partial failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/DropReplica.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ErrorLogListener.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/ErrorLogListener.inc

## Purpose

`ErrorLogListener.inc` implements a background thread that listens to QDB error-report messages and writes them to the MGM error log, either as plain text or through zstd logging. It also validates or creates the plain log file before listening.

## Important APIs, Types, and Functions

- Anonymous helper `CheckFileExistanceAndPerm(log_file, err)` validates existence, ownership, and user read/write permissions or creates the file with `0600`.
- `XrdMgmOfs::ErrorLogListenerThread(ThreadAssistant&)` starts the listener thread, chooses plain or zstd logging, opens/binds the log file if needed, creates `eos::mq::QdbListener`, and writes fetched messages.
- Static channel is `/eos/*/errorreport`; plain log path is `/var/log/eos/mgm/error.log`; zstd tag is `error`.

## Control Flow

At startup the thread checks whether zstd logging is enabled. Plain mode validates the file, opens it append/update, binds an `XrdSysLogger`, disables XRootD rotation, and logs startup. Zstd mode logs the selected tag. It then fetches messages from QDB until termination is requested. Each message is written via `logging.WriteZstd()` or `fprintf(file, "%s\n", out.c_str())`. On exit it flushes and closes the file.

## State and Persistence Behavior

The thread persists received error reports to `/var/log/eos/mgm/error.log` or zstd log segments managed by the logging subsystem. It does not alter namespace or configuration state. The listener consumes QDB pub/sub style events.

## Dependencies and Integration Points

Dependencies include `ThreadAssistant`, EOS logging singleton, `eos::mq::QdbListener`, QDB contact details, `XrdSysLogger`, POSIX file APIs, and MGM lifecycle management. It integrates distributed error-report messages into local MGM diagnostics.

## Risks and Edge Cases

- The permission check accepts files with at least one of user read/write bits rather than explicitly requiring both bits, despite the error wording.
- Wrong file owner or inaccessible path disables the listener thread entirely.
- Plain logging uses `fprintf` without explicit flush per message; data may be buffered until shutdown or stdio flush.
- Zstd mode depends on global logging configuration and paths outside this file.

## Test Signals

Tests should cover missing log creation, wrong owner, wrong permissions, open failure, plain versus zstd mode, QDB fetch/write loop, termination flush/close, and malformed/large message handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/ErrorLogListener.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Exists.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Exists.inc

## Purpose

`Exists.inc` implements XRootD/OFS existence checks for EOS paths. It distinguishes directories, files, and missing paths, supports high-level authorization and redirection behavior, and provides lower-level overloads that return metadata handles for internal callers.

## Important APIs, Types, and Functions

- `XrdMgmOfs::exists()` is the public XRootD wrapper with identity mapping, namespace mapping, external authorization, and access-mode/stall/redirect guards.
- `_exists(path, file_exists, error, client, ininfo)` is a lower-level overload that may still issue ENOENT redirects and therefore is documented as not for internal use.
- `_exists(path, file_exists, error, vid, cmd, fmd, ininfo)` returns shared pointers to found container or file metadata without ENOENT redirect handling.
- `_exists(fileName, exists_flag, out_error, vid, opaque, take_lock)` is a wrapper that creates metadata out-params.

## Control Flow

The public wrapper maps the path and identity, checks external authorization for `AOP_Stat`, applies access gates, and calls `_exists`. The client-based lower-level overload first rejects null/empty paths, then prefetches and checks for a container, then prefetches and checks for a file. If missing, it looks up the parent directory, loads parent attributes via `_attr_ls`, and if `sys.redirect.enoent` exists, parses optional host:port and returns `SFS_REDIRECT`.

The identity-based overload uses the same directory-first, file-second lookup but returns only `SFS_OK` and an enum flag with optional metadata pointers. It does not emit ENOENT redirects.

## State and Persistence Behavior

This file is read-only. It updates `MgmStats` for existence checks and ENOENT redirects. It fills caller-provided shared pointers to live metadata objects but does not mutate them.

## Dependencies and Integration Points

Dependencies include identity mapping, external authorization, namespace prefetch, `eosView`, `_attr_ls`, `XrdSfsFileExistence`, stall/redirect macros, and MGM stats. It is used by mkdir, symlink, FSctl locate, find fallback, auth-plugin exists requests, and many internal checks that need file-versus-directory classification.

## Risks and Edge Cases

- The client-based overload can redirect on missing paths via parent `sys.redirect.enoent`; internal callers should use the `VirtualIdentity` overload when redirects are inappropriate.
- Directory lookup wins over file lookup if both somehow exist for a path.
- Null/empty path returns `SFS_ERROR` without setting detailed `XrdOucErrInfo`.
- Parent attribute lookup during ENOENT handling can itself fail silently and skip redirect.

## Test Signals

Tests should cover existing directory, existing file, missing child with and without parent, ENOENT redirect host/port parsing, empty path, auth denial, no-symlink lookup behavior from `false` flags, metadata out-params, and callers that must avoid redirects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Exists.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/FAttr.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/FAttr.inc

## Purpose

`FAttr.inc` adapts EOS extended-attribute operations to XRootD's `XrdSfsFACtl` filesystem-attribute API. It reports support limits, maps requests to EOS attribute get/list/set/delete helpers, serializes names and values into XRootD-managed buffers, and returns per-attribute status codes.

## Important APIs, Types, and Functions

- Anonymous `GetFABuff(XrdSfsFACtl&, int sz)` allocates an `XrdSfsFABuff`, prepends it to `faCtl.fabP`, and reserves `sz` bytes.
- `XrdMgmOfs::FAttr(XrdSfsFACtl* faReq, XrdOucErrInfo&, const XrdSecEntity*)` handles support info and `faGet`, `faLst`, `faSet`, and `faDel`.
- Request-to-access mapping uses `AOP_Read` for get/list and `AOP_Update` for set/delete.
- It delegates to `_attr_get`, `_attr_ls`, `_attr_set`, and `_attr_rem`.

## Control Flow

If `faReq` is null, the function returns support limits (`usxMaxNsz`, `usxMaxVsz`) through the error environment or `ENOTSUP` if no env exists. Otherwise it derives path and CGI info from `faReq`, maps identity, applies namespace mapping and external authorization, and switches on request type.

For get, it strips any configured name prefix from requested attr names, fetches values one by one, records per-entry `faRC`, allocates one contiguous values buffer, and points `XrdSfsFAInfo::Value` into it. For list, it loads all attrs, allocates one buffer for null-terminated keys, optionally allocates another buffer for values when `retval` is set, and fills `faReq->info`. For set/delete, it loops over each attr, strips prefix, delegates to low-level mutation, and stores per-entry errno in `faRC`.

## State and Persistence Behavior

The adapter itself owns only response buffers allocated with `malloc` or `new`; XRootD owns eventual cleanup according to `XrdSfsFACtl` conventions. Set/delete persist changes through `Attr.inc` helpers, including audit and FUSE refresh side effects. Get/list are read-only.

## Dependencies and Integration Points

Dependencies include XRootD `XrdSfsFACtl`, EOS identity mapping, namespace mapping macros, external authorization, `Attr.inc` low-level helpers, and XRootD attr-size constants. It integrates modern xattr clients with EOS's older attr implementation.

## Risks and Edge Cases

- `pfx_len` is computed with `sizeof(faReq->nPfx)`, which is the fixed array size, not the runtime prefix string length; this needs tests because prefix stripping can be wrong if `nPfx` is not sized as intended.
- Value serialization for get/list does not null-terminate values; consumers must use `VLen`.
- Allocation failures must leave a consistent `faReq` state and return `SFS_ERROR`.
- List with values creates two buffers and overwrites `ptr` for the second; buffer ordering matters to cleanup.
- Delegated attr operations may return `SFS_ERROR` while overall set/delete loops continue and report per-entry `faRC`.

## Test Signals

Tests should cover support-info query, missing error env, get/list/set/delete with multiple attrs, prefix stripping, list with and without `retval`, binary/non-null-terminated values, allocation failure injection, per-entry status, hidden obfuscation key inheritance from `_attr_ls`, and security checks for update versus read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/FAttr.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Find.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Find.inc

## Purpose

`Find.inc` implements recursive namespace search and clone-marker management for the MGM. It can traverse directories with permission checks, match attributes and file names, enforce non-admin result limits, produce maps of found directories/files, and handle special `sys.clone` operations for listing, marking, creating, and cleaning clone state.

## Important APIs, Types, and Functions

- `_cloneFoundItem` records found container/file ids and traversal depth for delayed clone output.
- `_clone_escape()` curl-escapes names containing spaces or percent signs.
- `_cloneResp()` converts collected clone ids back into path output or compact JSON records, including attributes and stat tuples.
- `_cloneMD()` finds or creates `/proc/.../clone/<id>` clone anchor directories.
- `_clone()` recursively marks, lists, or cleans clone metadata according to flags `>`, `=`, `-`, `+`, `?`, and `!`.
- `XrdMgmOfs::_find()` is the main recursive find implementation.

## Control Flow

For `key == "sys.clone"`, `_find` parses the clone flag and id, rejects limited users, loads the root container, calls `_clone`, and emits clone output through `_cloneResp`. Clone recursion can set or clear container/file clone ids, create clone anchor directories, remove cloned files/containers on cleanup, and collect output outside the large lock.

Normal find initializes a breadth/depth list of directories, obtains per-user directory/file limits from `Access::GetFindLimits()`, and marks non-root/non-admin/non-sudo users as limited. It then loops by depth until no more directories, max depth, limit, or termination. For each directory it optionally sleeps, prefetches children, checks POSIX/ACL read+browse permission, checks public access, skips version directories or ctime-too-new entries, and then scans child directories and files.

Directory matches can be by any attr matching wildcard key, exact key with `*` value, exact key/value, or no key. File matches can include symlink display, file-name wildcard matching, ctime filtering, and result limits. If no file results are found, it falls back to checking whether the original path was itself a file. It always includes the queried directory when accessible. If `out_error.getErrInfo() == E2BIG`, limited results become an error rather than a warning.

## State and Persistence Behavior

Normal find is read-only except for stats and optional access helper side effects. Clone mode mutates namespace metadata: clone ids and clone FST markers on containers/files, creation/removal of clone directories, removal of cloned files via `_rem`, metadata store updates through directory/file services, and FUSE refresh/deletion notifications. Clone cleanup can remove stored clone artifacts under the MGM proc path.

## Dependencies and Integration Points

Dependencies include namespace iterators, `Prefetcher`, `Acl`/`_access`, `_attr_ls`, `_attr_get`, `Access::GetFindLimits`, public access rules, recycle-bin helpers, JSONCPP, `FileId`, file/directory services, FUSE xcast, `_rem`, and `ThreadAssistant`. It integrates with shell/proc commands that need recursive listings and backup/clone workflows.

## Risks and Edge Cases

- Clone mode is highly stateful and bypasses normal user limits; only privileged identities should be able to use it.
- `_clone` deliberately releases and reacquires `eosViewRWMutex` around prefetch in some paths; lock ordering regressions can deadlock or race.
- Hard-link handling in `_cloneResp` suppresses zombie targets and rewrites metadata to target files; restore tooling depends on emitted `H`/`L` fields.
- Result limiting can truncate silently with warnings unless fail-if-limited mode is requested through `E2BIG`.
- Permission checks combine direct container access and `_access`; differences between those paths affect find visibility.
- Large trees can consume substantial memory in `found_dirs` and `found`.

## Test Signals

Tests should cover recursive traversal, max depth, no-files mode, attr wildcard and exact matching, file wildcard matching, symlink display, version-dir skip, ctime filters, public access denial, ACL fallback, per-user limits with warning and `E2BIG` failure, assistant termination, original-path-is-file fallback, JSON clone output, clone mark/list/cleanup flags, hard-link clone output, and FUSE/deletion side effects from clone cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Find.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/FsConfigListener.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/FsConfigListener.inc

## Purpose

`FsConfigListener.inc` implements MGM background listeners for global configuration changes and filesystem status/geotag changes. It applies remote-master configuration on slaves, updates filesystem view structures when geotags change, and initiates drain status transitions when a master observes filesystem operational errors.

## Important APIs, Types, and Functions

- `processIncomingMgmConfigurationChange(key)` reads a global config value and either enforces access/iostat config or applies namespaced map/fs/quota/vid/policy config through the config engine and FsView.
- `ProcessGeotagChange(queue)` compares a filesystem's previous geotag in tree views with the new stat geotag and updates node/group/space `GeoTree` memberships.
- `FileSystemMonitorThread(ThreadAssistant&)` subscribes to `stat.errc`, `stat.geotag`, `configstatus`, and `stat.boot`, updates scheduler disk statuses, and marks disks drain on master-side ops errors.
- `FsConfigListener(ThreadAssistant&)` consumes global config change events from `MgmConfigQueue`; slaves apply modifications and deletions.

## Control Flow

Configuration changes without explicit namespaces are treated as access or iostat configuration and applied globally. Namespaced changes are set in `mConfigEngine`; `fs:` changes additionally take a write lock and reapply filesystem config after unregistering first, `quota:` changes are deferred to master reload, and other namespaced keys call `ApplyEachConfig`.

Geotag processing reads the filesystem under `FsView::ViewMutex`, gets fsid and new geotag, compares with the current tree membership, then upgrades to write locking and erases/reinserts the fsid in node, group, and space geo trees when changed.

The filesystem monitor registers interest filters, then processes events until termination. On master nodes, non-geotag events read fs id/status/error/space, update scheduler statuses, and if an operational error is present with suitable config/boot state, mark the filesystem drain and update scheduler state. The global config listener only applies events on slaves.

## State and Persistence Behavior

This file mutates in-memory and configured MGM state: config-engine values, FsView filesystem configuration, geo tree memberships, filesystem config status, scheduler disk status, and deletion of config keys. It intentionally skips quota updates on slaves because they could disturb namespace state and should reload on master transition.

## Dependencies and Integration Points

Dependencies include `FsView`, `FileSystem`, `FsNode`, `FsGroup`, `FsSpace`, `GeoTree`, config engine, access config, IO stats, messaging realm listeners, global config listener, filesystem scheduler, master/slave state, and `ThreadAssistant`. It is an integration layer between QDB/MQ events and the MGM's runtime scheduling/configuration views.

## Risks and Edge Cases

- Lock upgrade in geotag handling releases read lock before acquiring write lock; filesystem data can change between snapshot and update.
- Slave fs config applies unregister-first behavior to avoid stale state, but incorrect ordering can briefly remove fs entries from views.
- Quota changes are skipped on slaves; tests must ensure eventual master reload covers them.
- Drain triggering depends on combined `errc`, config status, and boot status; wrong enum parsing can over-drain or under-drain disks.
- Scheduler update failures are logged but do not roll back FsView state.

## Test Signals

Tests should cover access/iostat config changes, map/fs/vid/policy key application, config deletion, slave-only global application, quota skip, geotag no-op and changed updates across node/group/space trees, filesystem missing/initial-state skips, scheduler disk status updates, ops-error drain transition, and thread termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/FsConfigListener.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Fsctl.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Fsctl.inc

## Purpose

`Fsctl.inc` implements XRootD filesystem-control operations for EOS. It handles locate and statfs-like requests, the richer `FSctl` plugin dispatcher used by FUSE and EOS clients, fusex protobuf injection, and a small PLUGIO dispatch path.

## Important APIs, Types, and Functions

- `XrdMgmOfs::fsctl(cmd,args,error,client)` handles older `SFS_FSCTL_LOCATE` and `SFS_FSCTL_STATLS`.
- `XrdMgmOfs::FSctl(cmd,args,error,client)` validates and copies path/opaque arguments, maps identity, handles locate, PLUGIO, plugin commands, fusex commands, and `mgm.pcmd` dispatch.
- `dispatchSFS_FSCTL_PLUGIO()` currently handles `Arg1 == "tgc"` through `mTapeGc->handleFSCTL_PLUGIO_tgc()` and rejects unknown PLUGIO commands.
- Plugin command dispatch maps `mgm.pcmd` to functions such as `Access`, `AdjustReplica`, `Checksum`, `Chmod`, `Chown`, `Commit`, `Drop`, `Event`, `Getfmd`, `GetFusex`, `IsMaster`, `Mkdir`, `Open`, `Readlink`, `Redirect`, `FuseStat`, `Statvfs`, `Symlink`, `Utimes`, and `Version`.

## Control Flow

The simple `fsctl` path masks the opcode. Locate returns this MGM's manager host or IP/port as an XRootD locate data response. Statls parses path/opaque, chooses a space from `eos.space`, `EOS_MGM_STATVFS_DEFAULT_SPACE`, root/default behavior, or quota-only settings, sums space free/capacity from `FsView` or quota stats, scales by layout size factor, and writes an `oss.*` response string.

`FSctl` copies `Arg1` and `Arg2` into fixed buffers with length checks, detects `fusex:` protobuf payloads before treating Arg2 as CGI, maps identity with `AOP_Stat`, performs namespace mapping and illegal-name checks, and allows `is_master`/`version` without the usual `BOUNCE_NOT_ALLOWED`. Locate verifies the path is an existing file and returns manager location. PLUGIO dispatch is separate. Non-plugin commands return `EOPNOTSUPP`. Plugin `fusex:` requests are tagged as app `fuse` and delegated to `Fusex`. Other plugin commands use `lookupFsctl()` and switch to the corresponding command handler.

## State and Persistence Behavior

Locate/statls are read-only. Plugin dispatch can invoke mutating commands that persist namespace state, schedule operations, update replicas, or alter metadata. The file itself updates log id and MGM stats for identity mapping. Statls reads global space views and quota state but does not persist.

## Dependencies and Integration Points

Dependencies include XRootD FSctl constants, identity mapping, namespace mapping macros, `FsView`, `Policy`, `LayoutId`, `Quota`, FUSE/fusex, tape GC, and the broad set of MGM command handlers. It is one of the central command buses for EOS clients and FUSE.

## Risks and Edge Cases

- Path and opaque buffers are fixed at 16384 bytes; longer inputs fail with `EINVAL`.
- `fusex:` detection treats Arg2 as binary protobuf and skips CGI copying; parsing errors are delegated.
- Many plugin commands are identity-mapped as `AOP_Stat` before command-specific handlers run; command handlers must enforce their own mutation authorization.
- `is_master` and `version` bypass `BOUNCE_NOT_ALLOWED` by design for discovery.
- Statls behavior changes with environment variables and may return space-wide or quota-specific values.
- Locate marks results read-only even for write-capable files.

## Test Signals

Tests should cover locate host/IP formatting, IPv4 mapped formatting, statls by space and by quota path, layout scaling, env-variable branches, long Arg1/Arg2 rejection, fusex binary dispatch, PLUGIO `tgc`, unknown PLUGIO, every `mgm.pcmd` dispatch target, unauthenticated/version discovery behavior, and command-specific authorization after FSctl dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Fsctl.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Link.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Link.inc

## Purpose

`Link.inc` implements symbolic link creation and readlink for EOS namespace entries. It provides client-facing and identity-based symlink wrappers, a low-level `_symlink` namespace mutation, and readlink helpers that fetch the stored link target from file metadata.

## Important APIs, Types, and Functions

- `symlink(source_name,target_name,error,client,infoO,infoN,overwrite)` performs identity mapping, path decoding/mapping for both source and target, external authorization, access gates, and delegates to the identity overload.
- `symlink(source_name,target_name,error,vid,infoO,infoN,overwrite)` remaps source, checks write access on the source/link path, and delegates to `_symlink`.
- `_symlink(...)` validates inputs, checks parent existence and destination existence, optionally removes existing source, creates the link with `eosView->createLink()`, updates parent mtime/store, broadcasts FUSE refresh, and audits.
- `readlink(...)` and `_readlink(...)` map identity/path, authorize read, prefetch file metadata, and return `IFileMD::getLink()`.

## Control Flow

Client-facing symlink decodes `#space#` unless `eos.encodepath` is present, maps both names through namespace mapping, authorizes create on the source path, applies write access gates, and calls the lower overload. The identity overload remaps the source path again, checks `_access(source,W_OK)`, and calls `_symlink`.

`_symlink` rejects null names and identical source/target, checks that the source parent directory exists, checks that the source link path does not exist unless overwrite is requested, optionally removes it, then write-locks the namespace, creates the link metadata, updates parent directory mtime and store, releases the lock, sends FUSE refresh, and audits `SYMLINK`.

Readlink is read-only: it authorizes `AOP_Read`, maps the path, prefetches file metadata without symlink dereference, reads the link string, and returns it.

## State and Persistence Behavior

Symlink creation persists a new link metadata entry and parent mtime updates through `eosView`, emits a parent FUSE refresh, and writes an audit record when enabled. Overwrite can remove an existing entry before creating the new link. Readlink does not mutate state.

## Dependencies and Integration Points

Dependencies include namespace mapping, external authorization, `_access`, `_exists`, `_rem`, `eosView->createLink`, namespace locks, FUSE xcast, audit helpers, and XRootD security/error types. It is reachable through direct OFS calls and FSctl command dispatch.

## Risks and Edge Cases

- Naming is easy to misread: `source_name` is the link path and `target_name` is the link target in `_symlink`.
- Overwrite removes the existing source before creating the new link; creation failure after removal can lose the old entry.
- `_symlink` checks parent existence and source existence with `_exists`, which can invoke redirect-capable behavior depending on overload used.
- Permission is checked on the source/link path with `W_OK`, not directly on the target.
- Readlink assumes the path resolves to file metadata with a link payload; non-link files need coverage.

## Test Signals

Tests should cover encoded spaces, namespace mapping for both paths, create authorization, write-access denial, missing parent, existing source with and without overwrite, identical source/target, successful link metadata and parent mtime update, audit, FUSE refresh, readlink for symlink and non-symlink, and overwrite failure recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Link.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Mkdir.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Mkdir.inc

## Purpose

`Mkdir.inc` implements directory creation for EOS, including normal and recursive `SFS_O_MKPTH` creation. It enforces ACL/POSIX/token permissions, supports `sys.owner.auth` ownership rewriting, inherits parent mode and attributes, records birth time, updates stores and mtime notifications, emits FUSE broadcasts, and audits successful mkdirs.

## Important APIs, Types, and Functions

- `XrdMgmOfs::mkdir(inpath,Mode,error,client,ininfo,outino)` is the public wrapper with identity mapping and path/access gates.
- `XrdMgmOfs::_mkdir(path,Mode,error,vid,ininfo,outino,nopermissioncheck)` performs the actual creation.
- Permission logic uses parent or nearest existing ancestor attributes, `attr::checkDirOwner()`, `Acl`, POSIX `dir->access(X_OK|W_OK)`, immutable checks, explicit ACL `!w`, write-once/write grants, token denial, and optional `nopermissioncheck`.
- Recursive creation walks upward to find the nearest existing ancestor and then creates each missing component.

## Control Flow

The public wrapper maps identity with `AOP_Mkdir`, applies namespace mapping, token scope, global access checks, and calls `_mkdir`. `_mkdir` rejects non-absolute paths, resolves the parent, loads effective parent attributes before ACL construction, applies `sys.owner.auth` ordering so keyed owner auth can rewrite `vid` before permission checks and sticky `*` can rewrite ownership after permission checks.

If `SFS_O_MKPTH` is set and the full path already exists, it returns success. If the parent is missing and recursive mode is set, it finds the closest existing ancestor, repeats permission checks there, applies sticky ownership if needed, and creates each missing subpath under a write lock, inheriting mode and attributes from the current parent, setting mtime/btime, updating stores, notifying mtime changes, releasing the lock, and broadcasting FUSE metadata/refresh messages.

For the final directory, it write-locks the namespace, creates the container, sets uid/gid, inherits parent mode without the VTX bit, sets mtime and `sys.eos.btime`, inherits parent attributes except for version directories, optionally returns the new inode, commits parent and child stores, notifies mtimes, releases the lock, xcasts metadata and parent refresh, audits, and returns `SFS_OK`.

## State and Persistence Behavior

Mkdir persists new container metadata, parent mtime updates, inherited attributes, `sys.eos.btime`, uid/gid, and mode through `eosView->updateContainerStore()`. It notifies the directory service of mtime changes, emits `FuseXCastMD` and `FuseXCastRefresh`, and writes an audit record with a trailing slash path. Recursive mkdir can create multiple persistent containers.

## Dependencies and Integration Points

Dependencies include identity mapping, token authorization, namespace mapping, `Prefetcher`, `Acl`, `attr::checkDirOwner`, namespace locks, metadata stores, FUSE xcast, audit protobuf, and global access/stall/redirect macros. It is used by direct XRootD mkdir, auth-plugin requests, FSctl `mkdir`, and internal code that may set `nopermissioncheck`.

## Risks and Edge Cases

- The ordering around `sys.owner.auth` is security-sensitive and documented in comments; changes can alter both permission and ownership semantics.
- Recursive creation repeats permission checks at the nearest ancestor, then inherits attrs/mode at each level; inherited ACLs can change behavior for subsequent components.
- Explicit ACL `!w` must override POSIX permissions for non-sudo users.
- Version directories intentionally do not inherit attributes in the final branch.
- Partial recursive creation can leave earlier components if a later component fails.
- `nopermissioncheck` bypasses permission checks but still creates persistent metadata, so callers must be trusted.

## Test Signals

Tests should cover absolute-path validation, normal mkdir, recursive mkdir with existing final path, missing parent without recursive flag, parent immutable denial, ACL write/write-once/`!w` cases, POSIX XW denial, token denial, keyed and sticky `sys.owner.auth`, uid/gid/mode inheritance, attribute inheritance and version-directory exception, `sys.eos.btime`, `outino`, partial recursive failure behavior, audit path formatting, and FUSE notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/Mkdir.inc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/PathMap.inc -->
# Research: sources/distributed-fs/eos/mgm/ofs/cmds/PathMap.inc

## Purpose

`PathMap.inc` implements MGM path remapping configuration. It stores source-to-target prefix mappings, optionally persists new mappings to the config engine, and translates incoming paths using the longest matching configured prefix.

## Important APIs, Types, and Functions

- `XrdMgmOfs::ResetPathMap()` clears all mappings under `PathMapMutex`.
- `XrdMgmOfs::AddPathMap(source,target,store_config)` inserts a new mapping if the source is absent and optionally calls `mConfigEngine->SetConfigValue("map", source, target)`.
- `XrdMgmOfs::PathRemap(inpath,outpath)` normalizes double slashes, appends a slash for directory-style matching, checks exact path and exact slash-appended mappings, then walks subpaths from deepest to shallowest to apply longest-prefix replacement.

## Control Flow

Reset and add take write locks. Path remap takes a read lock, initializes output to input, collapses repeated `//`, appends a slash to simplify directory-prefix matching, and returns unchanged when the map is empty or the path has no subpaths. Exact `inpath` and slash-appended mappings win before prefix matching. Prefix matching scans from the deepest subpath upward, replaces only the matching prefix, removes the temporary trailing slash, and returns.

## State and Persistence Behavior

The in-memory `PathMap` is protected by `PathMapMutex`. `AddPathMap` can persist mappings through the config engine when `store_config` is true. `PathRemap` is read-only except for its output parameter.

## Dependencies and Integration Points

Dependencies include `eos::common::Path`, `XrdOucString`, EOS RW mutexes, and the MGM config engine. Path remapping integrates into the `NAMESPACEMAP` macro used across command handlers, so changes affect nearly every path-based operation.

## Risks and Edge Cases

- Duplicate source mappings are rejected; updates require reset or separate deletion logic elsewhere.
- The matching algorithm appends/removes a slash and also tests raw `inpath`, so trailing-slash behavior needs exact coverage.
- Longest-prefix replacement is string-based; malformed source/target slashes can produce unexpected paths.
- Config persistence is optional and currently has a TODO around stop config handling.

## Test Signals

Tests should cover empty map, exact path mapping, slash-appended exact mapping, longest-prefix precedence, double-slash normalization, root/no-subpath input, duplicate add rejection, config persistence call, reset behavior, and mappings that target paths with or without trailing slashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/ofs/cmds/PathMap.inc -->
