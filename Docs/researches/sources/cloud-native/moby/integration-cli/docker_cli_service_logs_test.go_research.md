## sources/cloud-native/moby/integration-cli/docker_cli_service_logs_test.go

Purpose: exercises `docker service logs` across retrieval, ordering, `--tail`, `--since`, `--follow`, task-id addressing, TTY/raw behavior, deleted containers, and log details. The local `logMessage` type coordinates async follow reads; `countLogLines` is a polling helper that runs `service logs -t --raw`.

Control flow creates swarm services that emit deterministic lines, waits for task/container readiness, then runs CLI log queries and validates stdout content. The follow test starts `docker service logs -f` with pipes and scans three log messages before killing the process. The deleted-container test removes the backing container and asserts logs returns within a timeout.

State and persistence are json-file log records, task/container IDs, service metadata, and log-driver detail fields. Dependencies include daemon suite helpers, `icmd`, `poll`, `exec.Command`, pipes, timestamps, and busybox shell loops. Risks include timing/order flakes, stdout/stderr multiplexing differences with TTY, and hung log streams. Test signals are exact log counts, timestamp-derived filtering, task IDs in lines, CRLF raw TTY output, and `--details` key-value text.
