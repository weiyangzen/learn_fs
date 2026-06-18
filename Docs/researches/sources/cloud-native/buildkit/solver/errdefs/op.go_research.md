<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/op.go -->
## sources/cloud-native/buildkit/solver/errdefs/op.go

Purpose: attaches the protobuf operation and human-readable operation description to errors so later solve-level wrappers can include op context.

Important APIs and types: `OpError` stores an underlying `error`, `*pb.Op`, and description map. `WithOp(err, anyOp, opDesc)` wraps only when `err` is non-nil and `anyOp` is actually `*pb.Op`.

Control flow: callers defer wrapping around cache map, exec, or slow-cache paths. `WithSolveError` later uses `errors.As` to recover `OpError` details and put them into the `Solve` typed detail.

State and dependencies: no persistence; the wrapper retains the original op pointer and map. It depends on `solver/pb`.

Integration points: `solver/jobs.go` calls `errdefs.WithOp` in shared op error paths, and `solve.go` consumes the result.

Risks and test signals: because the op pointer is retained, mutation after wrapping could affect details. Passing a non-`*pb.Op` silently returns the original error, which is intentional but can hide context if callers use the wrong value.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/op.go -->
