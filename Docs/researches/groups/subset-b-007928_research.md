# subset-b-007928 grouped research

Work item: `subset-b-007928`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.hh

## Purpose

This header defines the public response/result data model used by the XRootD client layer. It gives higher-level `File`, `FileSystem`, async readers, message handlers, copy jobs, ZIP archive helpers, and EC handlers typed wrappers around raw XRoot protocol replies: locate results, protocol info, stat and VFS stat results, directory listings, open results, read/page-read/vector-read payload descriptions, host redirect lists, extended attribute replies, and callback interfaces.

The file is declaration-heavy; parsing and PIMPL bodies live in `XrdClXRootDResponses.cc`, while this header fixes the object ownership, status shape, iterator API, and callback contract that most of `src/XrdCl` includes.

## Important APIs, types, and functions

- `LocationInfo` stores parsed `kXR_locate` locations. Nested `Location` records carry an address, `LocationType` (`ManagerOnline`, `ManagerPending`, `ServerOnline`, `ServerPending`), and `AccessType` (`Read`, `ReadWrite`). `ParseServerResponse()` and private `ProcessLocation()` populate the vector.
- `XRootDStatus` extends `Status` with a server/error message string, `GetErrorMessage()`, `SetErrorMessage()`, and `ToStr()`. For `errErrorResponse`, `ToStr()` formats the server error number and message.
- `xattr_t`, `XAttrStatus`, and `XAttr` represent extended attribute name/value/status results. `FileStateHandler` and `FileSystem` are friends because they construct and fill these response objects.
- `BinaryDataInfo` is an alias for `Buffer`, used when a response body is opaque bytes.
- `ProtocolInfo` carries XRoot protocol version and host/server flags, exposing `GetVersion()`, `GetHostInfo()`, and `TestHostInfo()`.
- `StatInfo` is the main file metadata object. It uses `std::unique_ptr<StatInfoImpl>` and exposes id, size, flags, modification/change/access times, mode, owner, group, checksum, `ParseServerResponse()`, `ExtendedFormat()`, and `HasChecksum()`.
- `StatInfoVFS` stores `kXR_vfs` values: read/write nodes/free/utilization and staging nodes/free/utilization, filled by `ParseServerResponse()`.
- `DirectoryList` owns a vector of heap-allocated `ListEntry` objects. `ListEntry` owns an optional `StatInfo*`, strips leading slashes from entry names, and exposes host/name/stat accessors. The list parses plain and stat-rich directory responses and has `HasStatInfo()` to classify server payloads.
- `OpenInfo` owns optional `StatInfo*` and stores the four-byte file handle plus 64-bit session id returned from open.
- `ChunkInfo`, `PageInfo`, `RetryInfo`, `TractInfo`, `ChunkList`, `TractList`, and `VectorReadInfo` model read-like results: byte chunks, page-read data plus CRC checksums/repair count, retry page ranges, vector preread tracts, and vector-read aggregate size/chunks.
- `HostInfo` and `HostList` describe redirected hosts, including flags, protocol version, whether the entry came from a load balancer, and its `URL`.
- `ResponseHandler` is the async callback base class. `HandleResponseWithHosts()` defaults to deleting `HostList` and delegating to `HandleResponse()`. Static `Wrap()` factories adapt lambdas taking either references or pointers.

## Control flow

Consumers normally receive raw protocol bodies in `XrdClXRootDMsgHandler.cc`, allocate one of these response objects, invoke a `ParseServerResponse()` method when required, wrap it in `AnyObject`, and pass it to a `ResponseHandler`. File-system convenience APIs then unwrap these types or expose them to the caller.

The response ownership flow is deliberately explicit. Many objects are allocated with `new` and transferred through `AnyObject` or callbacks. `DirectoryList` and `OpenInfo` destructors delete nested entries/stat info; `ResponseHandler::HandleResponseWithHosts()` deletes the host list by default; lambda wrappers in the `.cc` implementation are responsible for deleting or forwarding status/response pointers according to their callback flavor.

`StatInfo`, `PageInfo`, and `RetryInfo` hide internal layout behind PIMPLs, which keeps this public header stable while allowing the implementation file to change parser/storage details. Helper methods such as `TimeToString()` and `OctToString()` centralize presentation of metadata parsed elsewhere.

## State and persistence behavior

