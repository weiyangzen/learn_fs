# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestAsyncIPC.java

## Purpose
`TestAsyncIPC` verifies Hadoop IPC client's asynchronous call modes, async call limit enforcement, response future reuse, timeout handling, call-id/retry propagation, and `CompletableFuture` integration.

## Important APIs, Types, and Functions
The tests use `Client.setAsynchronousMode()`, `Client.getAsyncRpcResponse()`, `Client.getResponseFuture()`, `AsyncGetFuture`, `AsyncCallLimitExceededException`, `Client.setCallIdAndRetryCount()`, `Server.getCallId()`, `Server.getCallRetryCount()`, and `TestIPC.TestServer`. Nested caller classes are `AsyncCaller`, `AsyncCompletableFutureCaller`, and `AsyncLimitlCaller`.

## Control Flow
`setupConf()` enables high async-call capacity and async mode on the main thread. `internalTestAsyncCall()` starts a test server, creates clients, starts callers that issue async RPCs and store futures, then validates returned `LongWritable` values. Limit tests catch `AsyncCallLimitExceededException`, wait for prior futures, and resume. Call-id tests override `Client.createCall()` or install server listeners to validate retry counts in request and response headers. The CompletableFuture test delays server handling and verifies sending ten async calls is faster than sequential processing.

## State and Persistence
State is in client async counters, per-caller future maps/lists, expected value maps/lists, server listener callbacks, call-id maps, and temporary server/client threads. No files are persisted.

## Dependencies and Integration Points
The file integrates core IPC `Client`, `Server`, RPC headers, `TestIPC` test server, Hadoop `LongWritable`, `AsyncGetFuture`, `CompletableFuture`, `SubjectInheritingThread`, and IPC config key `IPC_CLIENT_ASYNC_CALLS_MAX_KEY`.

## Risks and Edge Cases
Async mode is thread-local, so caller threads explicitly re-enable it. Limit tests depend on server and handler timing. Sequential call-id validation sorts server-observed IDs because execution order is not guaranteed. `AsyncLimitlCaller` name contains a typo but behavior is clear.

## Test Signals
Signals are all futures resolving to sent values, async counter returning to its original count, timeout polling eventually completing, limit exceptions handled without lost calls, matching retry counts on server and response, unique sequential call IDs across 10,000 concurrent calls, and fast non-blocking CompletableFuture submission.
