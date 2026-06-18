# sources/cloud-native/containerd/integration/runtime_handler_unpack_labels_linux_test.go

## Purpose

`runtime_handler_unpack_labels_linux_test.go` verifies that creating a container with a runtime handler using a different snapshotter triggers unpack into that snapshotter and applies image-related snapshot labels.

## Important APIs, Types, and Functions

- `TestRuntimeHandlerUnpackWithSnapshotLabels` starts an isolated daemon with overlayfs as default and erofs as a second runtime snapshotter.
- It uses containerd introspection to check erofs plugin availability, CRI image pull, containerd image rootfs chain IDs, and erofs snapshot service `Stat`.

## Control Flow

The test writes a v3 config enabling snapshot annotations, starts a daemon, skips if erofs is absent/not ready, pulls nginx, computes chain IDs, creates an overlay sandbox, asserts erofs snapshots do not exist, creates an erofs sandbox/container, then asserts each erofs snapshot has target ref, manifest digest, layer digest, and image layer labels.

## State and Persistence Behavior

The important persisted state is snapshotter metadata and labels in the erofs snapshot service. The test also verifies CRI sandbox runtime handler state and container created state.

## Dependencies and Integration Points

It integrates CRI runtime/image services, containerd client image and snapshot APIs, plugin introspection, OCI image identity chain IDs, snapshotter label constants, and the erofs snapshotter plugin.

## Risks and Edge Cases

The test is skipped when erofs is not registered or fails plugin init. It assumes overlayfs image pull does not pre-unpack erofs snapshots and that snapshot labels are available when `disable_snapshot_annotations=false`.

## Test Signals

Failures indicate runtime-handler-specific unpack selection or snapshot annotation propagation regressions.
