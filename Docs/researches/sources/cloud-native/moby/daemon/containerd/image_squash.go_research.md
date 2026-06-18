<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_squash.go -->
# sources/cloud-native/moby/daemon/containerd/image_squash.go

Purpose: placeholder for Docker image squash support in the containerd image service.

Important APIs and flow: `SquashImage(id, parent)` immediately returns a Moby `NotImplemented` error.

State and persistence: none.

Dependencies and integration: satisfies daemon image-service interface expectations while signaling that squash is unavailable for the containerd backend.

Risks: callers expecting legacy graphdriver squash support must handle `NotImplemented`. There is no migration or compatibility shim here.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_squash.go -->
