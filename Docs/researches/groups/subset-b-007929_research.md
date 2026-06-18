# subset-b-007929 Research

Grouped research for the XRootD ZIP archive client helpers and the XrdCl HTTP plugin files in this work item. Each section preserves the original source path and is intended to be split into the corresponding source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.hh

## Purpose
`XrdClZipArchive.hh` declares `XrdCl::ZipArchive`, the client-side facade for treating an ordinary XRootD `File` as a ZIP archive. It supports opening and parsing an existing archive, listing central-directory contents, opening an archive member for read or append, reading member data, writing new entries, updating metadata, closing the archive, and exposing member stat and CRC information.

## Important APIs and Types
The public API centers on `OpenArchive`, `OpenFile`, `Read`, `PgRead`, `ReadFrom`, `PgReadFrom`, `Write`, `UpdateMetadata`, `AppendFile`, `Stat`, `GetCRC32`, `GetOffset`, `CloseArchive`, `CloseFile`, and `List`. `Read` and `PgRead` are convenience wrappers over the current `openfn`; `ReadFrom` and `PgReadFrom` take an explicit archive member name. `Stat` uses central-directory metadata plus the underlying archive file's `StatInfo`. `GetOffset` computes the member payload offset from central-directory ordering, ZIP64 size metadata, and any data descriptor.

The key private state includes the underlying `File archive`, archive size, central-directory existence/update flags, EOCD and ZIP64 EOCD records, `cdvec` and `cdmap`, original central-directory buffer/offset/count, current open stage, currently open member name, per-file inflate caches, the pending LFH for appended files, checkpoint state, and `newfiles` entries that may require LFH overwrite on close. `OpenStages` models the parser state from no data through EOCD, ZIP64 locator, ZIP64 EOCD, central-directory records, done, error, and open-without-parse.

## Control Flow
Opening moves through `OpenArchive` and parser stages until the central directory is available. Reads validate that the archive and member are open, then eventually map logical member offsets to underlying archive reads; compressed members are mediated through `ZipCache`. Append/write flow creates a new LFH, writes file bytes, remembers new central-directory state, and finalizes via `CloseArchive`. `Schedule`, `PkgRsp`, and `Free` adapt status/response objects to XrdCl's callback job manager.

## State and Persistence
Persistent archive changes are deferred in memory until writes and close operations update LFH/CD structures in the underlying archive file. `Clear` resets parser and central-directory state without owning external storage. `newfiles` tracks append entries whose local headers may need rewriting after final CRC/size metadata is known.

## Dependencies and Integration Points
This header binds `XrdCl::File`, `ResponseHandler`, `ResponseJob`, `JobManager`, `DefaultEnv`, and `PostMaster` to low-level `XrdZip` record types (`EOCD`, `CDFH`, `ZIP64_EOCD`, `LFH`). Friends in `XrdEc` and tests access internals. `ZipOperations.hh` wraps this API into the operation pipeline.

## Risks and Test Signals
Offset math in `GetOffset` is sensitive to ZIP64 sentinel values, data descriptors, and central-directory order. Only stored and deflated members are accepted. Inline callback scheduling transfers ownership of heap status/response objects, so tests should cover null handlers, failed stats, missing central-directory entries, ZIP64 archives, compressed sequential reads, unsupported compression methods, append close rewriting, and repeated open/clear cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipArchive.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipCache.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipCache.hh

## Purpose
`XrdClZipCache.hh` defines `ZipCache`, a small stateful zlib inflate coordinator used by `ZipArchive` when reading compressed ZIP members. It bridges asynchronous underlying archive reads, which may complete out of order, with ordered consumer read requests that must receive decompressed bytes in stream order.

## Important APIs and Types
`ZipError` carries an `XRootDStatus` when zlib initialization fails. `ZipCache` exposes `QueueReq(offset, length, buffer, handler)` for consumer read requests and `QueueRsp(status, offset, buffer)` for compressed input chunks returned by lower-level archive reads. Internal tuple types model pending requests and read responses. Responses are kept in a priority queue sorted by compressed offset, while requests are a FIFO queue.

## Control Flow
Construction initializes `z_stream` via `inflateInit2(&strm, -MAX_WBITS)`, intentionally using raw deflate mode without gzip headers. Both queue entry points lock `mtx`, add work, and call `Decompress`. `Decompress` chooses the next output request, accepts the next compressed response only when its offset equals `inabsoff`, checks response status, calls `inflate(Z_SYNC_FLUSH)`, advances the absolute compressed input offset by consumed bytes, fulfills a request when output is exhausted, and pops a response when input is fully consumed.

## State and Persistence
All state is in memory: the zlib stream, mutex, `inabsoff`, FIFO read requests, and pending out-of-order read responses. There is no disk persistence. The cache assumes a single logical inflate stream and ordered consumer offsets; it preserves decompression continuity across multiple queued requests.

## Dependencies and Integration Points
The file depends on zlib, XrdCl response types (`XRootDStatus`, `ChunkInfo`, `AnyObject`, `ResponseHandler`), STL containers, mutexes, and tuples. `ZipArchive` owns a `ZipCache` per archive member in `zipcache_t`.

## Risks and Test Signals
The critical risks are callback ownership, out-of-order compressed input, zlib return-code mapping, and deadlock/reentrancy from invoking handlers while state is locked. Tests should exercise response reordering, error responses before and after queued requests, truncated/corrupt deflate streams, exact output buffer boundaries, `Z_BUF_ERROR` continuation behavior, and multiple sequential requests over one compressed stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.cc

