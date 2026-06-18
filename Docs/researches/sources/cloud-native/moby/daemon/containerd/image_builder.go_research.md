# sources/cloud-native/moby/daemon/containerd/image_builder.go

## Purpose
Bridges Docker's classic builder layer/cache API to containerd images, content, snapshots, leases, and OCI manifests.

## Important APIs, Types, And Functions
- `GetImageAndReleasableLayer`, `pullForBuilder`, and `newROLayerForImage` resolve or pull builder base images and create read-only layer handles.
- `createLease`, `rolayer`, `rwlayer`, `NewRWLayer`, `Commit`, and `Release` manage temporary snapshots and leases.
- `CreateImage`, `createImageOCI`, `writeContentsForImage`, and `saveContainerConfig` create containerd images and content from Docker image configs and layer descriptors.
- Constants define classic builder image/content labels.

## Control Flow
Builder base resolution handles `FROM scratch`, local images unless force-pull is requested, and fallback pulls with auth/platform options. RO layer creation reads image config/rootfs diff IDs and leases the snapshot chain. RW layer creation prepares a snapshot, mounts it in a temp dir, commits it through containerd differ output, extracts diff ID labels, and returns a new RO layer. Image creation writes manifest/config/container-config blobs with GC labels, creates or replaces a dangling containerd image, logs create events, and unpacks it.

## State And Persistence
Creates leases, snapshots, content blobs, image records, dangling image names, parent labels, from-scratch labels, and container-config content labels. Temp mount directories and leases are released on `Release` or error cleanup.

## Dependencies And Integration Points
Depends on containerd client/snapshotter/differ/content/leases, OCI image-spec identity, Docker image-spec conversion, registry pull support, builder interfaces, archive empty-diff checks, events, and stream progress output. It is the core compatibility path for legacy Dockerfile build with containerd image store.

## Risks And Edge Cases
Every `GetImageAndReleasableLayer` caller must release returned layers to avoid lease leaks. Snapshot commit handles `AlreadyExists`, but mount/unmount failures can leave temp dirs or snapshots if cleanup fails. Empty diff handling avoids adding layers, so history and rootfs diff ID logic must stay aligned. Windows rejects `FROM scratch` in this path.

## Test Signals
No direct tests in this subset. Builder integration tests should cover local base reuse, forced pulls, platform mismatch warnings, RW layer commit/release, empty layer creation, parent labels, and unpack failures.
