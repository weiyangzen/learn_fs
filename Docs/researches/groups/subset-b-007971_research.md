# subset-b-007971 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.cc

## Purpose

This file implements the concrete SSI client-side task object that sends one request over an `XrdSsiSessReal` endpoint, waits for the server response, exposes either a single data response or a streaming response to the original `XrdSsiRequest`, and handles asynchronous completion/cancellation. It is the active state-machine body for `XrdSsiTaskReal` from the companion header.

## Important APIs, types, and functions

The main public methods implemented here are `SendRequest`, `XeqEvent`, `XeqEvFin`, `SetBuff` for synchronous and asynchronous stream reads, `Kill`, `Detach`, `Finished`, `SchedError`, and `SendError`. Private helpers are `Ask4Resp`, `GetResp`, and `RespErr`. Local helper classes include `AlertMsg`, which wraps server alert payloads for `XrdSsiRRAgent::Alert`, and `SchedEmsg`, a scheduler job that calls `SendError`.

The task state names map the header enum values `isPend`, `isWrite`, `isSync`, `isReady`, `isDone`, and `isDead`. The file also owns constants used to disable XRootD read recovery before response waits, a zero-byte stand-in `zedData`, and a `voidSession` used for forced detachment.

## Control flow

`SendRequest` requires `isPend`, binds the target node into the request, calls `GetRequest`, builds an `XrdSsiRRInfo` write descriptor, fakes an empty request as one zero byte, and starts an asynchronous `epFile.Write`. A successful write marks `mhPend`; a failed write stores SSI error info and schedules an asynchronous error job.

`XeqEvent` is the central callback. In `isWrite`, it handles write failure, posts any killer semaphore, releases the request buffer, and calls `Ask4Resp`. `Ask4Resp` sends an SSI wait command via `epFile.Fcntl`, marks the task `isSync`, and unlocks the session while the wait is pending. In `isSync`, a successful response is parsed by `GetResp`: alert payloads are delivered and the wait is reissued, full responses call `SetResponse`, stream responses call `SetResponse((XrdSsiStream *)this)`, and malformed or missing responses become error responses. In `isReady`, the callback completes an async stream read and calls `ProcessResponseData` outside the session lock.

## State and persistence behavior

There is no durable persistence. Runtime state lives in the session, endpoint file, request pointer, deferred-callback counter, message-handler pending flag, response buffer ownership (`mdResp`), stream read buffer pointers, and the task state. The session mutex protects task state and lifetime. `defer` prevents `Finished` cleanup while callbacks might re-enter user code. `mhPend` tracks outstanding XrdCl callback ownership. `mdResp` holds an `AnyObject` response alive when metadata/data buffers inside it are handed to upper layers.

## Dependencies and integration points

The file integrates with `XrdSsiRRAgent` for request/responder binding, alerts, request buffers, and shared error info; with `XrdSsiSessReal` for locking and endpoint access; with `XrdCl::File` asynchronous `Write`, `Fcntl`, and `Read`; with `XrdScheduler` for deferred error delivery; and with `XrdSsiUtils` for XRootD-to-SSI error conversion and byte dumping.

## Risks and edge cases

Lifetime is the main risk. `Kill` can block waiting for an in-flight write callback via `XrdSysSemaphore` to avoid freeing request memory before XrdCl finishes using it. `RespErr` deliberately unlocks the session while posting an error response, so callers must reset lock guards correctly. The stream path allows only one async read at a time and treats short reads as EOF. `GetResp` trusts the wire-format header lengths after basic bounds checks; malformed prefix or metadata lengths produce generic invalid-response errors. Several comments note unusual or "ugly" cleanup sequencing, which is accurate: new callbacks must preserve `defer` and `mhPend` invariants.

## Test signals

Useful tests are asynchronous request success, write failure, response wait failure, alert followed by final response, full data response, stream response with sync and async reads, cancellation during write and during response wait, forced detach/orphan cleanup, invalid response headers, missing response objects, and short stream reads. Thread-sanitizer or stress tests are especially relevant because the file's correctness depends on session lock discipline and callback lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.hh

## Purpose

This header declares `XrdSsiTaskReal`, the concrete SSI task/responder/stream object used by real SSI sessions. It combines `XrdSsiEvent` callback execution, `XrdSsiResponder` response delivery, and `XrdSsiStream` passive streaming into one object owned by an `XrdSsiSessReal`.

## Important APIs, types, and functions

`TaskStat` models task lifecycle: pending, writing, waiting synchronously for response metadata, stream-ready, done, and dead. Public APIs include `Init`, `SetTaskID`, `SendRequest`, `Kill`, `Detach`, `Finished`, `SchedError`, `SendError`, `PostError`, `SetBuff` overloads for stream reading, `XeqEvent`, and `XeqEvFin`. `Implementation` returns the concrete object pointer for framework callbacks, `ID` returns the task id, and `RequestID` forwards to the bound request.

The object also exposes an intrusive doubly-linked `attList` node for session attachment lists. Private members keep error info, session/request pointers, retained metadata response ownership, pending write semaphore, stream buffers, status, task id, callback-defer count, timeout, and message-handler-pending state.

## Control flow

Callers initialize reusable task objects with `Init`, assign a task/session id with `SetTaskID`, then call `SendRequest`. From there the implementation file drives the asynchronous state machine through XrdCl callbacks and responder callbacks. Stream users interact through the two `SetBuff` overloads after a stream response has put the task in `isReady`.

## State and persistence behavior

The header defines only transient runtime state. `Init` resets request binding, state, timeout, `wPost`, `mhPend`, `defer`, attachment links, and any retained metadata response. The destructor deletes `mdResp` if present. No data is persisted beyond the lifetime of the task/session.

## Dependencies and integration points

The class inherits from SSI framework abstractions and references `XrdSsiRequest`, `XrdSsiSessReal`, `XrdSysSemaphore`, XrdCl response types, and SSI response/error/stream types. The interface is designed to be called from session management and XrdCl callback infrastructure rather than directly by plugins.