## Purpose
`XrdClZipListHandler.cc` implements `ZipListHandler`, an asynchronous response handler that lets `DirList` with the ZIP flag treat a regular ZIP file as a directory while still delegating real directories to normal filesystem listing.

## Important APIs and Functions
`HandleResponse` owns the state machine. `DoDirList` retries an ordinary `FileSystem::DirList` after removing `DirListFlags::Zip`. `DoZipOpen` opens the URL with `ZipArchive::OpenArchive`. `DoZipClose` closes the archive after `ZipArchive::List` has produced a `DirectoryList`.

## Control Flow
The first callback corresponds to a stat operation. If stat says the URL is a directory, `DoDirList` forwards listing to a new `FileSystem` and marks the handler done. Otherwise it opens the URL as a ZIP archive. After `OPEN`, the handler calls `pZip.List`, stores the returned `DirectoryList`, and closes the archive. After `CLOSE`, it packages the directory list into an `AnyObject` and forwards success to the original handler. Any error is forwarded directly, and the handler deletes itself once done.

## State and Persistence
The object is self-owned and deletes itself after the asynchronous chain completes. It stores URL, flags, original handler, timeout start, current step, an owned directory-list result, a `File`, and a `ZipArchive`. No persistent state is written.

## Dependencies and Integration Points
This file integrates `ZipArchive`, `FileSystem`, `DirectoryList`, `StatInfo`, `XRootDStatus`, and `ResponseHandler`. It is the ZIP-aware listing bridge between regular XrdCl filesystem operations and archive member enumeration.

## Risks and Test Signals
Timeout arithmetic assumes a positive effective timeout and uses wall-clock `time(0)`. The code forwards the original response object on errors, so ownership expectations matter. Tests should cover listing a real directory with the ZIP flag, listing a valid archive, stat/open/list/close failures, timeout between stages, no handler leaks, and avoiding infinite recursion by clearing `DirListFlags::Zip`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.hh

## Purpose
`XrdClZipListHandler.hh` declares `ZipListHandler`, a `ResponseHandler` subclass used to implement ZIP-aware directory listing. It abstracts the multi-step decision of "ordinary directory list or archive list" behind one callback object.

## Important APIs and Types
The `Steps` enum has `STAT`, `OPEN`, `CLOSE`, and `DONE`. The constructor accepts a `URL`, path, listing flags, original response handler, and optional timeout; if no timeout is supplied it reads `RequestTimeout` from `DefaultEnv`. It stores the requested path back into `pUrl`. The override `HandleResponse` is implemented in the `.cc` file.

## Control Flow
The header describes three helper transitions: `DoDirList`, `DoZipOpen`, and `DoZipClose`. The object begins at `STAT`, advances to archive open for non-directory paths, closes after listing, and then forwards a `DirectoryList`.

## State and Persistence
State is per operation and in memory only: URL, listing flags, downstream handler, timeout, start time, result list, unused `File` member, `ZipArchive`, and integer step. The handler's lifetime is intentionally asynchronous and self-deleting.

## Dependencies and Integration Points
The declaration includes XrdCl response, filesystem, file, ZIP archive, constants, and default environment headers. It is likely instantiated by ZIP-aware directory listing code outside this work item.

## Risks and Test Signals
The class stores a raw downstream handler and self-deletes, so lifetime tests are important. The `pFile` member is present but unused in the implementation, which is a maintenance signal. Tests should verify default timeout loading, path rewriting on `URL`, and that every terminal state releases exactly one final response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipListHandler.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipOperations.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipOperations.hh

## Purpose
`XrdClZipOperations.hh` adapts `ZipArchive` methods to the generic XrdCl operation pipeline. It provides CRTP operation classes and factory functions so archive open, member open, reads, writes, append, stat, list, close-file, and close-archive can be composed like other XrdCl operations.

## Important APIs and Types
`ZipOperation` derives from `ConcreteOperation` and stores `Ctx<ZipArchive> zip`. Operation classes include `OpenArchiveImpl`, `OpenFileImpl`, `ZipReadImpl`, `ZipReadFromImpl`, `ZipWriteImpl`, `AppendFileImpl`, `CloseFileImpl`, `ZipStatImpl`, `ZipListImpl`, and `CloseArchiveImpl`. Inline factories expose `OpenArchive`, `OpenFile`, `Read`, `ReadFrom`, `Write`, `AppendFile`, `Stat`, `List`, and `CloseArchive`; `CloseFile` is a typedef.

## Control Flow
Each `RunImpl` extracts typed arguments from the operation tuple, computes a timeout as the minimum of pipeline and operation timeout, calls the corresponding `ZipArchive` method, and either lets the archive perform an asynchronous callback or immediately packages synchronous results into `AnyObject`. `OpenFile` and `CloseFile` are synchronous from the archive perspective and manually invoke the pipeline handler on success.

## State and Persistence
The operation wrappers own no archive data beyond the shared `Ctx<ZipArchive>`. Archive persistence and mutable state remain inside `ZipArchive`; these classes preserve pipeline arguments and handler flow.

## Dependencies and Integration Points
This header depends on `XrdClZipArchive.hh`, `XrdClOperations.hh`, `XrdClOperationHandlers.hh`, and `XrdClCtx.hh`. It is the integration layer between archive semantics and the broader XrdCl operation DSL.

## Risks and Test Signals
Timeout min logic can accidentally pass zero or stale operation defaults depending on pipeline usage. `ZipListImpl::ToString` returns `"ZipStat"`, likely a copy/paste observability issue. Tests should cover pipeline chaining, move construction across handler states, synchronous handler invocation, response object ownership, and failure propagation from each archive method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClZipOperations.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdClHttp/CMakeLists.txt

