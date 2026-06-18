<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_unix.go -->
# sources/cloud-native/moby/daemon/containerd/service_unix.go

Purpose: Unix/FreeBSD implementation placeholder for layer-folder introspection in the containerd image service.

Important APIs and flow: `GetLayerFolders` returns a Moby `NotImplemented` error on linux/freebsd.

State and persistence: none.

Dependencies and integration: satisfies daemon image-service interfaces for platforms where graphdriver layer folder paths are not exposed by this backend.

Risks: callers that need graphdriver-style layer folder paths must handle not-implemented when using the containerd store.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service_unix.go -->
