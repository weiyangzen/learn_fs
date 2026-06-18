# subset-b-007919 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.hh

## Purpose

This header declares `XrdCl::Channel`, the client-side communication channel between XRootD client code and a server endpoint. It is part of the PostMaster/Stream transport stack and owns the per-channel stream object, incoming queue, channel data object, tick generator hook, transport handler link, and synchronization needed to send messages and react to stream lifecycle events.

The ownership note is the most important documentation in the file. A channel is normally owned through a `std::shared_ptr` held by `PostMaster`; `Stream` and `AsyncSocketHandler` instances keep weak or temporary shared ownership during active connections; `PostMaster` also tracks non-owning raw channel pointers for finalization. The design is explicitly about safe lifetime across asynchronous socket handlers, redirect collapse, and global shutdown.

## Important APIs, types, and functions

`Channel(const URL&, Poller*, TransportHandler*, TaskManager*, JobManager*, const URL&)` constructs a channel for one server URL and its preferred URL. The object keeps non-owning pointers to `Poller`, `TransportHandler`, `TaskManager`, and `JobManager`, and owns `std::unique_ptr<Stream> pStream`.

`Send(Message*, MsgHandler*, bool stateful, time_t expires)` is the public async send entry point. It queues a protocol message and arranges for the caller's message handler to be notified when the message is sent or times out. The `stateful` flag makes physical stream disconnects visible as errors for operations that cannot silently recover.

`QueryTransport(uint16_t, AnyObject&)` forwards transport-specific queries. `RegisterEventHandler` and `RemoveEventHandler` attach `ChannelEventHandler` listeners. `Tick(time_t)` is the time-event hook used by the task/tick system. `ForceDisconnect` overloads cover ordinary forced disconnect, hush/suppressed notification disconnect, and internal stream-triggered disconnect with a known channel shared pointer and session id. `ForceReconnect`, `NbConnectedStrm`, and `SetOnDataConnectHandler` expose reconnection and data-stream state to higher-level copy and read paths.

`CanCollapse(const URL&)`, `DecFileInstCnt()`, `SetSelf(std::shared_ptr<Channel>&)`, and `Finalize()` are PostMaster integration points. `SetSelf` stores the weak self pointer used by socket handlers and stream callbacks; `Finalize` releases resources under the assumption that job, poller, and task managers have already stopped.

## Control flow

The header describes the channel as the middle layer between PostMaster and Stream. PostMaster creates and owns the shared channel, calls `SetSelf`, then clients submit messages through `Send`. The stream layer drives network I/O and channel events; channel-level handlers observe status changes and disconnect/reconnect decisions.

Timer flow enters through `Tick`, which likely drains timeouts in `pIncoming` and stream state. Disconnect flow can originate from external users via `ForceDisconnect`, from reconnect policy via `ForceReconnect`, or internally from a stream with the `ForceDisconnect(self, sess)` overload to avoid lifetime races while callbacks are in flight.

## State and persistence behavior

All state is in-memory transport state. There is no durable persistence. The main mutable members are the endpoint URLs, `pStream`, `pChannelData`, `pIncoming`, `pTickGenerator`, `pSelf`, and `pMutex`. The class coordinates asynchronous lifetime rather than storing file or application data.

`pSelf` is weak to avoid a channel/stream cycle. `pStream` is owned uniquely by the channel, while socket handlers may hold shared channel ownership until they close. Shutdown correctness depends on `Finalize` and force-disconnect paths not racing with in-flight socket callbacks.

## Dependencies and integration points

The header depends on `XrdClStatus`, `XrdClURL`, `XrdClPoller`, `XrdClInQueue`, `XrdClPostMasterInterfaces`, `XrdClAnyObject`, `XrdClTaskManager`, and `XrdSysPthread`. It forward-declares `Stream`, `JobManager`, `VirtualRedirector`, `TickGeneratorTask`, and `Job`.

Primary integration is with PostMaster for channel lookup and lifetime, Stream for actual message I/O, Poller for non-blocking socket events, TransportHandler for protocol details, TaskManager for ticking, and JobManager for callback jobs. `ClassicCopyJob` indirectly uses channel data-stream APIs through PostMaster when scaling parallel reads.

## Risks and edge cases

The lifetime model is delicate: raw non-owning channel pointers in PostMaster are valid only while finalization discipline is maintained, and weak self pointers require callers to lock shared ownership before async use. Redirect collapse can remove PostMaster ownership while socket handlers still hold the channel, so cleanup paths must tolerate channels no longer present in the primary map.

The class stores several non-owning manager pointers. `Finalize` documentation says those managers may already be stopped; implementation must therefore avoid queuing new work after finalization. Disconnect overloads also need consistent locking around `pStream` and `pIncoming` to avoid races with callbacks.

## Test signals

No direct test is included in this work item. Strong signals would come from connection/reconnect integration tests, PostMaster finalization tests, redirect-collapse tests, data-stream connection callbacks, and timeout/disconnect behavior under concurrent sends. Existing consumers such as `XrdClStream`, `XrdClPostMaster`, and copy data-stream scaling are the relevant integration surfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannel.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.cc

## Purpose

This file implements `XrdCl::ChannelHandlerList`, a small thread-safe helper for managing `ChannelEventHandler` listeners attached to a stream/channel. It supports registering handlers, unregistering handlers, and broadcasting channel events while pruning handlers that ask to be removed.

## Important APIs, types, and functions

`AddHandler(ChannelEventHandler*)` locks `pMutex` and appends the raw handler pointer to `pHandlers`.

`RemoveHandler(ChannelEventHandler*)` locks the same mutex, scans the list for pointer identity, erases the first match, and returns immediately.

`ReportEvent(ChannelEventHandler::ChannelEvent, Status)` locks the list, calls `OnChannelEvent(event, status)` for each handler, and erases handlers that return `false`. Returning `true` keeps the handler registered.