## Purpose
This CMake file conditionally builds the `XrdClHttp` client plugin. It detects libcurl, builds an object library containing the HTTP plugin implementation, links required XRootD, curl, OpenSSL, XML, and thread dependencies, then packages a versioned module plugin for installation.

## Important Build APIs and Targets
`find_package(CURL)` is required only when `FORCE_ENABLED` is set; otherwise lack of CURL returns early and disables the plugin. `XrdClHttpObj` is an object library containing factory, file, filesystem, operation, options-cache, timeout parser, utility, and worker sources. The module library name is `XrdClHttp-${PLUGIN_VERSION}`. Non-Apple platforms add an export-symbol version script. Installed public headers include the connection callout, header callout, response info, and response wrappers.

## Control Flow
Configuration first resolves CURL availability, exits if unavailable, creates the object library, links private dependencies, marks object code position-independent, creates the module library from the object library, attaches export options where supported, and declares install rules.

## State and Persistence
Build state is limited to generated build-system targets. Installation persists the module under `${CMAKE_INSTALL_LIBDIR}` and selected public API headers under `${CMAKE_INSTALL_INCLUDEDIR}/xrootd/XrdClHttp`.

## Dependencies and Integration Points
The plugin depends on `XrdCl`, `XrdUtils`, `XrdXml`, `CURL::libcurl`, `OpenSSL::Crypto`, and `Threads::Threads`. Runtime entry point export is controlled by `configs/export-lib-symbols` on ELF platforms.

## Risks and Test Signals
If CURL is absent and `FORCE_ENABLED` is false, the plugin silently disappears. Source-list drift is a risk when adding new operation files. Build tests should cover optional and forced CURL modes, module symbol export, install header completeness, and link correctness on Apple versus non-Apple platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpChecksum.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpChecksum.hh

## Purpose
`XrdClHttpChecksum.hh` defines checksum type metadata and `ChecksumInfo`, the in-memory cache used by the HTTP plugin to store checksum values parsed from HTTP digest headers.

## Important APIs and Types
`ChecksumType` enumerates CRC32C, MD5, SHA1, SHA256, `kAll`, and `kUnknown`. `GetTypeString`, `GetChecksumLength`, and `GetTypeFromString` convert between enum values, wire strings, and raw byte lengths. `ChecksumEntry` stores one type/value pair using a fixed 32-byte array. `ChecksumInfo` provides `IsSet`, `Get`, `Set`, and `GetFirst`.

## Control Flow
Checksum parsing code populates `ChecksumInfo` through `Set`. Consumers request the preferred type via `IsSet`/`Get`; otherwise `GetFirst` iterates all real checksum slots up to `kAll` and returns the first populated value.

## State and Persistence
Checksum state is in memory only. Each checksum value is raw bytes, not hex text; formatting is done by operation code such as `CurlChecksumOp::Success`.

## Dependencies and Integration Points
This header is used by header parsing and checksum query operations. It intentionally has minimal dependencies: arrays, strings, and tuples.

## Risks and Test Signals
`Get` maps invalid `kAll`/`kUnknown` requests to the CRC32C slot and documents undefined data if unset, so callers must use `IsSet`. Tests should verify digest string conversion, byte lengths, first-set ordering, unknown input handling, and no out-of-bounds access as enum values evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpChecksum.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpConnectionCallout.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpConnectionCallout.hh

## Purpose
`XrdClHttpConnectionCallout.hh` declares the public extension point that lets clients provide a custom socket acquisition path for HTTP requests, for example through a broker or out-of-band connection service.

## Important APIs and Types
`ConnectionCallout` is an abstract class with `BeginCallout` and `FinishCallout`. `BeginCallout` returns a listener FD and expiration time or `-1` with an error string. `FinishCallout` is invoked when the listener FD is readable and returns the connected socket FD or `-1`. `CreateConnCalloutType` is a C-linkage-compatible function pointer taking URL and `ResponseInfo` and returning an owned `ConnectionCallout *`.

## Control Flow
Users set the `XrdClConnectionCallout` property on a `File` or `FileSystem` to a serialized hex function pointer. Operations parse that pointer, call the creator with URL/response info, register the returned listener FD with the worker loop, and later finish the callout when ready.

## State and Persistence
The callout object is owned by the HTTP operation once created. It may outlive the initiating call until timeout or socket readiness. No repository or disk state is persisted.

## Dependencies and Integration Points
The interface uses `std::chrono`, strings, and `ResponseInfo`. Implementations are external to this plugin but integrate through `CurlOperation` socket callbacks and worker polling.

## Risks and Test Signals
Serializing function pointers through strings is inherently unsafe across ABI boundaries and must be tightly controlled by callers. Tests should cover malformed pointer properties, callout timeout, failed begin/finish, FD lifetime, and fallback to libcurl default connection behavior when the creator returns null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpConnectionCallout.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.cc

## Purpose
`XrdClHttpFactory.cc` implements the plugin factory entry point and global runtime initialization for the XrdCl HTTP plugin. It lazily sets environment defaults, starts the shared handler queue and curl workers, configures timeouts and credentials, and returns plugin `File` and `Filesystem` objects.

## Important APIs and Functions
`Factory::GetHeaderTimeoutWithDefault` maps operation timeouts to `timespec`. `Initialize` runs once under `m_init_once`. `SetupX509` imports certificate/proxy environment defaults. `Monitor` writes periodic JSON monitoring to logs and optionally an atomically replaced stats file. `Shutdown` joins the monitor thread. `Produce` enqueues an operation. `CreateFile`, `CreateFileSystem`, and `extern "C" XrdClGetPlugIn` expose the plugin to XRootD.

