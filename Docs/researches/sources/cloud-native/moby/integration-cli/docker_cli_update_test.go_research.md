## sources/cloud-native/moby/integration-cli/docker_cli_update_test.go

Purpose: declares `DockerCLIUpdateSuite`, a thin suite container shared by platform-specific update tests. The file has no tests or helper methods beyond the `ds *DockerSuite` field.

Control flow and behavior are provided by companion files such as `docker_cli_update_unix_test.go`. State is limited to the embedded suite pointer used for teardown and timeout forwarding in platform files. Dependencies are only package `main` and `DockerSuite` from the integration CLI harness.

Risks are structural: removing or renaming this type would break methods declared in build-tagged companion files. Test signals are indirect; the Go test compiler links methods with this suite type, and suite registration elsewhere depends on the type existing.