## Control flow

The control flow is deliberately linear. Registration and removal are direct list mutations under `XrdSysMutexHelper`. Event dispatch iterates with an erase-aware iterator so a handler can opt out through its return value without invalidating the traversal.

## State and persistence behavior

State is the in-memory `std::list<ChannelEventHandler*> pHandlers`. No handler is owned by the list, no durable persistence exists, and duplicate registrations are not rejected. If the same pointer is added twice, it receives events twice and `RemoveHandler` removes only the first entry.

## Dependencies and integration points

The implementation includes `XrdClChannelHandlerList.hh` and `XrdClPostMasterInterfaces.hh`. `XrdClStream.hh` contains a `ChannelHandlerList pChannelEvHandlers`, making this helper part of stream event propagation to channel users such as PostMaster, file state handlers, and copy/read code waiting on connection events.

## Risks and edge cases

Handlers are called while `pMutex` is held. If a handler calls back into this list or into code that attempts to register/remove handlers, deadlock is possible unless the broader code avoids that pattern. A slow handler also blocks all list mutations and event delivery.

Because pointers are raw and non-owning, callers must ensure handlers remain alive until removed or until they return `false` from an event. There is no duplicate suppression and no null pointer check.

## Test signals

No direct tests are visible. Useful tests would cover add/remove, self-removal by returning false, duplicate registration behavior, concurrent add/remove/report discipline, and a handler that removes another handler. Stream connection event tests indirectly exercise this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.hh

## Purpose

This header declares `XrdCl::ChannelHandlerList`, a mutex-protected list of `ChannelEventHandler` observers. It is a compact utility used by stream/channel code to centralize event listener management.

## Important APIs, types, and functions

`AddHandler`, `RemoveHandler`, and `ReportEvent` are the complete public surface. `ReportEvent` accepts a `ChannelEventHandler::ChannelEvent` and a `Status`, matching the interface declared in `XrdClPostMasterInterfaces.hh`.

The private state is `std::list<ChannelEventHandler*> pHandlers` and `XrdSysMutex pMutex`.

## Control flow

Callers add handlers before they need event notification, remove them when no longer interested, and stream/channel code calls `ReportEvent` when a channel event occurs. The implementation decides whether handlers stay subscribed based on `OnChannelEvent`'s boolean return.

## State and persistence behavior

The class stores only non-owning handler pointers. It does not persist state, transfer ownership, or define copy semantics. Since no copy constructor is deleted in the header, accidental copying would copy raw pointers and mutex state if allowed by the compiler/toolchain, but typical `XrdSysMutex` semantics should make copying unavailable or unsafe.

## Dependencies and integration points

The header depends on `<list>`, `XrdClPostMasterInterfaces.hh`, `XrdClStatus.hh`, and `XrdSysPthread.hh`. Its principal integration is as a member of `Stream`, where it connects low-level socket events to higher-level clients.

## Risks and edge cases

The header does not document ownership, duplicate policy, or callback locking semantics; those are important because the implementation calls handlers under lock. It also does not prevent null handlers or repeated insertion.

## Test signals

No direct tests are included. Compile-time coverage comes from `XrdClStream` and channel users. Runtime signals should focus on handler lifecycle, event ordering, and deadlock avoidance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClChannelHandlerList.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumHelper.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumHelper.hh

## Purpose

`CheckSumHelper` is a convenience wrapper around `XrdCksCalc` calculators for streaming checksum calculation in copy, stdio, ZIP, and error-correction paths. It hides calculator lookup through `DefaultEnv::GetCheckSumManager`, incremental updates, final formatting through `XrdCksData`, and raw final value extraction.

## Important APIs, types, and functions

The constructor stores a display name and checksum type. `Initialize()` is a no-op for an empty checksum type; otherwise it obtains the global `CheckSumManager`, requests a calculator for `pCkSumType`, logs failures, and stores the returned calculator in `pCksCalcObj`.

`Update(const void*, uint32_t)` feeds bytes into the calculator when one exists. `GetCheckSum(std::string&, std::string&)` finalizes the calculator, formats the digest as `<type>:<normalized-value>`, logs it, and returns an `XRootDStatus`. `GetRawCheckSum<T>` finalizes and reinterprets the raw digest as `T`, after verifying that `sizeof(T)` matches the calculator's final size. `GetType()` returns the configured checksum type.

`GetCheckSumImpl` is the shared private sanity check. It verifies initialization, asks the calculator for its actual type and output size, and rejects type mismatches.

## Control flow

Users construct a helper, call `Initialize`, feed every data block with `Update`, then call `GetCheckSum` or `GetRawCheckSum`. In `ClassicCopyJob`, local-file and stdio sources/destinations update helpers during streaming; remote checksum requests bypass local helpers and ask the remote server through `Utils::GetRemoteCheckSum`.

## State and persistence behavior

The helper owns one `XrdCksCalc*` and deletes it in the destructor. It keeps only transient checksum state. There is no persistence. Calling finalization methods before `Initialize` returns `errCheckSumError`; calling them after partial updates finalizes whatever bytes were seen.

## Dependencies and integration points

Dependencies include `XrdClXRootDResponses`, `XrdClConstants`, `XrdCksCalc`, `XrdClCheckSumManager`, `XrdClLog`, and `XrdClUtils`. Integration points include `ClassicCopyJob`, `XrdClEcHandler`, `Utils::NormalizeChecksum`, and `DefaultEnv` for logging and checksum manager access.

## Risks and edge cases

`GetCheckSum` allocates a fixed 265-byte buffer and asks `XrdCksData::Get` for 256 bytes; this assumes all supported checksum string encodings fit. `GetRawCheckSum` uses `reinterpret_cast<T*>` on the calculator's final buffer, which can carry alignment and endian assumptions; current ZIP CRC32 use is the intended case.