## Risks and edge cases

The class owns raw pointers and uses explicit lifetime conventions; copying would be unsafe and is implicitly avoided by normal usage. `RequestID` assumes `rqstP` is valid. `Init` deletes `mdResp`, so reinitialization while any upper-layer metadata/data pointer is still being used would be unsafe. The intrusive `attList` requires callers to preserve list invariants when moving tasks between session lists.

## Test signals

Header-level coverage comes from tests or integration runs that reuse a task object, bind it to a request/session, stream data through both `SetBuff` forms, and cancel at each state. ABI-sensitive checks should confirm enum values and inheritance remain compatible with callback dispatch users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTrace.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTrace.hh

## Purpose

This header defines SSI tracing masks and debug macros. It is intentionally lightweight so SSI implementation files can include it for conditional trace output without adding runtime cost in `NODEBUG` builds.

## Important APIs, types, and functions

The exported masks are `TRACESSI_ALL` and `TRACESSI_Debug`. In debug builds, `QTRACE(act)` tests `Trace.What`, `DEBUG(y)` emits `SYSTRACE` using the caller's `tident` and local `epname`, and `EPNAME(x)` declares a static endpoint name string. The header declares `extern XrdSysTrace Trace` in namespace `XrdSsi`.

## Control flow

There is no independent control flow. Callers place `EPNAME("...")` at function scope and wrap diagnostic messages with `DEBUG(...)`. The macro expands to a trace-flag check and system trace call when tracing is enabled.

## State and persistence behavior

The only state is the process-global `XrdSsi::Trace` object declared elsewhere. Trace flags are runtime configuration, not persistent state.

## Dependencies and integration points

This header depends on `XrdSys/XrdSysTrace.hh` in debug builds and integrates with files such as `XrdSsiTaskReal.cc` and `XrdSsiUtils.cc`. Its macros assume a `tident` symbol is visible in the calling method or class context, so it is coupled to SSI object's diagnostic naming convention.

## Risks and edge cases

The macro interface is fragile: missing `tident` or `epname` in a caller creates compile failures only in debug builds. Because `DEBUG(y)` evaluates stream expressions only when enabled, side effects inside debug expressions must be avoided. `NODEBUG` builds remove all debug code, so behavior must not depend on tracing side effects.

## Test signals

Build coverage should include both normal and `NODEBUG` configurations. Runtime trace tests can verify that setting `TRACESSI_Debug` emits messages and that clearing the flag suppresses them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTrace.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.cc -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.cc

## Purpose

This file implements SSI utility helpers for formatting byte buffers, mapping and returning errors, and asynchronously posting SSI error responses. It is shared support code for SSI request/responder paths such as `XrdSsiTaskReal`.

## Important APIs, types, and functions

`XrdSsiUtils::b2x` converts a byte buffer to a truncated hexadecimal string with an overflow suffix. `Emsg` formats an SFS-style error, logs it through `XrdSsi::Log`, and stores it in an `XrdOucErrInfo`. `GetErr`, `MapErr`, and `SetErr` translate `XrdCl::XRootDStatus` into errno-style values and SSI error text. `RetErr` schedules a `PostError` job that binds a request to a temporary responder and calls `SetErrResponse`.

The local `PostError` class is both an `XrdJob` and an `XrdSsiResponder`. It uses a recursive mutex because setting an error response can synchronously re-enter the responder `Finished` callback.

## Control flow

`RetErr` creates `PostError` with a duplicated error string and schedules it on `XrdSsi::schedP`. `PostError::DoIt` locks, sends the error response if still active, and either deletes itself immediately or lets `Finished` delete it after the responder callback. `Finished` unbinds the request, coordinates with the same mutex, and frees the job when both sides have completed.

## State and persistence behavior

There is no durable persistence. Runtime state is the transient scheduled job, bound request pointer, duplicated error text, error number, and active flag. The utility depends on global `Log` and scheduler pointers declared in namespace `XrdSsi`.

## Dependencies and integration points

The file depends on XRootD protocol error mapping, XrdCl response statuses, SSI request/responder infrastructure, SFS/Ouc error types, `XrdScheduler`, and `XrdSysError`. It is used by SSI task code to convert endpoint errors and by callers needing deferred error delivery to avoid lock clashes.

## Risks and edge cases

`b2x` treats `char` as signed when shifting; masking mitigates output but platform signedness is worth noting. `RetErr` duplicates `eTxt` without a null check before `strdup`. The `PostError` object self-deletes in two different paths and relies on the recursive mutex/`isActive` protocol; changes here can easily create use-after-free or leaks. `Emsg` always returns `SFS_ERROR` and logs the error user from `eDest`, so callers should not expect it to preserve original negative errno sign.

## Test signals

