# Research: subset-b-000491

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadRequestContext.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadRequestContext.java

## Purpose
`BlockReadRequestContext` is the per-stream state carrier for worker-side block reads. It wraps the incoming protobuf read request as an `alluxio.wire.BlockReadRequest` and tracks data-reader progress, client acknowledgements, terminal notifications, metrics, and the active `BlockReader`.

## Important APIs, Types, and Functions
The public surface is intentionally simple: getters and setters for `mDataReaderActive`, `mPosToQueue`, `mPosReceived`, `mEof`, `mCancel`, `mError`, `mDone`, `mCounter`, `mMeter`, and `mBlockReader`. Most mutable fields are annotated `@GuardedBy("BlockReadHandler#mLock")`, so callers are expected to coordinate through `BlockReadHandler`.

## Control Flow, State, and Persistence
The context starts with position zero, inactive reader, no EOF/cancel/error, and `done=false`. `mError` takes precedence over cancel and EOF, EOF takes precedence over cancel, and `mDone` is a sanity marker after SUCCESS or CANCEL response emission. There is no durable persistence here; persistence and IO are delegated to the `BlockReader` and the block store.

## Dependencies and Integration Points
It integrates `BlockReadHandler`, `BlockReader`, `Error`, Codahale counters/meters, and the wire `BlockReadRequest`. It is used by the gRPC data path to coordinate gRPC event threads and worker data-reader threads.

## Risks and Test Signals
The main risks are race-sensitive state transitions and accidentally reading or writing guarded fields outside `BlockReadHandler#mLock`. The precedence rules for error/cancel/EOF are documented but not enforced by this class. Test signals should focus on duplicate terminal responses, late cancel after success, error overriding EOF/cancel, metrics increments, and block-reader cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadRequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWorkerClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWorkerClientServiceHandler.java

## Purpose
`BlockWorkerClientServiceHandler` is the server implementation of the gRPC `BlockWorker` client-facing API. It connects network read/write streams, short-circuit local open/create streams, cache/load commands, block movement/removal, metrics clearing, and checksum RPCs to `DefaultBlockWorker`.

## Important APIs, Types, and Functions
The constructor extracts `DefaultBlockWorker` and `UfsManager` from `WorkerProcess`. `getOverriddenMethodDescriptors()` swaps in zero-copy data marshallers when `WORKER_NETWORK_ZEROCOPY_ENABLED` is set. `readBlock()` builds `BlockReadHandler` and attaches `onReady`; `writeBlock()` wraps the response observer for data-message marshalling and delegates request type selection to `DelegationWriteHandler`. `openLocalBlock()` and `createLocalBlock()` return short-circuit handlers. Unary methods call `mBlockWorker.asyncCache`, `cache`, `load`, `removeBlock`, `moveBlock`, `freeWorker`, `clearMetrics`, and `calculateBlockChecksum` through `RpcUtils`.

## Control Flow, State, and Persistence
The handler itself stores only worker references, marshallers, and the domain-socket flag. Read/write state lives in stream handlers. Unary calls mutate worker/block-store state indirectly: block removal, movement, cache population, loading, metrics reset, and checksum calculation all flow through `DefaultBlockWorker`.

## Dependencies and Integration Points
It bridges generated gRPC classes, `GrpcExecutors`, `DataMessageServerStreamObserver`, `DataMessageServerRequestObserver`, `ShortCircuitBlockReadHandler`, `ShortCircuitBlockWriteHandler`, `DelegationWriteHandler`, authenticated user context, `UfsManager`, and block-store allocation options.

## Risks and Test Signals
Risks include unchecked casts to `CallStreamObserver`/`ServerCallStreamObserver`, zero-copy marshaller consistency, authentication failures surfaced as `UNAUTHENTICATED`, and handler selection depending on the first write message. Test signals should cover zero-copy descriptor override, stream cancellation propagation, user impersonation, load partial-failure status mapping, and block move/remove session creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWorkerClientServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteHandler.java

## Purpose
`BlockWriteHandler` implements the standard Alluxio-block write path over gRPC. It creates a temporary block, reserves space as bytes arrive, appends buffers through a `BlockWriter`, and commits or aborts the block on stream completion or cancellation.

## Important APIs, Types, and Functions
`createRequestContext()` reads optional `spaceToReserve`, creates a `BlockWriteRequestContext`, calls `BlockWorker.createBlock`, chooses domain or remote write metrics, and increments the active write counter. `writeBuf()` expands reserved space with `requestSpace`, lazily creates the block writer, and appends the `DataBuffer`. `completeRequest()` closes the writer and calls `commitBlock`; `cancelRequest()` closes the writer and calls `abortBlock`; `cleanupRequest()` closes and calls `cleanupSession`.

## Control Flow, State, and Persistence
State flows through `BlockWriteRequestContext`: reserved bytes, current position, writer, and metrics. Successful completion persists the temp block as a committed Alluxio block via the worker. Cancellation or cleanup removes temporary state from the worker session.

## Dependencies and Integration Points
The class depends on `AbstractWriteHandler`, `BlockWorker`, `BlockWriter`, `CreateBlockOptions`, `DataBuffer`, worker write metrics, and the gRPC `WriteResponse` stream.

## Risks and Test Signals
Risks include active write counter imbalance on exceptions, reservation underestimation, append-size mismatches, and cleanup after partially created writers. Test signals should include normal commit, client cancel, error cleanup, dynamic `requestSpace`, domain-vs-remote metrics, and writer close idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequest.java

## Purpose
`BlockWriteRequest` is the immutable internal representation of a block-oriented gRPC write command. It extends common `WriteRequest` state with tier, medium type, and optional UFS-block creation options.

## Important APIs, Types, and Functions
The constructor reads `tier`, `mediumType`, and `createUfsBlockOptions` from `request.getCommand()`. Accessors expose `getTier()`, `getMediumType()`, `getCreateUfsBlockOptions()`, and `hasCreateUfsBlockOptions()`. `toStringHelper()` adds tier and UFS options to the base request description.

## Control Flow, State, and Persistence
The object is immutable after construction and does not perform IO. Its `CreateUfsBlockOptions` field controls whether `UfsFallbackBlockWriteHandler` can write a block to under storage instead of local block storage.

## Dependencies and Integration Points
It depends on protobuf `Protocol.CreateUfsBlockOptions` and the gRPC write command schema. It is consumed by `BlockWriteRequestContext`, `BlockWriteHandler`, and `UfsFallbackBlockWriteHandler`.

## Risks and Test Signals
Risks are mostly validation gaps: the constructor trusts the command type and command fields. Tests should cover presence/absence of UFS options, medium/tier propagation, and handler behavior when fields are missing or inconsistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequestContext.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequestContext.java

## Purpose
`BlockWriteRequestContext` extends the generic write context with block-write-specific resources: the local `BlockWriter`, reserved-space accounting, local-vs-UFS fallback mode, UFS resource/output stream, and UFS path.

