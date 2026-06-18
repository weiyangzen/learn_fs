## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/RegisterStreamerTest.java

**Purpose:** Tests streamed worker registration to the block master over gRPC, including response deadlines, completion handling, server errors, and successful multi-request registration.

**Important APIs:** Exercises `RegisterStreamer.registerWithMaster`, `BlockMasterWorkerServiceGrpc.registerWorkerStream`, streamed `RegisterWorkerPRequest/Response`, and configuration keys controlling stream timeouts, deadline, completion timeout, and batch size.

**Control flow:** Each test starts an in-process gRPC server with a custom `StreamObserver` supplier and creates a channel-backed `RegisterStreamer`. Server observers either never respond, respond without completing, error early, complete early, error on completion, or respond and complete successfully.

**State and persistence:** No durable state. Runtime state includes gRPC server/channel lifecycle, request counts per worker ID, and stream observer callbacks.

**Dependencies and integration:** Uses Alluxio gRPC test utilities, `ConfigurationRule`, NOSASL auth, worker store metadata maps, worker config list, and Java streams to generate block IDs.

**Risks:** Streaming registration is timing-sensitive; deadlines must fail promptly without hanging tests. Early server completion/error handling must map to the correct Alluxio status exception.

**Test signals:** Strong coverage for single and concurrent request timeouts, missing completion, early server error, early completion cancellation, completion-time error, and successful request count.
