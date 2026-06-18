# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/client.go

## Purpose
This file implements BeeSync's client wrapper for communicating back to BeeRemote. It supports dynamic provider replacement when BeeRemote sends updated callback configuration.

## Important APIs, Types, and Functions
`Config` stores static TLS/proxy settings plus dynamic `*flex.BeeRemoteNode`. `Client` embeds a `Provider`, stores config, and guards it with `readyMu`. `Provider` abstracts init/disconnect/update-work/submit-job operations. `New`, `CompareConfig`, `UpdateConfig`, `UpdateWorkRequest`, `SubmitJobRequest`, and `Disconnect` form the public API.

## Control Flow
`New` creates an empty client and applies initial dynamic config if present, tolerating nil config as an unready but valid client. `UpdateConfig` takes a write lock, disconnects the old provider, chooses a mock provider for `mock:0`, creates a gRPC provider for non-empty addresses, and rejects invalid addresses. Request methods take read locks, reject unready clients, call the provider, and classify gRPC status errors.

## State and Persistence Behavior
The client persists no job state. It owns connection/provider state and dynamic BeeRemote config. Updates are serialized against in-flight requests by the RW mutex, so provider replacement waits for active calls to finish.

## Dependencies and Integration Points
It is used by `sync/internal/workmgr` workers to send final work results and by the work manager during runtime config updates. It depends on protobuf `beeremote`/`flex`, gRPC status codes, protobuf equality, and concrete providers in `grpc.go`/`mock.go`.

## Risks and Edge Cases
There is no cancellation mechanism for in-flight `UpdateWorkRequest` calls during config updates; comments rely on worker retry behavior. Non-gRPC errors are treated as likely bugs but retryable for work updates. `NotFound` is non-retryable, matching force-deletion scenarios on BeeRemote. `UpdateConfig` disconnects the old provider before validating/creating the new one, so failed updates can leave the client without a provider.

## Test Signals
Work-manager tests use the mock provider path and exercise update-result retry behavior. There are no direct client tests for lock behavior, provider replacement failure, error classification, or `SubmitJobRequest`.
