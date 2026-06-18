# sources/cloud-native/buildkit/frontend/gateway/pb/gateway.proto

## Purpose

`gateway.proto` is the authoritative protobuf schema for BuildKit's frontend gateway bridge, package `moby.buildkit.v1.frontend`. It defines the `LLBBridge` service that frontends use to ask BuildKit to resolve image/source metadata, solve LLB graphs, inspect refs or containers, exchange frontend inputs, report final results, create/release execution containers, run bidirectional process streams, and emit warnings.

The Go package option maps generated code to `github.com/moby/buildkit/frontend/gateway/pb` with Go package name `moby_buildkit_v1_frontend`. The schema imports BuildKit solver, worker, source policy, API capability, fsutil stat, timestamp, and RPC status definitions, so it is a compact but high-impact contract between gateway clients, BuildKit workers, and solver internals.

## Important APIs, Types, and RPCs

The single service, `LLBBridge`, exposes these unary RPCs:

- `ResolveImageConfig`, gated by `apicaps:CapResolveImage`, resolves image config/digest/reference for a ref, platform, mode, resolver type, session/store, and source policies.
- `ResolveSourceMeta`, gated by `apicaps:CapSourceMetaResolver`, resolves typed metadata for image, Git, and HTTP sources.
- `Solve`, gated by `apicaps:CapSolveBase`, asks the bridge to solve an LLB definition or nested frontend.
- `ReadFile`, `ReadDir`, and `StatFile`, gated by read/stat caps, inspect filesystem content behind refs.
- `Evaluate`, gated by `apicaps:CapGatewayEvaluate`, forces evaluation of a ref.
- `Ping`, `Return`, and `Inputs` provide liveness/capability discovery, final result/error reporting, and frontend input discovery.
- `NewContainer` and `ReleaseContainer` manage gateway execution containers.
- `ReadFileContainer`, `ReadDirContainer`, and `StatFileContainer`, gated by `apicaps:CapGatewayExecFilesystem`, inspect container-mounted filesystems.
- `Warn`, gated by `apicaps:CapGatewayWarnings`, emits structured source-linked warnings.

The only streaming RPC is `ExecProcess(stream ExecMessage) returns (stream ExecMessage)`, a bidirectional process-control and I/O stream.

Important message groups:

- Result messages: `Result`, `RefMapDeprecated`, `Ref`, `RefMap`, `Attestations`, `Attestation`, `AttestationKind`, `InTotoSubject`, and `InTotoSubjectKind`.
- Source resolution messages: `ResolveImageConfigRequest/Response`, `ResolveSourceMetaRequest/Response`, `ResolveSourceImageRequest/Response`, `ResolveSourceGitRequest/Response`, `ResolveSourceHTTPRequest/Response`, `AttestationChain`, `Blob`, `Descriptor`, `ChecksumRequest`, and `ChecksumResponse`.
- Solve messages: `SolveRequest`, `CacheOptionsEntry`, and `SolveResponse`.
- Filesystem messages: `ReadFileRequest`, `FileRange`, `ReadFileResponse`, `ReadDirRequest`, `ReadDirResponse`, `StatFileRequest`, and `StatFileResponse`.
- Execution messages: `NewContainerRequest/Response`, `ReleaseContainerRequest/Response`, `ExecMessage`, `InitMessage`, `ExitMessage`, `StartedMessage`, `DoneMessage`, `FdMessage`, `ResizeMessage`, and `SignalMessage`.
- Miscellaneous messages: `ReturnRequest/Response`, `InputsRequest/Response`, `EvaluateRequest/Response`, `PingRequest`, `PongResponse`, and `WarnRequest/Response`.

## Control Flow and Protocol Semantics

The schema defines protocol shape rather than implementation. Common flows implied by the messages are:

1. A frontend can call `Ping` to discover `FrontendAPICaps`, `LLBCaps`, and available `Workers`.
2. The frontend may call `Inputs` to retrieve named frontend input definitions.
3. It can call `ResolveImageConfig` or `ResolveSourceMeta` to normalize source metadata before constructing or solving LLB.
4. It calls `Solve` with an LLB `Definition`, nested `Frontend`, frontend options, cache imports, frontend input definitions, evaluation flag, and source policies.
5. The returned `SolveResponse` may expose a deprecated string ref or a structured `Result`; the result can carry refs, metadata, and attestations.
6. The frontend can inspect produced refs with `ReadFile`, `ReadDir`, `StatFile`, or trigger `Evaluate`.
7. For execution, the frontend creates a container, exchanges `ExecMessage` frames over `ExecProcess`, optionally inspects the container filesystem, then releases the container.
8. Completion is reported through `Return`, carrying either a result or a structured `google.rpc.Status` error.

