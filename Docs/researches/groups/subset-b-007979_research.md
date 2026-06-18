# subset-b-007979 Research

Grouped source research for XRootD request execution handlers and ZIP record parsing helpers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdWVInfo.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdWVInfo.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdWVInfo.hh` defines the transient state block used by XRootD vector-write processing. It is a compact dynamically-sized carrier for decoded `kXR_writev` segments, current file handle grouping, resume indices, sync behavior, and monitoring flags. The source was read as a complete 47-line file.

## Important APIs, Types, and Functions

The only exported type is `struct XrdXrootdWVInfo`. Important fields are `wrVec`, a pointer to the embedded `XrdOucIOVec` array; `curFH`, the current grouped file handle; `vBeg`, `vPos`, `vEnd`, and `vMon`, which track vector progress and monitoring boundaries; `doSync`, which requests a file sync after each grouped write; `wvMon`, `ioMon`, and `vType`, which are intended to drive vector-write monitoring; and `ioVec[1]`, the flexible-array-style trailing storage allocated larger than the struct itself.

## Control Flow

This header has no executable flow, but its layout is consumed directly by `XrdXrootdProtocol::do_WriteV()`, `do_WriteVec()`, and checkpoint execution of embedded writev requests. The runtime flow is: allocate enough bytes for `XrdXrootdWVInfo` plus all decoded vector entries, populate the embedded `ioVec`, then advance `vPos` and `vBeg` as socket data is read and grouped `writev` calls are issued.

## State and Persistence Behavior

Instances are per-protocol-request heap allocations stored through `XrdXrootdProtocol::wvInfo`. The state can survive a short protocol resume when socket reads are incomplete, but it is not persistent beyond the connection/request and is freed on completion or error. The flexible-array layout means allocation size and field initialization are part of the contract.

## Dependencies and Integration Points

The only direct include is `XrdOuc/XrdOucIOVec.hh`. Integration is with XRootD protocol execution, SFS file `writev`, checkpointed writev handling, and optional file I/O monitoring. The struct must remain compatible with code that casts and indexes the trailing `ioVec` storage.

## Risks and Edge Cases

Because the struct uses a one-element trailing array rather than standard C++ flexible storage, any allocation-size mistake corrupts memory. The short index fields constrain vector counts to protocol limits and assume `XrdProto::maxWvecsz` remains safely within `short`. Monitoring fields are easy to misinitialize because they carry raw flags rather than a small typed state machine.

## Test Signals

Useful signals include writev tests with one file, multiple file handles, zero-length elements, partial socket reads that force resume, `doSync` enabled, and checkpoint-wrapped writev. Memory sanitizers should cover allocation and freeing paths, and monitoring tests should verify vector and per-segment counters when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdWVInfo.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXPath.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXPath.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXPath.hh` implements a small ordered path-prefix rule list for XRootD path validation and routing options. Protocol handlers use it to decide whether a normalized path is allowed, whether locking, CGI, slash, or multi-write checks should be bypassed, and which static redirect route applies. The source was read as a complete 102-line file.

## Important APIs, Types, and Functions

The exported class is `XrdXrootdXPath`. `Next()`, `Opts()`, and `Path()` expose list navigation and current rule data. `Set()` replaces options and optionally replaces owned path storage. `Insert()` allocates and inserts a new rule in path-length order, using one order for special option-bearing routes and another for ordinary rules. `Validate()` checks whether a candidate path starts with the first matching stored prefix and returns its option bits. Public flags include `XROOTDXP_OK`, `XROOTDXP_NOLK`, `XROOTDXP_NOCGI`, `XROOTDXP_NOSLASH`, and `XROOTDXP_NOMWCHK`.

## Control Flow

The list head is typically a sentinel. `Insert()` walks from `next` and orders longer or shorter prefixes depending on the rule's option bits, then links the new node into the singly linked list. `Validate()` computes or receives a path length, scans while the candidate is at least as long as the stored prefix, and returns the first prefix whose bytes match. XRootD request handlers call `XPList.Validate()`, `RPList.Validate()`, and `RQList.Validate()` after `rpCheck()`/`Squash()` normalization.

## State and Persistence Behavior

Each node owns a `strdup()`-allocated `path` freed by the destructor. There is no destructor recursion, so destroying a sentinel does not free the linked list unless callers walk it elsewhere. Rule state is process configuration state and is read by connection threads without local locking in this class.

## Dependencies and Integration Points

The header uses `<strings.h>` and `<cstdlib>` for C string and allocation APIs. It is integrated by `XrdXrootdXeq.cc` for path policy, static routing lists, no-lock local paths, no-CGI handling, no-leading-slash policy, and multi-write support flags.

## Risks and Edge Cases