`Initialize` does not delete an existing calculator before replacing it, so repeated initialization on one helper would leak. The helper is not thread-safe and should be confined to one transfer stream. `GetAddCks` call sites need to avoid adding their own type prefix twice; behavior differs between stdin and regular source helpers in this work item.

## Test signals

No focused helper tests are present. Indirect signals come from `xrdcp` checksum modes, ZIP append CRC metadata, `XrdClEcHandler` page checksum validation, and local checksum behavior in `Utils`. Useful tests would include empty type no-op, missing calculator, type mismatch, raw checksum size mismatch, repeated initialization, and normalized output for each built-in algorithm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumHelper.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.cc

## Purpose

This file implements `XrdCl::CheckSumManager`, the process-level registry and loader for checksum calculators. It pre-registers built-in `md5`, `crc32`, `crc32c`, and `adler32` calculators, dynamically loads other algorithms through `XrdCksLoader`, and can compute a checksum over a local file.

## Important APIs, types, and functions

The constructor creates an `XrdCksLoader` using the client version info and inserts built-in calculator prototypes into `pCalculators`. The destructor deletes all stored prototypes and the loader.

`GetCalculator(const std::string&)` locks `pMutex`, looks up the algorithm prototype, dynamically loads and caches a new prototype if missing, then returns `prototype->New()`. The caller owns the returned calculator.

`Calculate(XrdCksData&, const std::string&, const std::string&)` obtains a calculator, opens a local file with `open(O_RDONLY)`, reads it in 2 MiB blocks, updates the calculator, stores the final digest bytes into `XrdCksData`, and closes/cleans up.

## Control flow

Calculator lookup is lazy for non-built-in algorithms. A missing algorithm triggers loader lookup, logging, cache insertion on success, and a fresh calculator instance return. Local-file calculation is sequential: get calculator, open file, read/update until EOF, set result from final digest, cleanup.

## State and persistence behavior

`pCalculators` stores owned calculator prototypes for the life of the manager. The manager itself is normally a singleton-like object behind `DefaultEnv::GetCheckSumManager`. There is no durable persistence; the cache is process memory only.

## Dependencies and integration points

Dependencies include XRootD checksum classes (`XrdCksCalc`, `XrdCksLoader`, built-in calculator headers), logging/default environment, `XrdSysE2T`, mutex helpers, version macros, and POSIX `open/read/close`. It is used by `CheckSumHelper`, `Utils::GetLocalCheckSum`, and copy/checksum features across the client.

## Risks and edge cases

`Calculate` does not handle `read` returning `-1` after `EINTR` specially; it treats it as a hard error. It allocates the read buffer manually and closes the descriptor on read error and success, but there is no RAII for the fd. If `result.Set` does not copy digest bytes, it would depend on calculator lifetime; the surrounding XrdCks API is expected to copy.

`GetCalculator` logs dynamic loader errors using a fixed 1024-byte buffer. Algorithm names are case-sensitive at this layer; callers such as `CopyProcess::AddJob` lower-case checksum types for copy jobs. Returned calculators must be deleted by callers.

## Test signals

No direct tests are included. Indirect coverage comes from `xrdcp --cksum`, `xrdcp --cksrc`, local checksum utilities, ZIP CRC flows, and any tests around supported checksum type discovery. Good focused tests would verify built-in lookup, dynamic-load failure, local file success, read/open failure, and concurrent `GetCalculator` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.hh

## Purpose

This header declares `CheckSumManager`, the checksum calculator manager used by the XrdCl default environment. It provides calculator factory access and a local-file checksum helper.

## Important APIs, types, and functions

`GetCalculator(const std::string&)` returns a newly allocated `XrdCksCalc` for the requested algorithm or `0` on failure. `Calculate(XrdCksData&, const std::string&, const std::string&)` computes an algorithm-specific checksum over a file path and stores the result in `XrdCksData`.

The private `CalcMap` stores algorithm names to calculator prototypes, `pLoader` points to the plugin loader, and `pMutex` protects the prototype cache. Copy construction and assignment are declared private and not implemented.

## Control flow

Callers usually reach this manager through `DefaultEnv::GetCheckSumManager()`. They request calculators for streaming helpers or ask it to calculate a whole local file checksum. The implementation handles built-ins and dynamic plugin loading.

## State and persistence behavior

The manager stores process-local prototype calculators and a loader. There is no persistence, but the cache persists until `DefaultEnv` cleanup deletes the manager.

## Dependencies and integration points

The header depends on `<map>`, `<string>`, `XrdSysPthread`, and `XrdCksData`. It forward-declares `XrdCksLoader` and `XrdCksCalc`. Integration is with `DefaultEnv`, `CheckSumHelper`, `Utils`, and `ClassicCopyJob`.

## Risks and edge cases

The caller ownership contract for `GetCalculator` is documented but easy to violate. The manager is non-copyable by private declaration, but the header predates modern `= delete`, so diagnostics may be less clear. Algorithm name normalization is not centralized here.

## Test signals

Compile-time users include `DefaultEnv`, `CheckSumHelper`, `Utils`, and `ClassicCopyJob`. Runtime tests should assert calculator ownership, failure handling, and built-in algorithm availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckSumManager.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckpointOperation.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckpointOperation.hh

## Purpose

This header adds pipeline-operation wrappers for XRootD checkpoint commands and checkpointed writes. It lets higher-level code compose `Checkpoint`, `ChkptWrt`, and `ChkptWrtV` operations with the generic `FileOperation` pipeline framework used by XrdCl asynchronous operation chaining.

## Important APIs, types, and functions

`enum ChkPtCode` maps `BEGIN`, `COMMIT`, and `ROLLBACK` to `kXR_ckpBegin`, `kXR_ckpCommit`, and `kXR_ckpRollback`.

`CheckpointImpl<HasHndl>` derives from `FileOperation<CheckpointImpl, HasHndl, Resp<void>, Arg<ChkPtCode>>`. Its `RunImpl` extracts the checkpoint code, clamps the operation timeout to the pipeline timeout when smaller, and calls `file->Checkpoint(code, handler, timeout)`.

