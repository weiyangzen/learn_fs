# Research: sources/cloud-native/nydus-snapshotter/pkg/fanotify/fanotify.go

This file wraps an external fanotify binary and records accessed paths. `Server` stores the binary path, target container PID, image name, persistence path, formatting flags, timeout, stdout client, `exec.Cmd`, and syslog writer. `NewServer` constructs the state object.

`RunServer` skips work if an existing persist file should be preserved, starts the binary in a new mount namespace with `_MNTNS_PID` and `_TARGET=/` environment variables, pipes stdout into `conn.Client`, and launches goroutines for process wait, event receiving, and optional timeout shutdown. `RunReceiver` creates a plain path file plus a `.csv` file, writes a CSV header, reads events until EOF, and writes raw or human-readable size/latency values. `StopServer` sends SIGTERM to the process group and waits.

State is persisted in the configured text and CSV files. Integration points include syslog, mount namespace behavior, external fanotify server contract, display formatting utilities, and logrus. Risks include blocking process waits, unguarded `LogWriter` assignment to stderr, duplicated wait paths between the wait goroutine and `StopServer`, overwrite semantics, and no tests in this subset.
