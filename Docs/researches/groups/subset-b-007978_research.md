# subset-b-007978 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.hh

## Purpose

`XrdXrootdPgwFob` tracks page-write checksum or recovery failures for one `XrdXrootdFile`. It records page offsets that are currently bad, counts total errors and later fixes, and gives page-write logic a bounded way to decide whether too many unresolved page errors have accumulated.

## Important APIs, types, and functions

The class exports `addOffs()`, `delOffs()`, `hasOffs()`, and `numOffs()`. Offsets are normalized by shifting the page offset by `XrdProto::kXR_pgPageBL`; short final-page writes encode `dlen` in the low bits so the same page number can distinguish full and partial page records. `badOffs` is a `std::set<kXR_int64>` protected by `fobMutex`.

## Control flow

Page-write code calls `addOffs()` when a page is detected as bad. The method inserts the encoded offset, increments `numErrs`, and returns whether unresolved bad offsets are still within `kXR_pgMaxEos`. A later successful correction calls `delOffs()`, increments `numFixd`, and erases the encoded offset. Readers can query one offset via `hasOffs()` or total unresolved/fixed/error counts through `numOffs()`.

## State and persistence behavior

All state is in-memory and scoped to the owning `XrdXrootdFile`; there is no durable persistence in this header. The destructor is out-of-line and is integrated with page-write support code. The mutex makes the set safe for concurrent page-write/error-recovery activity on the same file object.

## Dependencies and integration points

The type depends on `XProtocol.hh` for page geometry constants and `XrdSysPthread.hh` for locking. It is referenced from `XrdXrootdFile`, page-write control, and bad-checksum handling paths.

## Risks and edge cases

The offset encoding must stay consistent with protocol page constants; changing page size or bit layout without updating this class can collide entries. Duplicate bad offsets still increment `numErrs`, so the counter is an event count rather than the set cardinality. `addOffs()` only reports whether the set is below the protocol limit; callers must enforce the returned value.

## Test signals

Relevant tests should exercise full-page and short-page encoding, duplicate insertion, deletion of absent offsets, concurrent add/delete behavior, and caller behavior when `kXR_pgMaxEos` is exceeded. Integration signals come from page-write checksum and retry tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPgwFob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.cc

## Purpose

This file implements the small object pool for `XrdXrootdPio`, the protocol's queued parallel-I/O descriptor. The pool reduces allocation churn for offloaded reads/writes and bound-stream I/O operations.

## Important APIs, types, and functions

`XrdXrootdPio::Alloc(int Num)` returns a linked list of at least `Num` cleared descriptors. `Recycle()` clears one descriptor and either pushes it to a static free list or deletes it when `FreeMax` cached entries already exist. Static members are `myMutex`, `Free`, and `FreeNum`.

## Control flow

Allocation first drains as many descriptors as possible from the free list under `myMutex`, detaches the returned chain, then allocates additional descriptors with `new` until the requested count is satisfied. Recycling locks the same mutex, checks the cache cap, clears the descriptor using `Clear(Free)`, and links it back onto the free list.

## State and persistence behavior

The only state is process-local pool state. Descriptors carry no durable data; `Clear()` zeros the resume pointer, `IOParms`, stream id, and next pointer before reuse.

## Dependencies and integration points

The implementation depends on `XrdXrootdPio.hh` and indirectly on `XrdXrootdProtocol`/`IOParms`. `XrdXrootdProtocol::Cleanup()` recycles active and free per-link PIO objects; execution paths in `XrdXrootdXeq.cc` allocate them for parallel stream/offload work.

## Risks and edge cases

The pool is global and bounded but never shrinks below objects already retained, so tests that expect exact allocation counts must account for reuse. `Alloc(0)` can still return the current free head if misused because the code checks `Free` before consuming `Num`; callers should pass positive counts. Descriptor ownership is manual and double recycling would corrupt the free list.

## Test signals

Useful tests cover allocating from empty and populated pools, clearing stale `IOParms` and stream ids, respecting `FreeMax`, and running recycle/allocation under concurrent worker threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.hh

## Purpose

`XrdXrootdPio` is the per-operation descriptor used by `XrdXrootdProtocol` to queue or resume parallel I/O. It records the protocol member function to resume, the `IOParms` for the file operation, and the stream id associated with the request.

## Important APIs, types, and functions

The public fields `Next`, `ResumePio`, `IO`, and `StreamID` form an intrusive queue node. `Alloc()`, `Recycle()`, `Clear()`, and `Set()` are the lifecycle helpers. `Set()` copies the resume member-function pointer, the `IOParms`, and two-byte stream id into the descriptor.

## Control flow

Protocol execution code allocates a small batch, fills entries with `Set()`, chains them through `Next`, and later invokes `ResumePio` through the owning protocol object. `Recycle()` returns descriptors to the global pool after `Cleanup()` dereferences any file objects attached through `IO.File`.

## State and persistence behavior

PIO descriptors are transient scheduling state only. The header deliberately stores raw pointers and a copied `IOParms` struct; reference management for `XrdXrootdFile` is handled by the caller, not by this type.

## Dependencies and integration points

The header depends on protocol types from `XProtocol/XPtypes.hh`, locking from `XrdSysPthread.hh`, and `XrdXrootdProtocol.hh` for `IOParms` and member-function pointer types. It is tightly integrated with bound streams, async/offloaded I/O, and protocol cleanup.

## Risks and edge cases

Because descriptors contain raw file pointers and member-function pointers, stale entries after recycle would be dangerous; `Clear()` is therefore part of the pool contract. The type has no copy prevention, so accidental by-value copies could duplicate ownership assumptions. `StreamID` is fixed at two bytes, matching the wire protocol.

