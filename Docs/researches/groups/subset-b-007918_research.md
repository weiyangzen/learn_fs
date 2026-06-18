# Research: subset-b-007918

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.cc

Purpose: implements `XrdCksLoader`, the dynamic/native checksum calculator loader used by clients and by checksum manager autoload. It validates caller/plugin ABI compatibility with `XrdVersionInfo`, pre-registers native `adler32`, `crc32`, and `md5`, and builds the plugin path template `libXrdCksCalc%s.so`.

Important APIs: constructor/destructor, `Load()`, and private `Find()`. `Load()` is mutex-protected, returns either the original cached calculator or a fresh `New()` clone, lazily constructs native calculators, loads external calculators with `XrdOucPinLoader`, resolves `XrdCksCalcInit`, verifies the returned type name, and stores plugin handles in `csTab`.

Control flow and state: persistent process state is the in-memory `csTab[8]`, `csLast`, `ldPath`, `verMsg`, and pinned plugins. There is no disk persistence here. Dependencies are `XrdCksCalc*`, `XrdOucPinLoader`, `XrdSysPlugin`, and version macros. Risks include fixed table capacity, C string ownership, error-buffer truncation via `strncpy`, and strict plugin entry/type contracts. Test signals: native load, incompatible version, plugin missing symbol, wrong plugin type, table overflow, and concurrent first load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.hh

Purpose: declares the checksum loader interface for obtaining `XrdCksCalc` implementations by algorithm name. The public contract states that native `adler32`, `crc32`, and `md5` are built in and up to five additional algorithms can be loaded from shared libraries.

Important APIs/types: `XrdCksLoader::Load(csName, csParms, eBuff, eBlen, orig)`, constructor with compile-time version info and optional library path, destructor, and private `csInfo` entries carrying `Name`, cached `Obj`, and pinned `Plugin`. `csMax` is 8 and `csTab` is an ordered fixed-size registry.

Control flow/state: the header establishes that callers normally receive a new calculator object whose `Recycle()` method owns destruction; `orig=true` is reserved for manager autoload. The first two members are explicitly version/error fields, suggesting plugin/version loader layout sensitivity. Dependencies are forward declarations for calculator/plugin/version types. Risks: fixed capacity, legacy raw pointers, and ownership split between `Recycle()`, `free()`, and `delete`. Test signals come from API-level construction/destruction, repeated loads, and plugin lifecycle validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksLoader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.cc

Purpose: implements an OSS-backed checksum manager adapter. It converts logical file names to physical file names through `XrdOss::Lfn2Pfn`, then delegates most checksum metadata operations to `XrdCksManager`, while overriding file reads and stat calls to use the OSS file interface.

Important APIs: public `Calc`, `Del`, `Get`, `List`, `Set`, `Ver`; protected `Calc(Pfn, MTime, XrdCksCalc*)` and `ModTime`. `LfnPfn` stores the original LFN immediately before the PFN buffer, allowing `Pfn2Lfn()` to recover the logical name when base-class callbacks pass the PFN pointer back.

Control flow/state: a namespace-global `ossP` points to the active OSS instance and `rdSz` is normalized to a 64 KiB multiple. `Calc` opens through `ossP->newFile`, verifies a regular file, reads chunks into a heap buffer, updates the calculator, and reports read errors through `XrdSysError`. Persistence remains xattr-based in the base manager. Risks: global `ossP`, pointer-layout coupling in `Pfn2Lfn`, and large-buffer allocation. Test signals: failed LFN conversion, non-regular object, read failure, successful Set/Get via OSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.hh

Purpose: declares `XrdCksManOss`, an `XrdCksManager` specialization for storage systems exposed through the OSS plugin API. It is intended for internal checksum support where logical file names must be resolved by OSS rather than directly opened by POSIX calls.

Important APIs: virtual overrides for `Calc`, `Del`, `Get`, `List`, `Set`, and `Ver`, plus protected overrides of low-level `Calc` and `ModTime`. The constructor receives `XrdOss*`, error destination, I/O size, version info, and an autoload flag passed to the base class.

