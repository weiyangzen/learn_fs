<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/grpc.go -->
# sources/cloud-native/cri-o/utils/errdefs/grpc.go

Purpose: converts local error classes to and from gRPC status errors.

Important APIs and flow: `ToGRPC` maps known sentinel classes to corresponding gRPC codes, preserves errors that are already gRPC statuses, and returns unmapped errors unchanged. `ToGRPCf` wraps an existing class with formatted context before mapping. `FromGRPC` maps status codes back to sentinel classes and rebases duplicate messages with `rebaseMessage`; unknown codes become `ErrUnknown`.

State and integration: stateless conversion layer between server-side CRI-O errors and gRPC clients. Risks include `status.FromError` treating non-status errors as unknown in helper paths, `FromGRPC` converting every unknown into `ErrUnknown`, and message rebasing relying on string suffixes. Test signal is indirect unless higher-level API tests check status codes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/grpc.go -->
