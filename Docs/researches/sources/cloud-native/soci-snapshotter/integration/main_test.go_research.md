# sources/cloud-native/soci-snapshotter/integration/main_test.go

Purpose: provides the integration test entrypoint, environment gates, log-level configuration, tool support checks, and global image-build setup/teardown.

Important APIs and flow: `TestMain` skips unless `ENABLE_INTEGRATION_TEST=true`, validates optional `CONTAINERD_LOG_LEVEL` and `SOCI_LOG_LEVEL`, checks dockershell/compose/exec support, runs `setup`, executes tests, then runs `teardown` and exits with the test code. `setup` locates the project root, reads Docker build args from the environment, renders the compose build template for the containerd snapshotter base and registry stages, and builds required images. `teardown` runs cleanup functions in order.

State and persistence: builds Docker/Compose images used by integration tests and registers cleanup callbacks. Global log-level variables are mutated from environment.

Dependencies and integration: integrates with Docker Compose, project test utilities, dockershell execution support, and logrus level parsing. It is the guard preventing accidental integration runs on unsupported hosts.

Risks and test signals: failures here abort the entire integration suite. Returning early instead of `os.Exit` when disabled makes the suite appear skipped by doing no work. Build setup is expensive and sensitive to Docker/Compose availability and build-arg correctness.