## Important APIs, Types, and Functions
The constructor wraps a gRPC `WriteRequest` as `BlockWriteRequest` and records initial bytes reserved. Accessors/mutators manage `BlockWriter`, `mBytesReserved`, `mIsWritingToLocal`, `mUfsResource`, `mOutputStream`, and `mUfsPath`.

## Control Flow, State, and Persistence
For normal local writes, `mBlockWriter` and `mBytesReserved` drive append and reservation state. For fallback writes, `mIsWritingToLocal` flips false and UFS fields hold the open under-storage resource and target output stream. The class itself persists nothing; handlers close, commit, abort, or delete resources.

## Dependencies and Integration Points
It is shared by `BlockWriteHandler` and `UfsFallbackBlockWriteHandler`, and relies on `WriteRequestContext`, `BlockWriter`, `CloseableResource<UnderFileSystem>`, and `OutputStream`.

## Risks and Test Signals
The context is `@NotThreadSafe`, so the owning `AbstractWriteHandler` lock must protect cross-thread state. Fallback mode transitions are subtle because local writer cleanup and UFS output creation can both be active during a switch. Tests should cover fallback after partial local write, fallback from short-circuit with bytes already in block store, cancel cleanup, and resource-close ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockWriteRequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DataMessageServerRequestObserver.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DataMessageServerRequestObserver.java

## Purpose
`DataMessageServerRequestObserver` is a response-side wrapper that also exposes data-message marshaller metadata for zero-copy request handling. It delegates normal stream events to the underlying response observer.

## Important APIs, Types, and Functions
The constructor passes request and response marshallers to `DataMessageMarshallerProvider` and stores the original observer. `onNext`, `onError`, and `onCompleted` simply delegate.

## Control Flow, State, and Persistence
No persistent or business state is stored beyond observer and marshaller references. The class enables downstream handlers, especially `DelegationWriteHandler`, to discover a request marshaller and poll raw buffers associated with protobuf messages.

## Dependencies and Integration Points
It integrates gRPC `StreamObserver`, `DataMessageMarshaller`, `DataMessageMarshallerProvider`, and the zero-copy write path in `BlockWorkerClientServiceHandler`.

## Risks and Test Signals
Risks are small but include type-parameter confusion and response lifecycle errors being hidden behind delegation. Tests should verify marshaller discovery, buffer polling by write handlers, and pass-through behavior for completion and errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DataMessageServerRequestObserver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DataMessageServerStreamObserver.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DataMessageServerStreamObserver.java

## Purpose
`DataMessageServerStreamObserver` adapts a `CallStreamObserver<T>` to accept `DataMessage<T, DataBuffer>` for zero-copy read responses. It stores buffers in a repository keyed by the response message before forwarding the message to gRPC.

## Important APIs, Types, and Functions
`onNext(DataMessage<T, DataBuffer>)` offers a non-null buffer to the repository, forwards the protobuf message, and polls the buffer back if forwarding throws. The standard `CallStreamObserver` methods delegate to the wrapped observer: readiness, ready handler, flow control, request count, and compression.

## Control Flow, State, and Persistence
The only durable state is the association between response messages and `DataBuffer`s inside the supplied `BufferRepository`. The wrapper avoids losing a buffer when gRPC rejects a message by polling it in the catch path.

## Dependencies and Integration Points
It depends on `BufferRepository`, `DataMessage`, `DataBuffer`, and gRPC `CallStreamObserver`. It is installed by `BlockWorkerClientServiceHandler.readBlock()` when zero-copy networking is enabled.

## Risks and Test Signals
Risks include leaked buffers if downstream lifecycle does not poll/release, message-key identity mismatches, and failure behavior during `onNext`. Test signals should cover non-null and null buffer forwarding, exception rollback, readiness delegation, and flow-control delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DataMessageServerStreamObserver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DelegationWriteHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DelegationWriteHandler.java

## Purpose
`DelegationWriteHandler` is the first receiver for a gRPC write stream. It inspects the first write command and delegates the rest of the stream to the correct concrete handler: Alluxio block, UFS file, or UFS fallback block.

## Important APIs, Types, and Functions
`createWriterHandler()` switches on `request.getCommand().getType()` and constructs `BlockWriteHandler`, `UfsFileWriteHandler`, or `UfsFallbackBlockWriteHandler`. `onNext()` lazily creates the handler and either passes a raw polled buffer from the marshaller or the protobuf request. `onError`, `onCompleted`, and `onCancel` forward to the concrete handler if one exists.

## Control Flow, State, and Persistence
The delegate is fixed by the first message in the stream. This class does not persist write data; persistence is handled by the selected handler. It keeps user info and the domain-socket flag so the concrete handler can set metrics and access controls.

## Dependencies and Integration Points
It integrates `DataMessageMarshallerProvider`, `WriteRequestMarshaller`, `DefaultBlockWorker`, `UfsManager`, authenticated user info, and all write handler variants.

## Risks and Test Signals
Risks include invalid command type, inconsistent later stream messages, no-op completion/cancel before a first message, and raw-buffer lifecycle errors. Tests should verify handler selection for all command types, zero-copy buffer handoff, invalid command rejection, and cancellation propagation before and after first data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/DelegationWriteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/Error.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/Error.java

## Purpose
`Error` is a small wrapper for communicating an `AlluxioStatusException` and a client-notification decision between gRPC event threads and worker data threads.

## Important APIs, Types, and Functions
The constructor stores the cause and `notifyClient` flag. `getCause()`, `isNotifyClient()`, and `toString()` are the only methods.

## Control Flow, State, and Persistence
The object is immutable and has no persistence behavior. It is used as terminal request state in read/write contexts where an internal error may or may not need to be sent back to the client.

## Dependencies and Integration Points
It depends on `AlluxioStatusException` and is referenced by `BlockReadRequestContext` and `WriteRequestContext`.

## Risks and Test Signals
The primary risk is semantic: callers must consistently honor `notifyClient`. Tests should verify that notify and non-notify errors produce the intended stream termination behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/Error.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcDataServer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcDataServer.java

## Purpose
`GrpcDataServer` starts and owns the worker data gRPC server for block operations. It configures Netty transport, RPC executor, service method overrides, flow control, keepalive, message size, and graceful shutdown.

## Important APIs, Types, and Functions
The constructor builds `BlockWorkerClientServiceHandler`, applies zero-copy descriptor overrides, starts a `GrpcServer`, and records domain-socket bind addresses. `createServerBuilder()` creates the worker RPC executor, registers queue/thread gauges, creates boss/worker event loop groups, chooses channel class, configures epoll mode, pooled allocator, and Netty watermarks. `close()` shuts down the filesystem context, server, event loops, and RPC executor. `getBindAddress()`, `isClosed()`, and `awaitTermination()` implement `DataServer`.

## Control Flow, State, and Persistence
Server state is process-local: socket address, event loop groups, gRPC server, optional domain socket address, and RPC executor. It does not store blocks, but all block IO reaches `DefaultBlockWorker` through the registered service.

## Dependencies and Integration Points
It integrates worker process services, `GrpcServerBuilder`, `GrpcSerializationUtils`, `BlockWorkerClientServiceHandler`, `ExecutorServiceBuilder`, Netty event loops/channels/options, metrics, `FileSystemContext`, and Alluxio network configuration.

