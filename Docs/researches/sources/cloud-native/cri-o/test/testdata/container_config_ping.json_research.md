<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config_ping.json -->
# sources/cloud-native/cri-o/test/testdata/container_config_ping.json

Purpose: privileged long-running container config fixture for network-oriented tests.

Important structure: same Fedora CI image and common env/labels as the baseline config, but command is `/bin/sleep` with `+Inf`, `privileged` is set, and the Linux resource/security fields mirror the baseline root container. The name remains `container1`.

State and integration: static CRI request body for tests that need a persistent privileged container, commonly to exec networking commands. Risks include CRI schema compatibility for the top-level `privileged` field, host policy rejecting privileged containers, and infinite sleep behavior depending on coreutils. Test signal is higher-level ping/network tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/testdata/container_config_ping.json -->
