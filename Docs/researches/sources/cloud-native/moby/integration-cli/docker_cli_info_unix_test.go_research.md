# sources/cloud-native/moby/integration-cli/docker_cli_info_unix_test.go

Purpose: Unix-only security option validation for daemon info. It extends `DockerCLIInfoSuite` with coverage for AppArmor and seccomp reporting.

Important APIs and functions: `client.New(client.FromEnv)` creates an Engine API client, `apiClient.Info` fetches structured daemon info, `config.SeccompProfileDefault` provides the expected default profile name, and local helpers `Apparmor`, `seccompEnabled`, `DaemonIsLinux`, and `testEnv.IsLocalDaemon` gate the test.

Control flow: the test skips unless running against a local Linux daemon and at least one of seccomp or AppArmor is enabled. It calls the API, reads `result.Info.SecurityOptions`, and checks for `name=apparmor` and/or `name=seccomp,profile=default` as appropriate.

State and persistence: read-only against daemon state. It validates current runtime security configuration rather than changing containers, images, or files.

Dependencies and integration points: depends on host kernel/security module configuration, Engine API behavior, and the daemon environment inherited through `client.FromEnv`.

Risks: host configuration variability is high; a daemon compiled or configured without these features skips. The test is intentionally Linux/local-only because remote or Windows daemons may report different security option sets.

Test signals: structured API info must include security option entries that match the enabled host security features.
