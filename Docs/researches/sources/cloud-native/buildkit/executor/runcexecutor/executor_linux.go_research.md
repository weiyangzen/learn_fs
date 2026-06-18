# Research: sources/cloud-native/buildkit/executor/runcexecutor/executor_linux.go

## Purpose
Linux runc invocation and IO/signal handling.

## Important APIs, Types, and Functions
`updateRuncFieldsForHostOS`, `run`, `exec`, `callWithIO`, `detectOOM`, `readMemoryEvent`.

## Control Flow
Sets up go-runc started channels, IO/TTY/resize, signal forwarding, process handles, kill behavior, waits for completion, and decorates OOM exits from cgroup memory events.

## State and Persistence
Transient runc monitor processes, pidfiles, IO pipes, console state, and cgroup reads.

## Dependencies and Integration Points
Depends on go-runc, containerd console, Linux signals, gateway errors, and cgroup files. Completes runc executor `Run`/`Exec` lifecycle.

## Risks and Edge Cases
SIGKILL routing, pidfile races, missing started messages, and OOM parsing are subtle.

## Test Signals
Requires actual runc integration tests.