Tests should cover short and truncated `b2x` output, XRootD error-response mapping, internal status mapping when `errNo` is zero, asynchronous `RetErr` delivery with immediate and delayed `Finished`, and error-message/log formatting through `Emsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.hh -->
# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.hh

## Purpose

This header declares SSI utility functions used for diagnostics and error translation. It isolates common helper APIs behind a stateless `XrdSsiUtils` class.

## Important APIs, types, and functions

The public static API includes `b2x`, `Emsg`, `GetErr`, `MapErr`, `RetErr`, and `SetErr`. Forward declarations keep the header light for `XrdCl::XRootDStatus`, `XrdOucErrInfo`, `XrdSsiErrInfo`, and `XrdSsiRequest`.

## Control flow

The header has no runtime control flow. It documents call shape: status-to-error helpers fill strings or `XrdSsiErrInfo`, `RetErr` posts an asynchronous request error, and `Emsg` logs plus fills an output error object.

## State and persistence behavior

The class has no member state and no persistence. The default constructor/destructor are empty; all meaningful operations are static.

## Dependencies and integration points

The declarations are used by SSI task/session code and bridge XrdCl, SSI, SFS, and Ouc error systems. The implementation relies on global SSI logging and scheduling.

## Risks and edge cases

Because the helper methods accept raw buffers and references to external error objects, callers must provide correctly sized output buffers and live request/error objects. `RetErr` in particular assumes the request remains valid until the scheduled job binds and responds.

## Test signals

Compilation coverage should include consumers that only need declarations. Behavioral tests belong with the implementation and should validate error mapping and asynchronous error posting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiUtils.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/CMakeLists.txt -->
# sources/distributed-fs/xrootd/src/XrdSut/CMakeLists.txt

## Purpose

This CMake fragment adds the XrdSut sources and headers to the `XrdUtils` target. XrdSut provides security utility support for bucketized authentication buffers, password-file persistence, cache entries, random helpers, and tracing.

## Important APIs, types, and functions

The fragment uses one `target_sources(XrdUtils PRIVATE ...)` call. It lists all implementation/header pairs in this work item plus `XrdSutRndm.hh` and `XrdSutTrace.hh`.

## Control flow

There is no runtime control flow. Build generation includes these files in the private source list for `XrdUtils`, so dependent libraries consume compiled symbols from `XrdUtils` rather than compiling XrdSut directly.

## State and persistence behavior

No runtime state is defined. Build state is the dependency relationship between `XrdUtils` and the listed files.

## Dependencies and integration points

This integrates XrdSut with the wider XRootD build. Security protocol implementations such as `XrdSecpwd` and `XrdSecgsi` depend on the resulting utility objects for buffer parsing, password-file access, caches, and random generation.

## Risks and edge cases

Adding a new XrdSut source/header without updating this list can produce link or install/build visibility failures. Since headers are marked private in `target_sources`, public installation/export behavior must be controlled elsewhere in the build system.

## Test signals

Build tests should verify `XrdUtils` compiles and links after any XrdSut file changes. Downstream security protocol build targets are the main integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.cc

## Purpose

This file implements general XrdSut helper routines for tracing, bucket-type names, secret input, terminal prompts, hex conversion, time formatting/parsing, path expansion/template resolution, directory creation, secure-ish memory clearing, and advisory file locking.

## Important APIs, types, and functions

Key functions are `XrdSutSetTrace`, `XrdSutBuckStr`, `XrdSutMemSet`, `XrdSutGetPass`, `XrdSutGetLine`, `XrdSutAskConfirm`, `XrdSutToHex`, `XrdSutFromHex`, `XrdSutTimeString`, `XrdSutExpand`, `XrdSutResolve`, `XrdSutHome`, `XrdSutMkdir`, and `XrdSutParseTime`. `XrdSutFileLocker` wraps an advisory `fcntl` lock for a file descriptor.

## Control flow

Trace setup initializes a static `XrdSysLogger`, `XrdSysError`, and global `sutTrace`, then maps requested masks to notification/debug/dump levels. Path expansion handles absolute paths, `~user` or `~`, and relative paths via `PWD`. Template resolution replaces `<host>`, `<vo>`, `<group>`, `<user>`, and `<rtag>`, with `<rtag>` generated by `XrdSutRndm`. Directory creation with `-p` expands the path and walks each slash-delimited parent. Time parsing supports unit-suffixed fragments or `hh:mm:ss` mode.

## State and persistence behavior

Persistent process state includes the global trace pointer and a cached home-directory string. `XrdSutFileLocker` holds a descriptor lock for its lifetime and unlocks in the destructor. No file contents are persisted here, except directories created by `XrdSutMkdir`.

## Dependencies and integration points

The file depends on `XrdOucString`, `XrdSysPwd`, `XrdSysLogger`, `XrdSysError`, `XrdSutRndm`, and XrdSut tracing macros. It supports XrdSec password/GSI protocols and XrdSut buffer/file code that need bucket names, path handling, timestamps, and locks.

## Risks and edge cases

`XrdSutMemSet` simply calls `memset`; the volatile signature may not fully prevent optimization on all toolchains. `XrdSutToHex` repeatedly uses `strncat`, so callers must provide the documented `2*lin+1` output buffer. `XrdSutFromHex` accepts odd-length input and uses `sscanf` without validating hex characters. `XrdSutTimeString` uses `%2d` formatting and then patches spaces to zero at selected positions. `XrdSutMkdir` does not check `XrdSutExpand` return before indexing the path. File locking uses non-blocking `F_SETLK` and reports only validity, not detailed errno.

## Test signals

Tests should cover bucket-name lookup boundaries, trace-mask mapping, hex round trips including odd and invalid input, time formatting length and parse modes, expansion of absolute/relative/home paths, template replacement including `<rtag>`, recursive directory creation, and file lock contention between two descriptors/processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.hh

## Purpose

This header defines XrdSut utility constants, bucket type identifiers, trace masks, general helper declarations, and the RAII file-lock helper class used by XRootD security utilities.

## Important APIs, types, and functions

Constants include buffer/print limits and the `kXRSBucketTypes` enum for serialized security exchange buckets such as crypto module, main buffer, seals, public key, cipher, random tag, user, host, credentials, messages, server/session ids, status, timestamps, certificates, algorithms, and AFS info. The header declares helper functions implemented in `XrdSutAux.cc`, optional external `XrdSutGetPass`, and `XrdSutFileLocker` with shared/exclusive lock modes.

## Control flow

The header only declares behavior. Consumers construct buckets and buffers using the enum values and call helpers for path/time/input/hex operations during security protocol setup and administration.

## State and persistence behavior

No state is stored in the header. The declared file-locker owns an advisory descriptor lock at runtime. Helper functions may inspect environment variables and user database state; `XrdSutMkdir` can create directories.

## Dependencies and integration points

The header depends on XRootD platform headers and protocol integer types. It forward-declares crypto factory, string, bucket, and buffer classes so security protocol code can use shared utility APIs with minimal includes.

## Risks and edge cases

The enum values are wire-format-visible in serialized XrdSut buffers; reordering or changing numeric values would break protocol compatibility. The default `XrdSutGetPass` is explicitly fallback-quality and can be replaced by defining `USE_EXTERNAL_GETPASS`. Several helper contracts rely on caller-allocated buffers of documented size.

## Test signals

Compatibility tests should assert bucket numeric values, especially `kXRS_cryptomod` and following values. Header consumers should compile with and without `USE_EXTERNAL_GETPASS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutAux.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.cc

