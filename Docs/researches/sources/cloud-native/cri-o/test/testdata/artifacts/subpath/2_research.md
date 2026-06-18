<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/2 -->
# sources/cloud-native/cri-o/test/testdata/artifacts/subpath/2

Purpose: small text payload used as a subpath OCI artifact fixture.

Important behavior: contains the text value `2`, pushed by `push-oci-artifacts` as `subpath/2:text/plain`. It lets tests verify that artifact entries preserve subpath names and simple content.

State and integration: static payload, no persistence. Risks are exact-content expectations and registry artifact drift after publishing. Test signal is artifact extraction/path validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/2 -->
