<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.pb.go -->
# sources/cloud-native/buildkit/session/secrets/secrets.pb.go

Purpose: generated protobuf message definitions for the Secrets session service.

Important APIs, types, and functions: defines `GetSecretRequest` with `ID` and `Annotations`, `GetSecretResponse` with `Data`, standard protobuf methods/getters, descriptor compression, map-entry metadata, and file initialization.

Control flow and state: generated descriptor initialization plus per-message protobuf state.

Dependencies and integration: generated from `secrets.proto`, used by handwritten secret client/provider code and gRPC stubs.

Risks and test signals: field numbers and map semantics are wire contracts. Generated file should not be edited. Test through secretsprovider behavior and protobuf round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.pb.go -->
