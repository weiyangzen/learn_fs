## sources/cloud-native/buildkit/util/grpcerrors/grpcerrors.go

Purpose: converts BuildKit errors to/from gRPC status errors while preserving status codes, stack traces, typed error details, unknown protobuf details, and contextual messages.

Important APIs/types: `TypedError` and `TypedErrorProto` contracts; `ToGRPC(ctx,err)`, `FromGRPC(err)`, `Code(err)`, `WrapCode(err,code)`, `AsGRPCStatus(err)`. Internal wrappers include `grpcStatusError`, `withCodeError`, and unwrap interfaces.

Control flow: `ToGRPC` starts from existing status or `status.New(Code(err), err.Error())`, fixes mismatched codes, expands status message when outer error has more context, collects stack traces and typed errors through all single/multi unwraps, and adds details as JSON-encoded `Any` values using containerd `typeurl`. `Code` prioritizes internal/resource-exhausted BuildKit errdefs, explicit `Code`, `GRPCStatus`, unwrap chains, joined errors, and context errors. `FromGRPC` decodes status details, splits stack and typed detail protos from unknown details, rebuilds a `grpcStatusError`, wraps stacks, applies typed `WrapError`, and enables stack handling.

State/persistence: no persistence; transforms error object graphs. Dependencies: gRPC status/codes, protobuf Any, containerd typeurl, BuildKit errdefs/stack/logging.

Integration points: server/client interceptors and APIs returning rich BuildKit errors. Risks: typed details must be registered with typeurl; joined errors pick the first non-OK/non-Unknown code; details are JSON-marshaled into Any values rather than binary proto wire format. Test signals: `grpcerrors_test.go` covers unknown-detail preservation, typed error preservation, code/status extraction, context mapping, and contextual message retention.