The class manually owns C strings and linked nodes, so leaks are possible if list lifecycle is not handled by the owner. `Set()` calls `strlen()`/`strdup()` without null checks beyond `pathdata`, and `Insert()` does not handle allocation failure. Prefix validation is byte-prefix based and does not enforce path-component boundaries, so configuration must avoid ambiguous prefixes such as `/a` matching `/abc` unless that is intentional. Concurrent mutation after startup would be unsafe.

## Test Signals

Tests should cover rule ordering for ordinary and option-bearing paths, exact and prefix matches, nonmatches, empty sentinel paths, path lengths passed explicitly to `Validate()`, `XROOTDXP_NOSLASH` behavior through callers, and ambiguous prefixes. Static redirect and no-lock/multi-write integration tests provide higher-level coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXPath.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.cc` is the main XRootD protocol execution implementation. It translates wire requests into authentication, session, namespace, file, query, I/O, redirect, monitoring, TLS, and filesystem-plugin calls. The source was read as a complete 4,449-line file, with checkpoint, fattr, and paged read/write handlers delegated to companion files.

## Important APIs, Types, and Functions

The file implements many `XrdXrootdProtocol` request handlers: `do_Auth`, `do_Bind`, `do_Chmod`, `do_CKsum`, `do_Clone`, `do_Close`, `do_Dirlist`, `do_DirStat`, `do_Endsess`, `do_gpFile`, `do_Locate`, `do_Login`, `do_Mkdir`, `do_Mv`, `do_Open`, `do_Ping`, `do_Prepare`, `do_Protocol`, `do_Qconf`, `do_QconfCX`, `do_Qfh`, `do_Qopaque`, `do_Qspace`, `do_Query`, `do_Qxattr`, `do_Read`, `do_ReadAll`, `do_ReadNone`, `do_ReadV`, `do_Rm`, `do_Rmdir`, `do_Set`, `do_Set_Cache`, `do_Set_Mon`, `do_Stat`, `do_Statx`, `do_Sync`, `do_Truncate`, `do_Write`, `do_WriteAio`, `do_WriteAll`, `do_WriteCont`, `do_WriteNone`, `do_WriteSpan`, `do_WriteV`, and `do_WriteVec`. Shared helpers include `SendFile`, `SetFD`, `fsError`, `fsOvrld`, `fsRedirNoEnt`, `fsRedirPI`, `getBuff`, `getCksType`, `logLogin`, `mapMode`, `MonAuth`, `rpCheck`, `rpEmsg`, `SetSF`, `Squash`, and `vpEmsg`. Local support includes `XrdXrootdSessID`, `getTime()`, `startUP`, and `OpenHelper`.

## Control Flow

The broad control flow is request-dispatch driven. Login/protocol negotiation establishes capability bits, optional TLS state, session IDs, monitoring identities, and authentication requirements. Authentication may be multi-step and can swap security protocols midstream. Filesystem operations first check static redirects, reject relative or `..` paths via `rpCheck()`, normalize repeated slash and `./` segments through `Squash()`, then call the SFS filesystem or file object and map return codes through `fsError()`.

Open flow maps wire options into SFS open flags, validates colocation/clone requests, checks local dig files, applies route policies, optionally locks the path, creates an SFS file object, performs open and optional clone, inserts an `XrdXrootdFile` into the per-link file table, enables sendfile or SXIO integration, starts monitoring/packet marking, and returns a file handle plus optional compression/stat data. Close serializes async/parallel users, checks paged-write checksum state, supports deferred close callbacks, removes the file table entry, and emits monitoring records through the table.

Read flow chooses memory-map, sendfile, normal async I/O, parallel-stream offload, or buffered synchronous reads based on file state, TLS state, transfer size, file size, and async limits. `do_ReadV()` groups vector reads by file handle, uses filesystem `readv`, builds protocol segment headers, and emits monitoring. Write flow similarly supports async writes, parallel-stream offload, buffered draining, resume after partial socket reads, `writev` batching by file handle, and error draining through `do_WriteNone()`. Parallel I/O uses `do_Offload()` and `do_OffloadIO()` to queue work on bound streams while holding file references and link references.

Query and metadata flow is mostly synchronous but supports deferred SFS callbacks for open/stat/query/sync/truncate. Prepare requests build path and opaque linked lists, manage native or alternate prepare backends, support cancel/query/stage/evict modes, and record native prepare IDs. Error flow centralizes SFS return handling: `SFS_ERROR` maps to XRootD errors and can trigger overload or not-found redirects; `SFS_REDIRECT` emits redirect frames and optionally invokes redirect plugins; `SFS_STARTED` and `SFS_STALL` become wait responses; `SFS_DATA` and `SFS_DATAVEC` return plugin data.

## State and Persistence Behavior

Most state is per connection: `Status`, `Client`, `Entity`, `AuthProt`, `Protect`, `FTab`, `Stream[]`, `PathID`, `ReqID`, `clientPV`, `CapVer`, TLS flags, async counters, packet marking handles, `IO`, `wvInfo`, and reusable request buffers. File state persists in `XrdXrootdFile` objects held by the file table, including stats, async mode, sendfile enablement, mmap state, paged-write state, and filesystem object pointers. Process/global state includes routing tables, path policy lists, monitor configuration, async limits, TLS context, checksum jobs, prepare configuration, and startup time. Native prepare state may be logged outside the connection through `XrdXrootdPrepare`.

## Dependencies and Integration Points

This file sits at the center of XRootD server integration. It depends on XrdSfs filesystem interfaces, XrdSec authentication/protection, XrdLink/XrdLinkCtl session management, XrdBuffer pools, XrdXrootd file table/lock/monitor/prepare/AIO/parallel I/O helpers, checksum helpers, redirect plugin helpers, packet marking, and the wire protocol structs from XProtocol. External plugins interact through SFS file operations, `fsctl`, `FSctl`, `FAttr` via companion files, checksum jobs, prepare backends, redirect helpers, and security providers.

## Risks and Edge Cases

The main risks are protocol-state and buffer-lifetime bugs. Many handlers mutate `argp->buff` in place to split opaque strings or restore query strings, so later code must know whether a path has been truncated at `?`. Parallel stream offload depends on careful locking, file references, and retry semaphores; races can leak refs or use a stream after disconnect if invariants drift. Error paths for writes must drain exactly the right socket stream, and foreign bound paths intentionally terminate on protocol violations. `do_WriteV()` sets `wvInfo->ioMon = (wvInfo->vMon > 1)` immediately after `vMon` is initialized to zero, which appears to prevent detailed vector-write monitoring even when `wvMon` is greater than one. `do_Mv()` sends an `ArgMissing` response for an empty destination but does not immediately return in the visible code, making that path worth auditing. Redirect loop prevention depends on CGI `tried=` mutation and configured canonical names. Several code paths assume protocol maximums keep stack arrays and short counters within bounds.

## Test Signals

High-value tests include protocol negotiation with capable/incapable TLS clients; multi-step auth success, failure, and protocol switching; bind/offload read and write across parallel streams; static route, plugin redirect, overload redirect, and not-found redirect cases; path normalization and relative-path rejection; open options for create/delete/clone/colocation/retstat/compression/POSC; deferred open/close/stat/sync/truncate callbacks; read modes covering mmap, sendfile, async, readv, EOF, and negative lengths; write modes covering async, partial socket reads, bad file handles, write draining, writev grouping, and checkpoint interactions; prepare cancel/query/stage/native logging; and monitor assertions for login, file open, read/write, readv, and redirects. Sanitizer and stress tests should focus on bound stream teardown, buffer reallocation, and error handling during outstanding async I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.hh` provides small macros and a file-handle wrapper shared by XRootD request execution sources. It is included by the main executor and companion handlers so they can pass consistent credentials, trace links, redirect boilerplate, and file-handle decoding. The source was read as a complete 55-line file.