## Control Flow
Initialization gets the default logger/environment, registers the `XrdClHttp` log topic, imports environment variables, validates queue/thread/stall/slow-rate settings, parses header timeout defaults, initializes the OPTIONS cache singleton, starts `CurlWorker` threads, and starts the monitor thread. Shutdown is triggered by a static destructor and signals the monitor condition variable.

## State and Persistence
Static process-wide state includes initialized flag, shared `HandlerQueue`, log pointer, init flag, stats location, start time, shutdown mutex/CV/thread, and shutdown flag. Monitoring may persist JSON by writing a temporary file and renaming it over `HttpStatisticsLocation`.

## Dependencies and Integration Points
The file integrates XrdCl plugin interfaces, default environment, logging, version export macros, HTTP file/filesystem classes, curl worker utilities, timeout parsing, X509 environment conventions, and POSIX file APIs.

## Risks and Test Signals
Global lazy initialization and shutdown races are the main risk. `SetupX509` declares `disable_proxy` but never reads the imported value back, so `HttpDisableX509` may not disable proxy probing. Tests should cover fork-before-init behavior, invalid environment values, stats-file write failures, repeated plugin create calls, shutdown during initialization, and X509 fallback precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.hh

## Purpose
`XrdClHttpFactory.hh` declares the final `Factory` class implementing `XrdCl::PlugInFactory` for HTTP-backed file and filesystem plugin instances.

## Important APIs and Types
The class overrides `CreateFile` and `CreateFileSystem`, exposes static `GetHeaderTimeoutWithDefault`, and provides `Produce` for queueing `CurlOperation` work. Private helpers include `Initialize`, `SetupX509`, `Monitor`, and static `Shutdown`. Static members hold shared queue/log/thread/shutdown state and defaults such as `m_poll_threads`.

## Control Flow
The header defines a lazy initialization model: object creation calls `Initialize`, which creates shared runtime infrastructure on first use. `shutdown_s` invokes `Shutdown` when the library unloads.

## State and Persistence
The factory state is process-wide rather than per factory instance. It owns a shared handler queue, monitor thread, initialization guard, stats location, start time, and shutdown signaling primitives.

## Dependencies and Integration Points
It depends on XrdCl plugin interfaces plus C++ threading primitives. It forward-declares `CurlOperation`, `CurlWorker`, and `HandlerQueue`, keeping operation details out of the public factory header.

## Risks and Test Signals
The static lifecycle makes ordering important when the shared library is unloaded. Tests should check that `CreateFile` and `CreateFileSystem` return null if initialization fails, `Produce` is not called before queue setup, and shutdown is idempotent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFactory.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.cc

## Purpose
`XrdClHttpFile.cc` implements the `XrdClHttp::File` plugin object, translating XrdCl file operations into asynchronous HTTP/curl operations. It covers open, close, stat, fcntl metadata, scalar reads, page reads, vector reads, sequential upload, full-download mode, prefetching, dynamic query parameters, header callouts, and monitoring counters.

## Important APIs and Functions
Public overrides implemented here include `Open`, `Close`, `Stat`, `Fcntl`, `Read`, `PgRead`, `VectorRead`, both `Write` overloads, `IsOpen`, `GetProperty`, and `SetProperty`. Important helpers include `ParseHeaderTimeout`, `GetHeaderTimeoutWithDefault`, `GetHeaderTimeout`, `GetMonitoringJson`, `ReadPrefetch`, `GetCurrentURL`, and `CalculateCurrentURL`.

Nested/anonymous handlers perform response transformations: `OpenResponseHandler` sets `m_is_opened`; `OpenFullDownloadResponseHandler` converts the first full-download `ReadResponseInfo` into `OpenResponseInfo`; `PgReadResponseHandler` converts `ChunkInfo` to `PageInfo` with CRC32C page checksums; `CloseCreateHandler` handles zero-byte object creation; `PrefetchResponseHandler` chains sequential reads on one GET; `PrefetchDefaultHandler` disables failed/expired prefetch; `PutResponseHandler` serializes writes on one PUT; `PutDefaultHandler` records upload failures; and the default header callout injects `Content-Length` for known-size PUT.

## Control Flow
`Open` parses the URL, handles a special no-op plugin-loading open, normalizes `xrdclhttp.timeout` and `oss.asize`, initializes prefetch state, and either starts a full-object GET or a `CurlOpenOp`. `Read`/`PgRead` try the sequential prefetch path first, fall back to standalone `CurlReadOp`/`CurlPgReadOp`, and reject non-sequential reads in full-download mode. `Write` starts or continues a single PUT, requiring sequential offsets. `Close` finalizes a PUT, creates a zero-sized object if opened write-only with no writes, or returns immediately for read handles.

## State and Persistence
Persistent remote state is changed by PUT and close-created zero-length objects. In-memory state tracks open flag, full-download flag, open flags, base/last/current URLs, mutable properties under shared mutex, header timeout, pending PUT/read operations, prefetch offsets and handlers, expected upload size, write offset, header callout pointer, and global prefetch counters.

## Dependencies and Integration Points
The file integrates `XrdCl` file plugin APIs, HTTP curl operation classes, response-info wrappers, timeout parsing, worker maintenance settings, XrdCl logging/env constants, CRC utilities, page size, JSON output, and header/connection callout mechanisms.

