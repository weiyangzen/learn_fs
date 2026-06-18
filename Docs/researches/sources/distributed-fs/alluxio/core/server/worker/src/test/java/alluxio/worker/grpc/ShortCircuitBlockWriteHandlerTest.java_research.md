# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandlerTest.java

Purpose: tests `ShortCircuitBlockWriteHandler` creating local temp block files and handling abort/commit lifecycle through direct path responses.

Important APIs and helpers: setup creates a temp directory, `CreateLocalBlockRequest`, handler, response observer, and in-file `TestBlockWorker`. Tests cover normal create/commit, a second request before commit aborting prior state, reserving space before creation, cancellation abort, and error abort.

Control flow and state: the first `onNext` creates a local temp file and responds with a path while leaving the stream open. `onCompleted` commits; `onError` and cancellation cleanup temp state. `TestBlockWorker` tracks temp and committed block sets, writes files, implements `requestSpace`, and cleans session state.

Dependencies and integration: depends on `CreateLocalBlockRequest/Response`, `NoopBlockWorker`, `CreateBlockOptions`, local filesystem, and a custom observer.

Risks and test signals: very useful lifecycle signal without a full real worker. The fake worker is not thread-safe and simplifies capacity/accounting, so concurrent behavior and real allocator failures are outside scope.
