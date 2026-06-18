## sources/distributed-fs/ipfs-kubo/test/sharness/t0065-active-requests.sh

Purpose: validates `ipfs diag cmds` reporting for active and inactive daemon API requests.

Important APIs and helpers: uses `test_init_ipfs`, daemon launch/kill helpers, `ipfs diag cmds`, `ipfs log tail`, `go-sleep`, `grep`, and shell process management via background PID, `kill`, and `wait`.

Control flow and state: starts a daemon, captures `diag cmds` output for a normal command, starts long-running `ipfs log tail` in the background, and checks that `diag cmds` reports `log/tail` as active. It then kills the log tail process, waits briefly, and checks the same command is retained as inactive.

Dependencies and integration points: exercises command instrumentation in the daemon, request lifecycle tracking, and the log streaming endpoint. The persisted repo state is minimal; the important state is daemon in-memory active request tracking.

Risks and test signals: catches leaks or incorrect active flags in diagnostic state, especially for streaming endpoints that are easy to leave open. Passing output contains `diag/cmds`, `log/tail`, `true` while active, and `false` after termination.
