<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/imagespec.go -->
# sources/cloud-native/moby/daemon/containerd/imagespec.go

Purpose: converts between Moby internal `image.Image`/`container.Config` structures and Docker OCI image-spec structures used in the containerd content store.

Important APIs and flow: `dockerOciImageToDockerImagePartial` builds a Moby image from a Docker OCI image config without setting legacy container fields or details. `dockerImageToDockerOCIImage` converts a Moby image to Docker OCI image JSON. `containerConfigToDockerOCIImageConfig` maps user, env, entrypoint, cmd, volumes, workdir, labels, stop signal, args escaped, exposed ports, healthcheck, on-build, and shell. `dockerOCIImageConfigToContainerConfig` parses exposed port strings back to `network.Port` keys and reconstructs a `container.Config`.

State and persistence: pure conversion functions; persistence occurs when callers marshal/store config blobs.

Dependencies and integration: used by import, load/save/inspect-style conversion paths, Docker image spec, OCI image spec, Moby container/network API types, and internal image representation.

Risks: partial conversion intentionally omits legacy container metadata and details, so callers needing those fields must fill them separately. Invalid exposed port strings are silently skipped on OCI-to-container conversion. Slice/map cloning is partial and relies on struct assignment for nested values.

Test signals: `image_import_test.go` covers exposed-port string conversion; broader config field round-trip coverage is limited.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/imagespec.go -->