All state is in-memory response state. There is no filesystem persistence here. The main persistent-like behavior is ownership/lifetime: `DirectoryList` owns `ListEntry*`; each `ListEntry` owns its `StatInfo*`; `OpenInfo` owns its optional `StatInfo*`; `StatInfo`, `PageInfo`, and `RetryInfo` own their PIMPLs. `LocationInfo` and `VectorReadInfo` use value vectors. `XRootDStatus` stores an additional message string alongside the inherited status fields.

Because these objects cross asynchronous boundaries, their destructors and pointer ownership are integration-critical. A caller that passes a raw `StatInfo*` into `ListEntry`, or a `ListEntry*` into `DirectoryList::Add()`, gives up ownership.

## Dependencies and integration points

The header depends on `XrdClBuffer.hh`, `XrdClStatus.hh`, `XrdClURL.hh`, `XrdClAnyObject.hh`, `XProtocol/XProtocol.hh`, STL containers, tuples, function wrappers, and `sys/uio.h`. It is widely included by client subsystems including `XrdClFile.hh`, `XrdClFileSystem.hh`, `XrdClFileStateHandler`, async reader/writer classes, socket/message queue code, message handlers, ZIP cache/archive code, EC helpers, and copy utilities.

Protocol constants from `XProtocol.hh` define many enum values, especially stat flags and protocol host flags. The concrete parser implementation in `XrdClXRootDResponses.cc` is therefore part of the behavioral contract even though the declarations live here.

## Risks and edge cases

- Raw pointer ownership is easy to misuse. `DirectoryList::ListEntry::SetStatInfo()` overwrites `pStatInfo` without deleting an existing pointer, so callers must avoid replacing owned stat info after construction unless they have handled the old pointer.
- `At()` methods do not bounds-check, so callers must validate sizes.
- `ResponseHandler` default methods do nothing except host-list deletion; missing overrides can silently drop responses.
- `XRootDStatus::ToStr()` special-cases only `errErrorResponse`; other server-message statuses append the message to `Status::ToString()`.
- `TimeToString()` uses `gmtime()` and `strftime()` without explicit null checks; invalid or platform-problematic time values would format poorly.
- The response parsers declared here consume text/binary server formats; malformed responses must be rejected in the `.cc` implementation, not in this header.
- Many response objects are mutable and not intrinsically synchronized. They should be populated before callback handoff or otherwise externally protected.

## Test signals

Useful tests should cover parser success/failure for locate, stat extended/basic formats, VFS stats, directory lists with and without stat blocks, page-read retry/checksum containers, and lambda `ResponseHandler::Wrap()` ownership behavior. Integration signals appear in `XrdClXRootDMsgHandler.cc` paths that call these parsers and in `XrdClFS.cc`/`XrdClFileSystem.cc` code that consumes `StatInfo`, `DirectoryList`, and `LocationInfo`. Memory-safety tests are valuable around destructor ownership and repeated callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.cc

## Purpose

This file implements the XRootD client transport handler. It owns message framing over nonblocking sockets, XRoot protocol handshake/login/authentication/bind state machines, TLS/protection decisions, request marshalling and response unmarshalling, multiplexing over substreams, connection idleness/brokenness checks, request signing, stream disconnect cleanup, and request-description logging.

It is the main protocol glue between `PostMaster`/socket infrastructure and XRoot protocol structs from `XProtocol.hh`.

## Important APIs, types, and functions