## Important APIs, Types, and Functions

`CRED` casts the current `Client` security entity for SFS calls. `TRACELINK` aliases `Link` for tracing macros. `STATIC_REDIRECT(xfnc)` checks `Route[xfnc].Port[rdType]` and returns a `kXR_redirect` response to the configured host and port. `struct XrdXrootdFHandle` wraps a `kXR_int32 handle` and provides `Set(kXR_char*)` plus a decoding constructor that copies bytes from protocol file-handle fields.

## Control Flow

The macros are expanded inside request handlers. `STATIC_REDIRECT` is an early-return guard before local filesystem work. `XrdXrootdFHandle` is used at the top of file-oriented operations to unmarshal wire handles into the integer used by the per-link file table.

## State and Persistence Behavior

The header owns no storage. `XrdXrootdFHandle` is stack-local in callers and persists only while a request is being handled. The macros depend on ambient `XrdXrootdProtocol` members such as `Client`, `Link`, `Response`, `Route`, and `rdType`.

## Dependencies and Integration Points

The header assumes XRootD protocol wire typedefs such as `kXR_int32` and `kXR_char` are already visible. It integrates with SFS credential passing, tracing, static route configuration, and the `XrdXrootdFileTable` lookup path used throughout the executor.

## Risks and Edge Cases

`STATIC_REDIRECT` hides a control-flow return and relies on the caller being in a context where `Response`, `Route`, and `rdType` are valid. `XrdXrootdFHandle::Set()` uses raw `memcpy` without endian conversion; this is correct only if protocol file handles are opaque bytes generated by the same server-side table representation. As a header without include guards visible in the excerpt, it depends on build discipline or higher-level inclusion patterns.

## Test Signals