Control flow/state: the interface preserves the same checksum manager semantics while replacing path translation and file I/O. Persistent checksum state is still in extended attributes controlled by `XrdCksManager`. Dependencies include `XrdCksManager`, `XrdOss`, `XrdSysError`, and `XrdVersionInfo`. Risks are mostly integration risks: callers must pass LFNs to public methods, and the implementation must keep base-class PFN callbacks meaningful. Test signals: parity with POSIX manager behavior through OSS-backed files, stale mtime checks, and plugin autoload interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.cc

Purpose: implements the main checksum manager for local physical files. It registers checksum algorithms, computes file checksums, stores/retrieves them in extended attributes, validates staleness using file modification time, supports configured or autoloaded plugins, and verifies supplied checksums.

Important APIs: `Calc`, `Config`, `Init`, `Find`, `Del`, `Get`, `List`, `ModTime`, `Name`, `Object`, `Size`, `Set`, `SetOpts`, and `Ver`. Native calculators include `adler32`, `crc32`, `crc32c`, and `md5`; configured plugin calculators are initialized through `XrdCksCalcInit`; autoload uses `XrdCksLoader`.

Control flow/state: `csTab[8]` stores algorithm metadata, lengths, plugin handles, and ownership flags. `Calc` clones a calculator, mmap-reads the file in `segSize` windows, writes `XrdCksXAttr` when requested, and records `fmTime/csTime`. `Get` maps missing xattrs to `-ESRCH` and stale metadata to `-ESTALE`; `Ver` recalculates stale/missing attributes before comparing. Dependencies are POSIX file APIs, `XrdOucXAttr`, `XrdSysFAttr`, plugin loader utilities, and calculators. Risks: fixed capacity, mmap platform flags, shared global `CksOpts`, plugin trust, and mtime-only freshness. Test signals: config parsing, plugin failures, stale xattr detection, list filtering, default checksum swapping, and mmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.hh

Purpose: declares `XrdCksManager`, the base checksum manager implementation and extensibility point for filesystem-specific managers. Public methods implement the `XrdCks` contract for calculating, configuring, deleting, getting, listing, setting, sizing, naming, and verifying checksum values.

Important APIs/types: virtual public manager methods, `Cks_nomtchk` option, protected `Calc(Pfn, MTime, CksObj)` and `ModTime()` hooks, and private `csInfo` with name, calculator object, plugin path/parameters, plugin handle, checksum length, and ownership flag.

Control flow/state: the class maintains a fixed-size registry of checksum implementations and optionally owns an `XrdCksLoader` for autoload. Subclasses can override the protected methods to adapt file reads and stat calls while retaining xattr persistence and algorithm handling. Dependencies are `XrdCks`, `XrdCksData`, `XrdCksCalc`, plugin/version/error types. Risks include raw ownership, registry size limit, and the need for subclasses to preserve base expectations around PFN identity and mtime. Test signals: subclass override behavior, option propagation, algorithm registry bounds, and lifecycle cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksWrapper.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksWrapper.hh

Purpose: declares a forwarding wrapper base for stacked checksum plugins. A plugin can derive from `XrdCksWrapper`, override selected `XrdCks` methods, and delegate everything else to the previous checksum plugin in the chain.

Important APIs: forwarding implementations for `Calc` with and without callback, `Del`, `Get`, `Config`, `Init`, `List`, `Name`, `Object`, `Size`, `Set`, and `Ver`. The protected `cksPI` reference is the antecedent plugin. The file also documents the `extern "C" XrdCksAdd2` factory signature via `XRDCKSADD2PARMS`.

