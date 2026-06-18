<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/solve.go -->
## sources/cloud-native/buildkit/solver/errdefs/solve.go

Purpose: wraps solve-time errors with structured information about the failing op, subject, input ids, mount ids, and operation description.

Important APIs and types: `SolveError` embeds `*Solve` and `Err`, implements `Error`, `Unwrap`, and `ToProto`. `WithSolveError(err, subject, inputIDs, mountIDs)` builds the detail and pulls `Op`/`Description` from any nested `OpError`. `(*Solve).WrapError` recreates a wrapper from decoded proto details. `MarshalJSON` and `UnmarshalJSON` use `protojson`.

Control flow: caller-provided subject is an alias to generated oneof interface `IsSolve_Subject`, commonly `Solve_File` or `Solve_Cache`. Nil input error returns nil to preserve Go wrapping conventions.

State and dependencies: no persistence; the wrapper keeps protobuf fields and an error chain. Dependencies include `typeurl`, `solver/pb`, `grpcerrors`, and protobuf JSON.

Integration points: `SlowCacheError` and file action errors expose `ToSubject` so upper layers can attach precise solve subjects. gRPC transport uses `ToProto`.

Risks and test signals: risks include missing op context if `WithOp` was not applied, and JSON compatibility for oneof details. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/solve.go -->