The `ExecMessage` protocol is the most stateful: `InitMessage` starts a process; `FdMessage` is used in both directions for stdin/stdout/stderr bytes; `ResizeMessage` and `SignalMessage` carry terminal and signal events from client to server; `StartedMessage`, `ExitMessage`, and `DoneMessage` come from server to client. The schema explicitly notes that `FdMessage` may arrive after `ExitMessage`, and `DoneMessage` is the final message for a process.

## State and Persistence Behavior

The schema itself has no persistence, but it names durable or semi-durable concepts: refs, LLB definitions, image digests/config blobs, source checksums, cache import options, attestation chains, blob descriptors, container IDs, worker records, and diagnostic source ranges. Those values are interpreted and persisted by BuildKit subsystems outside this file.

Compatibility state is encoded in field numbering and comments. `Result` keeps deprecated non-array refs at fields 1 and 2, current structured refs at 3 and 4, metadata at 10, and attestations at 12, while field 11 is reserved by comment for an old attestation format. `SolveRequest` notes field 4 was removed in BuildKit v0.11.0, keeps result-return flags at 5 and 6, has a deprecated inline-return-related `Final` field at 10, and includes cache imports and frontend inputs behind capability comments.

## Dependencies and Integration Points

Imported schemas are central to the integration:

- `github.com/moby/buildkit/solver/pb/ops.proto` supplies `pb.Definition`, `pb.Platform`, `pb.SourceOp`, `pb.Mount`, `pb.Meta`, `pb.SecurityMode`, source ranges, network mode, worker constraints, host IPs, and secret env structures.
- `github.com/moby/buildkit/api/types/worker.proto` supplies worker records in `PongResponse`.
- `github.com/moby/buildkit/sourcepolicy/pb/policy.proto` supplies source policy controls in resolution and solve requests.
- `github.com/moby/buildkit/util/apicaps/pb/caps.proto` supplies advertised capability records.
- `github.com/tonistiigi/fsutil/types/stat.proto` supplies file stat responses.
- `google/protobuf/timestamp.proto` and `google/rpc/status.proto` supply HTTP timestamps and structured errors.

Generated siblings `gateway.pb.go` and `gateway_grpc.pb.go` are direct outputs of this schema. Handwritten BuildKit bridge implementations, frontend clients, and tests should treat this proto as the compatibility source of truth.

## Risks and Edge Cases

Wire compatibility is the main risk. Deprecated and removed fields show that older peers exist or existed; reusing field numbers, changing oneof membership, changing map value types, or renaming service methods would create interop problems.

Capability comments are not enforced by protobuf. Runtime client/server code must check API capabilities before relying on fields or methods such as source metadata, cache imports, frontend inputs, gateway evaluation, container filesystem access, and warnings.

Several messages carry unbounded bytes: image configs, exporter attrs, git object bytes, checksum suffixes, file data, warning details, process I/O, and blobs. The schema does not define limits, chunking, or validation; the gRPC layer and BuildKit implementation must enforce resource limits.

`ExecMessage` multiplexes multiple message variants and process IDs over one bidirectional stream. Implementations need a clear state machine for process start, I/O, exit, done, signals, EOF, and terminal resize events, including the documented case where file data arrives after exit.

Some field names intentionally use uppercase names in proto (`Ref`, `Definition`, `FrontendOpt`, `ContainerID`) while others use lower-case names (`digest`, `media_type`, `hostname`). Generated JSON and Go names reflect these choices, so clients relying on JSON/proto reflection should not assume uniform casing.

## Test Signals

Important validation signals include:

- Regenerate Go outputs from this proto and assert the generated files match the repository.
- Run protobuf compatibility checks when changing field numbers, oneofs, enum values, or service methods.
- Exercise all capability-gated RPCs with peers that both do and do not advertise the relevant caps.
- Test solve result compatibility across deprecated string refs, deprecated ref maps, current `Ref`, current `RefMap`, metadata, and attestations.
- Test source resolution for image, Git, and HTTP variants, including checksum algorithms and timestamps.
- Test `ExecProcess` bidirectional stream ordering, EOF, exit/error status, done finality, resize, signal handling, and multi-process `ProcessID` separation.
