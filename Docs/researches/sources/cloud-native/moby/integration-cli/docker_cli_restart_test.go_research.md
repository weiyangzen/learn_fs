# sources/cloud-native/moby/integration-cli/docker_cli_restart_test.go

Purpose: integration tests for `docker restart`, restart policies, volumes across restarts, disconnected networks, auto-remove behavior, and restart-policy interaction with process death and user-defined networks.

Important APIs and functions: `DockerCLIRestartSuite`, `cli.DockerCmd`, `runSleepingContainer`, `cli.WaitRun`, `cli.WaitExited`, `waitInspect`, `inspectField`, `inspectFilter`, `inspectMountPoint`, `poll.WaitOn`, `os.FindProcess`, and platform skips for Windows isolation.

Control flow: tests restart stopped and running containers and poll logs for repeated output, verify volume mount count/source survives restart, restart a container disconnected from bridge, inspect `--restart=no`, `always`, and `on-failure` policies including invalid negative retry count, kill container processes to trigger restart policies, verify restart policy still works after manual restart, test links on a user-defined network after restart-policy recovery, exercise stop/start/kill with restart policies, and ensure `--rm` containers are restarted rather than removed by `docker restart`.

State and persistence: creates containers with logs, volumes, restart policies, user-defined networks, links, and process IDs. It relies on daemon state transitions and restart count persistence.

Dependencies and integration points: busybox, process signaling on the host, inspect state fields, mount persistence, network/link resolution, daemon restart manager, and OS-specific process isolation.

Risks: timing-sensitive waits around logs and restart manager; killing host PIDs is not portable to Hyper-V isolation; restart counts can be affected by slow daemon scheduling.

Test signals: restart must rerun commands/logs, preserve mounts and network configuration, correctly store restart policy settings, recover killed containers according to policy, maintain linked user-defined network resolution, and keep auto-remove containers alive through explicit restart.
