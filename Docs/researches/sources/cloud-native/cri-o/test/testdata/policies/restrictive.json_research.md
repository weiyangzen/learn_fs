<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/restrictive.json -->
# sources/cloud-native/cri-o/test/testdata/policies/restrictive.json

Purpose: restrictive policy fixture under testdata mirroring the top-level signature policy.

Important structure: default reject; Docker transport allows `quay.io/crio/signed` through sigstore verification with Fulcio issuer/email and Rekor key data; allows `quay.io/crio/fedora-crio-ci` insecurely for test infrastructure.

State and integration: static input for tests that need policy files in a `testdata/policies` tree. It persists no state. Risks are duplicate-fixture drift versus the top-level `policy-signature.json`, embedded key/certificate expiry or identity changes, and strict default rejection causing unrelated image pulls to fail. Test signal is image policy acceptance/rejection behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/restrictive.json -->