## Purpose

This file implements a minimal singly linked list used by `XrdSutBuffer` to manage `XrdSutBucket` pointers without owning the buckets themselves.

## Important APIs, types, and functions

`XrdSutBuckList` implements construction from an optional first bucket, destruction of list nodes, duplicate-checked `PutInFront` and `PushBack`, `Remove`, and pseudo-iterator methods `Begin` and `Next`. The private `Find` helper performs pointer-identity search.

## Control flow

Insertion first searches for the exact bucket pointer and adds a node only if not already present. `Remove` tries to use cached iterator state (`current`/`previous`) when valid, otherwise scans from the beginning. Iteration resets with `Begin`, then advances with `Next`.

## State and persistence behavior

The list stores node pointers, iterator cursor state, end pointer, and size. It does not delete the `XrdSutBucket` objects; `XrdSutBuffer` deletes buckets by iterating the list before the list nodes are destroyed.

## Dependencies and integration points

The file depends only on `XrdSutBuckList.hh` and, through that, `XrdSutBucket`. It is an internal support container for serialized authentication exchange buffers.

## Risks and edge cases

`End()` in the header dereferences `end` without null checking. `Remove` sets `previous = curr` after deleting `curr` in the non-head case, leaving a dangling cached previous pointer until the next iterator reset; current callers usually iterate/delete carefully, but this is fragile. The class is not thread-safe and uses raw pointers throughout. Pointer-identity duplicate detection means two equal bucket values can coexist if they are distinct objects.

## Test signals

Tests should cover empty list behavior, insertion order, duplicate pointer rejection, removal of head/middle/tail/missing buckets, iterator behavior after removal, and ownership interaction with `XrdSutBuffer` destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.hh

## Purpose

This header declares the lightweight linked-list container used to hold `XrdSutBucket` pointers in exchanged security buffers.

## Important APIs, types, and functions

`XrdSutBuckListNode` stores one bucket pointer and next node. `XrdSutBuckList` exposes `Size`, `End`, `PutInFront`, `PushBack`, `Remove`, `Begin`, and `Next`. The private `Find` helper is implemented in the source file.

## Control flow

The public API supports simple list mutation and single active iteration cursor. It is not a standard STL iterator and cannot support nested iteration on the same list.

## State and persistence behavior

The class stores only pointers and size; no persistence. The list owns nodes but not buckets.

## Dependencies and integration points

It includes `XrdSutBucket.hh` and is included by `XrdSutBuffer.hh`. It exists to avoid heavier container dependencies in old XrdSut code.

## Risks and edge cases

`End()` assumes the list is non-empty. The iterator state is mutable global state within the list object, so concurrent or nested scans will interfere. Callers must explicitly delete buckets if they own them.

## Test signals

Header-level tests are compile/ABI tests plus behavior covered by `XrdSutBuckList.cc` and `XrdSutBuffer` list use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuckList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.cc

## Purpose

This file implements `XrdSutBucket`, the unit of typed binary information exchanged inside XrdSut authentication buffers. Buckets carry a type id, byte size, and buffer pointer, with optional ownership through an internal `membuf`.

## Important APIs, types, and functions

Constructors accept a raw buffer, an `XrdOucString`, or another bucket. `Update(char *, int, int)` takes ownership of a raw buffer. `Update(XrdOucString &, int)` and `SetBuf` allocate and copy. `ToString` copies bucket bytes into a null-terminated `XrdOucString`. `Dump` prints hex and printable content. `operator==` compares byte contents only.

## Control flow

String constructors and update methods allocate exactly `s.length()` bytes and copy raw string bytes without appending null terminators. `Dump` walks each byte, appends hex tokens, classifies printable ASCII with a static mask, and prints eight-byte rows.

## State and persistence behavior

State is in-memory only. Ownership is split: `buffer` points to current content and `membuf` records the buffer to delete in the destructor. Raw-buffer construction sets both pointers to the incoming pointer, so the bucket owns and deletes that buffer.

## Dependencies and integration points

The file depends on `XrdOucString`, `XrdSutAux` bucket names, and XrdSut trace macros. It is used by `XrdSutBuffer` and security protocols to carry credentials, crypto material, status values, and nested buffers.

## Risks and edge cases

The copy constructor does not initialize fields if allocation fails, leaving members potentially undefined. `operator==` ignores type and compares only size/content, which may be intentional but can surprise callers. `SetBuf` and `Update(XrdOucString)` return `-1` for empty input after clearing the bucket, so an empty bucket cannot be represented as a successful update. `Dump` assumes `buffer` is valid when `size > 0`.

## Test signals

Tests should cover ownership transfer, copy construction, update/clear behavior, equality across same bytes with different types, string conversion for binary data containing nulls, and dump output stability for printable and non-printable data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.hh

## Purpose

This header declares `XrdSutBucket`, the typed byte-buffer object used as the atomic field inside XrdSut serialized authentication messages.

## Important APIs, types, and functions

Public data members are `type`, `size`, and `buffer`. Constructors support raw buffers, `XrdOucString`, and copy construction. Methods include `Update`, `SetBuf`, `Dump`, `ToString`, and equality/inequality operators. Private `membuf` tracks owned allocation.

## Control flow

The class is intentionally simple and leaves most validation to callers. Consumers create buckets, add them to `XrdSutBuffer`, and serialize/parse based on `type`.

## State and persistence behavior

No direct persistence. Bucket bytes are serialized by `XrdSutBuffer::Serialized` and may eventually be written into credentials or protocol messages. Destructor deletes `membuf`.

## Dependencies and integration points

It includes `XrdSutAux.hh` for bucket type constants and forward-declares `XrdOucString`. It is consumed by `XrdSutBuckList` and security protocol parsers.

## Risks and edge cases

