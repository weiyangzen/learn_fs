# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/cleanup.rs

Purpose: small cleanup binary for integration-test leftovers in podman.

Important APIs/types/functions: `main` uses `std::process::Command` and `INTEGRATION_TEST_LABEL` from the integration-test library. It runs `podman ps -a --filter label=... -q` and `podman images --filter label=... -q`, then removes matching containers/images.

Control flow: print start message, collect container IDs, remove each with `podman rm -f`, collect image IDs, remove each with `podman rmi -f`, print completion. Command failures are ignored unless the initial listing command itself cannot be spawned, in which case the section is skipped.

State and persistence: mutates local podman state by deleting containers and images with the integration-test label. It does not touch composefs repositories or temp directories.

Dependencies and integration points: used by developers/CI to clean resources created by tests that label podman objects with `composefs-rs.integration-test=1`.

Risks: cleanup is label-scoped, so tests must consistently apply the label or resources remain. It ignores command failures, which is convenient for best-effort cleanup but can hide permission or podman availability problems. Image removal with repeated IDs may be harmless but noisy.

Test signals: no direct tests. Effectiveness is visible after integration test runs by checking that labeled podman resources are gone.
