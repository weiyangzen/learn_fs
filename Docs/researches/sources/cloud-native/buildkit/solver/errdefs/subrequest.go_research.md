<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/subrequest.go -->
## sources/cloud-native/buildkit/solver/errdefs/subrequest.go

Purpose: represents unsupported frontend/gateway subrequests as typed errors.

Important APIs and types: `UnsupportedSubrequestError` embeds `*Subrequest` and an optional cause. It implements `Error`, `Unwrap`, and `ToProto`; `NewUnsupportedSubrequestError(name)` and `(*Subrequest).WrapError` are constructors. `init` registers the detail type with `typeurl`.

Control flow: message construction mirrors frontend capability errors, with a base `unsupported request <name>` string plus optional cause text.

State and dependencies: no persistent state. It depends on BuildKit `grpcerrors` and containerd `typeurl`.

Integration points: gateway frontend request handling can return this when a client requests an unsupported subrequest, while preserving machine-readable request name.

Risks and test signals: low algorithmic risk; main contract is gRPC detail preservation. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/subrequest.go -->