Coverage comes from every file-handle operation: read, write, close, sync, truncate-by-handle, fattr-by-handle, checkpoint, clone, and query. Static redirect tests for chmod, checksum, directory, locate, mkdir, mv, open, prepare, rm, rmdir, stat, truncate, and fattr paths verify macro behavior. Cross-platform tests should catch any handle-size or byte-order assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeq.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqChkPnt.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqChkPnt.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqChkPnt.cc` implements XRootD checkpoint requests and checkpoint-wrapped execution of modifying operations. It lets clients create, delete, query, restore, and predeclare checkpoint ranges before writes, paged writes, truncates, or writev operations. The source was read as a complete 302-line file.

## Important APIs, Types, and Functions

`XrdXrootdProtocol::do_ChkPnt()` handles direct checkpoint subcodes: begin maps to `XrdSfsFile::cpCreate`, commit to `cpDelete`, query to `cpQuery`, rollback to `cpRestore`, and `kXR_ckpXeq` delegates to `do_ChkPntXeq()`. `do_ChkPntXeq()` validates an embedded request header, rewrites `Request.header` to the subject request, optionally reads an embedded writev vector, extracts the target file handle, calls SFS checkpoint operations such as `cpWrite` or `cpTrunc`, and then dispatches the real write, pgwrite, truncate, or writev handler.

## Control Flow

Direct checkpoint flow validates the file handle, invokes the requested checkpoint method on the SFS file, returns checkpoint size data for query, and maps errors through `fsError()`. Embedded execution is two-pass for writev: the first pass validates stream ID and payload length, copies the embedded request body, fetches the vector if needed, and may resume after socket reads. The second pass checks the target file, performs a checkpoint range declaration, then calls the underlying operation. For writev, it rejects multi-file checkpoint writev because one checkpoint target is required.

## State and Persistence Behavior

Checkpoint state is stored by the underlying `XrdSfsFile` implementation, not by this file. The handler mutates `Request.header` to represent the embedded operation while setting `requestid` back to `kXR_chkpoint` during checkpoint preparation. For writev, it uses the protocol's `wvInfo` state allocated by `do_WriteV()` and frees it on unsupported multi-file cases. Socket-buffer state can persist across a resume while reading embedded writev arguments.

## Dependencies and Integration Points

The file depends on XProtocol request structs, XrdBuffer, XrdLink, XrdOucErrInfo, XrdSfsInterface, `XrdXrootdFile`, monitoring data, stats, trace macros, `XrdXrootdWVInfo`, and `XrdXrootdXeq.hh`. It integrates with the core write, pgwrite, truncate, and writev implementations in `XrdXrootdXeq.cc` and `XrdXrootdXeqPgrw.cc`, and with SFS file checkpoint support.

## Risks and Edge Cases

Embedded execution mutates global request fields, so every downstream handler must tolerate being called under a checkpoint wrapper. Bad file handles for write and pgwrite require draining or terminating the connection to avoid protocol desynchronization. The error branches for pgwrite/write set `IO.EInfo[0] = SFS_ERROR; IO.EInfo[0] = 0;`, which appears to zero the same slot instead of setting `IO.EInfo[1]`; that should be audited because it can affect the error returned after draining. Multi-file writev is explicitly unsupported. Invalid SFS checkpoint return codes are coerced to logic errors.

## Test Signals

Tests should cover begin, commit, query, rollback, invalid subcodes, invalid file handles, embedded stream-ID mismatch, invalid embedded request length, recursive checkpoint rejection, truncate-with-path rejection, checkpointed write, checkpointed pgwrite, checkpointed truncate-by-handle, single-file checkpointed writev, multi-file writev rejection, resume while reading embedded writev vectors, and SFS failures for `cpWrite`/`cpTrunc` that still require socket draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqChkPnt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqFAttr.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqFAttr.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqFAttr.cc` implements XRootD file-attribute requests for user extended attributes. It decodes wire-format attribute names and values, forces them into the user namespace, dispatches get/set/delete/list operations to the SFS `FAttr` API, and formats per-attribute result vectors. The source was read as a complete 595-line file.

## Important APIs, Types, and Functions

Local `faCTL` owns decoded `XrdSfsFAInfo` entries and tracks parse position. `Decode()` parses name entries encoded as two zero prefix bytes plus a NUL-terminated name, then optional value entries encoded as network-order `kXR_int32` length plus bytes. `FillRC()` writes per-variable mapped return codes into the name prefix area. `IOVec` allocates bounded `iovec` arrays using the platform maximum. `SendErr()` reports decode failures. Protocol methods are `do_FAttr()`, `ProcFAttr()`, `XeqFADel()`, `XeqFAGet()`, `XeqFALsd()`, `XeqFALst()`, and `XeqFASet()`.

## Control Flow

`do_FAttr()` first checks that user xattrs are configured, validates the subcode, determines read/write mode, and chooses handle-targeted or path-targeted processing. Handle mode verifies the file table entry and write mode for modifying requests. Path mode splits path and attribute payload, rejects relative or unsafe paths, normalizes paths, and honors static open-route redirection. `ProcFAttr()` validates the attribute count, initializes `XrdSfsFACtl`, optionally requests access checks, parses names/values unless this is list, and dispatches to delete/get/set/list helpers. Each helper calls `osFS->FAttr()`, maps filesystem errors through `fsError()`, and serializes either per-variable status, values, list buffers, or list-with-data tuples.

