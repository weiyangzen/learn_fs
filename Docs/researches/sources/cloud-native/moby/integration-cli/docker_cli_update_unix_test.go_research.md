## sources/cloud-native/moby/integration-cli/docker_cli_update_unix_test.go

Purpose: Unix/Linux coverage for `docker update` resource mutation semantics. Tests cover running, restarted, stopped, and paused containers; untouched fields; invalid memory values; swap memory; stats memory-limit stability; restart monitor behavior; and NanoCPUs conflicts/updates.

Control flow starts containers with memory/CPU settings, runs `docker update`, inspects `HostConfig`, and reads cgroup files inside containers. Some tests call the API stats endpoint, attach through a pty to exit a restart-policy container, or inspect through the Go client. Requirement gates skip unsupported cgroup and Linux capabilities; several tests skip cgroups v2.

State includes container `HostConfig`, kernel cgroup files, API stats responses, restart count, and NanoCPUs fields. Dependencies include `cli`, `dockerCmdWithError`, `inspectField`, `request.Get`, `creack/pty`, and cgroup feature probes. Risks are cgroup v1-specific paths, kernel validation ordering, resource feature variability, and pty cleanup. Test signals are exact byte values, error messages, unchanged memory stats, restart count `1`, and conflict messages for CPU quota versus NanoCPUs.
