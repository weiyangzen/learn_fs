# sources/distributed-fs/beegfs-go/rst/remote/internal/server/server.go

## Purpose
This file implements the BeeRemote gRPC server. It exposes job submission/query/update, worker-result ingestion, RST configuration discovery, stub content lookup, and capability reporting by adapting protobuf RPCs to the `job.Manager`.

## Important APIs, Types, and Functions
`Config` holds listen address and TLS files. `BeeRemoteServer` embeds the unimplemented protobuf server and stores logger, wait group, gRPC server, job manager, component registry, and start time. `New` configures optional TLS and registers the service. `ListenAndServe` starts serving in a goroutine. RPC methods include `SubmitJob`, `GetJobs`, `UpdatePaths`, `UpdateJobs`, `GetRSTConfig`, `UpdateWork`, `GetStubContents`, and `GetCapabilities`.

## Control Flow
The server creates a `grpc.Server`, binds a TCP listener, and forwards RPCs to job-manager methods. Streaming RPCs (`GetJobs`, `UpdatePaths`) create buffered response channels and a sender goroutine, then wait until the manager closes the channel. `SubmitJob` maps sentinel job-manager errors into response status enums instead of returning gRPC errors for expected job states. `UpdateJobs` maps missing DB entries to gRPC `NotFound`.

## State and Persistence Behavior
The server itself persists nothing. It tracks outstanding RPCs with a wait group so `Stop` can stop the gRPC server and wait for handlers. All durable job and work state is delegated to `job.Manager`. Capabilities include process start time from `startTime`.

## Dependencies and Integration Points
This is the public BeeRemote RPC boundary. It integrates `job.Manager`, `registry.ComponentRegistry`, `common/rst` sentinel errors, `common/kvstore` errors, gRPC TLS credentials, protobuf `beeremote` and `flex`, and timestamp conversion.

## Risks and Edge Cases
Streaming send errors are ignored intentionally so the sender drains the response channel and avoids blocking the producer; this means client disconnect details are not surfaced. `ListenAndServe` treats any `Serve` return as an error, so a normal stop may report through `errChan` depending on gRPC behavior. TLS is disabled when cert/key are absent or `TlsDisable` is true, with only a warning.

## Test Signals
No direct server tests are in this subset. Behavior is indirectly exercised by job-manager tests and by BeeSync worker/client integration expectations, but RPC-level streaming, TLS, listener failure, and capability responses need dedicated coverage.
