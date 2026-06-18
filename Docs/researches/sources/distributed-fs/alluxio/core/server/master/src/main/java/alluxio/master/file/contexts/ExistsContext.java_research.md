# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/ExistsContext.java

Purpose: wraps `ExistsPOptions` for master exists checks. It is a thin `OperationContext` specialization that ensures exists calls use configured master defaults.

Important APIs and types: `create` wraps a builder directly, `mergeFrom` merges a caller builder into `FileSystemOptionsUtils.existsDefaults`, and `defaults` creates a default context. The only behavior beyond the base class is diagnostic `toString`.

Control flow: RPC handling can accept user options, call `mergeFrom`, and pass the context through file-master path resolution. The base `OperationContext` can still carry cancellation trackers even though exists has no operation id override here.

State and persistence behavior: no persistent state is owned. Options may influence metadata sync or load behavior for exists depending on the fields in `ExistsPOptions`, but this wrapper does not add state.

Dependencies and integration points: depends on global configuration and file-system option utility defaults. It integrates with the master exists RPC and any call-tracking added through `OperationContext.withTracker`.

Risks: because it is a mutable builder wrapper, later builder mutation affects the context. Tests should detect if future `ExistsPOptions` fields need explicit context-side handling.

Test signals: default merging, string rendering, and behavior of exists calls with sync-related common options are the useful coverage points.
