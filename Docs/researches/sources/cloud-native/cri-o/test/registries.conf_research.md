<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/registries.conf -->
# sources/cloud-native/cri-o/test/registries.conf

Purpose: registries configuration fixture for CRI-O tests that need deterministic unqualified image search and alias resolution.

Important structure: `unqualified-search-registries` is ordered as `quay.io`, `registry.access.redhat.com`, and `docker.io`. The `aliases` table maps `image-for-testing` to `registry.crio.test.com/repo`.

State and integration: read by containers/image/containers-common registry resolution when tests point CRI-O at this file. It stores no state. Risks include tests accidentally depending on network-accessible default registries or alias names colliding with newer defaults. Test signal is higher-level image resolution behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/registries.conf -->
