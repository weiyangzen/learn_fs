<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.pb.go -->
# sources/cloud-native/containerd/api/types/descriptor.pb.go

## Purpose
Generated Go binding for the containerd `Descriptor` type, a simplified OCI-style content descriptor used to reference blobs in a content store.

## Important APIs and Types
`Descriptor` fields are `MediaType`, `Digest`, `Size`, and `Annotations map[string]string`. Generated methods provide protobuf reflection and nil-safe getters.

## Control Flow
No business logic. Initialization builds a descriptor with two message infos: `Descriptor` and its generated map entry.

## State and Persistence
The struct serializes content identity and metadata. It does not persist blobs itself; persistence is in content stores that interpret digest/size/media type.

## Dependencies and Integration Points
Depends on protobuf runtime/reflection. Used by task checkpoint responses, image/content APIs, and code that bridges containerd and OCI descriptor concepts.

## Risks
Digest and size are plain fields here; validation must happen elsewhere. Annotation map iteration order is nondeterministic unless deterministic marshaling is requested. Field number 4 is unused, so future schema work should avoid accidental incompatible reuse unless intentionally reserved by project policy.

## Test Signals
Round-trip descriptor serialization, OCI conversion tests, content-store validation tests for digest/size mismatch, and deterministic marshaling tests for annotations when needed.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.pb.go -->