Public mutable fields make it easy to break ownership or size invariants. The raw-buffer constructor takes ownership, so stack/static buffers must not be passed. There is no move/copy assignment definition.

## Test signals

Compile coverage should include consumers that manipulate public fields and use all constructors. Runtime tests belong with the implementation and buffer serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBucket.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.cc

## Purpose

This file implements `XrdSutBuffer`, the bucketized wire/message container used by XrdSec password and GSI protocols. It can parse an initial `&P=<protocol>,<options>` buffer or a serialized exchange buffer containing protocol id, step number, and typed buckets.

## Important APIs, types, and functions

Important methods are the buffer-parsing constructor, destructor, `UpdateBucket`, `Dump`, `Message`, `MarshalBucket`, `UnmarshalBucket`, `GetBucket`, `Deactivate`, and `Serialized`. The header also provides inline `AddBucket`, `Remove`, accessors, and step mutators.

## Control flow

Parsing first distinguishes `&P=` initial negotiation buffers from full exchange buffers. Full parsing reads a null-terminated protocol id, a network-order step, then repeats `type`, `length`, `data` until `kXRS_none`, skipping inactive buckets. Serialization performs the inverse: protocol string, network-order step, active buckets only, and a `kXRS_none` terminator. `MarshalBucket` stores a 32-bit integer in network byte order and `UnmarshalBucket` validates size before converting back.

## State and persistence behavior

The object owns buckets in `fBuckets` and deletes them in the destructor. It stores protocol name, options, and step as transient message state. Serialized bytes may be transmitted or nested in other buckets; no direct disk persistence occurs here.

## Dependencies and integration points

The file depends on XRootD security protocol id size, network byte-order helpers, `XrdOucString`, `XrdSutBucket`, `XrdSutBuckList`, and XrdSut tracing. It is heavily used by `XrdSecpwd` and `XrdSecgsi` handshake parsing and construction.

## Risks and edge cases

The parser has limited bounds validation. It reads `type` and `blen` before ensuring enough bytes remain for those fields, and the total-length calculation excludes only the step size, not the protocol prefix, so malformed inputs deserve careful fuzzing. Serialization copies `bp->buffer` for any active bucket regardless of null when size is nonzero. The destructor deletes buckets while iterating a list that does not own bucket nodes, relying on the list cursor remaining valid. `Serialized` allocation ownership depends on `opt` (`new[]` vs `malloc`), which callers must match.

## Test signals

Tests should cover initial negotiation parsing, full serialize/parse round trips, inactive bucket omission, integer marshal/unmarshal with wrong size, tagged bucket lookup, malformed/truncated buffers, zero-size buckets, nested buffers, and caller cleanup for both allocation modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.hh

## Purpose

This header declares `XrdSutBuffer`, the typed bucket container used to build and parse XRootD security handshake messages.

## Important APIs, types, and functions

Constructors create an outbound buffer from protocol/options or parse serialized bytes. Inline `AddBucket` overloads add raw buffers, strings, or existing bucket pointers. Other APIs update, remove, dump, serialize, deactivate, marshal/unmarshal integer buckets, find buckets by type/tag, inspect bucket count/protocol/options/step, and increment the step.

## Control flow

Consumers build messages by adding buckets and serializing, or parse incoming bytes then query buckets by type. The step number tracks handshake iteration.

## State and persistence behavior

The class owns its buckets and stores protocol/options/step in memory. Serialized output is caller-owned and can be transmitted or stored elsewhere.

## Dependencies and integration points

It includes `XrdSutBuckList.hh` and forward-declares `XrdOucString`. It is part of the security utility target and a core dependency of password/GSI security protocols.

## Risks and edge cases

The inline `AddBucket(char *bp, ...)` constructs a bucket that owns `bp`; callers must not reuse or free that memory. `GetBuckList` casts away constness. The API exposes raw bucket pointers and removal is only from the list, not deletion, so ownership transfer must be explicit.

## Test signals

Header/API tests should exercise all add overloads, removal without deletion, step mutation, and source compatibility for protocol consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutBuffer.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutCache.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutCache.hh

## Purpose

This header implements a generic in-memory cache for `XrdSutCacheEntry` objects, protected by a recursive table mutex and per-entry read/write locks. It is a template-like concrete cache used by security utility code for short-lived validated entries.

## Important APIs, types, and functions

`XrdSutCacheGet_t` is an optional condition predicate, and `XrdSutCacheArg_t` is a four-slot generic argument carrier. `XrdSutCache::Get(tag)` returns an existing entry read-locked. `Get(tag, rdlock, condition, arg)` returns an existing entry read-locked if valid by condition, otherwise write-locked for refresh, or creates a new write-locked entry. `Num` returns table count and `Reset` purges the hash table.

## Control flow

Each lookup locks the hash table, finds or creates an entry, then obtains the entry lock before returning. The conditional lookup first read-locks an existing entry and applies the predicate; failed predicates cause an unlock followed by write-lock acquisition so the caller can validate/update the entry. The `rdlock` output tells the caller which lock mode was obtained.

## State and persistence behavior

State is fully in-memory: an `XrdOucHash<XrdSutCacheEntry>` plus locks. There is no disk persistence. Returned entries remain locked until the caller unlocks `entry->rwmtx`, usually via `XrdSutCERef`.

## Dependencies and integration points

The header depends on `XrdOucHash`, `XrdSutCacheEntry`, and XrdSys pthread locks. It complements the file-backed `XrdSutPFCache` but stores generic `XrdSutCacheEntry` records.

## Risks and edge cases

The table mutex is held while entry locks are acquired, so lock ordering must remain consistent to avoid deadlocks. If entry locking fails, the entry status is set inactive but still returned in some paths. `Reset` purges the table without taking the table mutex in this inline implementation, so external synchronization expectations should be checked. Callers must always unlock returned entries.

## Test signals

Concurrency tests should cover simultaneous first lookup, condition pass/fail, lock failure simulation, reset under use, and correct `rdlock` reporting. Leak tests should verify purged entries are destroyed by the hash table policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.cc