## Risks and Test Signals
Risks include startup failures becoming runtime exceptions, shutdown ordering, event-loop shutdown timeouts, domain-socket address reporting, integer casts for configured byte sizes, and executor leak on partial construction failure. Tests should cover TCP and domain-socket startup, zero-copy service registration, close idempotence, bind-port reporting, and metric gauge registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcDataServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcExecutors.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcExecutors.java

## Purpose
`GrpcExecutors` defines shared executor pools for worker gRPC cache, read, serialized read-response, and write work. It also wraps each executor so authenticated client user context is transferred to worker threads.

## Important APIs, Types, and Functions
Static executors include `CACHE_MANAGER_EXECUTOR`, `BLOCK_READER_EXECUTOR`, `BLOCK_READER_SERIALIZED_RUNNER_EXECUTOR`, and `BLOCK_WRITER_EXECUTOR`. Pool sizes, queue types, and thread names come from worker network configuration. The static initializer registers executor metrics. `ImpersonateThreadPoolExecutor` overrides `execute` and `submit` variants to capture `AuthenticatedClientUser`, set it inside the worker thread, optionally increment `WORKER_ACTIVE_OPERATIONS`, and clean up thread-local state.

## Control Flow, State, and Persistence
This is process-global executor state. Cache manager work uses a bounded `UniqueBlockingQueue`; block reader and writer pools use `SynchronousQueue`; serialized read response has a small queue and caller-runs fallback. There is no durable persistence, but the pools gate all high-volume network IO concurrency.

## Dependencies and Integration Points
It integrates configuration properties, `MetricsSystem`, `ThreadFactoryUtils`, `AuthenticatedClientUser`, `DefaultBlockWorker.Metrics`, and gRPC read/write/cache handlers.

## Risks and Test Signals
Risks include rejected tasks under saturated synchronous pools, active-operation counter imbalance if unsupported executor APIs are used, static initialization using stale configuration, and thread-local impersonation leaks. Tests should verify user propagation, metric counters around success/failure, shutdown behavior, queue saturation, and unsupported `invokeAll`/`invokeAny` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcExecutors.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockReadHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockReadHandler.java

## Purpose
`ShortCircuitBlockReadHandler` handles local-client open/close streams for direct filesystem reads of worker-local block files. It pins the block, optionally promotes it, returns its path, and unpins on stream completion or error.

## Important APIs, Types, and Functions
`onNext()` validates a single open request, creates a session ID, retrieves volatile block metadata, validates integrity, optionally moves the block to top tier, pins the block, records access, increments active clients, and returns `OpenLocalBlockResponse.path`. `onCompleted()` unpins and decrements active clients. `onError()` logs, unpins, cleans the session, and reports a gRPC error.

## Control Flow, State, and Persistence
State includes one request, optional `BlockLock`, and a generated session ID. Pinning prevents eviction while the client reads the returned path. Optional promotion mutates block placement through the `BlockStore`.

## Dependencies and Integration Points
It depends on `BlockStore`, `TieredBlockStore.validateBlockIntegrityForRead`, `BlockLock`, `AllocateOptions`, `BlockStoreLocation`, `DefaultBlockWorker.Metrics`, `RpcUtils`, and gRPC `OpenLocalBlock*` messages.

## Risks and Test Signals
Risks include stale metadata after promotion, lock leaks on unusual errors, `getVolatileBlockMeta()` returning empty in alternative block stores, and active-client counter imbalance. Tests should cover missing block, corrupt block, promote/no-promote, duplicate open requests, client error, normal close, and cleanup-session behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockReadHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandler.java

## Purpose
`ShortCircuitBlockWriteHandler` handles local-client create/reserve/commit/abort streams for writing directly to worker-local temp block files. It returns a local path for the client to write and commits or aborts when the stream ends.

## Important APIs, Types, and Functions
`onNext()` handles either `onlyReserveSpace` requests by calling `requestSpace`, or initial create requests by creating a session and calling `createBlock`. `onCompleted()` commits, `onCancel()` aborts, and `onError()` cleans up unless cancellation was already handled. `handleBlockCompleteRequest()` forks gRPC context before invoking `commitBlock` or `abortBlock`.

## Control Flow, State, and Persistence
State is one create request and a generated session ID. Successful create persists a temporary block; successful completion commits it; cancellation or errors clean up/abort. A `ResourceExhaustedRuntimeException` can be propagated without cleanup when the client requested `cleanupOnFailure=false`, supporting UFS fallback writers.

## Dependencies and Integration Points
It depends on `BlockWorker`, `CreateBlockOptions`, `RpcUtils`, `GrpcExceptionUtils`, gRPC context/cancellation APIs, and create-local-block protobuf messages.

## Risks and Test Signals
Risks include reserve requests before create, session cleanup after resource exhaustion, double completion/cancel, and context cancellation interfering with commit. Tests should cover initial create, incremental reserve, commit, cancel, resource-exhausted fallback behavior, network error cleanup, and duplicate create rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandler.java

## Purpose
`UfsFallbackBlockWriteHandler` writes a block to local worker storage when possible and falls back to writing the block into UFS when local space is exhausted or when the request is already a fallback from short-circuit write.

## Important APIs, Types, and Functions
`createRequestContext()` requires `CreateUfsBlockOptions`, initializes metrics, and optionally creates a local temp block. `writeBuf()` first delegates to `BlockWriteHandler`; on `ResourceExhaustedRuntimeException`, it flips to UFS mode, closes the local writer, creates the UFS block, transfers existing temp bytes with `Files.copy`, cancels local temp state, and writes remaining bytes to the UFS stream. `handleCommand()` supports fallback initialization with existing `bytesInBlockStore`. `completeRequest()` either commits local block or calls `commitBlockInUfs`. `cancelRequest()` aborts local or deletes the UFS file.

## Control Flow, State, and Persistence
The handler can transition mid-stream from local temporary block persistence to under-storage file persistence. In UFS mode it creates an atomic, parent-creating UFS output stream and records UFS-tagged metrics. Completion persists either an Alluxio local block or a UFS block-master record.

## Dependencies and Integration Points
It composes `BlockWriteHandler`, `DefaultBlockWorker`, `UfsManager`, `UnderFileSystem`, `BlockUtils.getUfsBlockPath`, `CreateOptions`, worker metrics, and protobuf `CreateUfsBlockOptions`.

## Risks and Test Signals
This is high-risk code because it mixes two persistence modes. Risks include partial transfer mismatch, output-stream/resource leaks, duplicate UFS creation, deleting the wrong UFS path on cancel, and position accounting when `bytesInBlockStore` is supplied. Tests should cover local success, local-to-UFS transition, short-circuit fallback initialization, cancel in both modes, flush in both modes, metrics switch, and transfer failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteHandler.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteHandler.java

## Purpose
`UfsFileWriteHandler` handles full-file writes directly to an under file system. It exists because UFS file semantics require all file bytes to be written through one stream rather than independent block-level writers.