## Risks and Test Signals
Important risks include raw handler lifetimes, callbacks that may delete the `File`, sequential-only assumptions for full download and PUT, dynamic URL cache invalidation, disabled prefetch after short reads, and the moved-buffer constructor path where size accounting must remain correct. Tests should cover open flag combinations, 404 open-for-create, timeout parsing bounds, full-download sequential read EOF, prefetch continuation/failure resubmission, PUT queueing/final flush/partial-size close, dynamic query replacement, Fcntl XAttr JSON, page checksum correctness, and destructor waiting for active writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.hh

## Purpose
`XrdClHttpFile.hh` declares the HTTP file plugin class that implements `XrdCl::FilePlugIn`. It is the per-open-handle state container for HTTP file I/O and the declaration point for prefetch, PUT serialization, timeout, monitoring, property, and callout behavior.

## Important APIs and Types
The public interface mirrors XrdCl file operations: `Open`, `Close`, `Stat`, `Fcntl`, `Read`, `PgRead`, `VectorRead`, two `Write` overloads, `IsOpen`, `SetProperty`, and `GetProperty`. It exposes `Flags`, static timeout setters/getters, `ParseHeaderTimeout`, `GetHeaderTimeout`, federation metadata timeout accessors, and `GetMonitoringJson`.

Nested classes include `PutResponseHandler`, `PutDefaultHandler`, `PrefetchResponseHandler`, `PrefetchDefaultHandler`, and file-specific `HeaderCallout`. These declare the concurrency contracts for serialized upload and chained prefetch reads.

## Control Flow
The declaration shows two major data paths: read-side prefetch based on one long-running GET with continuations, and write-side PUT based on one curl upload that pauses between client writes. Public operations enqueue `Curl*Op` objects into the shared `HandlerQueue`.

## State and Persistence
Per-handle state includes open status, full-download flag, open flags, original/last/current URLs, shared queue, logger, property map with shared mutex, timeout values, current PUT op/handler/asize/write offset, current prefetch op/offset/size/handlers, header callout pointer, default header callout, and static prefetch counters. Remote persistence is performed by implementation-side PUT/close logic.

## Dependencies and Integration Points
The class depends on XrdCl file/plugin APIs, connection/header callout interfaces, atomics, synchronization primitives, variants, buffers, and forward-declared curl operations. `Factory` sets static timeout defaults; `CurlOpenOp` sets properties such as last URL/content length.

## Risks and Test Signals
The header exposes many raw pointers and atomics around asynchronous callbacks. Tests should focus on lifetime during close/destruction, mutex-protected property reads, header callout pointer replacement, prefetch disable checks, PUT handler queue ordering, and monitoring counter consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.cc

## Purpose
`XrdClHttpFilesystem.cc` implements the HTTP filesystem plugin, translating XrdCl filesystem-level operations into HTTP/WebDAV curl operations against a base URL.

## Important APIs and Functions
Implemented methods include constructor/destructor, `DirList`, `GetProperty`, `Locate`, `MkDir`, `Query`, `Rm`, `RmDir`, `SetProperty`, `Stat`, `SendResponseInfo`, `GetConnCallout`, and `GetCurrentURL`. Operations enqueue `CurlListdirOp`, `CurlMkcolOp`, `CurlChecksumOp`, `CurlQueryOp`, `CurlDeleteOp`, and `CurlStatOp`.

## Control Flow
The constructor normalizes the base URL path to `/` and clears query params. Filesystem operations build a full URL with `GetCurrentURL`, compute a header timeout through `Factory`, create the appropriate curl operation, and push it to the shared queue. `Locate` is synchronous and returns the base host/port as an online read location. `RmDir` delegates to `Rm`. `Query` handles checksum and XAttr codes and rejects other query codes.

## State and Persistence
The object stores base URL, queue, logger, mutable properties under shared mutex, and an atomic header callout pointer. Remote persistent changes occur through MKCOL and DELETE operations. The `XrdClHttpQueryParam` property can alter future request URLs.

## Dependencies and Integration Points
It integrates XrdCl `FileSystemPlugIn`, URL, logging, location and buffer response types, HTTP operation classes, response-info opt-in, and the connection/header callout property conventions also used by `File`.

## Risks and Test Signals
`GetConnCallout` uses `if (!GetProperty(...) && pointer_str.empty())`, which returns null for missing empty strings but may still try parsing non-empty values when `GetProperty` fails unexpectedly. `GetCurrentURL` uses `':'` instead of `'&'` when appending a query to a URL that already has `?`, which looks suspicious. Tests should cover URL normalization, query param appending, checksum type selection, queue produce exceptions, response-info opt-in, header/callout pointer parsing, and all unsupported query codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.hh

## Purpose
`XrdClHttpFilesystem.hh` declares `XrdClHttp::Filesystem`, the final HTTP implementation of `XrdCl::FileSystemPlugIn`.

## Important APIs and Types
The class overrides filesystem methods for `DirList`, `GetProperty`, `Locate`, `MkDir`, `Rm`, `RmDir`, `SetProperty`, `Stat`, and `Query`. Private helpers return a connection callout function pointer, determine whether to send extended response info, and build the current operation URL from base URL plus properties.

## Control Flow
The declaration establishes a thin enqueueing object: public methods translate XrdCl filesystem calls into concrete curl operations, while properties modify callouts and URL construction.

## State and Persistence
State consists of a shared handler queue, atomic header callout pointer, logger, base URL, and property map protected by shared mutex. Persistent remote effects happen in implementation methods via HTTP verbs.

## Dependencies and Integration Points
The file depends on connection/header callout public interfaces, XrdCl filesystem/log/plugin/URL headers, and STL shared mutex and property containers. It is created by `Factory::CreateFileSystem`.

