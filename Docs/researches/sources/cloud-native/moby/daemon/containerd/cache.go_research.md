# sources/cloud-native/moby/daemon/containerd/cache.go

## Purpose
Adapts the containerd-backed image service to Docker's classic builder image cache interface. It resolves images, parent/child metadata, locally built markers, and creates cached images using containerd content and image labels.

## Important APIs, Types, And Functions
- `ImageService.MakeImageCache` constructs a `cache.New` instance with `cacheAdaptor`.
- `cacheAdaptor.Get`, `GetByRef`, `SetParent`, `GetParent`, `Create`, `IsBuiltLocally`, and `Children` implement builder cache storage.
- `findContentByUncompressedDigest` locates a compressed content blob by the `containerd.io/uncompressed` label.

## Control Flow
`Get` loads the Docker image view, then walks image manifests looking for a config blob label that references stored classic `ContainerConfig` content. Parent labels are written to all references sharing a target digest. `Create` marshals target image config, resolves an optional extra layer's compressed digest, calls `CreateImage`, and returns the resulting image ID. Children are found through parent labels or from-scratch labels.

## State And Persistence
Persists classic builder metadata as containerd image labels (`org.mobyproject.image.parent`, `fromscratch`, and `containerconfig`) and content labels referencing stored container configs. It does not manage cache eviction itself.

## Dependencies And Integration Points
Depends on containerd image/content stores, daemon internal image/cache interfaces, layer DiffIDs, Moby multierror, and OCI descriptors. It integrates legacy Dockerfile builder cache behavior with the containerd image store.

## Risks And Edge Cases
Missing or malformed config labels are logged and skipped, so cache reads may silently lose `ContainerConfig`. `SetParent` updates every image sharing a target and can partially fail; errors are joined. `findContentByUncompressedDigest` walks labels and returns not found if differ output lacks expected metadata.

## Test Signals
No direct tests in this subset. Related builder and image tests should verify cache hits, parent links, from-scratch children, and locally-built image detection.
