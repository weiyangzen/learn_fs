# sources/cloud-native/buildkit/api/services/control/control.proto

## Purpose
Authoritative protobuf/gRPC contract for the BuildKit control plane. It describes how clients ask a BuildKit daemon to solve builds, stream progress, manage sessions, inspect/prune storage, list workers, query daemon info, and listen/update build history.

## APIs, Types, And Control Flow
Service `Control` defines unary RPCs `DiskUsage`, `Solve`, `ListWorkers`, `Info`, and `UpdateBuildHistory`; server-streaming RPCs `Prune`, `Status`, and `ListenBuildHistory`; and bidirectional streaming RPC `Session`. `SolveRequest` ties together LLB definitions, frontend settings, cache imports/exports, entitlements, source policy, multiple exporters, session IDs, compatibility version, and proxy network behavior. `StatusResponse` multiplexes vertex metadata, transfer/status updates, logs, and warnings. Build history messages model events, records, descriptors for logs/traces/errors, exporter responses, result descriptors, pinning, and step counts.

## Dependencies And Integration
Imports worker records, solver operation protobufs, source policy protobufs, timestamps, and `google.rpc.Status`. Generated outputs include `control.pb.go`, `control_grpc.pb.go`, and vtproto helpers. Clients in `client/*` and `cmd/buildctl/debug/*` consume this contract; servers implement it in the daemon control path.

## State, Risks, And Test Signals
Persistent/remote state includes cache records, build refs, sessions, build history records, log/trace descriptors, and worker metadata. API compatibility is the critical risk: field numbers must remain stable, deprecated fields must be honored for old clients, and streaming semantics must not regress. Test signals are proto lint, generated-file validation, compile, client integration tests, build history tests, and gRPC stream behavior.