## Risks and Test Signals
The primary risk is property concurrency and raw callout pointer lifetime. Tests should verify property get/set with concurrent reads, URL building from root and nested paths, response-info behavior, and that methods return `errOSError` when queue submission throws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpFilesystem.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpHeaderCallout.hh -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpHeaderCallout.hh

## Purpose
`XrdClHttpHeaderCallout.hh` declares the public extension interface for request header customization in the HTTP plugin.

## Important APIs and Types
`HeaderCallout` defines `HeaderList` as `std::vector<std::pair<std::string, std::string>>` and one pure virtual method, `GetHeaders(verb, url, headers)`, returning a shared pointer to a replacement or augmented header list.

## Control Flow
`File` and `Filesystem` accept a serialized pointer property named `XrdClHttpHeaderCallout`. Operations pass their current verb, URL, and headers through the callout before libcurl setup. The file-specific default callout wraps an optional user callout and may inject PUT `Content-Length`.

## State and Persistence
The interface owns no state. Implementations may be shared externally; the plugin stores raw pointers atomically and does not own them.

## Dependencies and Integration Points
The header depends only on memory, string, utility, and vector. It is installed as a public plugin header and used by `CurlOperation` setup.

## Risks and Test Signals
Because the plugin stores non-owning raw pointers, implementation lifetime must exceed active requests. Tests should cover null return handling, empty header lists, duplicate header behavior, and interaction with file-level Content-Length injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpHeaderCallout.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpChecksum.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpChecksum.cc

## Purpose
`XrdClHttpOpChecksum.cc` implements `CurlChecksumOp`, a checksum query operation that issues an HTTP HEAD with `Want-Digest` and returns an XrdCl query buffer containing the selected digest.

## Important APIs and Functions
The constructor derives from `CurlStatOp` and stores the preferred checksum type. `OptionsDone` intentionally does nothing so the parent stat operation does not switch to PROPFIND. `Setup` calls `CurlStatOp::Setup`, forces HEAD semantics (`CURLOPT_NOBODY`, no custom request), and adds `Want-Digest`. `Redirect` reapplies HEAD settings. `ReleaseHandle` clears HTTP headers. `Success` selects and hex-encodes the preferred or first available checksum.

## Control Flow
On success, parsed response headers are queried for checksums. If the preferred checksum exists, it is used; otherwise the first available checksum is used. Missing checksums produce `errCheckSumError`. Successful responses are formatted as `"type hex"` in a `QueryResponse` and may carry `ResponseInfo`.

## State and Persistence
The operation stores only the preferred checksum plus inherited curl/header state. It does not mutate remote state.

## Dependencies and Integration Points
It depends on `CurlStatOp`, `HeaderParser::ChecksumTypeToDigestName`, `ChecksumInfo`, `QueryResponse`, XrdCl buffers, and response-info plumbing. `Filesystem::Query(Checksum)` instantiates it.

## Risks and Test Signals
Checksum byte ordering and hex formatting are critical. Tests should cover preferred present, fallback present, none present, redirects retaining HEAD mode, unknown checksum request fallback in filesystem code, and handle reuse after `ReleaseHandle`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpChecksum.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpCopy.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpCopy.cc

## Purpose
`XrdClHttpOpCopy.cc` implements `CurlCopyOp`, an HTTP third-party-copy operation using the `COPY` verb and a text control channel for performance/failure markers.

## Important APIs and Functions
The constructor accepts source URL/headers, destination URL/headers, timeout, logger, and connection callout. It prefixes source headers with `TransferHeader`, stores destination headers normally, and lowers the minimum rate. `Setup` installs write callback/data, sets `CUSTOMREQUEST` to `COPY`, and adds the `Source` header. `WriteCallback` splits response text into lines and calls `HandleLine`. `HandleLine` parses `"Perf Marker"`, `"End"`, `"Stripe Bytes Transferred"`, `"success"`, and `"failure"` markers.

## Control Flow
During transfer, response body lines update byte-mark progress and optional callback notifications. Success currently reports a generic OK response to the handler. `ReleaseHandle` clears curl callbacks, custom request, headers, and transfer info callback.

## State and Persistence
Remote state is changed at the destination endpoint by the COPY request. In-memory state tracks source URL, partial line buffer, progress callback, latest byte marker, success marker flag, and failure text.

## Dependencies and Integration Points
The operation derives from `CurlOperation` and uses `ltrim_view` from HTTP utilities. It is declared in `XrdClHttpOps.hh`; instantiation likely occurs outside the listed files.

## Risks and Test Signals
The parsed `m_sent_success` and `m_failure` fields are not used in `Success`, so control-channel failures may not affect final status unless handled in omitted base code. Tests should cover fragmented response lines, malformed numeric markers, progress callback invocation, remote failure marker handling, and cleanup of curl handle options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpCopy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpDelete.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpDelete.cc

## Purpose
`XrdClHttpOpDelete.cc` implements `CurlDeleteOp`, the HTTP DELETE operation used by filesystem removal calls.

## Important APIs and Functions
The constructor forwards handler, URL, timeout, logger, response-info flag, connection callout, and header callout to `CurlOperation`. `Setup` calls the base setup then sets `CURLOPT_CUSTOMREQUEST` to `"DELETE"`. `ReleaseHandle` clears the custom request. `Success` returns an OK status and optionally a `DeleteResponseInfo`.

## Control Flow
`Filesystem::Rm` and `RmDir` enqueue this operation. Once curl completes successfully, `Success` marks the operation done without failure and invokes the original response handler.

