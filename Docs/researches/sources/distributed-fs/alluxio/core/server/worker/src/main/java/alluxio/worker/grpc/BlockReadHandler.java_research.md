# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/BlockReadHandler.java

Purpose: gRPC server-side stream observer for block read requests, including flow control, data-buffer production, optional block promotion, response serialization, metrics, and cleanup.

Important APIs: `onNext`, `onError`, `onCompleted`, `onReady`, `tooManyPendingChunks`, `createRequestContext`, and inner `DataReader` methods `runInternal`, `completeRequest`, `getDataBuffer`, `openBlock`, `replyError`, `replyEof`, and `replyCancel`.

Control flow: The first request creates and validates a `BlockReadRequestContext`, initializes queued and received offsets, and submits a `DataReader`. Later offset-received messages update flow-control state and may restart reading. `DataReader` loops while ready and under in-flight byte limits, opens the block lazily, reads chunk data using PAGE or FILE transfer paths, queues serialized responses, and marks EOF when requested bytes are exhausted or short read occurs. EOF, cancel, or error complete the request and close or abort temp blocks as appropriate.

State and persistence: Holds a volatile read context protected by a `ReentrantLock`, data reader executor, serializing executor, response observer, worker reference, domain-socket flag, pooled-buffer flag, and block-store type. Actual data comes from block files or UFS readers through `DefaultBlockWorker`.

Dependencies and integration: Uses `DefaultBlockWorker`, `BlockReader`, `AllocateOptions`, `DataMessageServerStreamObserver`, Netty buffers, metrics, `BlockReadRequestContext`, and worker network config. Promotion uses the top storage tier alias from `WORKER_STORAGE_TIER_ASSOC`.

Risks and test signals: Context can be null in some error paths, and flow control depends on client offset acknowledgements. Buffer retain/release correctness is critical. Tests should cover invalid request bounds, executor rejection, onReady restart, cancellation before/after reader start, PAGE and FILE buffer paths, pooled and unpooled modes, promote failures, temp block commit/abort behavior, EOF short reads, and metrics decrement on completion.