`ChkptWrtImpl<HasHndl>` wraps `file->ChkptWrt(offset, len, buffer, handler, timeout)`. `ChkptWrtVImpl<HasHndl>` wraps `file->ChkptWrtV(offset, iov, iovcnt, handler, timeout)` after copying a `std::vector<iovec>` into a stack array. Factory functions `Checkpoint`, `ChkptWrt`, and `ChkptWrtV` build timeout-configured operations from `Ctx<File>` and `Arg<>` values.

## Control flow

Users compose these operations into a pipeline. When the pipeline runs, each `RunImpl` pulls typed arguments from `this->args`, chooses the effective timeout, and dispatches the matching asynchronous private `File` method. Completion is reported through the provided `PipelineHandler`.

`XrdClZipArchive` is a visible consumer: it begins checkpoints, uses checkpointed vector writes for archive metadata/data, and commits checkpoints on close.

## State and persistence behavior

The operation objects hold a shared `Ctx<File>` wrapper and argument values. They do not persist state themselves. Persistence semantics belong to the remote server's checkpoint implementation: begin/commit/rollback and checkpointed writes are sent as file protocol operations.

## Dependencies and integration points

The header depends on `XrdClFileOperations.hh`, which supplies `FileOperation`, `Resp`, `Arg`, `Ctx`, `PipelineHandler`, and timeout mechanics. It integrates with private `File` methods, `FileStateHandler` checkpoint request construction, and ZIP archive update flows.

## Risks and edge cases

`ChkptWrtVImpl` uses `iovec iov[iovcnt]`, a variable-length array that is a compiler extension in C++ rather than standard C++. Empty vectors produce a zero-length VLA and call `ChkptWrtV` with `iovcnt == 0`, which may or may not be accepted by downstream code.

Timeout selection uses `pipelineTimeout < this->timeout ? pipelineTimeout : this->timeout`; if either value uses `0` as "no timeout", this minimum logic can unintentionally force zero. That behavior should match the rest of `FileOperation` conventions.

The buffer arguments are raw pointers. Callers must keep buffers alive until asynchronous completion. `Ctx<File>` can throw `logic_error` if unset, so factories require a valid file context before runtime.

## Test signals

No direct tests are included. Indirect signals come from `XrdClZipArchive` checkpointed archive writes and file-state-handler tests, if present elsewhere. Good tests would cover begin/write/commit ordering, rollback on failure, timeout propagation, vector write argument copying, and empty-vector behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckpointOperation.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.cc

## Purpose

This file implements the non-third-party `ClassicCopyJob`, the core byte-stream copy engine behind `xrdcp` and `CopyProcess` when a normal client-mediated transfer is used. It copies from stdin, local files, remote XRootD files, metalinks, ZIP archive entries, dynamic-size sources, or extreme-copy replica sources into stdout, local/remote files, or ZIP archives. It also handles chunk parallelism, substream scaling, page read/write when available, checksum modes, POSC cleanup, continue mode, transfer rate throttling and threshold failover, extended attributes, ZIP CRC metadata, write recovery, and progress callbacks.

Most implementation types are local to the file. The exported class stays small while the file contains a source/destination abstraction layer and concrete implementations for each transfer shape.

## Important APIs, types, and functions

Local helpers `Source` and `Destination` define the transfer contract. A `Source` can initialize, report size, seek for continue mode, produce `PageInfo` chunks, return checksums/additional checksums, copy xattrs, and optionally try another server. A `Destination` can initialize, accept chunks, flush queued writes, finalize, report checksum and size, set xattrs, and expose write-recovery redirect metadata.

Source implementations include `StdInSource`, `XRootDSource`, `XRootDSourceZip`, `XRootDSourceDynamic`, and `XRootDSourceXCp`. `XRootDSource` performs asynchronous chunked reads, scales outstanding requests by connected data streams, can use `PgRead`, and updates local checksum helpers. `XRootDSourceZip` reads a file inside a ZIP archive and supports `zcrc32`. `XRootDSourceDynamic` reads until short read/EOF instead of trusting a fixed size. `XRootDSourceXCp` uses `XCpCtx` and replica lists for multi-source extreme copy.

Destination implementations include `StdOutDestination`, `XRootDDestination`, and `XRootDZipDestination`. `XRootDDestination` opens a local or remote `File`, queues asynchronous writes or `PgWrite`, handles write-recovery metadata through `WrtRecoveryRedir`, calculates local destination checksums, and optionally creates/removes a `CpTarget` symlink. `XRootDZipDestination` appends a file into a ZIP archive, tracks `zcrc32`, updates archive metadata, and closes the archive.

`ClassicCopyJob::Run(CopyProgressHandler*)` is the exported operation. It reads all job properties, validates incompatible options, constructs the proper source and destination, performs the chunk loop, flushes/finalizes, copies xattrs, validates size, computes/checks checksums, emits monitor checksum events, and stores results.

## Control flow

`Run` begins by loading property-list options such as `checkSumMode`, `checkSumType`, `parallelChunks`, `chunkSize`, `posc`, `force`, `dynamicSource`, `zipArchive`, `xcp`, `preserveXAttr`, `xrate`, `xrateThreshold`, `rmOnBadCksum`, `continue`, `cpTimeout`, `zipAppend`, `addcksums`, and `doServer`. It rejects `force + continue` and `(force|continue) + zipAppend`, enables POSC when remove-on-bad-checksum is requested, and resolves checksum type `auto` via `Utils::InferChecksumType`.

It then constructs the source based on `xcp`, ZIP, stdio, dynamic source, or ordinary XRootD/local source. After source initialization and size discovery, it constructs stdout, ZIP append, or XRootD destination. For regular file destinations it adds an `oss.asize` CGI hint when source size is known, applies flags, and initializes the destination.

