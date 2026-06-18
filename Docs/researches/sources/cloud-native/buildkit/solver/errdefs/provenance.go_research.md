<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance.go -->
## sources/cloud-native/buildkit/solver/errdefs/provenance.go

Purpose: carries structured details when provenance material capture is incomplete.

Important APIs and types: `ProvenanceMaterialsIncompleteError` embeds `*ProvenanceMaterialsIncomplete` and an underlying error, implements `Unwrap` and `ToProto`, and is produced by `(*ProvenanceMaterialsIncomplete).WrapError`, `WithProvenanceMaterialsIncomplete`, and `NewProvenanceMaterialsIncomplete`.

Control flow: constructors preserve nil-error behavior, build a `ProvenanceMaterialsIncomplete` detail containing individual `ProvenanceMaterialIncomplete` entries, and rely on grpcerrors/typeurl to serialize the detail.

State and dependencies: no persistent state. It depends on `typeurl`, BuildKit `grpcerrors`, generated vtproto methods, and `pkg/errors` for the default message.

Integration points: provenance capture code can report which source materials could not be verified, including operation, request name, method, URI/final URI, and reason.

Risks and test signals: the primary risk is losing detailed incomplete-material entries during error transport. `provenance_test.go` directly round-trips this error through gRPC and asserts the URI/reason and message survive.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance.go -->
