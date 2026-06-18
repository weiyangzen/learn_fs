## sources/cloud-native/moby/integration-cli/docker_cli_stats_test.go

Purpose: covers `docker stats` CLI behavior on Linux: non-streaming completion, not-found errors, default running-only scope, `--all`, dynamic inclusion of newly created containers, and formatting.

Control flow starts busybox containers, waits for running/exited states, then invokes `stats` through `exec.Command` or CLI helpers. `TestStatsNoStream` guards with a three-second timeout; streaming behavior is tested by reading stdout with a scanner while creating another container. Regex checks ensure stats columns contain nonzero data for running containers and zeros for stopped containers under `--all`.

State is live cgroup/container metrics exposed by the daemon and CLI table rendering. Dependencies include Linux stats support, busybox `top`, `bufio.Scanner`, regex, and timeouts. Risks are resource-metric timing, output column assumptions after the 12-character ID, and streaming process cleanup. Test signals are container IDs/names in output, absence of stopped containers without `--all`, not-found messages, and formatted `{{.Name}}` output.