## Important APIs, Types, and Functions
`createRequestContext()` creates `UfsFileWriteRequestContext`. `writeBuf()` lazily creates the UFS file and writes bytes from `DataBuffer`. `flushRequest()` flushes the open stream. `completeRequest()` creates an empty file if needed, closes the stream, captures optional content hash, sets owner/group, and closes the UFS resource. `cancelRequest()` closes the stream and deletes the UFS file. `createUfsFile()` builds `CreateOptions` from proto owner, group, mode, and optional ACL, then creates a non-existing file.

## Control Flow, State, and Persistence
The target UFS file is created lazily on first data, flush, or completion. Successful completion persists the UFS file and metadata updates; cancellation deletes it. Content hash is stored in request context when the output stream supports `ContentHashable`.

## Dependencies and Integration Points
It integrates `AbstractWriteHandler`, `UfsManager`, `UnderFileSystem`, `CreateOptions`, `Mode`, ACL proto conversion, UFS write metrics, `ContentHashable`, and `UnderFileSystemFileOutStream` clients.

## Risks and Test Signals
Risks include losing ownership update failures because they are warnings, deleting after close on cancel, unsupported ACL behavior outside HDFS, and ensuring empty-file completion still creates a file. Tests should cover write/flush/complete, empty file create, cancel deletion, ACL and mode propagation, content hash capture, and UFS resource closure on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequest.java

## Purpose
`UfsFileWriteRequest` is the immutable internal representation of a gRPC write command targeting a full UFS file.

## Important APIs, Types, and Functions
The constructor extracts `ufsPath` and `CreateUfsFileOptions` from `request.getCommand().getCreateUfsFileOptions()`. Accessors expose `getUfsPath()` and `getCreateUfsFileOptions()`, and `toStringHelper()` adds UFS file details.

## Control Flow, State, and Persistence
The class is a value wrapper and performs no IO. Its fields direct `UfsFileWriteHandler` to the UFS mount, path, ownership, mode, and ACL for file creation.

## Dependencies and Integration Points
It depends on protobuf `Protocol.CreateUfsFileOptions` and extends base `WriteRequest`. It is held by `UfsFileWriteRequestContext`.

## Risks and Test Signals
The constructor assumes the command has create-UFS-file options; invalid command routing can fail with a proto default or null-like semantics. Tests should validate command type routing and option/path propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequestContext.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequestContext.java

## Purpose
`UfsFileWriteRequestContext` stores per-stream resources for UFS file writes: the acquired UFS resource, the create options used for the file, and the active output stream.

## Important APIs, Types, and Functions
The constructor wraps the gRPC request as `UfsFileWriteRequest`. Getters and setters manage `CloseableResource<UnderFileSystem>`, `CreateOptions`, and `OutputStream`.

## Control Flow, State, and Persistence
The context starts without UFS resources. `UfsFileWriteHandler` populates it lazily during file creation, then clears output stream and create options on complete or cancel. Persistence is controlled by the output stream and UFS APIs.

## Dependencies and Integration Points
It extends `WriteRequestContext<UfsFileWriteRequest>` and is consumed only by `UfsFileWriteHandler`.

## Risks and Test Signals
The context is not thread-safe by itself, and resource fields must be closed exactly once. Tests should cover completion, cancel, exception cleanup, and null-safe behavior when creation never happened.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/UfsFileWriteRequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequest.java

## Purpose
`WriteRequest` is the base immutable internal representation of a gRPC write command. It captures common fields used by all write variants: target ID, pin-on-create flag, and a generated worker session ID.

## Important APIs, Types, and Functions
The constructor reads `command.id` and `command.pinOnCreate`, then creates a fresh session ID with `IdUtils.createSessionId()`. Accessors expose `getId()`, `getPinOnCreate()`, and `getSessionId()`. `toString()` delegates to a subclass-extensible `toStringHelper()`.

## Control Flow, State, and Persistence
The generated session ID scopes temporary worker resources such as temp blocks. The object performs no persistence itself but is passed into handlers that create, commit, abort, or clean up resources.

## Dependencies and Integration Points
It integrates with gRPC write command schema, `IdUtils`, and subclasses `BlockWriteRequest` and `UfsFileWriteRequest`.

## Risks and Test Signals
Risks include one session ID per request object, which makes first-message construction timing important, and lack of base validation for command type or required fields. Tests should check session uniqueness and pin/id propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequestContext.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequestContext.java

## Purpose
`WriteRequestContext` is the generic shared state for gRPC write streams. It stores the immutable request object, current write position, optional terminal error, optional content hash, metrics, and a done marker.

## Important APIs, Types, and Functions
Generic `T extends WriteRequest` allows block and UFS file contexts to share base state. `getError`, `getPos`, `setError`, and `setPos` are guarded by `AbstractWriteHandler#mLock`. `getContentHash()` returns an `Optional`, and metrics setters install per-request counters/meters.

## Control Flow, State, and Persistence
The position starts at zero and is updated as buffers are accepted for writing. `mDone` marks EOF or cancel reception for sanity and cleanup logic. The class itself persists nothing, but the position and error state govern handler completion.

## Dependencies and Integration Points
It is used by `AbstractWriteHandler` subclasses, `Error`, Codahale metrics, and concrete write request wrappers.

## Risks and Test Signals
Risks include unsynchronized access to guarded fields, content hash only being available for some UFS output streams, and cleanup behavior depending on `isDoneUnsafe()`. Tests should cover concurrent error vs completion, position accounting, metrics increments, and content hash propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/WriteRequestContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/package-info.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/package-info.java

## Purpose
`package-info.java` documents the worker package role: worker process startup, remote worker utilities, data server responsibilities, and protocol-level block operations.

## Important APIs, Types, and Functions
There are no executable APIs. The documentation points to `AlluxioWorker#main`, `WorkerProcess`, `DataServer`, `GrpcDataServer`, `BlockWorker`, and `alluxio.proto.dataserver.Protocol`.

## Control Flow, State, and Persistence
The file documents that start scripts launch `AlluxioWorker`, `WorkerProcess` starts RPC/data services, and data server methods read/write blocks from worker storage, local filesystem short-circuit paths, and UFS.

## Dependencies and Integration Points
It frames the relationship among worker process lifecycle, gRPC data services, generated protobuf protocol, and block worker implementations.

## Risks and Test Signals
The risk is documentation drift as data-server behavior evolves, especially with paged block store and zero-copy paths. Test signals come from actual worker/data-server integration tests rather than this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageEvictor.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageEvictor.java

## Purpose
`BlockPageEvictor` wraps a page-cache `CacheEvictor` and filters out pages belonging to pinned blocks. It protects blocks that are being written, committed, read, or otherwise temporarily ineligible for eviction.

## Important APIs, Types, and Functions
`evict()` delegates to `evictMatching(mIsNotPinned)`. `evictMatching()` combines caller criteria with the not-pinned predicate. `addPinnedBlock()` and `removePinnedBlock()` update the pinned set. Normal cache access notifications pass through to the delegate.

## Control Flow, State, and Persistence
State is an in-memory `Set<String>` of pinned block identifiers. Reset clears both delegate state and pinned state. There is no durable persistence.