## Test signals

Signals include verifying `Set()` preserves stream id and `IOParms`, `Clear()` resets every reused field, and cleanup paths recycle descriptors only after file reference counts have been decremented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPio.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPlugin.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPlugin.cc

## Purpose

This file exposes the C ABI entry points used when the xroot protocol is loaded as an ancillary shared-library protocol. It constructs the protocol object and reports the protocol port to the hosting XRootD protocol driver.

## Important APIs, types, and functions

`XrdgetProtocol()` logs the startup banner, calls `XrdXrootdProtocol::Configure(parms, pi)`, and returns a new `XrdXrootdProtocol` on success. `XrdgetProtocolPort()` returns `pi->Port` when configured or the default xroot port `1094`. `XrdVERSIONINFO` annotates both exported entry points.

## Control flow

The host loads the shared object, calls `XrdgetProtocolPort()` early, then calls `XrdgetProtocol()`. Configuration failure returns null and logs initialization as failed; success returns an unbound prototype protocol instance whose `Match()` method later recognizes and binds xroot links.

## State and persistence behavior

This file stores no state. It delegates all configuration and static process state setup to `XrdXrootdProtocol::Configure()`.

## Dependencies and integration points

It depends on `XrdVersion.hh` and `XrdXrootdProtocol.hh`. A near-identical loader is also present in `XrdXrootdProtocol.cc` for builds where the protocol is not ancillary; build configuration must avoid duplicate exported definitions in the same link unit.

## Risks and edge cases

The default port behavior assumes one xroot port per protocol instance. Errors from `Configure()` are reduced to a null return and log text, so detailed diagnostics must come from configuration code. ABI compatibility depends on the exported names and version metadata remaining stable.

## Test signals

Integration tests should load the plugin through the XRootD protocol manager, verify default and configured port selection, and assert failed configuration returns null without leaving partially initialized protocol state usable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPlugin.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.cc

## Purpose

This file implements persistent logging for xroot `prepare` requests. It records request metadata and path lists as files in a configured directory, supports listing/opening/deleting those records, and periodically scrubs stale entries.

## Important APIs, types, and functions

`XrdXrootdPrepare::List()` iterates log files matching optional request id and user filters. `Log()` writes a prepare record named `<reqid>_<user>_<priority>_<numpaths>` and creates a symlink named `<reqid>`. `Logdel()` removes the symlink target and symlink. `Open()` opens a request id symlink and returns its size. `Scrub()` deletes stale records. `setParms()` configures scrub timing and log directory.

## Control flow

The constructor stores the scheduler/logger and schedules the scrub job when `LogDir` is configured. `DoIt()` calls `Scrub()` and reschedules itself. Request execution code builds `XrdXrootdPrepArgs`, calls `Log()` for tracked prepares, `List()` for query-style enumeration, and `Logdel()` for cancellation/removal.

## State and persistence behavior

Static process state includes `scrubtime`, `scrubkeep`, `LogDir`, and `LogDirLen`. Durable state is the prepare log directory: one data file per request and one request-id symlink. The file body stores paths separated by spaces with a final newline; metadata is encoded in the filename.

## Dependencies and integration points

The file uses POSIX directory, file, symlink, stat, and `writev` APIs. It integrates with `XrdScheduler` as an `XrdJob`, `XrdSysError` for diagnostics, `XrdOucTList` path lists, and protocol prepare/query handlers in `XrdXrootdXeq.cc`.

## Risks and edge cases

Filename construction trusts `reqid` and `user` strings supplied by callers; those must already be sanitized to avoid path separators or excessive length. `List()` mutates `dirent->d_name` by replacing underscores with spaces, which is common on mutable `dirent` buffers but is still a fragile parsing style. `Scrub()` uses underscore presence to identify records and may skip malformed files. `getUTC` is unrelated; all timestamps here use filesystem `mtime`.

## Test signals

Tests should cover directory validation, file/symlink creation, listing by request/user, deletion when either file or symlink is missing, stale scrub behavior, long request id rejection in `Logdel()`, and behavior when logging is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.hh

## Purpose

This header declares the prepare-log data model and scrub job. `XrdXrootdPrepArgs` carries parsed prepare request data, while `XrdXrootdPrepare` owns the static file-backed prepare tracking interface.

## Important APIs, types, and functions

`XrdXrootdPrepArgs` stores `reqid`, `user`, `notify`, `prty`, `mode`, a linked path list, and private listing state (`DIR *dirP`, cached filter lengths, ownership flags). `XrdXrootdPrepare` exposes `List()`, `Log()`, `Logdel()`, `Open()`, `Scrub()`, and two `setParms()` overloads, plus `DoIt()` for scheduled scrubbing.

## Control flow

Protocol code fills `XrdXrootdPrepArgs` from a `prepare` request. Depending on request mode it logs, lists, opens, or deletes records. The scheduled job calls `Scrub()` periodically and requeues itself using `scrubtime`.

## State and persistence behavior

`XrdXrootdPrepArgs` owns optional heap strings and path lists according to constructor flags; its destructor closes active directory iteration state. `XrdXrootdPrepare` uses static scheduler/logger/log-directory state and stores durable records as files outside the process.

## Dependencies and integration points

The header depends on POSIX `DIR`, `XrdJob`, `XrdScheduler`, `XrdSysError`, and `XrdOucTList`. It is integrated from protocol execution and configuration code for `xrootd.prepare` behavior.

## Risks and edge cases

Ownership flags make `XrdXrootdPrepArgs` flexible but easy to misuse: passing borrowed strings with `freestore=1` or borrowed path nodes with `freepaths=1` will cause invalid frees. `mode` is a four-byte fixed buffer, so parsing must bound writes. The `XrdXrootdPrepare` object is intentionally never deleted.