- `PluginUnloadHandler` registers an `atexit` callback for `root`/`xroot` transport handlers and uses an RW lock plus `unloaded` flag to prevent security plugin use during unload.
- `XRootDStreamInfo` tracks each substream status (`Disconnected`, `Broken`, `HandShakeSent`, `HandShakeReceived`, `LoginSent`, `AuthSent`, `BindSent`, `EndSessionSent`, `Connected`), protocol path id, and per-stream server flags.
- `StreamSelector` tracks outstanding response counts per data substream and selects the least-loaded connected stream for reads/page reads/readv responses.
- `BindPrefSelector` cycles through server-advertised bind-preference URLs.
- `XRootDChannelInfo` is the per-channel state block stored in `AnyObject`: server flags, protocol version, current/old session ids, SID manager, authentication/protection objects, stream vector, sent-open/close SID tracking, file-instance/open-file counters, wait barrier, TLS/TPC flags, bind selector, login token, and mutex.
- `GetHeader()`, `GetBody()`, and `GetMore()` implement nonblocking response reads. They allocate/reallocate `Message` buffers, preserve cursor progress across `suRetry`, unmarshal headers and status-more bodies, and validate `kXR_status` sizes.
- `InitializeChannel()` creates `XRootDChannelInfo`, sizes substreams from `SubStreamsPerChannel`, initializes the stream selector, and derives secure/TPC/login-token flags from the URL.
- `HandShake()`, `HandShakeMain()`, `HandShakeParallel()`, and `HandShakeDone()` implement the connection state machines.
- `IsStreamTTLElapsed()` and `IsStreamBroken()` use env-configured TTL/timeout settings, open-file/file-instance counts, allocated/old SIDs, and wait barriers to decide whether streams can be disconnected or are likely broken.
- `MultiplexSubStream()` rewrites read-like requests to carry a selected response path id, then returns `(up, down)` `PathID`.
- `SubStreamNumber()` decides how many substreams to create, including TLS-control/plain-data cases that require at least a second stream.
- `MarshallRequest()`, `UnMarshallRequest()`, `UnMarshallBody()`, `UnMarshalStatusBody()`, `UnMarchalStatusMore()`, and `UnMarshallHeader()` do endian conversion and integrity checks for XRoot protocol structures.
- `MessageReceived()` updates substream load counters, wait barriers, timed-out SID handling, and open/close counters. It can request a close for an open response that arrived after the request timed out.
- `MessageSent()` records open/close SIDs so later responses can update counters.
- `GetSignature()` signs/protects requests through `XrdSecProtect` when the negotiated protection policy requires it.
- `NeedEncryption()` decides when TLS must be enabled based on user URL, `NoTlsOK`, stream status, and server flags such as `kXR_gotoTLS`, `kXR_tlsLogin`, `kXR_tlsSess`, and `kXR_tlsData`.
- Private generation/processing helpers build and parse handshake, protocol, bind, login, auth, and end-session messages.
- `GenerateDescription()` and `FileHandleToStr()` produce log descriptions for many request types.

## Control flow

Incoming messages are read in two or three phases. `GetHeader()` reads exactly eight bytes, unmarshals `status` and `dlen`, and reports `suDone`. `GetBody()` reads the advertised response body. For `kXR_status` page-operation responses, `GetMore()` accounts for the nested body length, reads the correction/data segment, and calls `UnMarchalStatusMore()` to validate CRC32C and endian-convert fields.

The main stream handshake starts from `Disconnected`/`Broken`, sends initial handshake plus `kXR_protocol`, processes server handshake, processes protocol response, sends `kXR_login`, handles login, optionally performs one or more auth exchanges, optionally sends `kXR_endsess` for a previous session, and finally marks stream 0 `Connected`. Protocol negotiation may return `suRetry` when `WantTlsOnNoPgrw` causes a second protocol request with TLS enabled.

Parallel data streams follow a shorter state machine: send initial handshake/protocol expecting bind, process handshake, process protocol, send `kXR_bind`, then store the server-assigned path id and become `Connected`.

Request multiplexing is conservative. All requests use upstream stream 0 by default. For `kXR_read`, `kXR_pgread`, and `kXR_readv`, the transport chooses a connected data stream for the response path and rewrites the request body/path id before remarshal. Writes, writev, and pgwrite have path-id code intentionally disabled because server-side write multiplexing is noted as not working properly.

Authentication starts after login advertises security data. The transport creates `XrdOucEnv` with socket/user/password and `xrd.`/`xrdcl.` URL parameters, creates `XrdSecParameters`, loads the security factory, iterates protocols until one returns credentials, sends `kXR_auth`, handles `kXR_authmore`, falls back to another protocol on server auth error, and installs `XrdSecProtect` if the protocol response advertised protection requirements.

TLS is negotiated as a state-dependent side effect. `InitProtocolReq()` advertises TLS ability/want flags based on user settings and `InitTLS()`. `NeedEncryption()` is called by the stream layer around handshake transitions to switch TLS before login, before bind, after login/session, or immediately on `gotoTLS`.

## State and persistence behavior

All transport state is per-channel in `XRootDChannelInfo` and guarded by `info->mutex` for most operations. Important mutable state includes:

- `stream` vector status/path ids/server flags per substream.
- Current and old 16-byte session ids, needed for reconnect/end-session cleanup.
- `sidManager` state owned by a shared manager pool keyed by URL channel id.
- `sentOpens` and `sentCloses` sets that map request SIDs to pending open/close accounting.
- `openFiles`, atomic `finstcnt`, and `waitBarrier`, which influence idle/broken stream decisions.
- Authentication objects (`authProtocol`, `authParams`, `authEnv`) and negotiated protection (`protection`, `protRespBody`, `protRespSize`).
- `encrypted`, `istpc`, bind preferences, stream name, auth protocol name, and login token.