## Dependencies and Integration Points
It integrates `CacheEvictor`, `PageId`, and paged block store directories. `PagedBlockStoreDir` uses it for temp block pinning and commit/read protection.

## Risks and Test Signals
A notable risk is that the pinned set stores `String.valueOf(blockId)`, while block page file IDs are encoded strings like `paged_block_...`; callers must pin using values that match `pageId.getFileId()` or filtering will not work. Tests should verify pinning against actual `BlockPageId` file IDs, eviction matching, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageEvictor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageId.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageId.java

## Purpose
`BlockPageId` specializes cache `PageId` for pages that belong to Alluxio blocks. It encodes block ID and block size into the page file ID so page stores without page metadata can recover block metadata.

## Important APIs, Types, and Functions
`fileIdOf()` formats `paged_block_%016x_size_%016x`; `tempFileIdOf()` uses size `-1` as a temp placeholder. `parseBlockId()` and `parseBlockSize()` recover metadata from file IDs. `newTempPage()` creates temp pages. `downcast()` converts a generic `PageId` into a `BlockPageId`. Equality ignores block size for two `BlockPageId`s and compares block ID plus page index.

## Control Flow, State, and Persistence
The encoded file ID is persisted as the page-store file identity. On commit, temp file IDs are rewritten to final file IDs carrying real block size. The object caches parsed `blockId` and `blockSize` in final fields.

## Dependencies and Integration Points
It depends on `PageId`, regex parsing, and `Preconditions`. It is central to `PagedBlockWriter`, `PagedBlockReader`, `PagedBlockStoreDir`, and `PagedBlockMetaStore`.

## Risks and Test Signals
Risks include equality/hash-code compatibility with ignored block size, parsing unsigned negative block IDs, rejecting negative parsed block sizes, and string interning. Tests should cover temp IDs, final IDs, negative/large block IDs, invalid file IDs, downcast from plain `PageId`, and equality/hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/BlockPageId.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/NettyBufTargetBuffer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/NettyBufTargetBuffer.java

## Purpose
`NettyBufTargetBuffer` adapts a Netty `ByteBuf` to the page-store `PageReadTargetBuffer` interface, enabling page reads directly into gRPC/Netty buffers.

## Important APIs, Types, and Functions
`byteChannel()` returns a writable channel that writes source `ByteBuffer` bytes into the target `ByteBuf`. `remaining()` reports writable bytes. `writeBytes()` and `readFromFile()` write byte arrays or file-channel data into the `ByteBuf`. `byteArray()` and `byteBuffer()` are unsupported.

## Control Flow, State, and Persistence
State is only the target `ByteBuf` and an offset field that is never advanced by this implementation. All writes mutate the target buffer's writer index; no durable state is persisted.

## Dependencies and Integration Points
It is used by `PagedBlockReader` when reading cached pages through `CacheManager.get`. It depends on Netty `ByteBuf`, Java channels, and page-store target-buffer APIs.

## Risks and Test Signals
Risks include `offset()` always returning zero, unsupported buffer accessors, closing the file channel in `readFromFile()`, and writing beyond buffer capacity if callers miscompute lengths. Tests should cover channel writes, file reads, writable-byte bounds, and offset expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/NettyBufTargetBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMeta.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMeta.java

## Purpose
`PagedBlockMeta` implements block metadata for blocks stored as pages rather than a single local file.

## Important APIs, Types, and Functions
It stores block ID, block size, and `PagedBlockStoreDir`. `getBlockLocation()` returns the directory's `BlockStoreLocation`; `getPath()` returns the directory root path; `getParentDir()` is unsupported because paged dirs do not implement the old `StorageDir` contract.

## Control Flow, State, and Persistence
The object is immutable. Persistent bytes live in page-store files under the associated directory, and the metadata is tracked in `PagedBlockMetaStore`.

## Dependencies and Integration Points
It implements `BlockMeta` and is used by paged readers, writers, store metadata, and UFS fallback readers.

## Risks and Test Signals
Risks include callers expecting a single block file path or `StorageDir`; both are incompatible with paged storage. Tests should cover path/location reporting and avoid using `getParentDir()` on paged metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMetaStore.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMetaStore.java

## Purpose
`PagedBlockMetaStore` manages page metadata and block metadata for the paged block store. It wraps `DefaultPageMetaStore`, indexes committed and temporary blocks, keeps pages of the same block in one directory, commits temp pages to final page IDs, and emits block-store events.

## Important APIs, Types, and Functions
`BlockPageAllocator` reuses the directory of an existing block before delegating allocation. `hasBlock`, `hasTempBlock`, and `hasFullBlock` query indexed state. `addPage()` downcasts/rebuilds `BlockPageId` and creates `PagedBlockMeta` as needed. `addTempPage()` requires an existing temp block and increases temp size. `addTempBlock()` registers and pins temp blocks. `commit()` converts temp metadata to committed metadata and calls `commitFile()` with temp and final file IDs. `removePage()` deletes metadata and emits `onRemoveBlock` when the last page disappears. `getStoreMeta()` and `getStoreMetaFull()` build brief/full block-store metadata.

## Control Flow, State, and Persistence
The delegate page meta store owns page state, while two `IndexedSet`s track committed and temp block metadata by block ID and dir. Commit removes temp metadata, adds committed metadata, and rewrites page file IDs. Removing the final page removes block metadata and notifies listeners. Some interface methods are currently stubbed with `null` or empty usage.

## Dependencies and Integration Points
It integrates `DefaultPageMetaStore`, `Allocator`, `HashAllocator`, `PagedBlockStoreDir`, `BlockPageId`, `BlockStoreEventListener`, `BlockStoreLocation`, and page-cache locks.

## Risks and Test Signals
Risks include stubbed `PageMetaStore` methods (`getStoreDirOfFile`, `getUsage`, `removePage(PageId, boolean)`, `getAllPagesByFileId`), locking discipline relying on callers, duplicate commit handling, and listener callbacks while under metadata lock. Tests should cover restart page scan/addPage, temp block lifecycle, commit ID rewrite, full-block detection, last-page removal events, allocator directory affinity, and unsupported method callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockMetaStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockReader.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockReader.java

## Purpose
`PagedBlockReader` implements `BlockReader` for blocks stored in page cache, with optional fallback to UFS for cache misses. It can also cache UFS-read pages back into Alluxio.

## Important APIs, Types, and Functions
`read(offset,length)` validates and allocates a direct buffer, then delegates to private `read(ByteBuf, offset, length)`. The private read loop computes page IDs and page offsets, calls `CacheManager.get`, updates cache-read metrics, and on misses calls `PagedUfsBlockReader.readPageAtIndex`. `transferTo(ByteBuf)` streams from current position. `close()` records whether the block was read from local cache and/or UFS.

## Control Flow, State, and Persistence
The reader tracks current position, closed state, and whether any bytes came from cache/UFS. Cache hits read existing pages. Cache misses require a UFS reader; if configured to cache into Alluxio, the full UFS page is inserted into `CacheManager`.

