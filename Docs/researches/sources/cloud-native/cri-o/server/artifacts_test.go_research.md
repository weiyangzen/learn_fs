# sources/cloud-native/cri-o/server/artifacts_test.go

This server test file verifies `server.FilterMountPathsBySubPath`, which filters OCI artifact blob mount paths by a requested subpath. The tests construct a fixed list of `libartifact` blob mount paths and assert behavior for empty subpath, a directory subpath, `"."`, `"./"`-prefixed subpath, and a non-existing subpath.

State is local test data only. The expected control flow is that empty or dot subpaths return the original path list, directory filtering strips the requested directory prefix from returned names, and missing subpaths produce an error with nil result. Dependencies are Ginkgo/Gomega, context, `go.podman.io/common/pkg/libartifact/types`, and the server package.

Integration signal is important for OCI artifact mount support because CRI-O must mount only the requested subpath while preserving relative paths inside the container. Risks not shown include path traversal, Windows path separators, duplicate names, and behavior with files that share prefixes but are not children. This file tests behavior, not the implementation location.