There is no on-disk persistence. External process-global state includes the static security factory pointer in `GetAuthHandler()`, the `atexit` unload registration, environment settings read from `DefaultEnv`, and TLS/OpenSSL error queues cleared around auth.

## Dependencies and integration points

The implementation integrates with `XrdCl` socket/message/postmaster abstractions, `SIDManager`, `TransportManager`, `Tls`, `DefaultEnv`, logging, URL/env utilities, `XProtocol` wire structs/constants, `XrdNet` address utilities, `XrdOuc` CRC/token/env/error helpers, `XrdSec` authentication/protection plugins, `XrdSys` locks/timers/atomics/platform utilities, and the build version macro.

Upper layers call this through the `TransportHandler` interface declared in `XrdClXRootDTransport.hh`. Lower layers supply `Socket`, `Message`, and `HandShakeData`. Security plugins are loaded dynamically through `XrdSecLoadSecFactory()` and request protection through `XrdSecGetProtection()`.

## Risks and edge cases

- Wire-structure marshalling is broad and manual. Missing a new request type or using the wrong offset/length will produce protocol-incompatible messages.
- `UnMarshallRequest()` relies on symmetric marshalling and explicitly calls this ugly; any non-symmetric conversion change can break request rewriting.
- Several error-message paths allocate `new char[rsp->hdr.dlen-3]` and assume `dlen >= 4`; earlier unmarshalling checks cover some response classes but log paths still depend on valid server lengths.
- `MessageReceived()` dereferences `info` without a null check, unlike many other methods. A missing channel data object would crash.
- `Disconnect()` indexes `info->stream[subStreamId]` when the vector is not empty but does not bounds-check `subStreamId`.
- `DecFileInstCnt()` does not null-check `info` and does an unsynchronized load/subtract; it avoids underflow only by checking a relaxed load before `fetch_sub`.
- Authentication and protection lifetime is complex. `CleanUpProtection()` can call `CleanUpAuthentication()` only when `protection` exists, while plugin unload blocks operations through an RW lock and `unloaded` flag.
- TLS policy depends on multiple environment flags (`NoTlsOK`, `TlsNoData`, `WantTlsOnNoPgrw`) plus server protocol flags. Regression tests need matrix coverage.
- `GenerateEndSession()` combines signature and request buffers by grabbing memory from another `Message`; this depends on `Message::Grab()` semantics and can leak or alias incorrectly if those semantics change.
- `ProcessProtocolBody()` trusts protocol body tags and lengths after minimal checks; malformed bind/security requirement blocks are a security-sensitive parser surface.

## Test signals

Strong tests should include nonblocking partial header/body reads, invalid short response bodies, `kXR_status` CRC/request-id/stream-id mismatch detection, endian round-trips for every marshalled request type, handshake state transitions for main and data streams, protocol retry for TLS enforcement, auth-more/auth-failure protocol fallback, bind path-id assignment, open/close counter updates including `waitresp`, timed-out open response cleanup, stream TTL/broken decisions, request protection/signature generation, and request-description logging. Integration tests need real or mocked XRoot servers covering manager vs data server flags, TLS-required variants, and substream multiplexed reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.hh

## Purpose

This header declares `XrdCl::XRootDTransport`, the concrete `TransportHandler` for XRootD protocol channels. It exposes the transport contract used by the postmaster/network layer: message reading, channel initialization, handshake progress, stream health, multiplexing, marshalling/unmarshalling helpers, message notifications, protection signatures, TLS decisions, and bind preferences.

The declarations here define which parts of the large implementation in `XrdClXRootDTransport.cc` are public/static utility surface versus private handshake/auth helpers.

## Important APIs, types, and functions