## Purpose

This file implements generic in-memory cache entry buffers and entries. These mirror the persistent-file entry shape but use `XrdSysRWLock` for shared/exclusive access.

## Important APIs, types, and functions

`XrdSutCacheEntryBuf` owns an optional byte buffer and supports construction, copy construction, destruction, and `SetBuf`. `XrdSutCacheEntry` supports construction with name/status/count/mtime, copy construction, `Reset`, `SetName`, `AsString`, and assignment.

## Control flow

Constructors duplicate names and buffers when present. `Reset` clears the name, status, count, timestamp, and all buffers. `AsString` formats status/count/buffer lengths/modification time/name into a static display buffer. Assignment should copy all fields and buffers from another entry.

## State and persistence behavior

State is in-memory only: name, status, count, modification time, four buffers, and a read/write lock declared in the header. No disk I/O occurs.

## Dependencies and integration points

The file uses `XrdSutTimeString` from `XrdSutAux` and is used by `XrdSutCache`. The entry status enum in the header encodes inactive/disabled/allowed/expired/ok/special semantics for consumers.

## Risks and edge cases

The assignment operator appears defective: it calls `SetName(name)` instead of `SetName(e.name)` and calls `SetBuf(e.bufN.buf)` without passing `e.bufN.len`, so buffers are cleared rather than copied. `AsString` returns a static buffer and is not thread-safe. It also formats `name` with `%s` even if name is null. `SetBuf` clears existing data before allocation, so allocation failure loses the previous value.

## Test signals

Tests should cover deep copy construction, assignment preserving name and buffers, reset clearing all buffers, `AsString` with null and non-null names, and concurrent access patterns through `XrdSutCache`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.hh

## Purpose

This header declares generic cache-entry storage for XrdSut in-memory caches, including entry status values, four arbitrary buffers, metadata, and a read/write lock.

## Important APIs, types, and functions

`kCEntryStatus` defines inactive, disabled, allowed, expired, ok, and special states. `XrdSutCacheEntryBuf` owns one byte buffer. `XrdSutCacheEntry` stores name, status, count, modification time, four buffers, and `rwmtx`. `Length`, `Reset`, `SetName`, `AsString`, and assignment are the main entry APIs. `XrdSutCERef` is an RAII-ish lock holder for `XrdSysRWLock`.

## Control flow

Callers obtain entries through `XrdSutCache`, use the lock already held or manage it through `XrdSutCERef`, inspect/update fields, then unlock. The header exposes fields publicly for direct consumer mutation.

## State and persistence behavior

No direct persistence. The `Length` calculation describes a serializable shape similar to `XrdSutPFEntry`, but this cache entry is used in memory.

## Dependencies and integration points

It depends on protocol integer types and XrdSys pthread locks. It is consumed by `XrdSutCache.hh`.

## Risks and edge cases

Public fields and manual lock management can lead to races if callers bypass the cache's returned lock. `XrdSutCERef::Set` unlocks a prior lock when switching, which is convenient but can hide accidental lock replacement. Copying entries does not copy lock state, as expected, but assignment behavior must be validated in the source.

## Test signals

Tests should validate lock holder behavior, buffer ownership, length calculation for all buffer combinations, status transitions, and field updates under read/write locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutCacheEntry.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.cc

## Purpose

This file implements `XrdSutPFCache`, an in-memory cache of password-file entries (`XrdSutPFEntry`) with optional load/flush/refresh from an `XrdSutPFile`. It accelerates security credential lookups while preserving entry-level locking.

## Important APIs, types, and functions

Implemented methods include destructor, `Init`, public and private `Get`, `Add`, `Remove`, `Delete`, `Trim`, `Reset`, `Dump`, `Load`, `Rehash`, `Flush`, and `Refresh`. `Delete` also manages a static deferred-delete queue for entries that cannot be locked immediately.

## Control flow

`Init` allocates the pointer array and initializes the hash table. Public `Get` refreshes the hash if stale, read-locks the cache, finds exact or best wildcard entry, then repeatedly tries to lock the entry mutex, waiting up to `maxTries * retryMSW`. `Add` returns an existing locked entry if present, otherwise write-locks the cache, expands the array when full, appends a new entry, rehashes, and returns it locked through `XrdSutPFCacheRef`. `Load` reads a `PFile` header and index chain, reads active entries, copies them into cache entries, and rebuilds the hash. `Flush` writes newer cache entries back to a file.

## State and persistence behavior

The cache stores an array of `XrdSutPFEntry *`, current capacity/highest index, update timestamps, lifetime, a hash table mapping names to array indices, the backing file path, and initialization state. Persistence is optional and mediated by `XrdSutPFile`: `Load` populates from disk, `Flush` writes newer cache values, and `Refresh` reloads when the backing file is newer.

## Dependencies and integration points

The file depends on `XrdSutPFile`, `XrdSutPFEntry`, `XrdSutAux`, XrdSut tracing, `XrdOucHash`, XrdSys locks, and `XrdSysTimer`. It is used by XrdSec password protocol caches for admin, user, autologin, and server-public-key data.

## Risks and edge cases

There are several high-risk areas. `Init` sets `isinit = 1` on the allocation-failure path rather than the success path, which can cause repeated initialization attempts after success or false initialized state after failure. The expansion loop that should clear new array slots uses `for (i = cachemx + 1; i <= cachemx; i++)`, so it never initializes the new tail. `Remove(opt==1)` dereferences the hash lookup result without checking null. `Refresh` takes the cache write lock and then calls `Load`, which also write-locks; this depends on lock implementation behavior and may deadlock if non-recursive. Deferred deletion is a static queue shared across cache instances, so cleanup in one cache can process entries from another. Time comparisons use cache update time rather than exact file mtimes, so rapid file updates may be missed on coarse timestamp filesystems.

## Test signals

Tests should cover init success/failure, add beyond initial capacity, exact and wildcard get, entry-lock contention and retry timeout, remove missing/existing/prefix entries, deferred delete cleanup, trim by lifetime, load/flush/refresh round trips, null hash lookup paths, and concurrent use by multiple threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.hh

