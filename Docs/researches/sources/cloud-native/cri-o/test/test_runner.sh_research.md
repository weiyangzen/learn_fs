<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/test_runner.sh -->
# sources/cloud-native/cri-o/test/test_runner.sh

Purpose: Bats test entrypoint for CRI-O integration tests.

Important flow: enables Go coverage output directory if `GOCOVERDIR` is set, changes into the test directory, optionally exports user namespace UID/GID mappings when `TEST_USERNS=1`, raises `/proc/sys/user/max_user_namespaces` when writable, preloads images via `common.sh get_images`, chooses test arguments or `critest.bats` when `RUN_CRITEST=1`, sets parallel `JOBS`, enables one Bats retry, and runs non-serial tests in parallel followed by serial-tagged tests.

State and integration: mutates process environment and may write a sysctl in privileged CI. It depends on Bats, common CRI-O test helpers, image preloading, and tag discipline. Risks include `set -xe` leaking command details, host sysctl side effects, and test flakes hidden by one retry. Test signal is the top-level integration test orchestration itself.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/test_runner.sh -->