- Public lifecycle and I/O overrides: constructor/destructor, `GetHeader()`, `GetBody()`, `GetMore()`, `InitializeChannel()`, `FinalizeChannel()`, `HandShake()`, and `HandShakeDone()`.
- Stream health and routing: `IsStreamTTLElapsed()`, `IsStreamBroken()`, `Multiplex()`, `MultiplexSubStream()`, `SubStreamNumber()`, and `NeedControlConnection()` which always returns `true`.
- Wire conversion helpers: static `MarshallRequest(Message*)`, `MarshallRequest(char*)`, `UnMarshallRequest()`, `UnMarshallBody()`, `UnMarshalStatusBody()`, `UnMarchalStatusMore()`, and `UnMarshallHeader()`.
- Diagnostics and state queries: `LogErrorResponse()`, `NbConnectedStrm()`, `Disconnect()`, `Query()`, `GenerateDescription()`, and inline `SetDescription()`.
- Message event hooks: `MessageReceived()` and `MessageSent()` let the transport update stream-selection and open/close accounting.
- Security/TLS hooks: `GetSignature(Message*, Message*&, AnyObject&)`, `GetSignature(Message*, Message*&, XRootDChannelInfo*)`, `WaitBeforeExit()`, `NeedEncryption()`, and private auth/protection cleanup/loading methods.
- File/channel accounting: `DecFileInstCnt()` decrements the channel-bound file object count.
- Bind routing: `GetBindPreference()` returns server-advertised bind-preference URLs when available.
- Private handshake helpers: `HandShakeMain()`, `HandShakeParallel()`, message generators/processors for initial handshake/protocol/bind/login/auth/end-session, `ProcessProtocolBody()`, `InitProtocolReq()`, `GetCredentials()`, `GetAuthHandler()`, `ServerFlagsToStr()`, and `FileHandleToStr()`.
- `PluginUnloadHandler` is forward-declared and friended so unload coordination can access private transport state.

## Control flow

The transport handler interface is event-driven. The postmaster repeatedly calls `GetHeader()`, `GetBody()`, and for page status responses `GetMore()` as nonblocking sockets become readable. It calls `HandShake()` with `HandShakeData` until the returned status indicates done or continuation; `HandShakeDone()` gives a boolean guard for stream readiness.

Outgoing messages are prepared by upper layers and then passed through `MarshallRequest()` and optional `SetDescription()`. Before send, the postmaster can ask `Multiplex()`/`MultiplexSubStream()` for `(up, down)` path routing and can request a protection message with `GetSignature()`. After send/receive, `MessageSent()` and `MessageReceived()` feed transport bookkeeping.

The private handshake helpers split the protocol into clear phases: main control stream login/auth/session handling and parallel data-stream bind handling. The public `NeedEncryption()` hook allows the surrounding stream implementation to turn TLS on at specific points selected by private state.

## State and persistence behavior

The header itself declares only one data member: `PluginUnloadHandler *pSecUnloadHandler`. All channel-specific mutable state is hidden behind the forward-declared `XRootDChannelInfo` stored in `AnyObject`, constructed in the `.cc` file. That separation keeps the public class size small while preserving a rich per-channel state machine internally.

There is no durable persistence. `WaitBeforeExit()` coordinates process shutdown for dynamically loaded security/protection code; `NeedControlConnection()` documents that data streams depend on the control connection.

## Dependencies and integration points

The header depends on `XrdClPostMaster.hh` for `TransportHandler`, `HandShakeData`, `PathID`, and query/action contracts; `XrdClMessage.hh`; `XProtocol/XProtocol.hh`; `XrdSec/XrdSecInterface.hh`; and `XrdOuc/XrdOucEnv.hh`. It forward-declares `Tls`, `Socket`, `XRootDChannelInfo`, `PluginUnloadHandler`, `XrdSysPlugin`, and `XrdSecProtect`.

Consumers include the XRootD transport manager, message readers/writers, postmaster, file/file-system state handlers, and any code using static marshalling/unmarshalling helpers or query IDs such as `XRootDQuery::ServerFlags`.

## Risks and edge cases

- The public static wire helpers operate on raw `char*`/`Message*` buffers and require callers to know whether data is already marshalled.
- `UnMarchalStatusMore` is misspelled in the API, so downstream code must use that exact symbol.
- `NeedControlConnection()` being hardcoded `true` means any future transport variant that can run independent data streams would need a new handler or override change.
- `FinalizeChannel()` is declared but implemented as a no-op; channel state lifetime is therefore likely owned by `AnyObject`/postmaster conventions outside this class.
- Forward declarations hide important state invariants from header readers. Correct use requires following the `.cc` implementation, especially for TLS/auth/protection and stream accounting.

## Test signals

