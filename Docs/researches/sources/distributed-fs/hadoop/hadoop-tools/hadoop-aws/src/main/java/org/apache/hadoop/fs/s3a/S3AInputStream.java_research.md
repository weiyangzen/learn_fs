# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AInputStream.java

## Purpose

`S3AInputStream` is the classic S3A object input stream. It implements Hadoop seekable, positioned, readahead, unbuffer, vectored-read, and IO-statistics stream behavior over S3 range GET requests. Its core job is to turn file-position reads into efficient and recoverable HTTP range reads while tracking object version changes and deciding when to drain or abort underlying AWS response streams.

## Important APIs, Types, and Functions

The class extends `ObjectInputStream` and implements `CanSetReadahead` plus stream capabilities. Constructor state comes from `ObjectReadParameters` and `S3AReadOpContext`. Public methods include `seek`, `getPos`, `read()`, `read(byte[], int, int)`, `readFully`, `readVectored` overloads, `close`, `resetConnection`, `available`, `remainingInFile`, `remainingInCurrentRequest`, `setReadahead`, `getReadahead`, `unbuffer`, `hasCapability`, and test accessors `isObjectStreamOpen` and `getWrappedStream`.

Important internals include `reopen`, `lazySeek`, `seekInStream`, `closeStream`, `onReadFailure`, `streamReadResultNegative`, `calculateRequestLimit`, `validateReadahead`, vectored helpers `readSingleRange`, `readCombinedRangeAndUpdateChildren`, `populateChildBuffers`, `drainUnnecessaryData`, `populateBuffer`, `readByteArray`, `getS3ObjectInputStream`, and `getS3Object`. The stream tracks `pos`, `nextReadPos`, `contentRangeStart`, `contentRangeFinish`, `wrappedStream`, `closed`, `fileLength`, `readahead`, `ChangeTracker`, `asyncDrainThreshold`, and `stopVectoredIOOperations`.

## Control Flow

Sequential reads are lazy-seek based. `seek` only validates and records `nextReadPos`. On `read`, the stream calls `lazySeek`, which uses the read invoker to run `seekInStream` and reopen as needed. `seekInStream` may skip forward within the current HTTP response if the target is within the forward seek limit; otherwise it closes the current response and positions for a new range GET. Backward seek records statistics and switches adaptive `Normal` policy to `Random`. `reopen` closes any existing object stream, computes a range limit with `calculateRequestLimit`, builds a GET request with change-tracker constraints, opens the AWS response through callbacks, processes the response for change detection, and updates range/position state.

`read()` and `read(byte[], int, int)` both check closure and EOF, perform lazy seek, then use retry logic around the wrapped stream read. HTTP EOF/channel or timeout failures close the current stream for recovery and rethrow so the invoker can retry. Positive reads advance `pos` and `nextReadPos`, update stream and filesystem byte counters, and complete read-operation statistics. Negative results close the wrapped stream so the next read can reopen if needed. `readFully` synchronizes the whole positioned-read sequence, seeks to the requested offset, repeatedly reads until full, and seeks back to the original position in a finally block.

Close and unbuffer are connection-management paths. `close` marks the stream closed, stops vectored IO, closes or aborts the current response, closes callbacks, and then calls superclass close. `closeStream` decides whether to abort or drain based on `forceAbort`, remaining bytes in the current request, configured readahead, and async drain threshold. Small drains or blocking calls run inline; larger soft closes can submit an async `SDKStreamDrainer`.

Vectored reads validate/sort ranges, attach futures to every `FileRange`, close the normal stream, switch adaptive policy to random, then submit either one task per disjoint range or merged combined-range tasks. Combined reads fetch a larger range once, drain bytes between child ranges, allocate/populate child buffers, and complete each range future. Single-range reads GET just the requested range and fill the caller-allocated buffer. Vectored work checks `stopVectoredIOOperations` so close or unbuffer can interrupt active tasks.

## State and Persistence Behavior

The stream persists no filesystem data; all state is transient client-side read state. `pos` is the current wrapped-stream position, while `nextReadPos` is the logical position requested by Hadoop APIs. `contentRangeStart` and `contentRangeFinish` describe the active S3 range request. `wrappedStream` is the live AWS `ResponseInputStream<GetObjectResponse>` or null. `ChangeTracker` carries expected object version/etag constraints across GETs and detects remote changes. Statistics are accumulated into the stream statistics and merged through superclass/callback lifecycle.

`Normal` input policy starts sequential-like by requesting to object end, then becomes `Random` after backward seek or unbuffer. `Random` range limits use max(request length, readahead), capped at object length. `Sequential` and `Normal` range limits read to object end. Readahead is validated as non-negative and defaults when null.

## Dependencies and Integration Points

The stream depends on `ObjectInputStream` callbacks for building GET requests, obtaining objects, submitting async drain work, and closing audit/client resources. It uses AWS SDK `GetObjectRequest`, `GetObjectResponse`, and `ResponseInputStream`; Hadoop `FileRange`, `StreamCapabilities`, `CanSetReadahead`, `VectoredReadUtils`, and positioned-read validation; S3A `S3AReadOpContext`, `S3AInputPolicy`, `ChangeTracker`, `Invoker`, statistics classes, and range-formatting helpers. It is constructed by `S3AFileSystem` through `S3AStore.readObject` using object attributes and read context created during open.

## Risks and Edge Cases

The stream's synchronization protects normal read/seek state, but vectored range tasks run asynchronously and interact with close/unbuffer through an atomic stop flag; a new vectored read after unbuffer can reset the flag, so termination of older operations is not guaranteed by the code comment. Read failures before `wrappedStream` is reset can lead to retries with a null stream, handled explicitly by reopening in the retry block. EOF can mean real file end or a broken network response; some paths downgrade EOF to `-1` and others throw `EOFException`, so callers see different behavior depending on API.

Large unread response ranges are aborted rather than drained; smaller ones may be drained to preserve connection reuse, which affects latency and connection-pool behavior. `available` and remaining calculations depend on local position state and object length. Direct buffers in vectored reads use a temporary byte array path, while heap buffers assume array-backed buffers. Vectored reads do not attempt recovery while filling or draining a combined range; failures complete affected futures exceptionally. Change tracking can raise remote-file-changed exceptions when S3 responses do not match expected etag/version.

## Test Signals

Unit tests should cover `calculateRequestLimit` for all policies, null/negative readahead validation, lazy seek without immediate GET, forward seek skip versus reopen, backward seek adaptive switch, EOF handling at and beyond object length, read retry recovery after simulated socket timeout/HTTP EOF, close-stream drain versus abort thresholds, resetConnection behavior, close idempotence, unbuffer policy switch and stop flag, and capability reporting for readahead/unbuffer/IO statistics.

Vectored tests should cover empty ranges, disjoint ranges, merged ranges with draining between children, direct and heap buffers, interruption by close/unbuffer, exceptional futures on GET/read failure, range validation against known file length, byte/statistics accounting, and change-tracker failures. Integration tests should validate that filesystem open options and file statuses flow into stream contexts and produce expected S3 range headers.
