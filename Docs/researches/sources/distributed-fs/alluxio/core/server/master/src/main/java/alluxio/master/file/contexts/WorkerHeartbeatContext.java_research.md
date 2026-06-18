# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/WorkerHeartbeatContext.java

Purpose: wraps `FileSystemHeartbeatPOptions` for worker heartbeat handling in the file master.

Important APIs and types: `create` wraps a provided heartbeat options builder, and `defaults` creates a new builder through a private no-arg constructor. The context inherits cancellation tracking from `OperationContext`.

Control flow: worker heartbeat handling builds a context and passes it through file-system master heartbeat internals. There is no default merge utility here; `defaults` simply uses `FileSystemHeartbeatPOptions.newBuilder()`.

State and persistence behavior: this wrapper is transient. Heartbeat options may drive persisted or in-memory file block state changes elsewhere, but this class owns none of that behavior.

Dependencies and integration points: depends on heartbeat protobuf options and `OperationContext`. It integrates with worker-to-master heartbeat paths.

Risks: no explicit defaults are merged, so default behavior is whatever the protobuf builder provides. Future heartbeat options requiring configuration defaults would need changes here.

Test signals: heartbeat context creation, option propagation, default empty options, and debug rendering are adequate wrapper-level tests.
