# sources/cloud-native/moby/integration-cli/docker_cli_create_test.go

Purpose: integration tests for `docker create` and related container configuration persistence. The suite checks argument parsing, host config, port bindings, labels, volumes, workdir creation, entrypoint clearing, stop configuration, and invalid option handling.

Important APIs/types/functions: `DockerCLICreateSuite`; tests `TestCreateArgs`, `TestCreateHostConfig`, `TestCreateWithPortRange`, `TestCreateWithLargePortRange`, `TestCreateEchoStdout`, `TestCreateVolumesCreated`, `TestCreateLabels`, `TestCreateLabelFromImage`, `TestCreateHostnameWithNumber`, `TestCreateRM`, `TestCreateModeIpcContainer`, `TestCreateStopSignal`, `TestCreateWithWorkdir`, `TestCreateWithInvalidLogOpts`, `TestCreateUnsetEntrypoint`, and `TestCreateStopTimeout`.

Control flow: tests run `docker create` with specific CLI flags, inspect JSON or Go-template fields, then sometimes start the container to verify runtime behavior. Build-backed tests create temporary images with labels or entrypoints. Port range tests unmarshal `HostConfig.PortBindings`; labels and stop options use inspect helpers.

State and persistence: creates containers, volumes, images, labels, host config, stop signals/timeouts, workdirs, and port binding metadata. Invalid log options are expected to leave no container behind.

Dependencies and integration points: Docker CLI, inspect JSON, `network.PortMap`, build helper, fake build contexts, local daemon volume inspection, IPC mode on Linux, and Windows-specific workdir behavior via daemon OSType checks.

Risks: the large port range test touches 65,535 bindings and can be expensive. Some checks parse CLI output or inspect partial fields. Workdir verification uses `docker cp`, coupling create behavior to archive support. Platform differences around Windows busybox entrypoints and workdir creation are explicitly handled.

Test signals: failures point to CLI parsing regressions, config serialization errors, port range expansion problems, image label merge precedence bugs, invalid config cleanup failures, or changed inspect schema.
