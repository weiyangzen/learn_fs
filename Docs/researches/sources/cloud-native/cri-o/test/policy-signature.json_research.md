<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy-signature.json -->
# sources/cloud-native/cri-o/test/policy-signature.json

Purpose: containers/image signature policy fixture for CRI-O tests that require a restrictive default and explicit sigstore trust for a signed CRI-O image.

Important structure: `default` rejects all images. Under `transports.docker`, `quay.io/crio/signed` is accepted only with `sigstoreSigned`, repository identity matching, a Fulcio issuer/email constraint, embedded CA data, and embedded Rekor public key data. `quay.io/crio/fedora-crio-ci` is explicitly allowed with `insecureAcceptAnything` so test infrastructure images can still pull.

State and integration: this is static policy input consumed by containers/image through CRI-O image pull verification paths. It persists no state. Risks are fixture drift as sigstore identities, embedded certificates, or test image names change; because the default is reject, missing transport entries will turn into pull failures. Test signal comes from image signature policy tests that copy or reference this policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy-signature.json -->
