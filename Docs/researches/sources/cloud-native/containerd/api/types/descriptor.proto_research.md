<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.proto -->
# sources/cloud-native/containerd/api/types/descriptor.proto

## Purpose
Canonical proto definition of `containerd.types.Descriptor`, used to identify content-store blobs and OCI descriptor-like references.

## Important APIs and Types
`Descriptor` includes `media_type`, `digest`, `size`, and annotation map field number 5.

## Control Flow
No control flow. This is a schema-only file.

## State and Persistence
The message carries persistent content identity metadata. Actual blob storage, verification, and garbage collection live in content store implementations.

## Dependencies and Integration Points
No proto imports. The Go package is `github.com/containerd/containerd/api/types;types`. It integrates with OCI image spec descriptor concepts and containerd checkpoint/content APIs.

## Risks
Changing field numbers or semantics would break wire compatibility and stored metadata. Digest strings require validation outside the schema.

## Test Signals
Schema compatibility checks, generated-code checks, and conversion tests to/from OCI descriptors.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/descriptor.proto -->