## Purpose

This header declares the password-file entry cache used by XrdSut security code. It combines cache-wide read/write locking, per-entry mutex references, hash lookup, backing-file metadata, and cache-management APIs.

## Important APIs, types, and functions

`XrdSutPFCacheRef` tracks and unlocks a held entry mutex. `XrdSutPFCache` exposes status methods `Entries` and `Empty`, lifecycle methods `Init`, `Reset`, `Load`, `Flush`, `Refresh`, `Rehash`, `SetLifetime`, cache operations `Get`, `Add`, `Remove`, `Trim`, and debug `Dump`. Private helpers perform raw lookup and deferred-safe deletion.

## Control flow

Callers generally create a ref, call `Get` or `Add`, use the returned locked entry, then let the ref unlock. File-backed callers load or refresh from an `XrdSutPFile` and flush modified entries back.

## State and persistence behavior

The header defines in-memory state plus optional backing file path. Persistence happens through the implementation's `Load`/`Flush`/`Refresh` methods and `XrdSutPFile`.

## Dependencies and integration points

It depends on protocol integer types, `XrdSutPFEntry`, `XrdOucHash`, `XrdOucString`, and XrdSys locks. `XrdSecpwd` uses this cache for credential and public-key file data.

## Risks and edge cases

The API returns raw mutable entry pointers protected by an external ref object; forgetting the ref or keeping the pointer after unlock is unsafe. `Entries` returns `cachemx + 1`, which includes holes after removals and is not active-entry count. `Get(int)` only checks upper bound, not negative indices.

## Test signals

Header/API tests should cover ref locking/unlocking, empty state, index lookup boundaries, active-entry holes after removal, and integration with file-backed load/flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFCache.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.cc

## Purpose

This file implements password-file entry buffers and entries. A `XrdSutPFEntry` is the serializable record stored in `XrdSutPFile` and cached by `XrdSutPFCache`.

## Important APIs, types, and functions

`XrdSutPFBuf` owns one byte buffer and supports construction, copy construction, destruction, and `SetBuf`. `XrdSutPFEntry` supports construction with name/status/count/mtime, copy construction, `Reset`, `SetName`, `AsString`, and assignment. The status enum is declared in the header.

## Control flow

Construction duplicates names and buffers. `Reset` clears all fields and refreshes modification time. `AsString` formats a static display string with status/count/buffer sizes/time/name. Assignment should duplicate another entry's metadata and four buffers.

## State and persistence behavior

The entry's fields are the durable state persisted by `XrdSutPFile`: status, count, modification time, and four arbitrary buffers. The name is stored in the file index rather than the entry body, but cache copies hold it on the entry object too.

## Dependencies and integration points

The file depends on `XrdSutAux` for time formatting and is used by `XrdSutPFile` and `XrdSutPFCache`.

## Risks and edge cases

The assignment operator appears to have the same defects as `XrdSutCacheEntry`: it calls `SetName(name)` rather than `SetName(e.name)` and calls `SetBuf(e.bufN.buf)` without the source length, clearing buffers instead of copying them. `AsString` uses a static buffer and `%s` for `name`, so it is not thread-safe and can mishandle null names. `SetBuf` clears old data before allocation, so failures lose previous content.

## Test signals

Tests should verify copy construction, assignment preserving all buffers and names, reset semantics, display formatting, and round-trip persistence through `XrdSutPFile`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.hh

## Purpose

This header declares the password-file entry record used by XrdSut credential files and caches.

## Important APIs, types, and functions

`kPFEntryStatus` defines inactive, disabled, allowed, ok, one-time, expired, special, anonymous, and crypt states. `XrdSutPFBuf` stores one arbitrary byte buffer. `XrdSutPFEntry` stores name, status, count, modification time, four buffers, and an entry mutex. It exposes `Length`, `Reset`, `SetName`, `AsString`, and assignment.

## Control flow

`XrdSutPFile` serializes/deserializes these entries, while `XrdSutPFCache` locks and returns them for credential validation/update. Callers mutate public fields directly.

## State and persistence behavior

The entry's non-name fields are serialized into PFile entry records. Name is used as the index key. The mutex is runtime-only and not copied to disk.

## Dependencies and integration points

It depends on protocol integer types and XrdSys mutexes. It is included by password-file cache and file interfaces and by security protocol code that reads credentials.

## Risks and edge cases

Public fields make serialization invariants caller-managed. The mutex must be respected by cache users. `Length` must stay in sync with `XrdSutPFile::WriteEnt` and `ReadEnt`; changing either side breaks on-disk compatibility.

## Test signals

Compatibility tests should assert `Length` for known buffer sizes, status numeric values, and PFile round-trip compatibility across versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFEntry.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.cc

## Purpose

This file implements `XrdSutPFile`, a small binary file format and access layer for login/security records. It manages file headers, linked index entries, serialized `XrdSutPFEntry` records, advisory locking, hash-table lookup, entry update/removal, trimming of unreachable bytes, and browsing/debug output.

## Important APIs, types, and functions

Support types are `XrdSutPFEntInd` for index records and `XrdSutPFHeader` for the fixed file header. Public file APIs include constructor/destructor, `Init`, `Open`, `Close`, `UpdateHeader`, `RetrieveHeader`, `WriteEntry`, `UpdateCount`, `ReadEntry` by name or index offset, `RemoveEntry`, `RemoveEntries`, `Trim`, `SearchEntries`, `SearchSpecialEntries`, and `Browse`. Private low-level helpers read/write headers, indexes, and entries, reset byte ranges, update the hash table, and format errors.

## Control flow

Initialization creates a new file with a default header when requested or opens an existing file and optionally builds the hash table. `Open` handles normal files or `XXXXXX` temporary templates, applies read/write/truncate mode, and takes a whole-file advisory lock. `WriteEntry` reads the header, finds any existing active index by name, overwrites in place if the old allocation is large enough, or appends a new entry and updates the index/header. Removal marks entries inactive, zeros their old data, clears the index entry offset, increments `jnksiz`, decrements active entries, and updates header timestamps. `Trim` renames the old file, creates a new one, copies only active entries and rebuilt index records, then resets unreachable bytes to zero.

