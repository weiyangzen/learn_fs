<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/errors.go -->
# sources/cloud-native/cri-o/utils/errdefs/errors.go

Purpose: local copy/adaptation of containerd-style error classes for CRI-O utility code.

Important APIs: exported sentinel errors `ErrInvalidArgument`, `ErrNotFound`, `ErrAlreadyExists`, `ErrFailedPrecondition`, `ErrUnavailable`, and `ErrNotImplemented`, plus predicate functions using `errors.Is`. `ErrUnknown` is used internally for unmapped conversions.

State and integration: no runtime state; callers wrap these sentinels to communicate error class across package and gRPC boundaries. Risks include diverging from upstream containerd semantics and losing class information if callers format errors without wrapping. Test signal is mostly through gRPC conversion behavior in `grpc.go` consumers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/utils/errdefs/errors.go -->