The main loop calls `src->GetChunk(pageInfo)`, enforces `CPTimeout`, optionally sleeps to cap `xrate`, optionally triggers `TryOtherServer` when throughput falls below `xrateThreshold`, updates progress counters, sends the chunk to `dest->PutChunk`, and calls progress/cancel hooks. Destination write errors with `errRetry` populate `LastURL` and `WrtRecoveryRedir` so `CopyProcess` can retarget and rerun the job.

After EOF, it flushes outstanding writes, optionally copies extended attributes when both source and target support them, verifies the received byte count against known size, stores `size`, finalizes the destination, and performs checksum work. In `end2end` mode it obtains source and target checksums, lower-cases both strings, emits a monitor event, and fails with `errCheckSumError` on mismatch, optionally removing the target file.

## State and persistence behavior

The copy job stores no durable state outside the destination and result property list. In-flight state includes queued read/write `ChunkHandler` objects, heap-allocated buffers transferred through `PageInfo`, local checksum calculators, file/zip handles, retry metadata, and progress counters. Destination files are the durable side effect.

POSC behavior delegates to XRootD open flags for remote destinations and manually removes local destination files in destination destructors when the copy fails. `rmOnBadCksum` also removes the target after checksum mismatch. Continue mode starts the source at the current destination size and recomputes local checksums from scratch when needed.

## Dependencies and integration points

The file depends on `File`, `FileSystem`, `Monitor`, `Utils`, `CheckSumHelper`, `CheckSumManager`, `RedirectorRegistry`, `ZipArchive`, ZIP operations, `PostMaster`, `JobManager`, `XRootDTransport`, `XCpCtx`, POSIX I/O, semaphores, and the default environment.

It integrates with `CopyProcess` through property lists and retry result keys, with `xrdcp` through CLI-generated properties, with `TPFallBackCopyJob` as the fallback job, with monitor events for copy/checksum telemetry, with `RedirectorRegistry` for metalink metadata, with `DefaultEnv` for tuning variables, and with PostMaster data-stream callbacks for parallel reads.

## Risks and edge cases

Memory ownership is intricate: chunks allocate buffers with `new[]`, transfer them through `PageInfo`, and destinations delete them after write completion. Any early-return path must delete the buffer it owns; many paths do this manually. Asynchronous read/write queues rely on semaphores and cleanup loops, so deadlocks or leaks are possible if callbacks never arrive during shutdown.

The file mixes fixed-size, dynamic, ZIP, stdio, and xcp semantics. Continue mode is unsupported for stdin and xcp, incompatible with force, and requires checksum recomputation for local files. Size validation subtracts destination size in continue mode, so incorrect destination stat values can produce false success or false data errors.

Checksum behavior is broad and inconsistent in details: ZIP remote checksums only support selected modes, `additionalCkeckSum` is misspelled in result keys, additional checksum formatting differs by source type, and `GetRawCheckSum` depends on raw CRC layout. Calling `dest->Finalize()` again after checksum mismatch may double-close some destinations.

`xrateThreshold` failover assumes `TryOtherServer` is meaningful for the source. `XRootDSourceDynamic` and `XRootDSourceXCp` have different support levels. Write recovery depends on destination properties `WrtRecoveryRedir` and `LastURL`; missing or malformed metadata prevents retry. `XRootDZipDestination` notes that PgWriteV for ZIP append is not implemented.

## Test signals

No focused tests are in this work item. Strong integration tests would cover local-to-local, local-to-remote, remote-to-local, stdio, dynamic source, metalink, ZIP read, ZIP append, xcp, POSC cleanup, continue mode, write recovery retry, rate limiting, threshold source switch, xattr preservation, checksum modes including preset/auto/additional, bad checksum removal, cancellation, and cp timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.hh

## Purpose

This header declares `ClassicCopyJob`, the concrete `CopyJob` implementation for client-mediated copies. It is the normal fallback path when third-party copy is disabled or unavailable.

## Important APIs, types, and functions

The constructor accepts a job id, job property list, and job result list and forwards common initialization through `CopyJob`.

`Run(CopyProgressHandler*)` performs the copy and returns an `XRootDStatus`. `GetResult()` exposes the last stored result status.

Private helpers `SourceError` and `DestinationError` append `(source)` or `(destination)` to error messages and store the status as the final result. `SetResult` constructs and stores a final `XRootDStatus` from arbitrary constructor arguments.

## Control flow

`CopyProcess` creates `ClassicCopyJob` during `Prepare` for non-TPC jobs, then `QueuedCopyJob` calls `Run`. The implementation uses `SetResult`/source/destination error helpers for all terminal outcomes so `CopyProcess` can read the status from the result property list.

## State and persistence behavior

The class stores only `XRootDStatus result` in addition to inherited property/result pointers and URLs. Durable state changes happen in the `.cc` implementation by writing destination files or ZIP archives.

## Dependencies and integration points

The header depends on `XrdClCopyProcess.hh` and `XrdClCopyJob.hh`. It integrates with `CopyProcess`, `TPFallBackCopyJob`, `xrdcp`, and monitor/progress handling.

## Risks and edge cases

`SourceError` and `DestinationError` mutate the incoming status error message before storing it, which may surprise callers that reuse the same `XRootDStatus` object after passing it in. The result is separate from `pResults["status"]`; the implementation must keep both consistent at process level.

## Test signals

Tests should verify source/destination error labeling, result propagation, and interaction with `CopyProcess` retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClClassicCopyJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClConstants.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClConstants.hh

## Purpose

This header centralizes XrdCl log mask constants and default environment values. It defines default numeric and string settings used by connection management, copy behavior, TLS behavior, metalink handling, retry policies, checksums, and plugin configuration.

## Important APIs, types, and functions

