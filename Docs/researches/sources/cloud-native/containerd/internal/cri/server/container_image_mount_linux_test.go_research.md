# sources/cloud-native/containerd/internal/cri/server/container_image_mount_linux_test.go

## Purpose
This Linux-only test file validates snapshot option generation for image-volume mounts under user namespaces.

## Important APIs, Types, and Functions
`TestGetImageVolumeSnapshotOpts` covers `getImageVolumeSnapshotOpts`; `optsToInfo` applies returned `snapshots.Opt` values into a `snapshots.Info` for label comparison.

## Control Flow, State, and Persistence
The test constructs CRI `runtime.Mount` values with UID/GID mapping combinations, invokes the helper, and compares generated remapper labels. It also confirms the helper does not clear mappings on the mount object, because clearing is the responsibility of `mutateImageMount` after snapshot preparation.

## Dependencies and Integration Points
It depends on `containerd.WithRemapperLabels`, snapshot info labels, CRI ID mappings, and Linux build tags. It protects the image-volume/userns integration path.

## Risks and Test Signals
Risks include accepting unsupported multi-line idmaps, dropping mappings too early, or failing to idmap image volumes. Signals are exact label equality and expected errors for multiple UID mapping lines.
