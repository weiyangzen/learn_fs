<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontendcap.go -->
## sources/cloud-native/buildkit/solver/errdefs/frontendcap.go

Purpose: represents an unsupported frontend capability as a typed error payload.

Important APIs and types: `UnsupportedFrontendCapError` wraps `*FrontendCap` and an optional cause. It implements `Error`, `Unwrap`, and `ToProto`; `NewUnsupportedFrontendCapError(name)` creates a cause-free error; `(*FrontendCap).WrapError` attaches a cause. `init` registers the proto detail type.

Control flow: `Error` starts with `unsupported frontend capability <name>` and appends the wrapped error text when present. gRPC detail export is through `ToProto`.

State and dependencies: no persistent state. The wrapper owns only the `FrontendCap` detail and error chain. Dependencies are `typeurl` registration and BuildKit `grpcerrors`.

Integration points: consumed by frontend capability validation and clients that need to distinguish unsupported capability failures from generic solve failures.

Risks and test signals: risks are string compatibility for clients that inspect messages and preservation of typed detail across gRPC. No direct test appears in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontendcap.go -->