## State and Persistence Behavior

The file itself persists no attributes; persistence belongs to the backing filesystem or plugin. Decoding mutates the request buffer in place by replacing the leading two name bytes with `U.` or mapped return-code bytes. `faCTL` owns the `XrdSfsFAInfo` array until ownership is transferred into `XrdSfsFACtl`. Response data often references the mutated request buffer and filesystem-owned buffers for the duration of the response send.

## Dependencies and Integration Points

The handler depends on XProtocol, XrdBuffer, XrdLink, XrdOucErrInfo, `XrdSfsFAttr`, `XrdSfsInterface`, XrdSec credentials, `XrdXrootdFile`, monitor data, `XrdXrootdProtocol`, `XrdXrootdXeq.hh`, and `XrdXrootdXPath.hh`. It integrates with per-link open-file state, path validation from the main executor, static routing, SFS extended-attribute plugins, and XRootD monitor operation codes for read/write-like metadata changes.

## Risks and Edge Cases

Parsing is strict but in-place: malformed lengths, missing NUL terminators, or extra payload bytes return protocol errors, while valid names are rewritten before the SFS call. `SendErr()` reports `ctl.iNum` rather than the last processed index `iEnd`, which may make diagnostics less precise. `XeqFALsd()` has an unreachable fallback return after an earlier return expression; if no non-error entries produce data, the current path returns zero rather than explicitly sending an empty response. `FillRC()` overwrites name prefix bytes with status codes, so any later code expecting the namespace prefix after response construction would be wrong. Attribute count and max name/value sizes are security boundaries.

## Test Signals

Tests should cover unsupported configuration, invalid subcodes, list with nonzero count, get/set/delete with zero or too many variables, handle mode for read-only and write-open files, path mode with CGI and redirects, malformed name prefixes, empty names, overlong names/values, negative value lengths, extra trailing payload, partial per-attribute SFS failures, segmented large get/list responses, `aData` list mode, `isNew` set mode, and user namespace prefix enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqFAttr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqPgrw.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqPgrw.cc

## Purpose

`sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqPgrw.cc` implements page-level read and write requests with per-page checksums. These handlers support efficient verified transfer, retry of corrupted pages, asynchronous paged I/O, and close-time reporting of unresolved checksum errors. The source was read as a complete 639-line file.

## Important APIs, Types, and Functions

Constants derive protocol page/unit sizes and async thresholds: `pgPageSize`, `pgPageMask`, `pgUnitSize`, `pgAioMin`, and `pgAioHalf`. Protocol methods are `do_PgClose()`, `do_PgRead()`, `do_PgRIO()`, `do_PgWrite()`, `do_PgWAIO()`, `do_PgWIO()`, `do_PgWIO(bool)`, `do_PgWIORetry()`, and `do_PgWIOSetup()`. The code uses `XrdOucPgrwUtils` for checksum count, verification, and segment geometry; `XrdXrootdPgrwAio` for async; `XrdXrootdPgwCtl` for frame parsing and response construction; and `XrdXrootdPgwFob` for bad-offset tracking.

## Control Flow

Paged read unmarshals offset and length, rejects nonpositive lengths, gets the file handle, decodes optional path and retry flags, updates stats and monitoring, tries async when eligible, optionally offloads to a bound stream, then calls `do_PgRIO()`. `do_PgRIO()` chooses a page-multiple quantum bounded by iovec and buffer limits, reads data plus checksums from `XrdSfsFile::pgRead()`, converts checksums to network order, sends partial-result frames with original offsets, and sends an empty final result if EOF or zero bytes ended after partial framing.

Paged write validates that payload includes at least one checksum, validates path IDs enough to know whether stream draining is possible, allocates a per-file `XrdXrootdPgwFob`, updates stats/monitoring, offloads if requested, and enters `do_PgWIO()`. The write I/O path optionally uses async, validates retry size and bad-offset registration, sets up frame parsing with `XrdXrootdPgwCtl`, reads checksum/data frames from the socket, verifies checksums, records bad offsets, writes data through `XrdSfsFile::pgWrite()`, clears corrected retry offsets, advances frames, and returns bad-offset information. `do_PgClose()` checks the fob at close time and fails close if uncorrected checksum errors remain.

## State and Persistence Behavior

Paged write state is attached to the open `XrdXrootdFile`: `pgwFob` tracks checksum failures across writes until close, and `pgwCtl` is a protocol-level control object reused for frame parsing. Bad offsets persist for the open file lifetime and influence retry validation. File statistics record paged read/write operations and correction counts, but the actual file data and checksum persistence are delegated to the SFS implementation.

