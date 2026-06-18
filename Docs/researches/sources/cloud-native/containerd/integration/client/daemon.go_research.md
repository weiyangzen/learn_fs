<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon.go -->
# sources/cloud-native/containerd/integration/client/daemon.go

## Purpose
Provides a small process manager used by integration tests to start, stop, kill, wait for, and restart a containerd daemon under test.

## APIs, Types, And Functions
The central type is `daemon`, containing a mutex, daemon address, and `*exec.Cmd`. Methods are `start`, `waitForStart`, `Stop`, `Kill`, `Wait`, and `Restart`.

## Control Flow And State
`start` rejects duplicate starts, appends `--address`, launches the command, and stores the command/address. `waitForStart` polls every 500 ms, creates a client, checks `IsServing`, reads the plugin list, and fails if any plugin init error is not an allowed skip. `Stop` sends SIGTERM, `Kill` kills the process, `Wait` reaps and clears `cmd`, and `Restart` signals the process, waits, optionally invokes a callback, and relaunches with the same executable, arguments, stdout, and stderr.

## Persistence And Integration Points
The helper owns OS process state and a client connection address. It integrates with `client.New`, `IntrospectionService().Plugins`, `plugin.ErrSkipPlugin`, OS signals, and Windows-specific restart behavior that uses SIGKILL.

## Risks And Test Signals
The mutex prevents concurrent process mutation, but `Restart` holds the lock while waiting and relaunching, so tests depend on callbacks not reentering daemon methods. Failures expose daemon startup errors, plugin initialization failures, stale client sockets, or process lifecycle bugs that would invalidate many integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/daemon.go -->