Control flow/state: no persistence or independent algorithm state exists here; state is whatever the wrapped plugin owns. Dependencies include `XrdCks`, `XrdCksData`, `XrdCksCalc`, `XrdOucEnv`, and `XrdSysError`. Integration point is the stacked-plugin loader resolving `XrdCksAdd2`. Risks: lifetime of the previous plugin reference, callback overloads silently ignoring callbacks by default, and plugins forgetting to declare version metadata. Test signals: pass-through behavior, selective override behavior, stacked factory loading, and callback overload expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksWrapper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksXAttr.hh -->
# sources/distributed-fs/xrootd/src/XrdCks/XrdCksXAttr.hh

Purpose: defines the xattr payload adapter used by `XrdOucXAttr` to persist `XrdCksData` under algorithm-specific extended attribute names.

Important APIs/types: public `Cks` member, `postGet(Result)`, `preSet(tmp)`, `Name()`, `sizeGet()`, and `sizeSet()`. `Name()` builds `"XrdCks." + Cks.Name`; sizes are exactly `sizeof(Cks)`.

Control flow/state: `preSet` copies checksum data into a temporary object and converts `fmTime`/`csTime` to network byte order; `postGet` converts those fields back to host order after successful reads. The generated attribute name is cached in `VarName` until object mutation. Persistence is the filesystem extended attribute keyed by algorithm name. Dependencies are `XrdCksData`, endian conversion helpers, and platform definitions. Risks: cached name becomes stale if `Cks.Name` changes after `Name()` is called, binary struct compatibility, and architecture portability limited to converted time fields. Test signals: set/get round trip across byte order, multiple checksum names, and xattr name construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCks/XrdCksXAttr.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdCl/CMakeLists.txt

Purpose: defines the XrdCl client library build, optional erasure-coding sources, public/private header installation, and client executables.

Important APIs/targets: `add_library(XrdCl SHARED ...)`, `target_link_libraries` against XML, utilities, uuid, zlib, OpenSSL, threads, dl, and extras; optional `BUILD_XRDEC` source inclusion and `WITH_XRDEC`; install rules for public headers under `xrootd/XrdCl` and private headers under `xrootd/private/XrdCl`; optional `xrdcp` and `xrdfs` executables when `XRDCL_LIB_ONLY` is false.

Control flow/state: CMake exits early unless `ENABLE_XRDCL` is enabled. Library ABI is set by `SOVERSION` and `VERSION`. Persistence is build/install metadata rather than runtime state. Integration points span most XrdCl sources, OpenSSL, ZLIB, readline/ncurses for `xrdfs`, and symlink creation for `xrdcopy`. Risks: install header classification affects downstream consumers, optional EC dependency correctness, and install-time symlink behavior under DESTDIR. Test signals: configure matrices for enabled/disabled client library, EC on/off, lib-only mode, and install manifest validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAnyObject.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAnyObject.hh

Purpose: provides a lightweight type-safe holder for object pointers without a Boost dependency. XrdCl uses it to pass channel/query/response data across interfaces that cannot be templated.

Important APIs/types: `AnyObject::Set(Type object, bool own)`, `Get(Type&)`, `Has<Type>()`, `HasOwnership()`, internal abstract `Holder`, templated `ConcreteHolder`, and helper `To<T>(AnyObject&)`.

Control flow/state: `Set(nullptr)` clears the holder; otherwise it replaces the holder, records `typeid(Type)`, and conditionally owns deletion. The destructor calls the held pointer's `delete` only when `pOwn` is true, then deletes the holder. Dependencies are RTTI and C string comparison of `type_info::name()`. Risks: only pointer-like types are safe because `ConcreteHolder::Delete` does `delete pObject`; type matching via `type_info::name()` strings is fragile across ABI boundaries; `To<T>` dereferences without null validation. Test signals: owned/non-owned pointer lifecycle, wrong-type `Get`, null reset, and use through channel/query paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAnyObject.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClApply.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClApply.hh

Purpose: implements a C++11-era replacement for `std::apply`, expanding tuple elements into function or method calls.

Important APIs/types: `sequence`, recursive `seq_gen`, `tuple_call_impl`, `Apply(FUNC&&, tuple&)`, and method overload `Apply(METH&&, OBJ&, tuple&)` that binds a member function to an object and two placeholders.

