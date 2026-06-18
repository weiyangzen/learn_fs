# Research: sources/cloud-native/buildkit/client/workers.go

Purpose: exposes the client-side worker listing API used by `buildctl debug workers` and other callers that need daemon worker capabilities. The main data model is `WorkerInfo`, which mirrors control-service `WorkerRecord` fields for ID, labels, supported platforms, GC policy, BuildKit/Dockerfile versions, and CDI devices.

Important APIs and control flow: `Client.ListWorkers(ctx, opts...)` accumulates `ListWorkersOption` values into `ListWorkersInfo`, calls `ControlClient().ListWorkers`, wraps RPC errors with context, and converts protobuf records into stable client structs. `fromAPIGCPolicy` translates API GC policy durations and byte thresholds into `client.PruneInfo`.

State, dependencies, and integration: this file does not persist state; it is a typed adapter over the control gRPC API. It depends on `controlapi`, API type structs, platform conversion helpers in `solver/pb`, and version/CDI conversion helpers defined elsewhere in the client package.

Risks and test signals: incorrect conversion would make CLI worker output and programmatic worker discovery misleading, especially GC thresholds and platform lists. Tests are indirect through `buildctl debug workers` integration and daemon `Controller.ListWorkers`, with no file-local unit tests for filtering or conversion edge cases.
