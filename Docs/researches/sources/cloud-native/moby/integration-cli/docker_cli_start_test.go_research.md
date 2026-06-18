## sources/cloud-native/moby/integration-cli/docker_cli_start_test.go

Purpose: validates `docker start` behavior around attach mode, exit-code propagation, recorded start errors, paused containers, multiple starts, rename races, restart policies, and `--rm`. The suite wraps `DockerSuite` teardown and timeout.

Control flow uses CLI helpers to create/run containers, stops or waits for them, then invokes `start` variants. Tests use goroutines and timeouts for attach-return behavior, inspect helpers for `State.Error` and running state, and `icmd.Expected` for exit codes. Linux-only cases cover links, pause, and port conflicts.

State includes container runtime state, link dependencies, restart counters, names, port allocation, and inspect `State.Error`. Dependencies are `cli.DockerCmd`, `dockerCmdWithError`, `inspectField`, `runSleepingContainer`, and `icmd`. Risks include races in rename/attach test, timing around container exit, and platform unsupported features. Test signals include exact output, nonzero errors, exit codes 1/11/12/137, paused-container message, and correct running states after partial multi-container starts.