Control flow/state: all logic is compile-time template expansion plus moving tuple elements into the callable. There is no runtime persistence. Dependencies are `<functional>` and `<tuple>`. Integration point is the declarative operations layer that stores operation arguments in tuples and invokes handlers uniformly. Risks: the member-function overload is specialized to two placeholders, so it is not a general method apply; moving tuple members consumes argument state; compile errors can be hard to diagnose. Test signals: zero/two/multiple argument expansion, move-only arguments, and method overload arity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClApply.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClArg.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClArg.hh

Purpose: defines operation argument wrappers for XrdCl's declarative API. An argument can be a plain value, a future value, or a forwarded value, while exposing a uniform `Get()` and conversion operator.

Important APIs/types: `ArgBase<T>`, nested `ValueHolder`, `PlainValue`, `FutureValue`, `FwdValue`, movable `Arg<T>`, and string specialization `Arg<std::string>` accepting `const char*`. It depends on `Fwd<T>` and `Optional<T>`.

Control flow/state: `Get()` throws if unset, otherwise returns a cached value. Future-backed arguments call `future.get()` once and cache into `Optional<T>`; forwarded arguments dereference `Fwd<T>` at access time. State is local to each wrapper and move-only through `unique_ptr`. Integration point is operation composition and chaining. Risks: blocking `future.get()` inside argument access, dangling forwarded values, implicit conversion hiding unset errors, and string specialization copying instead of moving in one constructor. Test signals: unset access exception, future caching, move construction/assignment, forwarded lifetime, and `const char*` conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClArg.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncDiscardReader.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncDiscardReader.hh

Purpose: implements a raw reader used when raw data is not expected. Receiving raw bytes in this path is treated as a protocol error.

Important APIs: constructor forwarding URL/request to `AsyncRawReaderIntfc`, `Read(Socket&, uint32_t&)`, and `GetResponse(AnyObject*&)`. `Read` logs the unexpected raw-data condition and returns `errCorruptedHeader`; `GetResponse` returns `errInvalidResponse`.

Control flow/state: it inherits all base reader state but intentionally does not consume or persist data. The control decision is conservative: drop the connection because the stream may be desynchronized. Dependencies are socket/status/logging constants and the raw reader interface. Integration point is stream message handling when an unexpected raw body handler is installed. Risks: behavior is intentionally disruptive but protects protocol framing; tests should assert no silent discard. Test signals: unexpected raw body results in corrupted-header status, response retrieval returns invalid response, and reconnect/retry is triggered by the owning stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncDiscardReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSReader.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSReader.hh

Purpose: reads handshake response messages asynchronously, preserving partial progress across poll events.

Important APIs/types: constructor binding transport, socket, stream name, stream, and substream; `Read()`, `ReleaseMsg()`, `Reset()`, and `Stage` values `ReadStart`, `ReadHeader`, `ReadMsgBody`, `ReadDone`.

Control flow/state: `Read()` loops its state machine until it must return, allocating a `Message`, asking `TransportHandler::GetHeader`, then `GetBody`, returning `suRetry` on partial socket progress. `ReleaseMsg()` transfers ownership and resets the stage. There is no persistence outside the in-flight `unique_ptr<Message>`. Dependencies are transport handler, socket, stream, status, and logging. Risks: callers must only release after a complete read; any transport framing bug propagates into handshake failure. Test signals: partial header/body retry, complete message release, reset reuse, and transport error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSWriter.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSWriter.hh

Purpose: writes handshake request messages asynchronously and supports replaying a previously sent message for handshake wait/retry behavior.

Important APIs/types: `Reset(Message*)`, `Replay()`, `HasMsg()`, `Write()`, and stages `WriteRequest`/`WriteDone`. It owns the outgoing message through `unique_ptr<Message>`.

