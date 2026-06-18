<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/cni.json -->
# sources/cloud-native/buildkit/hack/fixtures/cni.json

Purpose: CNI bridge network fixture for BuildKit tests that need a deterministic CNI configuration.

Important APIs, types, and functions: CNI version `1.0.0`, network name `buildkit`, bridge plugin, bridge `buildkit0`, default gateway, IP masquerade, hairpin mode, and host-local IPAM range `10.10.0.0/16`.

Control flow and state: declarative CNI config. Runtime state is created by CNI plugins when tests use the fixture.

Dependencies and integration: depends on standard CNI bridge and host-local plugins. Used by test harnesses that point BuildKit worker networking at fixture config.

Risks and test signals: bridge name and subnet can conflict with host networking. Tests should verify setup and teardown under privileged CI environments.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/hack/fixtures/cni.json -->