## Dependencies and Integration Points
It depends on `CacheManager`, `BlockPageId`, `PagedBlockMeta`, `PagedUfsBlockReader`, `NettyBufTargetBuffer`, `NioDirectBufferPool`, Netty `ByteBuf`, and metrics.

## Risks and Test Signals
Risks include pooled buffer release responsibility, failing when UFS options are absent for cache misses, assuming full requested bytes after UFS page read, and unsupported channel reads. Tests should cover full cache hit, cache miss with cache-fill, missing UFS reader, partial last page, bounds validation, `transferTo`, and close metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStore.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStore.java

## Purpose
`PagedBlockStore` is a `BlockStore` implementation that stores worker blocks as cache-manager pages rather than monolithic block files. It coordinates block locks, page metadata, UFS reads, master commits, and block-store event listeners.

## Important APIs, Types, and Functions
`create()` builds worker cache-manager options, page store dirs, `PagedBlockMetaStore`, and the `CacheManager`. `pinBlock`/`unpinBlock` manage read locks. `createBlockWriter()` registers a temp block and returns `PagedBlockWriter`. `commitBlock()` validates temp bytes, pins during commit, commits page IDs, updates metadata, notifies listeners, and calls `commitBlockToMaster()`. `createBlockReader()` returns a `PagedBlockReader` for cached blocks or creates metadata and a UFS-backed reader for UFS reads. `removeBlock()` locks, removes all pages, deletes page-store data, and emits remove events. Metadata methods return `PagedBlockStoreMeta`.

## Control Flow, State, and Persistence
Persistent block bytes are page-store entries managed by `CacheManager` and `PageStoreDir`; block metadata is in `PagedBlockMetaStore`. Reads pin blocks in the evictor until the delegating reader closes. UFS reads may add block metadata and cache pages. Commits notify the master with worker ID, used bytes, tier, medium, block ID, and size.

## Dependencies and Integration Points
It integrates `CacheManager`, page-store dirs, `BlockLockManager`, `BlockMasterClientPool`, `UfsManager`, `UfsInputStreamCache`, `PagedBlockReader`, `PagedUfsBlockReader`, `PagedBlockWriter`, listeners, and the `BlockStore` contract.

## Risks and Test Signals
Several `BlockStore` APIs are incomplete or placeholder: `load`, `moveBlock`, `accessBlock`, `getTempBlockMeta`, `getVolatileBlockMeta`, `cleanupSession`, and inaccessible-storage handling. `createBlock()` only reserves a temp file and returns a dummy path; actual temp metadata is created by `createBlockWriter()`. Tests should cover temp write/commit, master commit failure, UFS read with and without cache, remove-block lock timeout, listener ordering, incomplete method callers, and paged store compatibility with short-circuit handlers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreDir.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreDir.java

## Purpose
`PagedBlockStoreDir` adapts a page-cache `PageStoreDir` into a block-aware directory. It tracks mappings from block IDs to committed and temp pages, exposes block-store location, and rewrites temp page IDs on commit.

## Important APIs, Types, and Functions
`fromPageStoreDirs()` wraps raw dirs. `putPage()` and `putTempPage()` update block-to-page maps and delegate to the underlying dir. `scanPages()` downcasts page IDs to `BlockPageId` and rewrites returned `PageInfo` to this dir. `commit()` validates temp/final block IDs, delegates commit, converts temp page IDs to final IDs carrying block size, and moves pages from temp to committed maps. `abort()` removes temp pages and unpins. `deletePage()` updates committed mapping and unpins when last page is gone.

## Control Flow, State, and Persistence
The delegate owns physical page persistence; this class maintains in-memory block/page indexes. Commit transitions pages from temp namespace to final namespace. Abort removes temp metadata and delegates temp-file abort.

## Dependencies and Integration Points
It depends on `PageStoreDir`, `PageStore`, `PageInfo`, `BlockPageId`, `BlockPageEvictor`, `BlockStoreLocation`, and `PagedBlockMetaStore`.

## Risks and Test Signals
Risks include empty `deleteTempPage`, `getUsage()` returning empty, synchronized assumptions around non-thread-safe multimaps, and pin matching in `BlockPageEvictor`. Tests should cover scan recovery, commit rewrite, abort cleanup, delete last page unpin, page counts/bytes, and delegate failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreDir.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreMeta.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreMeta.java

## Purpose
`PagedBlockStoreMeta` presents paged-store capacity, usage, directory, and block-location information through the `BlockStoreMeta` interface.

## Important APIs, Types, and Functions
It defines `DEFAULT_TIER`, `DEFAULT_MEDIUM`, and `DEFAULT_STORAGE_TIER_ASSOC`, reflecting that the paged store currently models one top tier/medium. Constructors build either brief metadata with only counts or full metadata with block locations. Interface methods return capacity/used bytes by tier and dir, directory paths, lost storage, block counts, block lists, and tier association.

## Control Flow, State, and Persistence
The object is an immutable snapshot assembled from `PagedBlockMetaStore`. It persists nothing. Optional block lists are only populated by the full constructor.

## Dependencies and Integration Points
It depends on Alluxio storage tier associations, `BlockStoreLocation`, `BlockStoreMeta`, `Pair`, and Guava immutable collections. It is returned by `PagedBlockStore.getBlockStoreMeta*`.

## Risks and Test Signals
Risks include single-tier assumptions, `getBlockList()`/`getBlockListByStorageLocation()` returning null in brief mode, and default medium/tier mismatch with deployments. Tests should cover brief vs full metadata, per-dir maps, empty/lost storage behavior, and master registration compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockStoreMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockWriter.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockWriter.java

## Purpose
`PagedBlockWriter` implements `BlockWriter` by appending block bytes into temporary cache pages.

## Important APIs, Types, and Functions
`append(ByteBuffer)` and `append(ByteBuf)` split incoming bytes across page boundaries, create `BlockPageId.newTempPage` IDs, and call `CacheManager.append` with a temporary cache context. `append(DataBuffer)` prefers a Netty `ByteBuf` output and falls back to a read-only `ByteBuffer`. `getPosition()` returns bytes written; `getChannel()` is unsupported.

## Control Flow, State, and Persistence
The writer tracks `mPosition` and advances it after successful appends. Page bytes are persisted through the cache manager into temp page files. Final commit is handled by `PagedBlockStore`/`PagedBlockMetaStore`, not the writer.

## Dependencies and Integration Points
It depends on `CacheManager`, `BlockPageId`, `CacheContext`, `DataBuffer`, Netty `ByteBuf`, and `BlockWriter`.

## Risks and Test Signals
Risks include per-page byte-array copies, no `close()` override, unsupported channel access, append failure after partial page writes, and reliance on `DataBuffer.getNettyOutput()` casting. Tests should cover page boundary writes, ByteBuf and ByteBuffer paths, fallback path, append failure, and position accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedBlockWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedTempBlockMeta.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedTempBlockMeta.java

## Purpose
`PagedTempBlockMeta` represents a temporary paged block while it is being written.