Control flow/state: `Write()` sends the message through `Socket::Send`, returns on `suRetry`, then flushes with `Socket::Flash`. `Replay()` resets the message cursor to zero and returns to `WriteRequest` without replacing the owned message. Dependencies are socket, status, logging, and `XrdSysE2T` for error text. Risks: `Write()` assumes `outmsg` is non-null when called; replay depends on cursor-correct message reuse; flush errors are logged and returned. Test signals: partial send retry, successful flush, replay after kXR_wait, and null-message guarding in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSWriter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgReader.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgReader.hh

Purpose: reads normal XRootD responses asynchronously and dispatches completed messages to the owning `Stream`.

Important APIs/types: `Reset()`, `Read()`, helper `ReadAttnActnum()`, `IsStatusRsp()`, `HasEmbeddedRsp()`, and stages for header, attention, more-body, message body, raw data, and completion. It uses `shared_ptr<Message>` because `MsgHandler` may share ownership.

Control flow/state: after reading a header, `kXR_attn` responses read an action code and may unwrap embedded async responses. Otherwise the stream can install an incoming handler for raw bodies. `kXR_status` may request raw or additional body reads through `InspectStatusRsp`. Completed messages call `strm.OnIncoming`. State persists as current stage, message, byte count, and handler across `suRetry`. Dependencies are transport, socket, stream, response structs, and logging. Risks: protocol boundary parsing, corrupted status handling, and shared ownership with handlers. Test signals: attention embedded response, status with raw/more data, partial socket retries, corrupted handler action, and final `OnIncoming` size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgWriter.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgWriter.hh

Purpose: writes queued normal requests, optional transport signatures, and optional raw request bodies for a substream.

Important APIs/types: `Reset()`, `Write()`, stages `WriteStart`, `WriteSign`, `WriteRequest`, `WriteRawData`, and `WriteDone`. It obtains `(Message*, MsgHandler*)` from `Stream::OnReadyToWrite`, does not own the main message, and owns only the optional signature message.

Control flow/state: `WriteStart` selects a message and asks the transport for a signature. Subsequent stages send signature, request, raw body via `MsgHandler::WriteMessageBody`, flush the socket, and notify `Stream::OnMessageSent`. `suRetry` preserves cursor/stage state. Dependencies are transport, socket, stream, channel `AnyObject`, and logging. Risks: assumes a non-null `outhandler` when checking raw status, size accounting combines message/signature/raw bytes, and `ECONNRESET` handling is in the caller. Test signals: empty queue returns `suAlreadyDone`, signature path, raw-body partial writes, flush failure, and sent callback size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgWriter.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncPageReader.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncPageReader.hh

Purpose: reads page-read responses where each page of user data is preceded by a CRC32C digest. It fills caller-provided chunks and a digest vector using scatter/gather I/O.

Important APIs/types: constructor sizing `digests`, `SetRsp(ServerResponseV2*)`, `Read(Socket&, uint32_t&)`, and private IOV helpers `CalcRdSize`, `InitIOV`, `ShiftIOV`, `shiftdgbuf`, and `shiftpgbuf`. It uses `ChunkList`, `iovec`, `XrdOucPgrwUtils`, and `XrdSys::PageSize`.

Control flow/state: `SetRsp` maps response offset into chunk/digest indices. `Read` initializes an alternating digest/page iovec, calls `Socket::ReadV`, converts completed digest words with `ntohl`, advances chunk and digest cursors, and returns `suRetry` on partial progress. State is in response length, chunk index/offset, digest index/offset, and current iovec. Risks: off-by-one/page alignment bugs, digest buffer bounds, and iov limit assumptions. Test signals: unaligned first/last page, multi-chunk reads, partial ReadV progress, digest byte-order conversion, and zero-length responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncPageReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReader.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReader.hh

Purpose: reads raw body data for regular read responses into caller-provided chunks and produces the user-visible read response object.

Important APIs: constructor, `Read(Socket&, uint32_t&)`, `GetResponse(AnyObject*&)`, private `GetChunkInfo()` and `GetVectorReadInfo()`. It inherits buffer/state fields from `AsyncRawReaderIntfc`.

