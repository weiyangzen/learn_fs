## sources/cloud-native/moby/integration-cli/environment/environment.go

Purpose: small wrapper around `internal/testutil/environment.Execution` that records the Docker CLI binary path for integration CLI tests.

Important API: package variable `DefaultClientBinary` reads `TEST_CLIENT_BINARY`, `init` defaults it to `docker`, `Execution` embeds `environment.Execution` and stores `dockerBinary`, `DockerBinary` returns that path, and `New` constructs the base environment then resolves the CLI via `exec.LookPath`.

Control flow is straightforward: environment discovery happens first, then binary lookup, then a pointer to the composed `Execution` is returned. State is process environment plus the embedded daemon/test environment. Dependencies are Go `os`, `os/exec`, and Moby testutil environment package. Risks are missing `docker` binary, stale `TEST_CLIENT_BINARY`, and shadowing between client binary and daemon binary. Test signals are startup failures from `New` and later use of `DockerBinary()` by suites.
