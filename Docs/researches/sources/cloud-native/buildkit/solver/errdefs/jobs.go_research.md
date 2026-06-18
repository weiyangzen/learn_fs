<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/jobs.go -->
## sources/cloud-native/buildkit/solver/errdefs/jobs.go

Purpose: provides a solver-level typed error for missing jobs.

Important APIs and types: `UnknownJobError` stores a job id, implements `Code() codes.Code` returning `codes.NotFound`, and formats `no such job <id>`. `NewUnknownJobError(id)` is the public constructor.

Control flow: there is no complex flow; the solver job registry constructs this error from `Solver.Get` after waiting for a job id and timing out.

State and dependencies: only the missing id is stored. The dependency on `google.golang.org/grpc/codes` lets BuildKit's error conversion map the error to `NotFound`.

Integration points: `solver/jobs.go` uses this in `Solver.Get` when a requested job never appears within the bounded wait.

Risks and test signals: behavior is simple, but the gRPC code is semantically important for clients. No direct unit test in this subset; job lifecycle integration tests exercise jobs broadly, not this exact timeout path.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/jobs.go -->