## Important APIs, Types, and Functions
It extends `PagedBlockMeta` but overrides `getBlockSize()` to return mutable temp size. `setBlockSize()` only allows growth and rejects shrinking.

## Control Flow, State, and Persistence
The temp size starts at zero and grows as temp pages are added. It is converted to immutable `PagedBlockMeta` during commit. Persistence is in page-store temp pages, not in this object.

## Dependencies and Integration Points
It is used by `PagedBlockMetaStore.addTempBlock`, `addTempPage`, and `commit`, and by `PagedBlockStore.commitBlock`.

## Risks and Test Signals
Risks include size drift if page additions fail after updating metadata or vice versa. Tests should verify monotonic size enforcement, add-page size accumulation, and commit size matching cached temp bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedTempBlockMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedUfsBlockReader.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedUfsBlockReader.java

## Purpose
`PagedUfsBlockReader` reads block data from UFS, optimized for page-sized reads and stream reuse through `UfsInputStreamCache`. It supports both direct reads and page-fill reads used by `PagedBlockReader`.

## Important APIs, Types, and Functions
The constructor validates offset, stores UFS options, allocates a direct last-page cache, and initializes UFS bytes-read metrics tagged by UFS and optional user. `read()` fills an output buffer from the cached last page and a UFS channel. `readPageAtIndex()` reads a whole page, caches it in `mLastPage`, copies it to caller buffer, and increments UFS metrics. `transferTo()` streams from current position to Netty or `ByteBuffer`. Inner `UfsReadableChannel` lazily acquires an `InputStream` from `UfsInputStreamCache` with proper UFS offset and releases it on close.

## Control Flow, State, and Persistence
State includes current reader position, closed flag, last page index and buffer, and UFS stream/channel state per channel. No block data is persisted by this class; callers may cache returned pages into `CacheManager`.

## Dependencies and Integration Points
It integrates `UfsManager`, `UnderFileSystem`, `OpenOptions`, `UfsInputStreamCache`, `BlockMeta`, `UfsBlockReadOptions`, `NioDirectBufferPool`, UFS read metrics, and `PagedBlockReader`.

## Risks and Test Signals
Risks include pooled buffers returned from `read()` needing release discipline, last-page buffer mutation assumptions, stream-cache release during concurrent reads, metric map being instance-local rather than shared, and exact offset math combining block offset and UFS file offset. Tests should cover page reads, last-page partial reads, repeated same-page reads, transferTo, close behavior, UFS missing/unavailable errors, and user-tagged metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/PagedUfsBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/UfsBlockReadOptions.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/UfsBlockReadOptions.java

## Purpose
`UfsBlockReadOptions` is an immutable value object describing how to read a block from UFS: mount ID, offset within the UFS file, UFS path, whether to cache into Alluxio, and optional user.

## Important APIs, Types, and Functions
`fromProto()` validates required mount ID, offset, and UFS path, then converts `noCache` to `cacheIntoAlluxio`. Accessors expose each field. `equals()` and `hashCode()` include mount ID, offset, path, and cache flag, but not user.

## Control Flow, State, and Persistence
The object performs no IO. It controls how `PagedUfsBlockReader` opens UFS streams and whether `PagedBlockReader` caches fetched pages.

## Dependencies and Integration Points
It depends on protobuf `Protocol.OpenUfsBlockOptions` and is used by `PagedBlockStore`, `PagedBlockReader`, and `PagedUfsBlockReader`.

## Risks and Test Signals
Risks include `getUser()` returning nullable as a plain `String`, equality ignoring user despite metrics depending on user, and callers swallowing missing-option errors for MUST_CACHE-like paths. Tests should cover required-field validation, no-cache inversion, nullable user, and equality semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/page/UfsBlockReadOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/ByteArrayDataBuffer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/ByteArrayDataBuffer.java

## Purpose
`ByteArrayDataBuffer` is a test-only `DataBuffer` implementation backed by a byte array. It gives tests a simple buffer source that can expose Netty and read-only `ByteBuffer` views.

## Important APIs, Types, and Functions
The constructor stores array, offset, and length. `getNettyOutput()` returns an unpooled wrapped `ByteBuf`; `getLength()` returns length; `getReadOnlyByteBuffer()` returns a read-only view. Byte-copy and stream-read methods are intentionally unsupported. `release()` is a no-op.

## Control Flow, State, and Persistence
The buffer is immutable with respect to offset/length but references the original byte array. It has no persistence and relies on GC for cleanup.

## Dependencies and Integration Points
It implements `DataBuffer` for test code and depends on Guava preconditions and Netty `Unpooled`.

## Risks and Test Signals
Because many `DataBuffer` methods throw `UnsupportedOperationException`, it is only suitable for code paths using Netty output or read-only buffer. Tests using write handlers that call `readBytes()` must use a fuller buffer implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/ByteArrayDataBuffer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/NioDataBufferTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/NioDataBufferTest.java

## Purpose
`NioDataBufferTest` verifies basic behavior of `NioDataBuffer`, the production `DataBuffer` backed by a `ByteBuffer`.

## Important APIs, Types, and Functions
`before()` creates a five-byte increasing buffer. `nettyOutput()` asserts `getNettyOutput()` returns either a Netty `ByteBuf` or `FileRegion`. `length()` checks `getLength()`. `readOnlyByteBuffer()` verifies the returned buffer is read-only and equals the original contents.

## Control Flow, State, and Persistence
The test uses in-memory buffers only. No persistent state is created.

## Dependencies and Integration Points
It depends on `BufferUtils`, `NioDataBuffer`, Netty buffer/file-region types, and JUnit assertions.

## Risks and Test Signals
Signals are limited to basic representation and length behavior. Gaps include release behavior, stream copy methods, partial reads, direct vs heap buffer variations, and interaction with zero-copy gRPC marshalling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/network/protocol/databuffer/NioDataBufferTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AllMasterRegistrationBlockWorkerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AllMasterRegistrationBlockWorkerTest.java

## Purpose
`AllMasterRegistrationBlockWorkerTest` verifies startup registration behavior for `AllMasterRegistrationBlockWorker` when workers are configured to register with all masters.

## Important APIs, Types, and Functions
`before()` configures test mode, embedded journal, multi-master RPC addresses, and installs a `BlockSyncMasterGroup` factory returning the mocked block master client. `workerMasterRegistrationFailed()` makes primary registration throw and asserts startup fails with a fatal primary-master message. `workerMasterRegistration()` verifies normal startup.

## Control Flow, State, and Persistence
The test uses mocked clients and `DefaultBlockWorkerTestBase` state. It checks startup control flow rather than durable persistence.

## Dependencies and Integration Points
It integrates worker configuration, `AllMasterRegistrationBlockWorker`, `BlockSyncMasterGroup`, mocked block/file-system master clients, and worker startup.

## Risks and Test Signals
The strong signal is that primary-master registration failure is fatal. A stated gap is behavior when standby registration fails; the TODO notes a missing test for worker startup with standby failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AllMasterRegistrationBlockWorkerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AsyncBlockRemoverTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AsyncBlockRemoverTest.java