## Test signals

Signals include destructor ownership behavior, list state cleanup, scheduling after logdir configuration, and correct handling of disabled logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdPrepare.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.cc

## Purpose

This file implements the core xroot protocol lifecycle: plugin entry points, handshake recognition, request read/dispatch, request-signature verification, response stream setup, connection recycle, stat formatting, buffer exchange, and continuation-based socket reads.

## Important APIs, types, and functions

Extern C entry points `XrdgetProtocol()` and `XrdgetProtocolPort()` initialize the protocol in some build modes. `Match()` validates the initial client handshake and binds a pooled `XrdXrootdProtocol` to an `XrdLink`. `Process()` reads request headers and arguments, `Process2()` dispatches by request code, and `ProcSig()` reads `kXR_sigver` payloads. `Recycle()`, `Cleanup()`, and `Reset()` own connection teardown/reuse. `getData()`, `getDataCont()`, `getDataIovCont()`, and `getDumpCont()` implement slow-link continuations. `Buffer()`, `Claim()`, `Swap()`, and `Reclaim()` implement `XrdSfsXio`.

## Control flow

`Match()` peeks for the xroot handshake, sends a protocol response, consumes the handshake, initializes entity/link/response state, and increments match stats. `Process()` first resumes partial reads or prior operations, then reads a `ClientRequest`, stores a copy for signature verification when needed, unmarshals byte order, reads non-write argument data, and calls `Process2()`. `Process2()` enforces signatures, requires login except for login/protocol/bind, handles high-volume file-handle operations first, permits ping/protocol without authentication, then dispatches authenticated operations and redirects selected clients before filesystem work.

## State and persistence behavior

The file defines many static process configuration values: filesystem pointers, security services, TLS policy, async limits, redirect tables, buffer sizes, stats, and global protocol object pool. Per-link state includes link pointer, file table, monitor info, request/response buffers, signature state, async counters, stream binding state, page-write state, and `ReqID`. There is no persistent storage here; durable effects occur through filesystem calls in request handlers outside this file.

## Dependencies and integration points

It depends on XRootD link/buffer/scheduler/stat/security/TLS/SFS libraries, protocol structs from `XProtocol`, monitoring, file tables, async/page-write helpers, and tracing. It is the integration hub for request execution files such as `XrdXrootdXeq.cc`, async I/O, callbacks, transit bridging, and admin/configuration support.

## Risks and edge cases

The continuation state machine is subtle: `Resume`, `myBlen`, `gdCtl.Status`, and callbacks must stay consistent on slow links and disconnects. Signature verification depends on preserving the original request before byte-order mutation. Bound-stream recycle waits for subordinate activity and can deadlock if stream state is not signaled correctly. Static configuration is process-wide, so tests must isolate it carefully.

## Test signals

High-value signals include handshake accept/reject, request dispatch before/after login, negative data length rejection, signed request success/failure/ignored paths, slow partial argument reads, iovec continuation, dump/discard continuation, recycle during blocked reads, stream verification, and stats synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.hh

## Purpose

This header declares `XrdXrootdProtocol`, the central protocol object for xroot client sessions. It combines `XrdProtocol`, callback-driven input, direct I/O/sendfile support, and SFS exchange-buffer support in one per-link state machine.

## Important APIs, types, and functions

Public entry points include `Configure()`, `Match()`, `Process()`, `Recycle()`, `Stats()`, `SendFile()`, `SetFD()`, `Claim()`, `Swap()`, `Reclaim()`, `VerifyStream()`, `getData()` overloads, and `DoIt()`. Private request handlers cover authentication, open/read/write/vector I/O, page read/write, prepare, query, metadata, redirection, TLS, and configuration directives. `XrdXrootd::gdCallBack` and `XrdXrootd::IOParms` define callback and I/O parameter contracts.

## Control flow

The object is driven by `XrdLink`: `Match()` binds a link, `Process()` reads and dispatches requests, handler methods update `Response` and state, and `Recycle()` returns the object to `ProtStack`. Callback methods resume partial network reads and page writes. Parallel stream state uses `Stream[]`, `PathID`, semaphores, and mutexes to coordinate subordinate paths.

## State and persistence behavior

Static members store process configuration, filesystem/security services, redirect policy, TLS requirements, async thresholds, stats, and global route tables. Instance members store the active link, file table, monitor context, client/security entity, request-signature buffers, async counters, get-data continuation state, page-write control, buffer sizing, stream binding, protocol caps, and current request/response objects.

## Dependencies and integration points

The header depends on XRootD core protocol/link abstractions, SFS direct I/O and XIO, security interfaces, monitoring, request-id and response helpers, and protocol wire definitions. Almost every `XrdXrootd` execution module includes this header.

## Risks and edge cases

The class has a very large mutable surface; invariants are distributed across many `.cc` files. Static configuration makes unit isolation difficult. Member-function pointers in `Resume` and `ResumePio` must only reference methods valid for the current state. The copy assignment operator is deleted, but the object still has manual `Assign()`/pooling patterns that require careful reset/cleanup.

## Test signals

Tests should focus on externally visible protocol behavior: login/auth gates, dispatch table coverage, async and sendfile thresholds, TLS policy enforcement, bound-stream behavior, cleanup idempotence, and stats counters. Static config parser tests are also important because many handlers depend on process-wide members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdProtocol.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.cc

## Purpose

This file implements the process-wide adapter around `XrdXrootdRedirPI`. It centralizes plugin invocation, host/CGI or URL parsing, target network-address caching, TTL refresh, and conversion of plugin string replies into `Outcome`.

## Important APIs, types, and functions

`Init()` stores the plugin, logger, and IP hold time. `IsActive()` reports whether a plugin exists. `Redirect()` handles host and URL redirect forms. `ParseURL()` splits `scheme://host[:port][/tail]`. `SetClockForTesting()` replaces the clock for cache tests. Internal `LookupTarget()` owns a static `std::map` of `netInfo` entries with `XrdNetAddr`, expiry, mutex, and atomic refs.

## Control flow

For host-form redirects (`port >= 0`), `Redirect()` validates the port, splits `host?cgi`, resolves/caches the target address, calls `plugin->Redirect()`, and commits a rewritten port only when the plugin returns a replacement. For URL-form redirects (`port < 0`), it parses URL components, resolves the host, calls `RedirectURL()`, and leaves the negative option value unchanged. Empty plugin replies map to `Unchanged`, `!message` maps to `Error`, and other strings map to `Replaced`.

## State and persistence behavior

State is static and in-memory only: the plugin/logger pointers, TTL, test clock, and unbounded target-address cache. Cache entries are immortal once inserted, refresh after `gIPHold`, and keep the previous good address if refresh fails.

## Dependencies and integration points

The file depends on `XrdNetAddr`, `XrdNetAddrInfo`, private utility `splitHostCgi`, logger and mutex/atomic helpers, and `XrdXrootdRedirPI`. It is called from xroot redirect execution and shared with HTTP TPC redirect logic.

## Risks and edge cases

`Init()` writes globals without locking and assumes it runs before workers call `Redirect()`. The cache is intentionally unbounded; acceptable for a small redirect-target set but risky if targets are attacker-controlled. URL parsing is simple and does not fully handle IPv6 bracket semantics or malformed authorities. On first DNS failure, redirects silently remain unchanged except for logs.

## Test signals

Tests should cover host CGI splitting, port range validation, URL parse success/failure, empty/replacement/error plugin replies, port rewrite semantics, DNS failure fallback, TTL refresh, stale-address reuse on refresh failure, and test-clock restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.hh

## Purpose

This header documents and declares the shared redirect-plugin helper. It gives protocol and non-protocol subsystems one thread-safe API for optional redirect rewriting.

## Important APIs, types, and functions

`Outcome` is the tri-state result: `Unchanged`, `Replaced`, or `Error`. `Init()` registers the plugin, logger, and address-cache TTL. `IsActive()` is a cheap plugin-presence check. `Redirect()` invokes either host or URL plugin methods based on `port`. `ParseURL()` is exposed for unit tests. `SetClockForTesting()` is an explicit test-only hook.

## Control flow

Callers initialize once after loading `redirlib`. At redirect time they pass a target, mutable port/options integer, client address, and output strings. The helper normalizes plugin behavior so callers do not duplicate string-contract or DNS-cache logic.

## State and persistence behavior

The header declares only static behavior. Implementation state is process-wide and in-memory; no redirect decisions are persisted.

## Dependencies and integration points

It forward-declares `XrdNetAddrInfo`, `XrdSysError`, and `XrdXrootdRedirPI` to avoid exposing implementation details. It integrates with `XrdXrootdProtocol::fsRedirPI()` and HTTP TPC handling.

## Risks and edge cases

The API uses a mutable `int &port` for two meanings: host-form port and URL-form redirect options. Callers must follow the documented sign convention. The test clock hook is process-global and must never be used by production code.

## Test signals

Header-level tests should pin the public contract: no plugin means unchanged, host form can mutate port, URL form cannot, error messages have the leading `!` stripped, and `ParseURL()` handles the intended grammar.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirPI.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirPI.hh

## Purpose

This header defines the redirect plugin interface for xrootd. A plugin can rewrite redirect targets based on original target address, client address, port, CGI data, and URL components.

## Important APIs, types, and functions

`Redirect()` is the required host-form method. `RedirectURL()` is optional and defaults to no rewrite. `XrdXrootdRedirPI_Args` and `XrdXrootdRedirPI_t` define the C factory signature `XrdXrootGetdRedirPI()`, including previous plugin pointer, logger, parameters, config path, and environment.

## Control flow

The server loads a shared plugin, calls its factory, and passes the resulting object to `XrdXrootdRedirHelper`. For each redirect, the helper calls `Redirect()` or `RedirectURL()`. A non-empty reply replaces the target; an empty reply keeps the original; a reply beginning with `!` reports a fatal error message to the client.

## State and persistence behavior

The interface owns no state. Concrete plugins may keep configuration or caches; ownership is external to this header.

## Dependencies and integration points

It depends on C++ `std::string`, `uint16_t`, and forward-declared XRootD network/logger/environment types. It integrates with plugin loading, compatibility checks via `XrdVERSIONINFO`, and the redirect helper.

## Risks and edge cases

Plugin authors must include CGI data in replacement host targets when needed. `RedirectURL()` should not change the original protocol. The factory comment mistakenly says "file system object" in its return description, but the typedef correctly returns `XrdXrootdRedirPI *`.

## Test signals

Tests belong mostly to helper/plugin integration: factory loading, chaining via `prevPI`, reply-string interpretation, URL default no-op behavior, and compatibility metadata enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdRedirPI.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdReqID.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdReqID.hh

## Purpose

`XrdXrootdReqID` packs the information needed to route an asynchronous response back to the correct link and stream. It overlays a 64-bit id with link instance, link id/file descriptor, and two-byte stream id fields.

## Important APIs, types, and functions

`getID()` returns the packed 64-bit value. The overload `getID(unsigned char *sid, int &lid, unsigned int &linst)` decodes fields. `setID()` overloads set the packed id, set decoded fields, or update only the stream id. `Stream()` returns a pointer to the stored stream bytes.

## Control flow

Request handlers store the current stream id in `ReqID`. Async callback paths later decode the id, map the link id/instance through `XrdLinkCtl`, and send an attention/asynchronous response to the original client or bridge.

## State and persistence behavior

The state is a single union value in memory. It is not portable durable data; field layout depends on the local ABI and is used only within the process.

## Dependencies and integration points

It depends on `cstring` for `memcpy` and is included by `XrdXrootdProtocol`, `XrdXrootdResponse`, job/callback code, and async response logic.

## Risks and edge cases

The constructor `XrdXrootdReqID(const unsigned char *sid, ...)` appears to pass a null pointer to `setID()` when `sid` is non-null and `"\0\0"` when it is null, which is suspicious and should be verified against compiler warnings/tests. The union layout assumes the same endian/packing for encode and decode inside one process.

## Test signals

Tests should round-trip stream id, link id, and instance values; validate packed-id preservation; exercise default construction before use; and specifically cover the pointer conditional in the stream/link constructor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdReqID.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.cc

## Purpose

This file serializes xroot server responses. It supports ordinary OK/error/data responses, redirect/status responses, sendfile payloads, bridged `XrdXrootdTransit` callbacks, and delayed asynchronous attention responses.

## Important APIs, types, and functions

`Send()` overloads build `ServerResponseHeader` plus optional data, iovec, error code, info integer, file descriptor, sendfile vector, or `ServerResponseStatus`. The static `Send(XrdXrootdReqID&, XResponseType, iovec*, ...)` sends async attention responses. `Set()` stores stream id and trace string. `srsComplete()` fills status response bodies and computes CRC32C.

## Control flow

Every send path first traces the outgoing response, prepares network byte order fields, and either calls the active bridge or writes to `XrdLink`. For sendfile, the header is inserted as the first vector and file regions follow. Static async send decodes `ReqID` to a live link, references it, checks link instance, and sends either a bridged attention response through `XrdXrootdTransit::Attn()` or a direct `kXR_attn/kXR_asynresp` envelope.

## State and persistence behavior

`XrdXrootdResponse` stores the current link, optional transit bridge, reusable header, iovec scratch array, and trace stream id. It does not persist data; it only formats outbound wire messages.

## Dependencies and integration points

The file depends on `XrdLink`, `XrdLinkCtl`, CRC utilities, protocol wire structs, tracing, request ids, and `XrdXrootdTransit`. It is used by protocol handlers, jobs, callbacks, async I/O, stats, and transit bridge code.

## Risks and edge cases

All length/status fields must be converted correctly to network byte order. Several bridge branches pass `dlen` or `ioLen` values to callbacks, so mismatched iovec length accounting can corrupt client-visible payload boundaries. Static async sends must handle stale file descriptors or recycled link instances safely; instance checking is critical.

## Test signals

Tests should cover OK/error/redirect/iovec/status/sendfile serialization, bridge-vs-direct behavior, CRC32C in status responses, async response routing to direct and bridged links, stale link instance rejection, and stream-id trace formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.hh

## Purpose

This header declares the response writer used by xroot protocol handlers. It abstracts the difference between writing to a client `XrdLink` and returning results through a transit bridge.

## Important APIs, types, and functions

The class exposes overloads for success, message, error, raw data, iovec data, typed response data, redirects/info responses, sendfile, status responses, and static async response sends. `Set()` binds either an `XrdLink`, an `XrdXrootdTransit`, or a stream id. `isOurs()` distinguishes direct-link responses from bridged ones.

## Control flow

Protocol handlers set the stream id from the current request, then call the appropriate `Send()` overload. The implementation fills `Resp` and writes through the link or bridge. Static send is used by job/callback code that only has a packed `ReqID`.

## State and persistence behavior

The class owns no payload memory. It keeps a reusable header and small iovec array, borrowing caller data during send. It has no durable state.

## Dependencies and integration points

It depends on wire protocol types, `XrdXrootdReqID`, `XrdLink`, `XrdXrootdTransit`, and `XrdOucSFVec`. It is embedded in `XrdXrootdProtocol` and used across job, callback, async, stats, and bridge paths.

## Risks and edge cases

Borrowed buffers must remain valid for the duration of synchronous `Link->Send()`. Copy/assignment copy link, bridge, and stream id but not any ownership, so response objects are lightweight handles. Sendfile methods assume sendfile enablement has already been checked by callers.

## Test signals

Compile and behavioral tests should verify overload selection, bridge/direct path switching, stream-id preservation after copy/assignment, and async static send integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdResponse.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.cc

## Purpose

This file implements xroot protocol statistics formatting and response delivery. It produces the protocol XML stats block and delegates option-driven global stats collection to `XrdStats`.

## Important APIs, types, and functions

The constructor initializes every counter. `Stats(char *buff, int blen, int do_sync)` formats `<stats id="xrootd">...` XML, optionally returning maximum size when `buff` is null. `Stats(XrdXrootdResponse&, const char *opts)` maps option characters to `XRD_STATS_*` flags and streams the global stats response through an inner callback.

## Control flow

Protocol code updates counters directly and may first synchronize per-link counts into `SI`. When queried, `Stats()` locks `statsMutex`, snapshots counters into XML, unlocks, then appends filesystem stats if configured. The response overload returns simple OK when no option flags are requested, otherwise asks `XrdStats` to call back with buffers or iovecs and sends them through `XrdXrootdResponse`.

## State and persistence behavior

Stats are in-memory counters only. Filesystem stats are pulled live from `fsP`; global server stats are pulled from `xstats`. No counters are persisted across process restart.

## Dependencies and integration points

It depends on `XrdStats`, `XrdSfsFileSystem`, and `XrdXrootdResponse`. It integrates with protocol `Stats()`, query handlers, monitoring, and filesystem stats providers.

## Risks and edge cases

Counter updates outside `statsMutex` can be approximate; some fields are accumulated per-link before sync. XML is produced with `snprintf`; callers must respect the size query path. JSON stats are explicitly not enabled for `J` in this parser.

## Test signals

Tests should verify counter initialization, XML content and size-query behavior, filesystem stats appending, option-to-flag mapping, callback response paths for buffer and iovec, and no-option OK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.hh

## Purpose

This header declares `XrdXrootdStats`, the protocol-specific counter block and stats responder for xrootd.

## Important APIs, types, and functions

Counters cover matches, errors, redirects, stalls, get/put file, opens, reads, prereads, readv/writev segments, writes, sync, misc operations, async operations, refresh requests, login/auth outcomes, and signature outcomes. Public methods are `setFS()`, `Stats(char*, int, int)`, and `Stats(XrdXrootdResponse&, const char*)`.

## Control flow

Protocol instances update counters during request execution and synchronize per-link counters into the shared stats object. Query paths call `Stats()` to serialize counters or proxy to the global `XrdStats` object.

## State and persistence behavior

All fields are process memory. `statsMutex` is inherited from `XrdOucStats` and protects formatted snapshots and selected aggregate updates.

## Dependencies and integration points

The header depends on `XrdOucStats` and forward-declared filesystem/global stats/response types. It is referenced from protocol, async, callback, configuration, and execution files.

## Risks and edge cases

Public mutable counters are simple and fast but allow unsynchronized updates. Consumers should treat them as operational telemetry rather than exact transactional accounting.

## Test signals

Tests should ensure every counter appears in XML, filesystem stats are optional, and query options exercise global stats integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdStats.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.cc

## Purpose

This file emits third-party-copy monitoring records as JSON lines into an `XrdXrootdGStream`. It normalizes local path specs into full URLs, formats timestamps, and reports copy direction, protocol, client, streams, IP family, return code, and size.

## Important APIs, types, and functions

The constructor initializes logging and captures `XRDHOST[:XRDPORT]` into a static `hostport`. `getURL()` converts path-like specs into `<protocol>://<hostport>/<path>`. `getUTC()` formats `timeval` as UTC ISO-like strings. `Report()` builds JSON from `TpcInfo` and inserts it into `gStream`.

## Control flow

TPC code fills `TpcInfo`, including begin/end times and URLs, then calls `Report()`. `Report()` resolves source/destination display URLs, formats begin/end timestamps, builds a JSON object with push/pull and IPv4/IPv6 indicators, warns if truncated, and inserts the null-terminated message into the stream.

## State and persistence behavior

`hostport` is static process memory initialized from environment and intentionally leaked for process lifetime. Reports are transient inserts into `XrdXrootdGStream`; persistence depends on the configured stream consumer.

## Dependencies and integration points

The file depends on `XrdSysError`, `XrdXrootdGStream`, and `XrdXrootdTpcMon`. It is configured from monitoring setup and used by TPC transfer paths.

## Risks and edge cases

`getURL()` produces `protocol://hostport//path` for a path beginning with `/` because the format includes `/%s`; this may be intended by existing consumers but should be checked. JSON strings are not escaped, so quotes or control characters in client IDs or URLs can produce invalid JSON. Timestamp milliseconds use `tv_usec` directly with `%03u`, which prints microseconds as at least three digits rather than dividing to milliseconds.

## Test signals

Tests should cover env-derived hostport, local path URL normalization, external URL pass-through, UTC formatting, truncation warning, gStream rejection warning, JSON escaping expectations, and push/pull plus IP-family flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.hh

## Purpose

This header declares the TPC monitoring reporter and its event payload. It gives transfer code a compact structure for reporting completed third-party-copy activity.

## Important APIs, types, and functions

`TpcInfo` contains client id, begin/end `timeval`, source/destination URL specs, file size, ending return code, options, stream count, and reserved byte. `isaPush` and `isIPv4` option bits describe transfer direction and IP family. `Init()` resets defaults. `XrdXrootdTpcMon::Report()` emits one event.

## Control flow

Callers construct or reuse `TpcInfo`, call `Init()`, fill transfer fields, and pass it to `Report()`. The reporter uses its configured protocol and gStream sink.

## State and persistence behavior

The reporter stores a borrowed protocol string and a reference to `XrdXrootdGStream`. The destructor is private because instances are intended to live for process/configuration lifetime.

## Dependencies and integration points

It forward-declares logger and gStream types and is configured by xrootd monitoring code. TPC handlers depend on the payload schema.

## Risks and edge cases

`size_t fSize` formatting and downstream JSON consumers must agree on width. Default strings are empty string literals, so callers should not mutate them. The private destructor prevents stack allocation by ordinary callers.

## Test signals

Tests should verify `Init()` defaults, option bit interpretation, reporter construction with a gStream, and schema stability of emitted records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTpcMon.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTrace.hh

## Purpose

This header defines trace bit flags and trace macros for the xroot protocol subsystem. It provides low-overhead conditional logging that compiles out under `NODEBUG`.

## Important APIs, types, and functions

Trace flags include `TRACE_DEBUG`, `TRACE_EMSG`, `TRACE_FS`, `TRACE_LOGIN`, `TRACE_MEM`, `TRACE_REQ`, `TRACE_REDIR`, `TRACE_RSP`, `TRACE_STALL`, `TRACE_AUTH`, `TRACE_FSIO`, `TRACE_FSAIO`, and `TRACE_PGCS`. Macros `TRACE`, `TRACEI`, `TRACEP`, and `TRACES` wrap `SYSTRACE` with different link/request-id contexts. `TRACING(x)` tests enabled flags.

## Control flow

Code sets a local `TraceID` and, when needed, `TRACELINK`. A macro checks `XrdXrootdTrace.What` for the requested flag and emits a structured trace message. In release/no-debug builds the macros become no-ops.

## State and persistence behavior

The header uses the external global `XrdXrootdTrace`; it persists no state itself. Trace output persistence depends on the configured XRootD logger.

## Dependencies and integration points

It depends on `XrdSysTrace` and `XrdSysHeaders` when debugging is enabled. It is included across protocol, prepare, response, transit, and execution modules.

## Risks and edge cases

Macros require caller-side identifiers such as `TraceID`, `TRACELINK`, `Response`, or `trsid` to exist for specific variants. This keeps call sites terse but makes misuse a compile-time or context error. Side effects in trace expressions are skipped when the flag is disabled.

## Test signals

Signals are mostly compile/configuration checks: all macro variants compile in representative contexts, no-debug builds remove trace dependencies, and trace flag parsing enables the expected bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.cc

## Purpose

This file implements the global pending-request queue used by `XrdXrootdTransit` for `kXR_waitresp` bridge operations. It stores a request until an asynchronous attention response arrives.

## Important APIs, types, and functions

`Queue()` pushes an item onto `rqstQ`. `Remove(XrdLink*, short sid)` removes the first matching pending request by link and stream id. `Clear(XrdXrootdTransit*)` deletes all pending requests owned by a transit object. Static state is protected by `myMutex`.

## Control flow

When a bridged request receives `waitresp`, transit code allocates `XrdXrootdTransPend`, copies the request, and queues it. Later `XrdXrootdTransit::Attn()` calls `Remove()` with the link and stream id from the attention response; if found, transit resumes using the stored request. Recycle/disconnect calls `Clear()` to avoid dangling pending work.

## State and persistence behavior

The queue is process memory only. Each node owns a copied `ClientRequest` and borrowed link/bridge pointers. There is no timeout in this file; lifetime is controlled by attention arrival or bridge cleanup.

## Dependencies and integration points

It depends on protocol wire structs, `XrdSysMutex`, `XrdLink`, and `XrdXrootdTransit`. It is tightly coupled to `XrdXrootdResponse::Send()` async attention routing.

## Risks and edge cases

The queue is a simple LIFO singly linked list and linear search; many pending waitresp requests could make attention delivery O(n). Matching uses a `short` stream id view over the two stream bytes, so byte-order consistency with the sender is essential. If attention never arrives and cleanup is missed, entries leak until transit recycle.

## Test signals

Tests should cover queue/remove order, non-matching link or stream id, clear-by-bridge, concurrent queue/remove, and attention after recycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.hh

## Purpose

This header declares the pending-transit request node used to bridge delayed xroot responses back to an injected request.

## Important APIs, types, and functions

`XrdXrootdTransPend` stores `next`, `link`, `bridge`, and a union containing either the copied `ClientRequest` or a `short` stream id view. Public methods are `Queue()`, static `Remove()`, and static `Clear()`.

## Control flow

Transit wait-response handling creates a node from the current link, bridge, and request. The node is queued globally. Async response handling removes it by link and stream id, then uses the copied request to restore transit state.

## State and persistence behavior

Nodes are heap-allocated transient state. The static queue is process memory and is mutex-protected in the implementation.

## Dependencies and integration points

The header depends on `XProtocol.hh`, `XrdSysPthread.hh`, `XrdLink`, and `XrdXrootdTransit`. It is used only by transit bridge code.

## Risks and edge cases

The union overlay assumes the stream id occupies the same leading bytes in the copied request representation used by `Remove()`. That should be validated on all supported platforms. Ownership is manual; callers must delete removed nodes or clear them.

## Test signals

Tests should validate stream id matching through the union, lifecycle ownership, and bridge cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransPend.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.cc

## Purpose

This file adapts bridged file responses into an `XrdLink::sfVec` sendfile operation. It lets bridge result callbacks send protocol headers/trailers plus one or more file regions.

## Important APIs, types, and functions

`XrdXrootdTransSend::Send(const iovec *headP, int headN, const iovec *tailP, int tailN)` builds a dynamic `sfVec` array from optional header iovecs, the stored file region(s), and optional trailer iovecs, then calls `linkP->Send(sfVec, numV)`.

## Control flow

For a single file descriptor, the method inserts one file segment with `sfOff`, `sfLen`, and `sfFD`. For an existing `XrdOucSFVec`, it copies file entries starting at index 1 because index 0 is reserved for a protocol header in normal response code. It deletes the temporary vector after the send.

## State and persistence behavior

The object stores borrowed file-vector or fd information from construction. It performs no persistence and does not own the underlying file descriptors.

## Dependencies and integration points

It depends on `XrdLink` and `XrdXrootdTransSend.hh`. It is created by `XrdXrootdTransit::Send()` when the protocol response uses sendfile.

## Risks and edge cases

The allocation size for vector-backed sends uses `numV - sfFD` while the send call passes `numV`; because `sfFD` is negative `sfvnum`, this allocates extra space but sends only `headN + tailN + 1` entries, potentially omitting copied file-vector entries if `sfvnum` is greater than one. This should be reviewed with actual `sfVec` expectations. Borrowed file descriptors must remain valid during the send.

## Test signals

Tests should cover single-fd sendfile, multi-vector sendfile, header/trailer inclusion, correct vector count passed to `XrdLink::Send`, and failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.hh

## Purpose

This header declares `XrdXrootdTransSend`, a `Bridge::Context` subclass that carries sendfile metadata for bridged file responses.

## Important APIs, types, and functions

Two constructors capture either a single `fdnum/offset/dlen` or an `XrdOucSFVec` array plus count and length. `Send()` is the bridge callback method that writes headers, file regions, and trailers to the underlying link.

## Control flow

`XrdXrootdTransit` constructs this context when a protocol handler emits sendfile output through a bridge. The bridge result object calls `Send()` to actually transfer file bytes.

## State and persistence behavior

State is transient and borrows the link and file metadata. The union stores either an offset or a pointer to the original sendfile vector; `sfFD` is positive for single fd and negative for vector count.

## Dependencies and integration points

It depends on `XrdXrootdBridge.hh`, `XPtypes.hh`, and `sys/uio.h`, plus forward-declared `XrdLink`. It integrates with transit bridge file callbacks.

## Risks and edge cases

The sign-overloaded `sfFD` is compact but easy to misuse. The vector constructor borrows `sfvec`; callers must ensure it remains valid until `Send()` completes.

## Test signals

Tests should verify constructor mode selection, context stream/request metadata, and send behavior for both single and vector file paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransSend.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.cc -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.cc

## Purpose

This file implements `XrdXrootdTransit`, the bridge that lets another protocol inject xroot requests into the xroot protocol stack and receive results through a `Bridge::Result` callback instead of raw socket responses.

## Important APIs, types, and functions

`Alloc()` obtains and initializes a transit object. `Init()` has static and per-instance forms. `Run()` accepts an xroot request header and optional data. `Process()` interleaves the real protocol and injected xroot request. `Send()` overloads translate xroot responses into bridge callbacks. `Wait()`, `WaitResp()`, `Redrive()`, `Proceed()`, `Attn()`, and `AttnCont()` handle wait and async response flows. `Disc()` and `Recycle()` dismantle the bridge.

## Control flow

Initialization binds the transit protocol to the link, arms bridge mode, sets security/entity fields, registers monitoring, and marks the session logged in. `Run()` validates the request against `ReqTable()`, unmarshals lengths, copies arguments into `argp`, handles partial write data specially, and marks the bridge active. `Process()` lets the original protocol run, then dispatches the injected request through `XrdXrootdProtocol::Process()` or `Process2()`. Normal responses call `Bridge::Result` methods for data, done, errors, redirects, waits, or files.

## State and persistence behavior

Transit stores borrowed real protocol/result/link/security pointers, copied request arguments for redrive, wait counters, wait condition state, run status atomics, and monitor/client identity inherited from `XrdXrootdProtocol`. It has no durable persistence; it only mediates live requests. Pending `waitresp` state is stored in `XrdXrootdTransPend`.

## Dependencies and integration points

It depends on security entities, links, buffers, SFS, scheduler, stats, tracing, pending queue, sendfile adapter, and the base protocol class. It is used by protocol bridge APIs and by static response attention routing.

## Risks and edge cases

Concurrency is delicate: `runStatus`, `runWait`, `waitPend`, scheduled jobs, and recycle/disconnect must agree to prevent re-entry or use-after-free. `Run()` returns `true` even after some validation failures by storing `runError`, so callers must drive processing to receive the error callback. Wait-time accounting can cancel long waits with `kXR_Cancelled`. Partial write bridging depends on `do_WriteSpan` and buffer lifetime callbacks.

## Test signals

Tests should cover supported/unsupported request table entries, argument copy and redrive after wait, wait notification and timeout behavior, waitresp attention completion, recycle while waiting, bridge error/data/done/redir/file callbacks, re-entry rejection, and disconnect restoration of the original protocol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.hh -->
# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.hh

## Purpose

This header declares `XrdXrootdTransit`, a concrete `XrdXrootd::Bridge` implemented by subclassing `XrdXrootdProtocol`. It allows in-process protocol bridging while reusing xroot request handlers.

## Important APIs, types, and functions

Public methods include `Alloc()`, static `Init()`, `ReqTable()`, `Run()`, `Process()`, `Recycle()`, `Disc()`, `Proceed()`, `Redrive()`, `Attn()`, `Send()` overloads, `setSF()`, and `SetWait()`. Private helpers include `Fail()`, `Fatal()`, `ReqWrite()`, `RunCopy()`, `Wait()`, and `WaitResp()`. Nested `SchedReq` adapts member callbacks to `XrdJob`.

## Control flow

The bridge is allocated from `TranStack`, initialized with a link and result callback, substitutes itself as the link protocol, and accepts one active injected request at a time. Scheduled jobs resume after waits or after deferred processing.

## State and persistence behavior

Private state tracks the original protocol, result object, copied args, run status, wait totals/max, reinvocation flags, write buffers, protocol name, creation time, and wait condition variables. All state is per-live bridge object and in-memory.

## Dependencies and integration points

The header depends on atomics, XRootD object pools, bridge interfaces, scheduler jobs, and `XrdXrootdProtocol`. It integrates with `XrdXrootdTransPend`, `XrdXrootdTransSend`, and response async routing.

## Risks and edge cases

Subclassing the full protocol object gives reuse but also inherits a large amount of mutable session state. Only one active bridged request is allowed; callers must handle `Run()` failure on re-entry. Wait scheduling and condition-variable state must be cleaned during recycle.

## Test signals

Tests should validate object-pool reuse, one-request-at-a-time enforcement, wait settings, callback scheduling, and cleanup of pending wait state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTransit.hh -->
