# sources/cloud-native/containerd/internal/cri/server/container_image_mount.go

## Purpose
This file implements CRI image-volume mounts. It mutates CRI mount entries that reference an image into host bind mounts backed by unpacked image snapshots and cleans those snapshots when the sandbox is removed.

## Important APIs, Types, and Functions
Key functions are `mutateMounts`, `ensureLeaseExist`, `mutateImageMount`, `cleanupImageMounts`, and `ensureImageSubPath`. They use containerd images, leases, snapshot services, mount helpers, platform resolution, `identity.ChainID`, and CRI mount image fields.

## Control Flow, State, and Persistence
`mutateMounts` ensures a sandbox lease and calls `mutateImageMount` for each extra mount. Image mounts must have empty host path, be readonly, and specify an image. The code resolves and unpacks the image, prepares a snapshot at a sandbox/image-specific host path, mounts it, optionally validates a directory `ImageSubPath` with `os.OpenInRoot`, assigns `HostPath`, and clears UID/GID mappings after snapshot idmap options have been applied. Cleanup unmounts, removes snapshots, and deletes image-volume directories.

## Dependencies and Integration Points
It integrates CRI OCI volume source semantics, containerd image service, snapshotter selection, sandbox leases, platform-specific mount detection, Linux idmap snapshot labels, and sandbox cleanup.

## Risks and Test Signals
Risks include path traversal through subpaths, non-readonly image mounts, stale mounted snapshots, idmap double-application, lease loss, and cleanup impacting old pods. Linux snapshot option tests cover idmap label generation; subpath safety relies on `OpenInRoot`.
