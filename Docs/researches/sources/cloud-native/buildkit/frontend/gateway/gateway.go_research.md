# sources/cloud-native/buildkit/frontend/gateway/gateway.go

## Purpose

This file implements the image-based BuildKit gateway frontend and the server-side LLBBridge gRPC service exposed to frontend containers. It loads an external frontend source, runs it as a container, forwards solve/source/container/filesystem/warning APIs over stdio, and converts returned protobuf results back into solver results.

## Important APIs, Types, And Functions

- `NewGatewayFrontend` parses optional allowed repositories and returns a `frontend.Frontend`.
- `gatewayFrontend.checkSourceIsAllowed` enforces source repository allowlists.
- `(*gatewayFrontend).Solve` loads the external frontend image/context, prepares metadata and environment, starts the bridge server, runs the frontend container, and returns its result.
- `metadataMount`, `bind`, and `bindMount` expose the current frontend definition at `/run/config/buildkit/metadata/frontend.bin`.
- `llbBridgeForwarder` implements `pb.LLBBridgeServer` with solve, source metadata, image config, reads, evaluate, ping, return, inputs, container, exec, warning, and cleanup behavior.
- `serveLLBBridgeForwarder`, `newPipe`, and `serve` create an HTTP/2 gRPC server over process stdio pipes.
- `processIO`, `outputWriter`, and `ExecProcess` implement multiplexed process stdin/stdout/stderr, resize, signal, started, exit, and done messages.
- Helper functions include `wrapSolveError`, `registerResultIDs`, `cloneRef`, `convertRef`, `ToPBResolveSourceMetaResponse`, checksum conversion, attestation-chain conversion, `getCaps`, and `addCapsForKnownFrontends`.

## Control Flow

`Solve` rejects deprecated gateway development mode, requires `frontend.KeySource`, checks allowlist, and creates a forwarder-backed docker UI client. If a named context for the source exists, it loads that; otherwise it resolves an image config for the source, pins digest when available, and builds an `llb.Image` marked as frontend usage. The source state is solved to a worker ref, converted to a mutable rootfs, and run with args/env/cwd derived from image config. Build options are injected as indexed `BUILDKIT_FRONTEND_OPT_N` environment variables, along with session ID, workers JSON, and exported product.

Capabilities are read from frontend image labels and requested `frontend.caps`; known legacy dockerfile frontend digests get input capability added manually. Unsupported requested caps return unimplemented solve errors. The bridge server is started over two pipes before executing the frontend. The frontend definition is mounted read-only as metadata. If executor run fails and the frontend did not already return an error/result, that run error becomes the gateway result.

The LLBBridge service maps protobuf calls to the underlying `FrontendLLBBridge`: resolving source metadata, resolving image config, solving LLB/frontend requests, reading refs, statting refs, evaluating refs, returning final results, exposing inputs, creating containers, reading container mounts, releasing containers, executing container processes, and sending warnings. Solve responses allocate opaque ref IDs and retain result proxies. Return clones refs so returned results outlive the server ref table.

`ExecProcess` maintains one bidirectional stream for all process messages. Init creates a process I/O pipe set, starts the target container process, sends Started before output, forwards output as file messages, turns process wait errors into Exit messages, handles nonzero exit as normal return data, and sends Done after file pipes close. Incoming File, Resize, and Signal messages are routed by process ID.

## State And Persistence Behavior

`gatewayFrontend` stores only immutable worker info and allowed repository names. `llbBridgeForwarder` stores per-run mutable state: ref ID map, worker ref ID map, final result/error, done channel, active containers, mounted snapshot mounters, pipe handles, and server-closed flag. Mutexes protect result/ref state, containers, and mount caches. `Discard` releases containers, unmounts mounters, releases worker refs, releases result refs on error, and releases outstanding refs.

Temporary metadata directories are created with `os.MkdirTemp` and removed by deferred release. Source rootfs mutable refs are released at the end of `Solve`. The gRPC server lifecycle is tied to a cancelable context and stdio pipe connection.

## Dependencies And Integration Points

This file is a central integration point for distribution reference parsing, docker UI named contexts, LLB source and solve APIs, executor, worker refs, cache managers, sessions, snapshot mounts, source metadata resolution, protobuf gateway service definitions, gRPC/http2 transport, tracing, API capability sets, warning APIs, image specs, signal maps, and typed gRPC errors.

## Risks And Edge Cases

Security and lifecycle risks are high. Allowed repositories must be normalized consistently because tags are stripped before comparison. Frontend images control entrypoint, env, labels, working directory, and requested caps. Build options are injected through environment variables, so parsing in the client must match the indexed `key=value` format. Resource cleanup spans rootfs refs, temporary metadata dirs, pipe connections, containers, mounts, result refs, and worker refs.

Concurrency risks include simultaneous gRPC calls mutating ref maps, process streams sending messages concurrently, and server shutdown racing with executor failure. The code uses thread-safe stream sending and locks, but send/receive ordering is delicate: Started is intentionally sent before output and before wait is allowed to send Exit. Capability compatibility paths are complex; older frontend images without caps labels get special cases only for known digests. `ReadFileContainer` and related APIs address containers by `Ref` field carrying container ID, which is semantically overloaded.

## Test Signals

`gateway_test.go` directly tests allowed source matching, including no restrictions, tag-insensitive repository matching, rejection of other repositories, and Docker Hub normalization for `alpine`. Broader integration tests exercise gateway reference operations. Missing focused tests include capability negotiation, frontend env option parsing, gRPC return formats, process I/O ordering, container release on errors, and source metadata conversion.
