<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/unrestrictive.json -->
# sources/cloud-native/cri-o/test/testdata/policies/unrestrictive.json

Purpose: unrestrictive policy fixture under `testdata/policies`, duplicating the top-level permissive policy shape for tests that load policy directories.

Important structure: default accepts anything, but `docker-daemon` rejects `quay.io/crio/hello-world` and requires Red Hat GPG signature material for `registry.access.redhat.com`.

State and integration: static containers/image policy file. It has no persistence. Risks include duplicate drift with `test/policy.json`, large embedded key data, and transport-specific behavior surprising tests that use `docker` rather than `docker-daemon`. Test signal is targeted pull/signature-policy tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/policies/unrestrictive.json -->
