# sources/cloud-native/buildkit/solver/pb/platform.go

## Purpose
This file adapts the generated solver protobuf `Platform` type to and from the OCI image-spec `ocispecs.Platform` structure. It is a small boundary layer used by source identifiers and solver metadata code that need to carry platform data through protobuf APIs without leaking protobuf-specific structs into containerd/OpenContainers helper calls.

## Important APIs
`(*Platform).Spec()` converts protobuf fields into `ocispecs.Platform`. `PlatformFromSpec` performs the reverse conversion. `ToSpecPlatforms` and `PlatformsFromSpec` map slices in both directions. `OSFeatures` is cloned with `slices.Clone` when present, which prevents callers from accidentally sharing mutable slice backing arrays between protobuf and OCI representations.

## Control Flow
All functions are straight conversions. The slice functions preallocate output to the input length and call the scalar conversion for each element. No validation or normalization is performed here; callers are expected to pass already-valid platform data.

## State and Persistence
The file has no persistent state. Its main state behavior is alias avoidance for `OSFeatures`, preserving value semantics across conversion boundaries.

## Dependencies and Integration Points
It depends only on Go `slices` and `github.com/opencontainers/image-spec/specs-go/v1`. It is used by source resolution code such as container image and blob identifiers when converting frontend/platform metadata into OCI platform structs.

## Risks
`Spec()` assumes the receiver is non-nil; a nil `*Platform` would panic. The conversions also intentionally omit any future fields not represented in the protobuf type, so schema drift must be handled when platform definitions evolve.

## Test Signals
No direct tests are in this subset. Coverage is indirect through source identifier and image pull tests that pass platform constraints into image resolution.
