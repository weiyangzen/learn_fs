<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.proto -->
# sources/cloud-native/buildkit/session/secrets/secrets.proto

Purpose: protobuf contract for retrieving secrets over a BuildKit session.

Important APIs, types, and functions: package `moby.buildkit.secrets.v1`, Go package `github.com/moby/buildkit/session/secrets`. Service `Secrets` exposes unary `GetSecret`. Request includes `ID` and annotations map. Response includes secret `data` bytes.

Control flow and state: schema only; runtime state lives in provider stores and RPC messages.

Dependencies and integration: drives generated Go, gRPC, and vtproto code. Used by Dockerfile secret mounts and secret providers.

Risks and test signals: annotations are in schema but not used by the simple provider. Compatibility requires stable field numbers. Test with generated code and provider integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets.proto -->
