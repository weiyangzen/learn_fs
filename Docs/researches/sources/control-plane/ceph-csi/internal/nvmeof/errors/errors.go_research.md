# sources/control-plane/ceph-csi/internal/nvmeof/errors/errors.go

Purpose: Centralizes NVMe-oF-specific sentinel errors and maps them to gRPC status codes.

Important APIs/types/functions: Exports `ErrRbdQoSExists`, `ErrMetadataNotFound`, `ErrMetadataCorrupted`, `errorToGRPCCode`, and `ToGRPCError`.

Control flow: `ToGRPCError` returns nil for nil input, checks `errors.Is` against known sentinels, and returns mapped `status.Error`. Unknown errors become `codes.Internal`.

State and persistence behavior: No persistent state. The package is a pure error classification layer.

Dependencies and integration points: Used by controller metadata retrieval, QoS modification, and unpublish/delete error handling. Depends on gRPC `codes/status` and Go `errors`.

Risks: The map uses error values as keys and iteration order is undefined, though the current sentinels are distinct. New sentinel errors need explicit mapping or they degrade to Internal.

Test signals: No direct tests, but controller paths use these conversions for NotFound, Internal, and InvalidArgument status behavior.