Log masks include `AppMsg`, `UtilityMsg`, `FileMsg`, `PollerMsg`, `PostMasterMsg`, `XRootDTransportMsg`, `TaskMgrMsg`, `XRootDMsg`, `FileSystemMsg`, `AsyncSockMsg`, `JobMgrMsg`, `PlugInMgrMsg`, `ExDbgMsg`, `TlsMsg`, and `ZipMsg`.

Default integers include connection and stream timeouts, retry counts, copy chunk settings (`DefaultCPChunkSize`, `DefaultCPParallelChunks`, `DefaultCPInitTimeout`, `DefaultCPTPCTimeout`, `DefaultCPTimeout`), xcp block size, TCP keepalive settings, metalink settings, TLS toggles, write recovery retry limit, copy retry count, and page read/write default.

Default strings include poller preference, network stack, monitor settings, plugin paths, recovery toggles, redirector defaults, TLS debug level, client config paths, copy target symlink, and copy retry policy.

`to_lower(std::string)` lower-cases a key. `theDefaultInts` and `theDefaultStrs` map lower-cased environment variable names to default values.

## Control flow

`DefaultEnv` consumes these constants and maps during environment initialization. Command-line tools and copy jobs then query `DefaultEnv::GetEnv()` for mutable runtime values, falling back to these defaults.

## State and persistence behavior

The constants are compile-time defaults. The two `static std::unordered_map` objects are header-defined internal-linkage maps in each translation unit that includes the header. Runtime environment overrides live elsewhere in `Env`; this header does not persist state.

## Dependencies and integration points

Dependencies include `<cstdint>`, `<unordered_map>`, `<string>`, and `<algorithm>`. Integration is broad: `DefaultEnv`, `CopyProcess`, `ClassicCopyJob`, `XrdClCopy.cc`, logging, TLS configuration, PostMaster, and file recovery code all rely on these names and defaults.

## Risks and edge cases

Defining non-const static maps in a header gives each translation unit its own copy. That avoids ODR conflicts because of internal linkage but increases initialization work and can hide divergence if code mutates a local copy. `to_lower` calls `::tolower` on `char` without unsigned conversion, which can be undefined for negative non-ASCII bytes.

New environment defaults must be added both as constants and to the correct map to be discoverable. Some defaults are used directly in code as fallback values, so inconsistent map registration can create split behavior.

## Test signals

Compile-time integration is extensive. Runtime tests should check that `DefaultEnv` registers expected defaults, CLI overrides replace them, and copy-related defaults (`CPChunkSize`, `CPParallelChunks`, `CpRetry`, `CpRetryPolicy`, `CpUsePgWrtRd`) flow into `CopyProcess` and `ClassicCopyJob`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClConstants.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopy.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopy.cc

## Purpose

This file implements the `xrdcp` command-line executable. It parses `XrdCpConfig`, configures the XrdCl environment, builds `CopyProcess` jobs from source/destination arguments and options, displays progress and checksums, runs the prepared copy process, reports errors, and returns shell-compatible status codes.

## Important APIs, types, and functions

`ProgressDisplay` implements `CopyProgressHandler`. It tracks ongoing jobs, prints per-job or summary progress bars to stderr, throttles progress updates to once per second, prints source/target/additional checksums from result property lists, and uses `XrdSysRecMutex` for thread-safe updates.

Helpers include `AllOptionsSupported` for early unsupported SOCKS proxy rejection, `AppendCGI` for adding opaque CGI parameters to URLs, `ProcessCommandLineEnv` for applying `-D` environment definitions, `FileType2String`, `CountSources`, `AdjustFileInfo`, `IndexRemote` for recursive remote directory expansion, and `CleanUpResults`.

`main` is the full CLI driver: parse config, configure logging and delegation, derive booleans, parse checksum options, set environment knobs, normalize destination/source URLs, determine whether the target is a directory, optionally index remote recursive sources, build one property list per source, append a process configuration job, call `Prepare`, call `Run`, print errors, free result lists, and return `XRootDStatus::GetShellCode()` on failure.

## Control flow

After `XrdCpConfig::Config`, unsupported options abort with code 50. CLI `-D` definitions update `DefaultEnv`. Logging level and progress printing are configured, then flags such as force, POSC, TPC, ZIP append, server mode, delegation, recursion, makedir, dynamic source, xattrs, remove-on-bad-checksum, and continue are translated to local variables.

Checksum flags choose `checkSumMode`, `checkSumType`, optional preset, and progress checksum printing. Environment options set substream count, retry policy, TLS behavior, ZIP metalink checksum behavior, chunk size, xcp block size, and parallel chunk count. A scope-exit object stops PostMaster on process exit.

The destination is normalized to a URL string, including absolute `file://` conversion for local paths. Remote target `Stat` decides whether the target is a directory and catches authorization errors. Multiple sources require a directory or stdout target. Remote recursive directory sources are expanded with `DirList(Recursive|Locate|Merge)`.

For each source, the code normalizes local paths to `file://`, appends source and destination CGI, preserves recursive directory layout when needed, fills the property list keys consumed by `CopyProcess`/`ClassicCopyJob`, and calls `process.AddJob`. A final configuration job sets process parallelism, then `Prepare` resolves jobs and `Run` executes them.

## State and persistence behavior

The executable owns transient `PropertyList` result objects and deletes them after execution. Persistent effects are delegated to copy jobs writing targets, creating directories, ZIP appends, and optional target removal on failure. Environment state in `DefaultEnv` is process-local. The scope-exit PostMaster stop is a shutdown side effect.

## Dependencies and integration points

Dependencies include `XrdApps/XrdCpConfig`, `XrdApps/XrdCpFile`, `CopyProcess`, `DefaultEnv`, `Log`, `FileSystem`, `Utils`, `DlgEnv`, optimizers, `XrdSys` helpers, and private utility obfuscation. It is built as the `xrdcp` executable in `XrdCl/CMakeLists.txt`.

