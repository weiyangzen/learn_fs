# sources/cloud-native/moby/daemon/migration.go

## Purpose
This file migrates older persisted container platform/OS metadata into `Container.ImagePlatform`, using image manifests, content store config blobs, image service metadata, and host defaults as fallbacks.

## Important APIs, Types, And Functions
`migrateContainerOS` updates a container in place. `deduceContainerPlatform` returns the best platform or an aggregated error. `platformReader` abstracts platform lookup. `daemonPlatformReader` implements it with `ImageService` and containerd `content.Provider`.

## Control Flow
For pre-OS containers with no deprecated `OS` and no `ImageManifest`, the default host platform is returned. If `ImageManifest.Platform` is set, it wins. Otherwise the manifest blob is read, its config descriptor is read, and the config is unmarshaled as an OCI platform. If that fails or is malformed, the image service is queried by `ImageID`. If all paths fail, errors are joined and wrapped. `migrateContainerOS` logs a warning and preserves the deprecated OS value as `ImagePlatform.OS` on failure.

## State, Persistence, And Dependencies
The function mutates only the in-memory container; persistence occurs later through normal container checkpointing. Dependencies include containerd content reads, OCI image descriptors/manifests, Docker image service, `platforms.DefaultSpec`, and internal multierror aggregation.

## Integration Points
This migration supports daemon restore across image store formats, graphdriver/containerd image store differences, and legacy containers created before platform metadata existed.

## Risks And Edge Cases
If an image ID points to a multi-platform image index rather than a platform-specific manifest, fallback lookup may choose a host-preferred platform rather than the original platform. Missing content store support returns an error for manifest-based deduction. Malformed config with missing OS or architecture is treated as invalid.

## Test Signals
`migration_test.go` covers graphdriver nil manifests, pre-OS defaulting, Linux/Windows image IDs, missing images, containerd manifest lookup, fallback to image ID, and priority of `ImageManifest` over `ImageID`.
