# sources/cloud-native/moby/integration-cli/docker_cli_network_test.go

Purpose: defines shared suite types for CLI network tests and full daemon/network-driver integration tests.

Important APIs and types: `DockerCLINetworkSuite` wraps `*DockerSuite` for ordinary CLI-network tests, while `DockerNetworkSuite` holds an `httptest.Server`, `*DockerSuite`, and `*daemon.Daemon` for tests that need local daemon control or remote driver simulation.

Control flow: only lifecycle hooks are present here. `DockerCLINetworkSuite` delegates teardown and timeout to `DockerSuite`; `DockerNetworkSuite` fields are initialized and exercised in the Unix-specific file.

State and persistence: no direct state changes in this file. It establishes the storage for per-test daemon handles and remote plugin HTTP server references used elsewhere.

Dependencies and integration points: `context`, `testing`, `net/http/httptest`, and the integration `daemon` helper. This file is the cross-platform suite declaration paired with Unix implementation in `docker_cli_network_unix_test.go`.

Risks: because behavior lives in build-tagged companions, missing or mismatched suite hooks can silently affect a large number of network tests.

Test signals: indirect; successful compilation and suite registration enable the network integration tests to run with the correct fixture ownership.