## State and Persistence
The remote target is deleted. The only additional in-memory state is the response-info opt-in flag.

## Dependencies and Integration Points
The file depends on `XrdClHttpOps.hh`, `XrdClHttpResponses.hh`, and XrdCl logging. It relies on base `CurlOperation` for HTTP status-to-XRootD error mapping.

## Risks and Test Signals
Tests should cover successful delete with and without response info, HTTP 404/403 mapping through base failure logic, queue submission from filesystem methods, and handle reuse after custom request reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpDelete.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpListdir.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpListdir.cc

## Purpose
`XrdClHttpOpListdir.cc` implements `CurlListdirOp`, a WebDAV `PROPFIND Depth: 1` directory listing operation that converts XML multistatus responses into XrdCl `DirectoryList` entries.

## Important APIs and Functions
`Setup` sets the write callback, request data pointer, `CUSTOMREQUEST` to `PROPFIND`, and `Depth: 1`. `WriteCallback` accumulates the XML response with a 10 MB cap. `ParseProp` extracts resource type, content length, last modified time, href, and executable bit. `ParseResponse` extracts a single DAV response entry. `Success` parses the XML, skips the first entry representing the directory itself, and fills a `DirectoryList` or `DirectoryListResponse`.

## Control Flow
After curl success, the operation parses XML with TinyXML. It requires root `D:multistatus`, iterates `D:response` elements, rejects malformed entries, and converts each child entry into a `ListEntry` with host address, name, and `StatInfo` flags.

## State and Persistence
The operation does not mutate remote state. It stores response-info preference, host address, and the accumulated response body.

## Dependencies and Integration Points
It depends on TinyXML, XrdCl directory/stat response types, HTTP response-info wrappers, and `Filesystem::DirList`. Namespaces are handled by string comparisons against `D:` and `lp1:` prefixes.

## Risks and Test Signals
XML parsing is prefix-specific and assumes a depth-one response where the first entry is the directory itself. The `href` parsing is marked not robust. Tests should cover namespace variants, missing fields, invalid sizes/dates, large response rejection, executable flag, directory size defaulting to zero, and response-info propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpListdir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpMkcol.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpMkcol.cc

## Purpose
`XrdClHttpOpMkcol.cc` implements `CurlMkcolOp`, the WebDAV directory creation operation used by `Filesystem::MkDir`.

## Important APIs and Functions
`Setup` sets `CURLOPT_CUSTOMREQUEST` to `"MKCOL"`. `Fail` remaps HTTP 405/invalid-request responses to `kXR_ItExists`, matching mkdir-on-existing-directory semantics. `Success` returns OK and optional `MkdirResponseInfo`. `ReleaseHandle` clears the custom request.

## Control Flow
`Filesystem::MkDir` queues this operation. Base `CurlOperation` handles HTTP execution and status conversion; this class only customizes method, success response, and 405 failure mapping.

## State and Persistence
The operation creates a remote collection/directory. In memory it stores only inherited operation state and a response-info flag.

## Dependencies and Integration Points
It depends on response wrappers, XrdCl logging/status constants, and WebDAV server support for MKCOL.

## Risks and Test Signals
Tests should validate 405-to-exists mapping, successful mkdir with/without response info, unsupported WebDAV verb errors, and custom request cleanup for reused handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpMkcol.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOpen.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOpen.cc

## Purpose
`XrdClHttpOpOpen.cc` implements `CurlOpenOp`, the HTTP open operation built on stat semantics, plus `CurlPrefetchOpenOp` behavior for full-download open.

## Important APIs and Functions
`CurlOpenOp` derives from `CurlStatOp`. `SetOpenProperties` records effective URL as `LastURL`, optional object size as prefetch size, ETag, and Cache-Control on the `File`. `Success` rejects directories, stores `ContentLength`, and calls `SuccessImpl(false)`. `Fail` treats 404 as success for create/write/delete open flags. `CurlPrefetchOpenOp::Pause` special-cases the first pause to set open properties from the GET response before delegating to read pause behavior.

## Control Flow
Normal open uses HEAD/PROPFIND stat behavior, then populates file properties needed by later `Stat`, `Read`, and prefetch. Full-download open starts a GET; the first pause after headers establishes the same properties and lets `OpenFullDownloadResponseHandler` mark the file open.

## State and Persistence
No remote state is necessarily changed by open, though create-style opens can accept missing objects and later writes create them. File object properties persist in memory for the handle lifetime.

## Dependencies and Integration Points
The operation integrates `File`, `CurlStatOp`, response info, curl effective URL introspection, and open flag semantics. `File::Open` constructs it.

## Risks and Test Signals
Tests should cover directory open rejection, 404 create success, effective URL after redirect, content length property setting, ETag/cache-control propagation, full-download first-pause behavior, and `ReleaseHandle` clearing socket callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOpen.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOptions.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOptions.cc

## Purpose
`XrdClHttpOpOptions.cc` implements `CurlOptionsOp`, an advisory OPTIONS request used to discover allowed HTTP/WebDAV verbs and cache them for redirect and operation decisions.

## Important APIs and Functions
`Setup` configures the curl handle for `OPTIONS` and no response body. `Success` writes parsed allowed verbs into `VerbsCache`. `Fail` records unknown verbs in the cache but otherwise ignores failure so the parent operation can continue. `ReleaseHandle` clears custom request and `CURLOPT_NOBODY`.

## Control Flow
The worker inserts this operation when a parent operation requires verb discovery. On success or failure, the cache is updated and worker logic resumes the parent operation.

## State and Persistence
State is cached in the process-wide `VerbsCache`; no remote state changes occur.

