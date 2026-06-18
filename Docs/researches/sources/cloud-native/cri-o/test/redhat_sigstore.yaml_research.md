<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/redhat_sigstore.yaml -->
# sources/cloud-native/cri-o/test/redhat_sigstore.yaml

Purpose: short sigstore registry configuration fixture for Red Hat registry signature tests.

Important structure: maps `docker.registry.access.redhat.com` to the Red Hat hosted sigstore URL. It provides the external signature source that containers/image can use when checking Red Hat images.

State and integration: static YAML read by image-signature policy tooling. It has no local persistence. Risks are external URL availability and schema compatibility with the containers/image version under test. Test signal comes from policy/signature integration paths that load this file alongside policy fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/redhat_sigstore.yaml -->