## Dependencies and Integration Points

The file depends on XrdSfs interfaces, platform iovec limits, XProtocol definitions, XrdBuffer, XrdLink, CRC/page utilities, XRootD AIO file objects, monitor/file stats, paged AIO, paged write control/fob classes, protocol state, trace macros, and the shared executor header. It integrates with the main close path, bound-stream offload, async I/O limits, per-file monitoring, checkpointed pgwrite execution, and SFS `pgRead`/`pgWrite` support.

## Risks and Edge Cases

Paged write protocol desynchronization is high risk because malformed frame setup can make it impossible to drain the socket reliably; the code intentionally closes the connection on those cases. Retry writes are constrained to one page, with unaligned offsets computed specially; off-by-one errors would either reject valid retries or allow cross-page correction. `do_PgClose()` converts outstanding checksum offsets into a close failure, so clients must handle write-success followed by close checksum failure. `do_PgRIO()` relies on page geometry and iovec calculations staying within stack array sizes. Async eligibility must avoid retry requests and respect per-link/server limits.

## Test Signals

Tests should cover aligned and unaligned pgread, EOF and short final results, retry-flag pgread, async and synchronous paths, bound stream offload, invalid/zero lengths, invalid handles, checksum conversion, pgwrite with valid frames, checksum failures producing bad-offset responses, too many bad offsets, retry writes for registered and unregistered offsets, retry crossing a page boundary, malformed frame setup causing connection error, SFS pgWrite failures requiring drain, checkpointed pgwrite, and close with zero, corrected, and uncorrected checksum errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdXeqPgrw.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipCDFH.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipCDFH.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipCDFH.hh` defines the Central Directory File Header representation for XRootD ZIP support. It parses, stores, serializes, and indexes ZIP central-directory entries, including ZIP64 extra fields for overflowed sizes, offsets, and disk numbers. The source was read as a complete 357-line file.

## Important APIs, Types, and Functions

The namespace exports `struct CDFH`, `cdvec_t` as `std::vector<std::unique_ptr<CDFH>>`, `cdmap_t` as filename-to-index map, and `cdrecs_t` as filename-to-record map. Static `Parse()` overloads read fixed-count or signature-delimited central directory records. `CalcSize()` and static `Serialize()` combine existing original central-directory bytes with appended records. Constructors build a CDFH from an `LFH` plus mode and offset, or parse one from a buffer. `GetOffset()` chooses the 32-bit header offset or ZIP64 extra offset. `ParseExtra()` locates and decodes ZIP64 data. Instance `Serialize()`, `IsZIP64()`, and `HasDataDescriptor()` expose serialization and feature checks.

## Control Flow

Fixed-count parsing walks `nbCdRecords`, validates the central-directory signature, constructs a `CDFH` with a maximum remaining buffer size, advances by `cdfhSize`, and records filename-to-index mappings. Signature-delimited parsing stops when the next signature is not a CDFH signature, leaving the caller's buffer pointer at the first non-CDFH record. Serialization writes fields in ZIP order, then filename, optional extra, and optional comment. Construction from an LFH mirrors file metadata and creates a central-directory ZIP64 extra if the local-header extra or local-header offset requires it.

## State and Persistence Behavior

`CDFH` is an in-memory representation of archive metadata. Persistent state is the serialized central-directory record written into a ZIP archive. Parsed records own `filename`, `comment`, and an optional `Extra`. ZIP64 values are stored in `extra` when 32-bit fields are overflow sentinels.

## Dependencies and Integration Points

The header includes `XrdZipLFH.hh`, `XrdZipUtils.hh`, and `XrdZipDataDescriptor.hh`, plus STL containers and `sys/types.h`. It integrates with local file headers, data descriptor flags, ZIP64 extra parsing, archive central-directory indexing, and any XRootD ZIP reader/writer code that appends files or looks up entries by name.

## Risks and Edge Cases

The fixed-count `Parse()` checks `bufferSize < cdfhBaseSize` without accounting for the current `offset`, then reads `buffer + offset`; this is safe only because `bufferSize` is decremented in parallel, but it is easy to break if modified. The buffer constructor validates total record size only when `maxSize > 0`; callers using the default must already guarantee enough bytes for variable fields. `ParseExtra()` silently leaves `extra` null if overflow fields require ZIP64 data but the extra record is absent, so later `GetOffset()` on an overflowed offset assumes valid `extra`. Filename duplicate handling overwrites the map entry while retaining both vector entries.

## Test Signals

Tests should parse central directories with zero, one, and many records; truncated fixed fields; truncated filename/extra/comment; invalid signatures; duplicate filenames; ZIP64 compressed size, uncompressed size, offset, and disk overflow combinations; data-descriptor flag detection; appended serialization after an original central directory; and round-trip serialization for LFH-derived and parsed records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipCDFH.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipDataDescriptor.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipDataDescriptor.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipDataDescriptor.hh` defines constants for ZIP data descriptor records. These records appear when CRC and sizes are written after file data rather than in the local header. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions

