# sources/cloud-native/moby/integration-cli/docker_cli_info_test.go

Purpose: tests `docker info` baseline output and container state counters. `DockerCLIInfoSuite` delegates teardown and timeout to `DockerSuite`, so each test relies on the shared integration cleanup model.

Important APIs and functions: `cli.DockerCmd` drives the CLI, `testEnv.DaemonInfo` and `DaemonIsLinux` gate expected fields, and `existingContainerStates` runs `docker info --format {{json .}}`, unmarshals it into `map[string]any`, and extracts `Containers`, `ContainersRunning`, `ContainersPaused`, and `ContainersStopped`.

Control flow: `TestInfoEnsureSucceeds` builds a required-prefix list, conditionally adds Linux, runtime, and experimental fields, then scans raw `docker info` text. The running, paused, and stopped tests snapshot existing counters, create or transition a busybox container, rerun `docker info`, and assert only the intended counter changes.

State and persistence: the tests intentionally mutate daemon container state but do not inspect disk. They are sensitive to pre-existing containers, so the helper snapshots current counts before creating new state.

Dependencies and integration points: relies on busybox, the integration CLI wrapper, daemon OS capability checks, and JSON formatting from the CLI info command.

Risks: output-prefix assertions can break on CLI wording changes; JSON numeric decoding assumes float64; counter tests are vulnerable to concurrent container creation by other tests or leaked containers.

Test signals: success means `docker info` exposes required metadata and accurately reflects running, paused, and stopped container totals after lifecycle transitions.
