<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_idmapped_linux_test.go -->
# sources/cloud-native/containerd/integration/client/container_idmapped_linux_test.go

## Purpose
Tests Linux overlayfs idmapped snapshot behavior for single ID maps, multi-range ID maps, and parallel unpack. It verifies that remapped overlay snapshots expose expected host ownership and hide implementation lower directories from direct host paths.

## APIs, Types, And Functions
The file contains `TestIDMappedOverlay`. It uses `overlayutils.SupportsIDMappedMounts`, `userns.IDMap`, `containerd.WithRemapperLabels`, `containerd.WithUserNSRemapperLabels`, `containerd.WithUnpackLimiter`, `WithNewSnapshot`, `oci.WithUserNamespace`, snapshot `Mounts`, and OCI ID mappings.

## Control Flow And State
The test skips unless overlayfs idmapped mounts are supported. Each table case pulls `testMultiLayeredImage` with unpack, creates a container using the overlayfs snapshotter and user namespace mapping, reads the snapshot mount options, rejects host-visible lowerdir paths, stats the overlay upperdir, and checks the upperdir UID/GID against the expected host mapping. Cleanup deletes the container snapshot and test image synchronously.

## Persistence And Integration Points
State is persisted in the overlayfs snapshotter, image service, content store, and snapshot labels that encode remapping metadata. The test integrates the client API, image unpacking, snapshot mount materialization, kernel overlayfs idmapped support, and container spec user namespaces.

## Risks And Test Signals
The test is kernel- and filesystem-dependent and will skip on hosts lacking idmapped overlay mounts. A failure signals broken snapshot label translation, unsafe lowerdir exposure, incorrect multi-map handling, or parallel unpack races affecting idmapped ownership.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/container_idmapped_linux_test.go -->
