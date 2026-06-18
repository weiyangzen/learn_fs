<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/push-oci-artifacts -->
# sources/cloud-native/cri-o/test/testdata/artifacts/push-oci-artifacts

Purpose: helper script to publish OCI artifact test fixtures to `quay.io/crio/artifact`.

Important flow: requires `oras`, changes into `test/testdata/artifacts`, and pushes tags for a single file, executable script, multiple files, and subpath entries with `application/x.test.test.test.v1` artifact type.

State and integration: writes remote registry artifacts; it assumes credentials and network access when used manually or in maintenance. Risks include wrong working directory if invoked outside repository layout, registry tag mutation, and missing `oras`. Test signal is indirect: CRI-O tests consume the pushed artifact tags.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/push-oci-artifacts -->