The exported `struct DataDescriptor` has static `GetSize(bool zip64)`, returning signature plus three 64-bit values for ZIP64 or signature plus three 32-bit values for classic ZIP. It also defines `flag = 1 << 3`, the general-purpose bit indicating a data descriptor, and `sign = 0x08074b50`, the descriptor signature.

## Control Flow

There is no runtime parsing flow in this header. Callers use `HasDataDescriptor()` on CDFH or LFH-related metadata to detect the flag, then use `GetSize()` to compute how many bytes a descriptor should occupy for the ZIP64 mode being processed.

## State and Persistence Behavior

No mutable state is owned. The constants describe serialized archive state that lives in ZIP files.

## Dependencies and Integration Points

The only include is `<cstdint>`. The header is included by `XrdZipCDFH.hh` and likely ZIP reader/writer code that needs descriptor sizing and flag interpretation.

## Risks and Edge Cases

The size model assumes the descriptor includes the optional signature; ZIP variants may omit that signature, so callers must know which form they are handling. `GetSize()` returns `uint8_t`, which is sufficient for the current 16-byte and 28-byte sizes but would be fragile if extended formats were added.

## Test Signals

Tests should assert classic and ZIP64 descriptor sizes, flag matching against CDFH/LFH general bit flags, and reader behavior for archives with descriptor signatures, without descriptor signatures if supported elsewhere, and with ZIP64 size fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipDataDescriptor.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipEOCD.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipEOCD.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipEOCD.hh` defines the End of Central Directory record representation for XRootD ZIP support. It locates, parses, constructs, serializes, and logs the EOCD metadata that terminates a ZIP archive and points to the central directory. The source was read as a complete 159-line file.

## Important APIs, Types, and Functions

`EOCD::Find()` scans backward for signature `0x06054b50`. The buffer constructor parses disk numbers, record counts, central-directory size and offset, comment length, optional bounded comment, computed `eocdSize`, and initializes `useZip64` false. The construction constructor takes central-directory offset, count, and size, writes overflow sentinels for 16-bit counts and 32-bit offsets as needed, and marks `useZip64` when the offset overflows. `Serialize()` writes the record to a `buffer_t`, and `ToString()` formats fields for logging. Constants include `eocdBaseSize = 22` and `maxCommentLength = 65535`.

## Control Flow

Finding an EOCD starts from `size - eocdBaseSize` and decrements to zero, returning the first matching signature. Parsing then reads fixed fields and, if `maxSize` is provided, validates that the comment fits before copying it. Serialization emits fixed fields followed by the comment. Archive-writing code uses the constructor to choose classic fields or overflow sentinels.

## State and Persistence Behavior

The struct is an in-memory form of persistent ZIP end metadata. Serialized state includes disk fields, central-directory counts, size, offset, and comment. `useZip64` is runtime guidance for writing ZIP64 structures and is not itself serialized in EOCD.

## Dependencies and Integration Points

The header includes `XrdZipUtils.hh`, `XrdZipLFH.hh`, `XrdZipCDFH.hh`, `<string>`, and `<sstream>`. It integrates with central-directory construction, ZIP64 overflow handling, archive scanning, and logging.

## Risks and Edge Cases

`Find()` takes an unsigned `size` and computes `size - eocdBaseSize` before assigning to `ssize_t`; if `size` is smaller than the base size, unsigned underflow can produce an invalid starting offset. The constructor marks ZIP64 only when the central-directory offset overflows, not when record count or size overflows; count overflow writes sentinels but does not set `useZip64` by itself in the visible code. `ToString()` omits an `=` after `cdSize`, a harmless logging defect. Bounded parsing depends on callers passing `maxSize`.

## Test Signals

Tests should cover finding EOCD with empty and maximum comments, no signature, buffers smaller than 22 bytes, false signatures inside comments, bounded parse truncation, record-count overflow, offset overflow, central-directory size overflow expectations, serialization round trip, and `ToString()` content for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipEOCD.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipExtra.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipExtra.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipExtra.hh` defines the ZIP64 extended information extra field used by XRootD ZIP support. It stores 64-bit compressed/uncompressed sizes, local-header offset, and disk number when classic ZIP fields overflow. The source was read as a complete 183-line file.

## Important APIs, Types, and Functions

`struct Extra` has constructors from file size, from another `Extra` plus central-directory offset, and default zero initialization. `Find()` scans an extra-field byte region for header ID `0x0001`. `FromBuffer()` validates header ID and expected data size, then conditionally reads fields according to overflow flags. `Serialize()` writes the header and included 64-bit fields when `totalSize > 0`. `enum Ovrflw` defines `NONE`, `UCMPSIZE`, `CPMSIZE`, `OFFSET`, and `NBDISK`. Stored fields are `dataSize`, `uncompressedSize`, `compressedSize`, `offset`, `nbDisk`, and `totalSize`.