Compile-level tests should catch signature drift between this header and `XrdClXRootDTransport.cc`. Behavioral tests should exercise every `TransportHandler` override through the postmaster abstraction rather than only static helpers, plus focused unit tests for static marshalling/unmarshalling helpers. Shutdown tests should cover `WaitBeforeExit()`/security unload behavior, while integration tests should confirm `NeedControlConnection()`, substream counts, multiplexing, and bind preferences behave correctly for manager, data-server, TPC, and TLS configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDTransport.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.cc

## Purpose

This file implements `XrdCl::ZipArchive`, a remote ZIP archive helper built on XRootD file operations. It can open an archive, parse the central directory including ZIP64 metadata, read entries by name with local-buffer or remote-read paths, support deflated-entry reads through `ZipCache`, list archive contents as `DirectoryList`, append new files, update metadata, serialize a new central directory, and close/commit changes.

It is an asynchronous pipeline-oriented bridge between XRootD remote file I/O and ZIP structure parsers from `XrdZip`.

## Important APIs, types, and functions

- Template `ReadFromImpl<RSP>()` is shared by `ReadFrom()` (`ChunkInfo`) and `PgReadFrom()` (`PageInfo`). It validates archive state, finds the central directory entry, computes the actual local-file-data offset, handles supported compression methods, serves from local archive buffer when possible, queues deflate reads through `ZipCache`, or issues remote `RdWithRsp<RSP>()` pipelines.
- Constructor initializes `archive`, sizes/flags (`archsize`, `cdexists`, `updated`, `cdoff`, `orgcdsz`, `orgcdcnt`), open parser stage (`None`), and checkpoint flag (`ckpinit`).
- `OpenOnly()` opens a remote ZIP file without parsing the central directory, sets `archsize` and `openstage = NotParsed`, and calls the user handler.
- `OpenArchive()` opens and parses the archive. It reads the trailing EOCD search window, locates EOCD, optionally follows ZIP64 EOCD locator/record, reads central directory records, validates offsets and compressed-size totals, stores original central-directory bytes, and marks `openstage = Done`.
- `OpenFile()` opens an existing archive member for read or prepares a new `LFH` for append when `OpenFlags::New` is used.
- `GetCD()` serializes the current central directory plus EOCD/ZIP64 EOCD/locator as needed.
- `SetCD()` installs a central directory from an external buffer for archives previously opened with `OpenOnly()`.
- `CloseArchive()` writes updated local file headers and central directory at `cdoff`, optionally wraps operations in checkpoint commit, closes the underlying file, and clears state on success.
- `ReadFrom()` and `PgReadFrom()` delegate to the shared template.
- `List()` builds a `DirectoryList` with per-entry `StatInfo` derived from archive stat info and each entry's uncompressed size.
- `WriteImpl()` appends data, writing an `LFH` before the first data chunk when needed, uses `ChkptWrtV` if overwriting an existing central directory, updates `archsize`/`cdoff`, adds `CDFH`/`cdmap`/`newfiles` records, and initializes checkpoints when necessary.
- `UpdateMetadata()` updates CRC32 in both the central-directory entry and stored new-file LFH.
- `AppendFile()` creates an LFH and writes a whole new entry in one call.

## Control flow

Opening a parsed archive is a staged async pipeline. After `Open()`, empty files immediately become `Done` with no central directory. Non-empty files read up to `EOCD::maxCommentLength + EOCD::eocdBaseSize + ZIP64_EOCDL::zip64EocdlSize` bytes from the tail. The read continuation loops over `openstage`: parse EOCD, detect whole-archive-in-buffer shortcut, detect ZIP64 locator, read ZIP64 EOCD when needed, read central directory records, copy original CD bytes, parse `CDFH` records, validate offsets/aggregate compressed size, and finish. `Pipeline::Repeat()` is used when the same read stage must be reissued with new offset/size/buffer.

Reading an entry derives its data offset indirectly: it finds the next central-directory record or CD offset, subtracts compressed size and optional data-descriptor size, then adds the requested relative offset. For stored entries, data is either copied from `me.buffer` or read remotely. For deflated entries, requests are queued in a per-file `ZipCache`; if the whole archive is buffered the compressed bytes are fed to the cache immediately, otherwise the code reads remote compressed bytes and queues them as cache responses.

Appending is append-only relative to `cdoff`. The first write for a new file writes local-file-header plus user data; subsequent writes omit the LFH. The original central directory may be overwritten, so checkpointed writes are used when `archsize > cdoff`. Closing an updated archive writes any modified LFHs for overwritten CRC metadata, writes the serialized central directory, optionally commits the checkpoint, closes, clears state on success, and reports through the response handler.

