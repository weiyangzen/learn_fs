# sources/cloud-native/moby/integration-cli/docker_cli_prune_test.go

Purpose: declares `DockerCLIPruneSuite`, the shared suite holder for prune CLI tests implemented in Unix-specific files.

Important APIs and types: `DockerCLIPruneSuite` contains `ds *DockerSuite`, matching the integration suite pattern used by other CLI command groups.

Control flow: no test logic exists here; lifecycle methods are supplied in `docker_cli_prune_unix_test.go`.

State and persistence: no direct state changes.

Dependencies and integration points: this file exists so prune tests share suite registration and can attach teardown/timeout behavior in build-tagged companions.

Risks: minimal, but suite declaration changes can affect all prune tests.

Test signals: indirect compile-time/suite-registration signal only.
