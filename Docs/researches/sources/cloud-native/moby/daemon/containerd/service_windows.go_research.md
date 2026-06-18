<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_windows.go -->
# sources/cloud-native/moby/daemon/containerd/service_windows.go

Purpose: Windows implementation of layer-folder discovery for containerd snapshots.

Important APIs and flow: `GetLayerFolders` validates the RW layer, asserts it is the local `*rwLayer`, retrieves snapshot mounts, extracts Windows parent paths from the first mount with `GetParentPaths`, and returns parent paths plus the writable mount source.

State and persistence: read-only over snapshot mount metadata.

Dependencies and integration: used by Windows daemon paths that need the ordered layer folder list compatible with hcsshim runhcs logic. Depends on `rwLayer.mounts` and containerd mount helper behavior.

Risks: assumes at least one mount and that the first mount has Windows parent path metadata. Fails for unexpected layer implementations. Error messages include container ID context.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_windows.go -->