## State and persistence behavior

`ZipArchive` persists no metadata outside the remote archive file, but it mutates the remote file through XRootD writes. Important in-memory state includes:

- `archive`, the underlying `XrdCl::File`.
- `archsize`, current archive size as tracked by open/write operations.
- `cdexists`, `updated`, `ckpinit`, and `openstage` state flags.
- `cdoff`, `orgcdsz`, and `orgcdcnt`, representing central-directory location and original CD shape.
- `eocd`, `zip64eocd`, `cdvec`, `cdmap`, and `orgcdbuf`, representing parsed and original ZIP metadata.
- `buffer`, which may hold either a tail/CD read buffer or the entire archive for local serving.
- `openfn` and `lfh`, representing the currently open archive entry/new local header.
- `newfiles`, tracking appended files and LFHs that may need CRC/header rewrites.
- `zipcache`, one deflate cache per compressed entry.

Remote persistence occurs in `WriteImpl()` and `CloseArchive()`: entry bytes are appended before the central directory, and close writes final metadata. Checkpoints are used to make central-directory overwrite safer when appending to an archive with an existing CD.

## Dependencies and integration points

The file depends on `XrdClFileOperations.hh` and `XrdClCheckpointOperation.hh` pipeline combinators (`Open`, `Read`, `RdWithRsp`, `Write`, `WriteV`, `VectorWrite`, `ChkptWrtV`, `Checkpoint`, `Close`, `Final`, `Async`), `XrdClZipArchive.hh`, logging/default env/constants/utils, `XrdZip` structures (`EOCD`, `CDFH`, `LFH`, `DataDescriptor`, `ZIP64_EOCD`, `ZIP64_EOCDL`), `ZipCache`, `DirectoryList`, `StatInfo`, and POSIX `sys/stat.h`.

Friend declarations in the header allow EC components (`XrdEc::StrmWriter`, `Reader`, `OpenOnlyImpl`) and tests to access internal state. The archive reports async completion through `ResponseHandler` and packages read responses as `ChunkInfo` or `PageInfo`.

## Risks and edge cases

- ZIP offset math is delicate. The file data offset is inferred from the next record and compressed size rather than by reading the LFH extra/name lengths directly; unusual layouts, prepended data, or malformed central directories can expose edge cases.
- Deflated remote reads use `relativeOffset` to derive compressed read offsets, but compressed and uncompressed offsets are not equivalent. `ZipCache` may compensate by needing sequential compressed data, but sparse reads into deflated files are a key risk area.
- Only stored (`compressionMethod == 0`) and deflated (`Z_DEFLATED`) entries are supported; all other methods return `errNotSupported`.
- `memcpy(usrbuff, me.buffer.get() + offset, size)` assumes `buffer` covers the requested absolute offset. That is true only when the whole archive was buffered; parser stages reset `buffer` after CD-only reads.
- `SetCD()` parses external metadata only when `openstage == NotParsed` and performs less explicit corruption handling than `OpenArchive()`.
- `WriteImpl()` advances `archsize` and `cdoff` before the async write completes. A later write failure sets callback error state but callers must treat the archive object carefully after failures.
- `CloseArchive()` has code using `uint32_t lfhlen = lfh->lfhSize` inside a loop over `newfiles` where `nf.lfh` is the intended object; if `lfh` is null at close, this would be unsafe. The serialized buffer uses `nf.lfh`, so the length source deserves review.
- Asynchronous lambdas capture `this` and references such as `&cache`/`&me`; callers must keep the `ZipArchive` object alive until callbacks finish.
- Central-directory validation checks offsets and aggregate compressed size but does not fully validate every local header or data descriptor.

## Test signals

Tests should cover empty archives, normal EOCD parsing, ZIP64 EOCD locator/record parsing, max-comment EOCD search, malformed signatures/offsets/sizes, whole-archive buffered reads, CD-only reads, stored file remote reads, deflated full and partial reads through `ZipCache`, reads past EOF, unsupported compression, directory listing metadata, append-new-file flow, duplicate append rejection, CRC metadata update, close with and without checkpoint, close failure state, `OpenOnly()` plus `SetCD()`, and object lifetime under async callbacks. Regression tests should specifically inspect `CloseArchive()` LFH rewrite length handling and compressed sparse-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.cc -->
