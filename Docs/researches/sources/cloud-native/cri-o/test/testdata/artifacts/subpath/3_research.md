<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/3 -->
# sources/cloud-native/cri-o/test/testdata/artifacts/subpath/3

Purpose: companion text payload for subpath OCI artifact tests.

Important behavior: contains the text value `3`, pushed as `subpath/3:text/plain`. Together with `subpath/2`, it verifies multi-entry subpath handling.

State and integration: static payload, no persistence. Risks are exact-content dependencies and stale remote artifacts. Test signal is artifact pull/extract behavior that checks multiple named payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/artifacts/subpath/3 -->