## State and persistence behavior

Persistent state is the binary file: fixed header (`fileID`, version, change/index times, active entry count, first index offset, unreachable byte count), a linked list of index records (`name`, next index offset, entry offset, entry size), and serialized entry records (`status`, count, mtime, four buffer lengths, buffer bytes). Runtime state includes the current file name, descriptor, validity flag, optional hash table mapping names to index offsets, hash update time, and last error code/string.

## Dependencies and integration points

The file depends on POSIX file APIs, `XrdOucHash`, `XrdOucString`, `XrdSutAux`, `XrdSutPFEntry`, XrdSut tracing, and `XrdSysE2T`. It is the backing store for `XrdSutPFCache` and is used by XrdSec password administration/protocol code for admin, user, autologin, and server-key data.

## Risks and edge cases

This file has several concrete correctness risks. `ReadEntry(const char *,...)` calls `Open(1 &wasopen)` instead of `Open(1, &wasopen)`, so it passes a boolean expression as the open mode and never fills `wasopen`. `UpdateCount` dereferences `fHashTable->Find(tag)` without a null check. `Open` checks write compatibility with `if (!(omode | O_WRONLY))`, which should likely be a bitwise-and test. Write helpers allocate buffers but do not delete them before returning, creating leaks. The format writes host-endian integers, so files are not portable across endian/word-size assumptions. `ReadEnt` does not clear existing entry buffers before allocating new ones, so reusing an entry object can leak prior buffers. Error formatting casts integer addresses through `const char *`, making calls type-unsafe. `Trim` switches `fFd` between backup and new file descriptors and must restore/close carefully.

## Test signals

High-value tests include create/open/close with locking contention, header round trip, write/read first entry, overwrite with smaller and larger entries, remove and trim, hash and no-hash lookup, wildcard search, special-entry search, count update/reset/read, browse output, temporary-file creation, corrupt/truncated file handling, and leak/ASAN runs around repeated reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.hh -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.hh

## Purpose

This header declares the `XrdSutPFile` binary credential-file API, its file-format constants, error codes, header/index record types, and public operations for reading and updating password-file entries.

## Important APIs, types, and functions

Constants define file id/version, fixed header offsets, create/open flags, and max lock tries. `EPFileErrors` enumerates internal error categories. `XrdSutPFEntInd` represents an index entry with name, next-index offset, entry offset, and entry size. `XrdSutPFHeader` represents the fixed header. `XrdSutPFile` exposes lifecycle, open/close, update, read, search, browse, and trim APIs.

## Control flow

Consumers construct or initialize a file object, then call read/write/search helpers. The class opens and closes internally for most operations unless already open, and it maintains an optional hash table to speed name lookup.

## State and persistence behavior

The declared format is persistent and offset-based. Header offsets are hard-coded constants, so file layout compatibility depends on these values and on the serialized order implemented in the source. Runtime fields track descriptor state, hash table, last hash update time, last error, and name.

## Dependencies and integration points

It depends on XRootD protocol integer types, `XrdOucHash`, `XrdOucString`, and `XrdSutPFEntry`. `XrdSutPFCache` is a friend because it needs low-level read/open/close access for cache loading.

## Risks and edge cases

The class has a copy constructor but no assignment operator, while it owns a file descriptor and heap pointers; copying can duplicate descriptor ownership unsafely. The public API uses `kXR_int32` for file offsets, limiting usable file size and assuming offset values fit 32 bits. Changing `XrdSutPFEntry::Length` or header offsets breaks compatibility with existing files.

## Test signals

Header-level compatibility tests should pin offsets, file id/version, header length, index length, and public API compile use by `XrdSutPFCache` and security admin code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutPFile.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.cc -->
# sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.cc

## Purpose

This file implements the XrdSut random helper used to generate random strings, byte buffers, random tags, and unsigned integers for security protocol support.

## Important APIs, types, and functions

`XrdSutRndm::Init` seeds the C library PRNG from `/dev/urandom` if possible or `time(0)` otherwise. `GetString(const char *,...)` maps option names to character classes. `GetString(int,...)` returns null-terminated random strings from printable, alphanumeric, hex, or crypt-like sets. `GetBuffer` returns caller-owned random bytes, optionally filtered by the same classes. `GetRndmTag` returns an eight-character crypt-like tag. `GetUInt` returns `rand()`.

## Control flow

All generation lazily initializes the static `fgInit` flag. String generation repeatedly pulls `rand()` values, slices bits into candidate characters, checks a static mask, and appends accepted characters until the requested length is reached. Buffer generation similarly emits four candidate bytes per `rand()` call and filters when requested.

## State and persistence behavior

The only state is the process-global `fgInit` flag and the C library PRNG state seeded by `srand`. No persistence occurs.

## Dependencies and integration points

The file depends on POSIX `open/read/close`, `time`, `rand/srand`, `XrdOucString`, and XrdSut tracing. It is used by XrdSut template resolution and by XrdCrypto/XrdSec password/GSI code for salts, tags, keys, IV-like buffers, and serial values.

## Risks and edge cases

This is not a cryptographically strong generator despite seeding from `/dev/urandom`; after seeding it uses `rand()`, which is predictable and global-state-based. It is not thread-safe around initialization or PRNG access. If `/dev/urandom` is unavailable, seeding with `time(0)` is weak. Negative lengths are not validated before `new char[len+1]` or `new char[len]`. Debug logging can print generated secret material. Character masks are hand-coded and should be tested carefully.

## Test signals

Tests should cover each character class, invalid option fallback, zero and negative length handling, forced reinitialization, `/dev/urandom` fallback behavior via dependency injection or platform tests, caller ownership of `GetBuffer`, and security review signals for consumers requiring cryptographic randomness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdSut/XrdSutRndm.cc -->
