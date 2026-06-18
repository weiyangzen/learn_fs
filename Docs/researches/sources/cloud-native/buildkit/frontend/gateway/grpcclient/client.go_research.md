# sources/cloud-native/buildkit/frontend/gateway/grpcclient/client.go

## Purpose

This file implements the gRPC client used inside external frontend containers. It connects to the BuildKit gateway LLBBridge over stdio, exposes the public `client.Client` API, performs capability negotiation and compatibility fallbacks, returns final results, resolves metadata, runs gateway exec containers, and represents remote refs.

## Important APIs, Types, And Functions

- `GrpcClient` extends `client.Client` with `Run`.
- `New`, `current`, `RunFromEnvironment`, `grpcClientConn`, and `stdioConn` initialize the client from explicit parameters or BuildKit environment.
- `grpcClient.Run` runs a `client.BuildFunc` and sends a `Return` request or old inline final solve.
- `defaultCaps` and `defaultLLBCaps` define frozen fallback capabilities for older servers.
- `Solve`, `ResolveSourceMetadata`, `ResolveImageConfig`, `BuildOpts`, `CurrentFrontend`, `Inputs`, and `Warn` implement core client operations.
- `messageForwarder`, `procMessageForwarder`, `msgWriter`, `container`, and `containerProcess` implement gateway exec process stream handling.
- `reference` implements remote ref filesystem and state APIs.
- Environment helpers `opts`, `sessionID`, `workers`, and `product` parse gateway runtime environment.

## Control Flow

`New` pings the server with a timeout, fills missing capability lists with defaults, and creates a grpc client with an exec message forwarder. `Run` decides whether the server supports explicit `Return`; if so, it defers conversion of the build result or error into `ReturnRequest`. Without `Return`, it uses the legacy inline final solve path by marking the solve request for the returned ref as final and serializing metadata into exporter attrs. It always releases the exec message forwarder at the end.

`Solve` checks LLB metadata caps, propagates cache import options from top-level build opts when absent, sends a protobuf solve request, handles evaluate either natively or by deferred `StatFile(".")`, then converts deprecated or modern ref wire formats and attestations to client results. `ResolveSourceMetadata` uses the new source-meta resolver when supported; otherwise it falls back to image config resolution only for docker-image/oci-layout and rejects newer image attestation or HTTP checksum features. `ResolveImageConfig` similarly prefers source metadata when supported, else uses the older resolve-image RPC.

Gateway exec uses a single shared stream. `NewContainer` sends container creation, starts the stream once, and returns a remote container handle. `container.Start` registers a process ID, sends Init with requested file descriptors, waits for Started, forwards stdin as file messages, receives output/exit/done messages, converts nonzero exits to `pb.ExitError`, and deregisters on wait. Resize and Signal become stream messages with capability/known-signal checks. Container filesystem methods require `CapGatewayExecFilesystem`.

## State And Persistence Behavior

`grpcClient` stores server caps, LLB caps, build opts, session ID, worker list, a map from returned ref IDs to solve requests for legacy final return, and a long-lived message forwarder. The message forwarder owns a context, one exec stream, per-process message channels, a start-once guard, and stored start error. Remote refs contain their ID and optional definition. No durable filesystem state is created except reading `/run/config/buildkit/metadata/frontend.bin` in `CurrentFrontend`.

## Dependencies And Integration Points

It integrates with gateway protobuf client stubs, grpc interceptors, insecure stdio transport, `llb`, source resolver options, image utility rewrite errors, API caps, solver protobuf caps, typed grpc errors, signal maps, filesystem stat types, Open Containers descriptors/platforms/digests, and the public gateway client interfaces.

## Risks And Edge Cases

Compatibility logic is dense. Capability polarity must be read carefully because `Supports` returns nil on support. Old servers may omit caps and get default caps; changing defaults would break compatibility. In `Run`, the deferred exec release assignment appears to set `retError = err` when both `err != nil` and `retError != nil`, which would replace an existing build error with release error rather than preserve the original; this may be intentional but is worth review. Process stream handling depends on Started, Exit, Done ordering and can block if stdin is an interactive source; the code intentionally keeps stdin copy outside the errgroup. Result attestation conversion assumes `a.Ref` is non-nil before checking `a.Ref.Id` in `Solve`, which could panic if protobuf attestations omit a ref. Environment option parsing trusts the `BUILDKIT_FRONTEND_OPT_N=key=value` format.

## Test Signals

No direct tests in this subset cover grpc client behavior. Integration tests exercise the client indirectly inside external frontend scenarios elsewhere. Needed targeted tests include Run return/legacy paths, capability fallbacks, source metadata fallback errors, attestation ref nil handling, process I/O exit conversion, and environment option parsing.