Control flow/state: `ReadStart` initializes the first chunk, `ReadRaw` bounds reads to response `dlen`, calls `ReadBytesAsync`, advances chunk/message counters, and moves to the next chunk. If the response has more data than supplied buffer space, it reports corrupted header rather than trying to resynchronize. `GetResponse` returns `ChunkInfo` for normal read or `VectorReadInfo` for virtual readv. Dependencies are socket, stream response structs, status, and logs. Risks: buffer-size mismatch, chunk index bounds, and total byte accounting. Test signals: partial reads, multi-chunk fill, too-small buffer error, virtual readv response mapping, and invalid response after `dataerr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReaderIntfc.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReaderIntfc.hh

Purpose: declares the common base for asynchronous raw-body readers used by regular reads, vector reads, discard/error handling, and related protocols.

Important APIs/types: `SetDataLength(int)`, `SetChunkList(ChunkList*)`, pure virtual `Read()` and `GetResponse()`, helper `ReadBytesAsync`, `ChunkStatus`, `buffer_t`, and shared `Stage` enum.

Control flow/state: `ReadBytesAsync` loops on `Socket::Read` until the requested segment is filled or the socket returns `suRetry`/error. Shared mutable state tracks the response data length, bytes read from the current message, total raw bytes, chunk index/offset/remaining length, per-chunk status, discard buffer, and `dataerr`. Dependencies are URL/message/socket/status/logging types. Integration point is `AsyncMsgReader` raw handler logic. Risks: derived classes must reset inherited fields consistently; `SetChunkList` only resizes status when chunks are non-null; partial-read counters are easy to misuse. Test signals: retry preservation, chunk-list setup, zero/short reads, and derived reader error states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReaderIntfc.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.cc

Purpose: implements the event-driven socket handler connecting `Poller` events to XrdCl `Stream` behavior. It owns async connect, handshake, TLS negotiation, request writing, response reading, timeouts, and fault forwarding for a substream.

Important APIs: constructor/destructor, `Connect`, `PreClose`, `Close`, `Event`, read/write event dispatchers, connection completion, handshake read/write, normal read/write, fault/timeouts, TLS handshake, wait-response replay, and address helpers. It composes `AsyncHSWriter`, `AsyncHSReader`, `AsyncMsgWriter`, and `AsyncMsgReader`.

Control flow/state: `Connect` initializes the socket, keepalive options, poller registration, and write notification. `Event` maps TLS-specific events, processes reads before writes, and delays `ECONNRESET` write faults to allow one read. Handshake progresses through transport `HandShake`, optional kXR_wait replay, optional TLS, then swaps to normal message reader/writer and calls `Stream::OnConnect`. Persistent runtime state includes socket, poller, transport channel data, stream references, timeout timestamps, TLS/wait flags, and an open-channel shared pointer to protect lifetime. Dependencies span socket/poller/task/stream/transport/logging and response structs. Risks: lifetime reentrancy after `OnError`, timeout edge cases, TLS retry mapping, and preserving HS message for replay. Test signals: async connect errors, handshake suRetry/suDone, kXR_wait timeout, TLS retry, normal read/write retry, corrupted header, close/preclose idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.hh

Purpose: declares `AsyncSocketHandler`, the `SocketHandler` implementation used by XrdCl streams for asynchronous network I/O.

Important APIs/types: constructors, `SetAddress`, `GetAddress`, `Connect`, `PreClose`, `Close`, `Event`, `EnableUplink`, `DisableUplink`, stream/address getters, and protected event/handshake/fault/TLS helpers. State members include poller, transport, channel data, substream, stream name, socket, handshake data, timeout fields, TLS/reset flags, async reader/writer objects, and channel lifetime guard.

Control flow/state: the interface models a two-phase lifecycle: connecting/handshaking, then normal request/response I/O. It exposes only the operational entry points to callers while keeping the protocol state machine protected. Dependencies are XrdCl socket/poller/transport/task/URL/async reader-writer headers and compiler annotations. Risks: copy constructor recreates a handler around shared raw dependencies, event callbacks can trigger stream deletion, and uplink notification errors are fatal. Test signals: state transition coverage, copy construction behavior, poller notification failures, and helper address formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncSocketHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncVectorReader.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncVectorReader.hh

Purpose: reads vector-read responses composed of repeated `readahead_list` records followed by raw data for the matching requested chunks.

Important APIs: constructor, `Read(Socket&, uint32_t&)`, `GetResponse(AnyObject*&)`, and inherited raw-reader state. Extra state is `rdlstoff`, current `readahead_list`, and `rdlstlen`.

Control flow/state: `ReadStart` prepares to read a chunk header. `ReadRdLst` validates enough message bytes remain, reads and byte-swaps `rlen`/`offset`, finds the matching caller chunk, then `ReadRaw` reads the chunk payload while checking message boundaries. Completed chunks are marked in `chstatus`; `GetResponse` requires all chunks done and returns `VectorReadInfo`. Malformed boundaries or unmatched chunks cause `errCorruptedHeader` and reconnect. Dependencies are socket, response structs, chunk lists, logging, and byte-order helpers. Risks: O(n) chunk lookup per response chunk, duplicate chunk ambiguity, strict exact offset/length matching, and boundary validation. Test signals: multi-chunk response, reordered chunks, partial header/body retry, missing chunk, oversized declared chunk, and all-done validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncVectorReader.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClBuffer.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClBuffer.hh

Purpose: provides an owning binary buffer with an append cursor for XrdCl messages and related payloads.

Important APIs/types: constructors, move assignment, `Allocate`, `ReAllocate`, `Free`, `Zero`, `GetBuffer`, `GetSize`, `GetCursor`, `SetCursor`, `AdvanceCursor`, `Append`, `GetBufferAtCursor`, `FromString`, `ToString`, `Grab`, `Release`, and protected `Steal`.

Control flow/state: memory is managed with `malloc/realloc/free`; copies are disabled and moves transfer pointer, size, and cursor. `Append` grows the buffer as needed and advances the cursor; offset append does not move the cursor. `Grab` takes ownership of externally allocated memory expected to be `free`-compatible; `Release` transfers ownership out. Dependencies are C allocation/string headers and exceptions. Risks: `GetBuffer` can return null+offset when empty, `ToString` truncates at embedded NUL by constructing from C string, `realloc` failure loses original pointer, and `Grab` allocator mismatch. Test signals: move lifecycle, append growth, release ownership, binary strings with NUL bytes, and allocation failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClBuffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.cc

Purpose: implements `Channel`, the client-side connection abstraction tying a URL, transport handler, stream, poller, task manager, and job manager together.

Important APIs/types: internal `TickGeneratorTask`, `Channel` constructor/destructor, `Send`, `Tick`, `Finalize`, `ForceDisconnect`, session-scoped force disconnect, `ForceReconnect`, `NbConnectedStrm`, `SetOnDataConnectHandler`, `CanCollapse`, `DecFileInstCnt`, `QueryTransport`, event handler registration/removal, and `SetSelf`.

Control flow/state: construction initializes transport channel data, creates/configures a `Stream`, and registers a periodic tick task at `TimeoutResolution`. Destruction invalidates the tick task, destroys the stream, and finalizes transport channel data. Most methods forward to `Stream` or `TransportHandler`, making `Channel` an orchestration/lifetime boundary. Persistent runtime state includes `pChannelData`, `pStream`, task registration, and a self shared pointer passed to stream. Dependencies include stream, transport, poller/task/job managers, redirector registry, and defaults. Risks: tick task lifetime races, force-disconnect session filtering, query routing split at ID 2000, and self-reference management. Test signals: construction/destruction task invalidation, send forwarding, timeout ticks, forced reconnect/disconnect, query routing, and event handler forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.cc -->
