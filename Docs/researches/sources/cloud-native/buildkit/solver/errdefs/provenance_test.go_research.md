<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance_test.go -->
## sources/cloud-native/buildkit/solver/errdefs/provenance_test.go

Purpose: verifies that provenance-incomplete typed errors survive BuildKit's gRPC error conversion path.

Important APIs and types: `TestProvenanceMaterialsIncompleteRoundTrip` constructs `NewProvenanceMaterialsIncomplete`, converts with `grpcerrors.ToGRPC` and `grpcerrors.FromGRPC`, then uses `require.ErrorAs` for `*ProvenanceMaterialsIncompleteError`.

Control flow: the test creates one incomplete material with operation digest, command-like name, method, URI, and reason. After round-trip, it validates the entry count, selected fields, and human message.

State and dependencies: test-only, no persistence. It depends on `testing`, BuildKit `grpcerrors`, and testify `require`.

Integration points: protects the contract used by provenance reporting, clients, and any middle layer that forwards BuildKit errors through gRPC status details.

Risks and test signals: strong signal for typeurl registration and vtproto serialization of this specific detail. It does not cover multiple entries, `FinalUri`, or nested wrapping depth.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/provenance_test.go -->
