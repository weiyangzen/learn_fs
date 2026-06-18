## sources/cloud-native/buildkit/solver/errdefs/compatibility.go

Purpose: typed error support for unsupported BuildKit compatibility-version features.

Important APIs/types/functions: init registers `CompatibilityFeature` with `typeurl`. `UnsupportedCompatibilityFeatureError` embeds the proto and wrapped error. `Error` formats `unsupported compatibility-version <version> feature <feature>` plus wrapped error text. `Unwrap` returns the cause. `ToProto` exposes the typed error payload. `NewUnsupportedCompatibilityFeatureError` constructs a standalone error. `CompatibilityFeature.WrapError` wraps an existing error with proto metadata.

Control flow: direct construction and formatting only.

State and persistence: type registration is global process state. Error proto can be serialized through BuildKit gRPC error utilities.

Dependencies and integration points: integrates with `grpcerrors.TypedErrorProto` and containerd typeurl for typed error propagation.

Risks and test signals: message formatting is part of user-facing diagnostics. Type URL string stability matters for remote clients. No direct tests in this subset.