## Control Flow

When writing from a file size, the constructor emits size fields only if the file is at least the 32-bit overflow sentinel. When converting LFH extra to CDFH extra, the constructor copies existing size fields and appends offset data if the local-header offset overflows. Parsing first locates the ZIP64 block, validates that its payload size exactly matches the expected overflow fields, then reads fields in the ZIP64-prescribed order selected by the flags.

## State and Persistence Behavior

`Extra` is an in-memory representation of a serialized ZIP extra field. `totalSize` controls whether anything is written. The field persists in local headers and central-directory headers when serialized.

## Dependencies and Integration Points

The header depends on `XrdZipUtils.hh`, `<cstdint>`, and `<sys/types.h>`. It is used by `LFH` and `CDFH` parsing/serialization to handle ZIP64 overflows and by central-directory construction to add offset overflow metadata.

## Risks and Edge Cases

`Find()` advances through variable-length blocks without checking that the next header and data length fit within `end`; malformed extra fields can make it read a short block header or skip beyond the buffer. `FromBuffer()` requires `dataSize == exsize`, but APPNOTE ZIP64 extras may contain fields for only the overflowed values and can coexist with other extra data; the strictness is intentional only if callers compute exactly expected ZIP64 payload sizes. `Serialize()` writes offset only when sizes are absent or positive; combinations involving zero-size ZIP64 files plus offset overflow need careful validation.

## Test Signals

Tests should cover no-overflow files, size overflow, offset overflow, combined size and offset overflow, parsing each flag combination, wrong header ID, wrong data size, truncated extra blocks, multiple extra fields before ZIP64, malformed datasize that exceeds buffer length, and serialization byte-for-byte compatibility with `LFH` and `CDFH` round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipExtra.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipLFH.hh -->
# sources/distributed-fs/xrootd/src/XrdZip/XrdZipLFH.hh

## Purpose

`sources/distributed-fs/xrootd/src/XrdZip/XrdZipLFH.hh` defines the Local File Header representation for XRootD ZIP support. It creates, parses, and serializes the per-file header that precedes file data, including ZIP64 extra metadata for large files. The source was read as a complete 178-line file.

## Important APIs, Types, and Functions

`struct LFH` provides static `initSize()` to choose a 32-bit size or overflow sentinel, a writing constructor from filename, CRC, file size, and timestamp, a parsing constructor from a buffer and optional size bound, `Serialize()`, and `ParseExtra()`. Fields include `minZipVersion`, `generalBitFlag`, `compressionMethod`, DOS timestamp, CRC32, compressed and uncompressed size, filename and extra lengths, filename, optional `Extra`, and computed `lfhSize`. Constants are `lfhSign = 0x04034b50` and `lfhBaseSize = 30`.

## Control Flow

Writing construction initializes a stored method entry, sets both compressed and uncompressed sizes to the input file size or the 32-bit overflow sentinel, creates an `Extra`, selects minimum ZIP version 10 or 45 depending on ZIP64 use, and computes header size. Parsing validates the signature, reads fixed fields with `from_buffer()`, checks variable-field bounds when `bufferSize` is supplied, copies the filename, and parses ZIP64 extra data only when 32-bit sizes are overflow sentinels. Serialization writes fixed fields, filename, and serialized extra data in order.

## State and Persistence Behavior

`LFH` holds an in-memory copy of persistent ZIP local-header metadata. The serialized state is written before file data in the archive. It owns filename and optional ZIP64 `Extra` data; file data itself is not represented here.

## Dependencies and Integration Points

The header includes `XrdZipUtils.hh`, `XrdZipExtra.hh`, and STL string/memory/algorithm helpers. It integrates with `CDFH` construction, archive file entry writing, ZIP64 extra parsing, DOS timestamp conversion, and code that locates file data after the local header.

## Risks and Edge Cases

The parser is bounded only when `bufferSize` is nonzero; default construction from an untrusted pointer requires prior validation. If overflowed sizes require a ZIP64 extra but `Extra::Find()` returns null, `extra` remains a default object with zero sizes, which may hide malformed archives until later size use. Filename length is stored as `uint16_t`; constructing from a longer `std::string` would truncate length semantics. The code assumes stored/no-compression entries because compressed and uncompressed sizes are initialized identically.

## Test Signals

Tests should cover small-file construction, ZIP64-size construction, serialization round trips, parsing invalid signatures, truncated fixed headers, truncated filename and extra data with bounds, missing ZIP64 extra when size sentinels are present, multiple extra records, zero-length filenames if allowed by caller policy, maximum 16-bit filename/extra lengths, and compatibility with `CDFH(LFH*, mode, offset)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdZip/XrdZipLFH.hh -->