It integrates with `CopyProcess` via property names, with `ClassicCopyJob` and TPC jobs through those properties, with `ProgressDisplay` through result keys such as `sourceCheckSum`, `targetCheckSum`, `additionalCkeckSum`, `size`, and `status`, and with `DefaultEnv` for all runtime tuning.

## Risks and edge cases

`AppendCGI` appends `?` and then may append `&` based only on whether any ampersand exists; URLs with an existing `?` but no `&` get `&` inserted, while edge cases around trailing delimiters are fragile. Recursive path handling relies on `XrdCpFile` directory offsets and manual slash manipulation.

The code pushes result objects even if `AddJob` fails, then continues building jobs. Depending on the failure, later `Prepare`/`Run` may not reflect every reported `AddJob` error. Parallel progress output is protected by a mutex but writes to shared stderr from other code can still interleave.

The result key `additionalCkeckSum` is misspelled consistently with `ClassicCopyJob`. Changing it would break CLI output unless both sides migrate. Remote target pre-stat can fail with errors other than not-found/not-authorized and still leave `targetExists=false`, pushing errors later into open time.

## Test signals

No direct tests are included. High-value tests would invoke `xrdcp` for local copies, force/continue validation, checksum print modes, multiple-source directory requirements, remote target stat errors, recursive remote indexing with a fake filesystem, CLI environment overrides, TPC option translation, ZIP append, and progress checksum printing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopy.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyJob.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyJob.hh

## Purpose

This header declares `CopyJob`, the abstract base class for all XrdCl copy job implementations. It standardizes property/result storage, source/target URL extraction, and the virtual `Run` operation used by `CopyProcess`.

## Important APIs, types, and functions

The constructor stores pointers to a job property list and result list, stores the job id, and calls `Init()`. `Init()` reads `"source"` and `"target"` from the property list into `URL pSource` and `URL pTarget`; retry code can call it again after mutating properties.

`Run(CopyProgressHandler*)` is pure virtual. `GetProperties`, `GetResults`, `GetSource`, and `GetTarget` expose job state to orchestration, retry, monitoring, and progress code.

## Control flow

`CopyProcess::Prepare` creates concrete `CopyJob` instances after validating and normalizing properties. `QueuedCopyJob` calls `Run`, inspects the result, and may mutate properties and call `Init` before retrying.

## State and persistence behavior

`CopyJob` does not own the property or result lists; they are owned by `CopyProcess`/caller. It stores source and target URL snapshots that must be refreshed with `Init` after relevant property changes. No durable persistence exists here.

## Dependencies and integration points

The header depends on `XrdClPropertyList.hh`, which supplies `PropertyList`, `URL`, `XRootDStatus`, and `CopyProgressHandler` dependencies through surrounding includes. Concrete implementations include `ClassicCopyJob`, `ThirdPartyCopyJob`, and `TPFallBackCopyJob`.

## Risks and edge cases

The base class assumes `"source"` and `"target"` exist and have types accepted by `PropertyList::Get`; validation happens in `CopyProcess::AddJob`. Non-owning pointers mean caller lifetime must exceed job lifetime. Forgetting to call `Init` after changing source/target properties leaves stale URLs.

## Test signals

Tests should focus on `CopyProcess` creation and retry behavior rather than this base class alone: property validation, URL refresh after write recovery, and result list propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyJob.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.cc -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.cc

## Purpose

This file implements `CopyProcess`, the orchestrator for one or more copy jobs. It validates and defaults job properties, resolves metalinks and target paths, chooses classic versus third-party fallback jobs, runs jobs serially or in parallel, performs retry policy handling, emits monitor/progress events, and cleans up registered redirectors and job objects.

## Important APIs, types, and functions

The local `QueuedCopyJob` adapts a `CopyJob` to `XrdCl::Job`. Its `Run` method reports progress begin/end, emits monitor copy begin/end events, runs the copy job, handles write-recovery retries by retargeting to `WrtRecoveryRedir`, handles generic retry for socket/timeout/threshold errors according to `CpRetry` and `CpRetryPolicy`, stores `"status"` in results, and posts an optional semaphore.

`CopyProcessImpl` stores job property lists, result-list pointers, and allocated `CopyJob*` objects.

`CopyProcess::AddJob` handles configuration jobs, validates required source/target, fills default booleans and settings, lower-cases checksum type, pulls defaults from `DefaultEnv`, logs properties, and stores the caller's result pointer.

`Prepare` validates URLs, registers metalink redirectors, handles `xrdcl.unzip` source CGI, resolves directory targets by appending source or metalink target names, marks TPC intent CGI parameters, and creates either `TPFallBackCopyJob` or `ClassicCopyJob`.

`Run` reads process parallelism from a trailing configuration job. It runs jobs sequentially in-process when `parallel == 1`, or queues `QueuedCopyJob`s into a temporary `JobManager` and waits on a semaphore when parallelism is greater than one.

## Control flow

Callers add one or more regular jobs and optionally a configuration job. `AddJob` only stores normalized properties. `Prepare` turns those properties into live job objects and performs URL/metalink/path normalization. `Run` then executes the jobs and returns the first failure status.

Retry handling is inside `QueuedCopyJob`. `errRetry` from a destination write uses `LastURL` to preserve/extend a `tried` CGI parameter and `WrtRecoveryRedir` to retarget host/port/protocol. Generic retries for socket errors, `errOperationExpired`, and `errThresholdExceeded` either enable continue mode or force overwrite depending on `CpRetryPolicy`.

## State and persistence behavior

The process owns copied `PropertyList` objects and allocated job objects, but not result lists. It persists no durable state. Side effects are job execution and redirector registry references. `CleanUpJobs` releases metalink redirectors and deletes jobs.

## Dependencies and integration points