## Purpose
`AsyncBlockRemoverTest` verifies that asynchronous block removal drains queued blocks both when worker removal succeeds and when it throws.

## Important APIs, Types, and Functions
`blockRemove()` mocks `BlockWorker.removeBlock` to record block IDs and returns normally. `failedBlockRemove()` records block IDs and throws `IOException`. Both create `AsyncBlockRemover` with concurrency 10, enqueue 100 blocks, wait until all were attempted, and assert the queue is empty.

## Control Flow, State, and Persistence
State is an in-memory blocking queue and concurrent set of attempted removals. The test confirms removal attempts are not left queued after errors.

## Dependencies and Integration Points
It depends on Mockito, `CommonUtils.waitFor`, `WaitForOptions`, `BlockWorker`, and `AsyncBlockRemover`.

## Risks and Test Signals
Signals cover successful drain and failed-attempt drain. Gaps include duplicate block suppression, shutdown behavior, retry policy, session IDs, and listener/master reporting around removals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/AsyncBlockRemoverTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockHeartbeatReporterTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockHeartbeatReporterTest.java

## Purpose
`BlockHeartbeatReporterTest` validates how `BlockHeartbeatReporter` accumulates, clears, and merges block heartbeat deltas for moves, removals, and lost storage.

## Important APIs, Types, and Functions
`generateReportEmpty()` checks empty output. `generateReportMove()` records moves to MEM/SSD/HDD and checks added blocks by location. `generateReportStateClear()` verifies reports clear state. `generateReportRemove()` checks removed block IDs. `generateReportMoveThenRemove()` ensures a moved-then-removed block is not reported as added. `generateAndRevert()` and `generateUpdateThenRevert()` validate `mergeBack()` after failed heartbeat submission with additional local updates.

## Control Flow, State, and Persistence
The reporter is in-memory. Generating a report clears pending deltas, and `mergeBack()` reintroduces a failed report while preserving newer changes.

## Dependencies and Integration Points
It depends on worker storage locations, configuration for register-to-all-masters, and block heartbeat report structures used by worker-master heartbeat RPCs.

## Risks and Test Signals
The test strongly covers delta coalescing and rollback semantics. Gaps include concurrency, large reports, interaction with `BlockMasterClient.heartbeat`, and storage-lost edge cases across duplicate paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockHeartbeatReporterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockLockManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockLockManagerTest.java

## Purpose
`BlockLockManagerTest` exercises read/write lock behavior, session cleanup, lock pool limits, reuse, and concurrency stress for `BlockLockManager`.

## Important APIs, Types, and Functions
Tests cover `acquireBlockLock`, `tryAcquireBlockLock`, `checkLock`, and `cleanupSession`. They verify multiple read locks, write-lock exclusion, failed validation for wrong session/block/no record, max-lock exhaustion, rejection of write lock when same session already holds read/write lock, lock reuse only after all uses close, and a 200-thread stress scenario.

## Control Flow, State, and Persistence
The lock manager state is in memory. Tests use try-with-resources to close locks and mutate configuration for maximum lock count, reloading properties after each test.

## Dependencies and Integration Points
It depends on `BlockLockManager`, `BlockLock`, `BlockLockType`, Alluxio configuration, temporary folder JUnit rule, and concurrency primitives.

## Risks and Test Signals
This is a strong concurrency regression suite. Remaining risks include fairness/starvation, long timeout behavior, cleanup while locks are actively in use, and interactions with actual block-store operations under failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockLockManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMapIteratorTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMapIteratorTest.java

## Purpose
`BlockMapIteratorTest` verifies `BlockMapIterator` batching of block-location maps into proto entries without duplicate tier/medium locations in a batch.

## Important APIs, Types, and Functions
`convertStream()` builds large MEM/SSD/HDD maps with two dirs each and iterates batches. `convertStreamMergedTiers()` uses uneven dir sizes. Both assert that each returned batch has no duplicate `Block.BlockLocation` constructed from tier alias and medium type.

## Control Flow, State, and Persistence
The test generates in-memory maps of decreasing block IDs and consumes iterator batches. It performs no persistence.

## Dependencies and Integration Points
It depends on `BlockMapIterator`, `BlockStoreLocation`, `LocationBlockIdListEntry`, proto `Block.BlockLocation`, and Guava immutable collections.

## Risks and Test Signals
The main signal is that registration/heartbeat streaming can batch location entries without duplicate logical locations. Gaps include exact batch sizing, ordering, empty maps, medium type propagation, and memory behavior for very large maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMapIteratorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterClientTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterClientTest.java

## Purpose
`BlockMasterClientTest` verifies worker-to-block-master client metadata, request conversion, heartbeat, registration, commit, UFS commit, worker ID lookup, and register lease behavior against an in-process mock gRPC server.

## Important APIs, Types, and Functions
`clientInfo()` checks service type/name/version. `convertBlockListMapToProtoMergeDirsInSameTier()` validates directory entries merge by tier. `commitBlock()` and `commitUfsBlock()` assert request fields reach mock RPCs. `getId()` maps worker address to ID. `heartBeat()` validates used bytes, removed blocks, added blocks, lost storage, and returned command. Lease tests cover allowed/denied `requestRegisterLease`. `registerWithoutStream()` and `registerWithStream()` exercise both registration paths.

## Control Flow, State, and Persistence
Each test creates a mock `BlockMasterWorkerService` server on a configured address, constructs a client, invokes one path, and shuts the server down in `@After`. State is in memory; persistence is simulated through recorded request maps/lists.

## Dependencies and Integration Points
It depends on gRPC server/channel helpers, master client context, Alluxio configuration, generated block-master worker service RPCs, worker net address conversion, retry policy, auth configuration, and `BlockMasterWorkerServiceTestUtils`.

## Risks and Test Signals
This is a high-value request-shape suite. Gaps include real reconnects, multi-master failover, streaming registration payload content beyond worker ID, RPC deadline behavior, authentication-enabled channels, and server-side errors after partial stream writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterClientTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterWorkerServiceTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterWorkerServiceTestUtils.java

## Purpose
`BlockMasterWorkerServiceTestUtils` provides test helpers for creating gRPC servers with a single service and channels to those servers.

## Important APIs, Types, and Functions
`createServerWithService(serviceType, handler, address)` uses global configuration; the overload accepts an explicit `AlluxioConfiguration`. Both build a `GrpcServer` with `GrpcServerAddress` and `GrpcService`. `createChannel(address)` and its overload build `GrpcChannel`s for a socket address and configuration.

## Control Flow, State, and Persistence
The helpers construct server/channel objects but do not start or close them automatically. Tests manage lifecycle.

## Dependencies and Integration Points
It integrates `GrpcServerBuilder`, `GrpcChannelBuilder`, `GrpcServerAddress`, `GrpcService`, `ServiceType`, Alluxio configuration, and gRPC `BindableService`.

## Risks and Test Signals
Risks include tests leaking servers/channels if callers do not close them, and helper defaults masking configuration-sensitive behavior. Useful tests assert callers start/shutdown servers and use explicit configs for auth or retry scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterWorkerServiceTestUtils.java -->
