## sources/cloud-native/buildkit/solver/errdefs/context.go

Purpose: normalizes cancellation detection across Go context errors, gRPC status codes, and known stream EOF/canceled string cases.

Important APIs/types/functions: `IsCanceled(ctx, err)` returns true when `err` is `context.Canceled`, gRPC code is `Canceled`, or the context cause is canceled and the error string contains `EOF` or the cancellation text.

Control flow: checks strong typed conditions first, then handles a known gRPC/containerd behavior where a canceled stream followed by `Recv` may produce EOF or untyped concatenated strings.

State and persistence: none.

Dependencies and integration points: uses BuildKit `grpcerrors.Code` and gRPC `codes.Canceled`. Helps solver callers decide whether an error should be treated as cancellation rather than failure.

Risks and test signals: string matching can produce false positives if an unrelated error contains EOF after context cancellation, but the context-cause guard narrows it. No direct tests in this subset.