## Dependencies and Integration Points
It depends on `CurlOperation`, `VerbsCache`, and header parsing for allowed verbs. Worker logic in HTTP utilities recognizes `CurlOptionsOp` and reactivates parent operations.

## Risks and Test Signals
OPTIONS failure is intentionally non-fatal, so tests should verify parent continuation on 405 or network failure, correct cache entries for allowed verbs, no-body setup cleanup, and redirect paths that require a second OPTIONS lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOptions.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpPut.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpPut.cc

## Purpose
`XrdClHttpOpPut.cc` implements `CurlPutOp`, the streaming HTTP upload operation used by `File::Write` and close-created zero-byte objects.

## Important APIs and Functions
Constructors accept either a non-owned buffer view or an owned `XrdCl::Buffer`. `Setup` enables upload, installs read callback/data, and sets object size when known. `ReadCallback` feeds libcurl from `m_data`, pauses when more client data is needed, and returns 0 when final. `Pause` reports successful consumption of the current chunk. `Continue` updates handler and buffer data, marks final on zero-size continuation, and queues the op on the continue queue. `ContinueHandle` unpauses curl. `Fail`, `Success`, and `ReleaseHandle` manage callbacks and curl option cleanup.

## Control Flow
`File::Write` creates one `CurlPutOp` at offset zero. Each subsequent sequential write calls `Continue`; when libcurl asks for data and none is available, `Pause` invokes the active handler and waits for the next continuation. `Close` finalizes by queueing a zero-size continuation.

## State and Persistence
The operation writes the remote object. It stores current curl handle, continue queue, optional owned buffer, non-owned data view, default error handler, offset/object-size fields, and final flag.

## Dependencies and Integration Points
It depends on libcurl upload callbacks, `HandlerQueue`, `File::PutResponseHandler`, connection/header callouts, and base `CurlOperation` timeout/error logic.

## Risks and Test Signals
The owned-buffer constructor initializes `m_data` from the moved-from parameter rather than `m_owned_buffer`, which deserves focused testing. Other risks are non-owned buffer lifetime, pause/resume races, zero-size final writes, and handle reuse. Tests should cover chunked PUT, buffer and raw-pointer overloads, final flush, failure with no active handler, continue-queue exceptions, and content-length injection via header callout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpPut.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpQuery.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpQuery.cc

## Purpose
`XrdClHttpOpQuery.cc` implements the success path for `CurlQueryOp`, currently supporting XAttr-style metadata queries.

## Important APIs and Functions
`CurlQueryOp::Success` checks `m_queryCode`. For `XrdCl::QueryCode::XAttr`, it creates an `XrdCl::Buffer` containing the parsed ETag header, packages it into an `AnyObject`, and calls the handler with success. Unsupported query codes log an error and call `Fail`.

## Control Flow
`Filesystem::Query(XAttr)` constructs a `CurlQueryOp`, which inherits stat/header-fetch behavior from `CurlStatOp`. After headers are available, this file converts header state into the XrdCl query response.

## State and Persistence
The operation does not modify remote state. It reads response headers into inherited state and emits a buffer.

## Dependencies and Integration Points
It depends on XrdCl filesystem query codes, buffers, logging, and the inherited `CurlStatOp` setup. File-level `Fcntl` has a separate XAttr JSON path.

## Risks and Test Signals
Only ETag is returned for XAttr here, while `File::Fcntl` returns richer JSON; consumers may see inconsistent metadata shapes. Tests should cover missing ETag, unsupported query code failure, handler ownership, and response status mapping from the inherited stat operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpQuery.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpRead.cc -->
# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpRead.cc

## Purpose
`XrdClHttpOpRead.cc` implements scalar HTTP GET reads and page reads. `CurlReadOp` supports normal range reads plus prefetch continuations; `CurlPgReadOp` converts successful reads to page-checksummed responses.

## Important APIs and Functions
`CurlReadOp::Setup` installs write callback/data, chooses curl buffer size for large reads, and adds an inclusive `Range` header unless length is `UINT64_MAX`. `Continue` supplies a new client buffer to a paused prefetch GET and drains any overflow buffer. `Write` validates multipart and offset headers, copies response bytes to the client buffer, stores overflow bytes when libcurl delivers more than the current buffer can hold, and pauses when no buffer is available. `DeliverResponse`, `Pause`, `Success`, `Fail`, `ContinueHandle`, and `ReleaseHandle` manage callback and curl lifecycle. `CurlPgReadOp::Success` computes CRC32C per page and returns `PageInfo`.

## Control Flow
Standalone reads finish after one requested range. Prefetch reads issue a larger GET and repeatedly pause as each client buffer is filled; continuations unpause the same curl handle. Error bodies are captured separately in `m_err_msg` and are not copied to the client buffer.

## State and Persistence
The operation is read-only. In-memory state includes requested offset/length, bytes written, current buffer pointer/size, overflow buffer and offset, object offset within a prefetch stream, default handler, error body, and continue queue.

## Dependencies and Integration Points
It depends on `CurlOperation`, libcurl callbacks, `File::ReadPrefetch`, `HandlerQueue`, XrdCl `ChunkInfo`/`PageInfo`, CRC utilities, and page-size constants.

## Risks and Test Signals
Key risks are offset validation against server `Content-Range`, unsupported multipart byteranges, overflow buffer correctness, paused transfer timeouts without active handlers, and page checksum coverage for partial pages. Tests should cover zero-length reads, full-object reads, range header endpoints, short reads, oversized server responses, continuation after done, error body capture, and page checksums.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpRead.cc -->
