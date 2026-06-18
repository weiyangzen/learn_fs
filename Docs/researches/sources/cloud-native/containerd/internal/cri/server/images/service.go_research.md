
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service.go -->
# sources/cloud-native/containerd/internal/cri/server/images/service.go

## Purpose

This file defines the CRI image service core type, construction options, gRPC wrapper, runtime snapshotter mapping, local image resolution, and accessors for image and snapshot metadata.

## Important APIs, Types, and Functions

Important types are `imageClient`, `ImagePlatform`, `CRIImageService`, `GRPCCRIImageService`, and `CRIImageServiceOptions`. Key functions are `NewService`, `UpdateRuntimeSnapshotter`, `LocalResolve`, `RuntimeSnapshotter`, `GetImage`, `GetSnapshot`, `ImageFSPaths`, `Config`, and `GRPCService`.

## Control Flow

`NewService` creates an optional download semaphore from config, initializes the CRI image store, snapshot store, runtime platform mapping, transfer service, unpack keyed locker, and other dependencies, then starts a background snapshots syncer. `UpdateRuntimeSnapshotter` lazily initializes the runtime-platform map and adds a runtime mapping only when one does not already exist. `LocalResolve` treats valid digests as image IDs; otherwise it normalizes Docker references and resolves them through the in-memory image store, falling back to treating the input as an image ID. `RuntimeSnapshotter` returns the runtime override when set, otherwise the default image snapshotter.

## State and Persistence Behavior

The service owns in-memory image and snapshot stores, runtime-platform mappings, download limiter, and snapshot syncer. Persistent containerd image/content/snapshot state is accessed through injected stores and clients; this file initializes the wrappers but does not itself persist image metadata.

## Dependencies and Integration Points

Dependencies include containerd client image APIs, content/images/snapshot stores, transfer service, CRI config, CRI image and snapshot stores, keyed locks, semaphores, Docker reference parsing, digests, platform defaults, and CRI runtime API. It is the construction and dependency-injection hub for all files in `server/images`.

## Risks and Edge Cases

`NewService` assumes non-nil options fields that later methods require. `LocalResolve` silently returns empty string on parse/resolve errors before falling back to ID lookup, which can obscure why a reference failed. `UpdateRuntimeSnapshotter` intentionally does not override existing mappings. The snapshots syncer starts an untracked goroutine with no stop hook.

## Test Signals

Existing tests cover local resolution across many Docker reference forms and runtime snapshotter override behavior. Additional tests should cover service construction with nil dependencies, download limiter creation, runtime mapping non-overwrite behavior, and snapshot syncer interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/service.go -->
