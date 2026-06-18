# sources/distributed-fs/ipfs-kubo/test/cli/log_level_test.go

Purpose: comprehensive coverage for `ipfs log level` behavior across CLI, HTTP RPC, wildcard aliases, default levels, shell escaping, and go-log/slog interoperability.

Important APIs/functions: `TestLogLevel`, helpers `getExpectedSubsystems`, `parseCLIOutput`, `parseHTTPResponse`, `validateAllSubsystemsPresent`, and `validateAllSubsystemsPresentCLI`. Inline helpers start `ipfs log tail`, trigger identify protocol, and wait for subsystem log matches.

Control flow: CLI subtests start daemons, list subsystems, get/set levels for `*`, `all`, specific subsystems, default keyword, and shell-escaped wildcard forms. HTTP RPC subtests POST to `/api/v0/log/level` and validate JSON `Levels` or `Message`. Slog tests set levels via env or CLI, tail logs, trigger a normal CLI request and libp2p identify, and wait for both `cmds/http` and `net/identify` loggers.

State and persistence: runtime log levels are process state, not repo persistence. Test daemons and log-tail subprocesses are started/stopped per subtest.

Dependencies/integration: uses Kubo log RPC, go-log subsystem list, go-libp2p slog bridge, HTTP API, shell execution, and harness process env.

Risks: large parallel daemon count and timing-sensitive log tailing can flake. Subsystem names are implementation-coupled. Test signals are CLI lines, JSON fields, messages, and streamed JSON log entries.
