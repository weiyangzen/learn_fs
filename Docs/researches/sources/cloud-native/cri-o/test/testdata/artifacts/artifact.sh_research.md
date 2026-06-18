<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/artifact.sh -->
# sources/cloud-native/cri-o/test/testdata/artifacts/artifact.sh

Purpose: tiny executable OCI artifact payload fixture.

Important behavior: shell script prints a fixed greeting. It is pushed by the artifact helper as an executable-like test artifact, letting tests verify artifact retrieval and execution/payload handling separate from image layers.

State and integration: static file consumed by `push-oci-artifacts` and registry artifact tests. It persists no state. Risks are only file mode/content drift if tests expect exact output. Test signal is artifact pull/use behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/artifact.sh -->