Dependencies include constants/default environment, logging, `ClassicCopyJob`, `TPFallBackCopyJob`, `FileSystem`, `Monitor`, `Utils`, `JobManager`, `RedirectorRegistry`, and semaphores. Integration points include `xrdcp`, `XrdClFS` copy commands, third-party copy implementations, monitor subscribers, and metalink virtual redirectors.

## Risks and edge cases

The `bools` default array includes `"target"` even though target is not a boolean; this does not affect valid jobs because target was already required, but it is confusing and dangerous if validation changes. Configuration jobs are stored in the same property vector as regular jobs while `pJobResults` only has regular job entries; `Prepare` indexes `pJobResults[i]` after skipping configuration jobs, which is safe only for the expected ordering where configuration is trailing or merged separately. A configuration job inserted before regular jobs could misalign indices.

Parallel execution shares a single `CopyProgressHandler` and monitor across jobs. The CLI progress handler is mutex-protected, but custom handlers must be thread-safe. Retry mutation of property lists is in-place and assumes no other thread reads the same job properties concurrently.

`Prepare` registers metalinks and `CleanUpJobs` releases them, but if `Prepare` fails after registering some redirectors and before jobs are created for them, release coverage depends on whether corresponding jobs were pushed. Target directory inference and path appending are string-heavy and sensitive to trailing slashes and metalink target names.

## Test signals

Useful tests would cover defaults insertion, checksum type lower-casing, missing source/target, configuration job merging and ordering, target directory path resolution for regular/metalink/ZIP sources, metalink registration/release on success and failure, TPC marking, write-recovery retry URL rewriting, generic retry policy `force` versus `continue`, serial first-error return, and parallel job result aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.hh

## Purpose

This header declares the public copy-process API used by `xrdcp`, `XrdClFS`, and library callers to schedule and run file-copy jobs. It also declares `CopyProgressHandler`, the progress/cancellation callback interface shared by copy implementations.

## Important APIs, types, and functions

`CopyProgressHandler` has virtual hooks `BeginJob`, `EndJob`, `JobProgress`, and `ShouldCancel`, all with default no-op behavior except `ShouldCancel`, which defaults to false.

`CopyProcess` exposes `AddJob(const PropertyList&, PropertyList*)`, `Prepare()`, and `Run(CopyProgressHandler*)`. `AddJob` accepts the property contract documented in the header: source, target, force, POSC, coerce, makedir, third-party mode, checksum settings, chunk settings, init/TPC/copy timeouts, dynamic source, configuration jobs, and result keys.

`MarkTPC(PropertyList&)` is a private helper that adds `xrdcl.intent=tpc` CGI to source and target URLs before TPC job creation.

## Control flow

Callers create a process, add jobs, add an optional configuration job, call `Prepare`, then call `Run`. Progress hooks are invoked around and during each job, and cancellation is checked during chunk transfer by concrete jobs.

## State and persistence behavior

`CopyProcess` hides its mutable state behind `CopyProcessImpl* pImpl`, keeping ABI exposure small. It does not persist state itself; jobs write destinations and fill caller-provided result property lists.

## Dependencies and integration points

The header depends on `URL`, `XRootDResponses`, `PropertyList`, `<cstdint>`, and `<vector>`. It is the main public integration point for XrdCl copy functionality, bridging CLI commands, filesystem commands, `ClassicCopyJob`, TPC fallback, and progress UI.

## Risks and edge cases

The property contract is stringly typed. Typos or mismatched types are mostly caught at runtime, and result keys must match exact spellings used by implementations. Callback implementations used with parallel jobs must be thread-safe. Because `Prepare` and `Run` are separate, callers must not mutate job properties unexpectedly between them unless they understand the lifecycle.

## Test signals

Tests should exercise the public contract through `AddJob`/`Prepare`/`Run`, including property defaults, cancellation, progress callback order, result keys, serial and parallel execution, and TPC intent marking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.hh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCtx.hh -->
# sources/distributed-fs/xrootd/src/XrdCl/XrdClCtx.hh

## Purpose

`XrdCl::Ctx<T>` is a small shared operation-context wrapper. It stores a shared pointer to a raw `T*`, allowing copied pipeline operation objects to share and later update the same underlying context pointer while exposing pointer-like dereference operators.

## Important APIs, types, and functions

Constructors create an empty shared pointer-to-pointer, initialize from `T*`, initialize from `T&`, copy, or move. Assignment from `T*` or `T&` updates the shared stored pointer rather than replacing the shared holder.

`operator*` returns `T&` and `operator->` returns `T*`. Both throw `std::logic_error("XrdCl::Ctx contains no value!")` when the stored pointer is null.

## Control flow

Pipeline APIs accept `Ctx<File>` and similar values by copy/move. Because copies share the same `T**` holder, one stage can update the context pointer and other copies observe the new target. Operation wrappers such as `Checkpoint`, `ChkptWrt`, and other file operations dereference `Ctx<File>` when running.

## State and persistence behavior

The only state is process-local pointer indirection stored in `std::shared_ptr<T*>`. The wrapper does not own the `T` object; it owns only the pointer slot. There is no persistence.

## Dependencies and integration points

Dependencies are `<memory>` and `<stdexcept>`. Integration is with `XrdClFileOperations` and all operation-builder headers that accept `Ctx<File>` or other operation contexts.

## Risks and edge cases

The type name can suggest ownership, but it does not own the context object. Dangling pointers are possible if the referenced object dies while operations still hold `Ctx` copies. The shared pointer-to-pointer design means assignment through one copy mutates all copies, which is intentional but surprising.

Dereferencing an empty context throws at runtime. There is no const-propagation of the pointed object beyond constness of the wrapper. Thread-safety is limited to `shared_ptr` control-block mechanics; concurrent assignment/dereference of the raw pointer slot is not synchronized.

## Test signals

Useful tests would cover empty dereference exceptions, copy-shared assignment behavior, move construction, reference and pointer construction, and operation wrappers observing updated contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdCl/XrdClCtx.hh -->
