<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontend.go -->
## sources/cloud-native/buildkit/solver/errdefs/frontend.go

Purpose: defines typed frontend failure details that can wrap ordinary errors and survive gRPC conversion.

Important APIs and types: `FrontendError` embeds `*Frontend` plus an underlying `error`, implements `Error`, `Unwrap`, and `ToProto`, and is created through `(*Frontend).WrapError`. `Frontends(err)` walks nested `FrontendError` wrappers and returns cloned `Frontend` details in unwrap order. `init` registers the `Frontend` type with `typeurl`.

Control flow: `Error` deliberately avoids expanding message detail when an inner error exists, preventing deeply nested frontend wrappers from producing unwieldy strings. `Frontends` uses `errors.As`, recurses into `Unwrap`, then appends `CloneVT` of the current detail.

State and dependencies: no persistence; each wrapper stores the protobuf detail and underlying error. It depends on `containerd/typeurl` and BuildKit `grpcerrors` for typed error transport.

Integration points: used by frontends/gateway paths that need to label errors with frontend name/source and by gRPC conversion code that recognizes `TypedErrorProto`.

Risks and test signals: risks are mostly error-chain ordering and message bloat if `Error` changes. There is no direct test in this subset; generated vtproto and grpcerrors round-trip coverage for related errdefs provide indirect confidence.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/frontend.go -->
