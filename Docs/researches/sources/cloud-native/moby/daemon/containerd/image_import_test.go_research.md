<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import_test.go -->
# sources/cloud-native/moby/daemon/containerd/image_import_test.go

Purpose: regression coverage for Docker container config to Docker OCI image config conversion, which import uses after applying Dockerfile-style changes.

Important APIs and flow: `TestContainerConfigToDockerImageConfig` builds a `container.Config` with `ExposedPorts`, calls `containerConfigToDockerOCIImageConfig`, and asserts that the OCI config uses string keys such as `80/tcp`.

State and persistence: no persistent state; the test is pure conversion logic.

Dependencies and integration: uses Moby API container/network types and `gotest.tools` assertions. It protects the conversion in `imagespec.go`, not just import, because the helper is shared by image creation/conversion paths.

Risks and gaps: this only covers exposed-port formatting. It does not cover import archive compression, history/comment fields, labels, healthcheck, shell, on-build, or unpack behavior.

Test signals: references the historical regression for Moby issue 45904.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_import_test.go -->
