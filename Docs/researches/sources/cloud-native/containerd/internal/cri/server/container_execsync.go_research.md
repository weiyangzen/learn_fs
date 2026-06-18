# sources/cloud-native/containerd/internal/cri/server/container_execsync.go

## Purpose
This file implements synchronous CRI exec, including bounded stdout/stderr collection, process creation inside an existing task, TTY handling, timeouts, IO attachment, and cleanup.

## Important APIs, Types, and Functions
Key types/functions are `cappedWriter`, `ExecSync`, `execOptions`, `execInternal`, `execInContainer`, and `drainExecSyncIO`. It uses containerd `Task.Exec`, `Process.Wait`, `Process.Start`, `Process.Kill`, `Process.Delete`, CRI IO helpers, and optional streaming IO endpoints.

## Control Flow, State, and Persistence
`ExecSync` caps each output stream at 16 MiB and calls `execInContainer`. The shared exec path loads the container spec/task, adjusts process args and TTY env, creates fifo or streaming IO based on runtime config, waits for the exec process, starts it, attaches IO, handles terminal resize, applies timeout cancellation with SIGKILL, drains IO, and deletes the process on exit. No durable container metadata is changed.

## Dependencies and Integration Points
The code integrates CRI runtime config, sandbox endpoints, container store, sandbox store, containerd task/process APIs, `remotecommand` terminal sizing, tracing, and `DrainExecSyncIOTimeout`.

## Risks and Test Signals
Risks include goroutine leaks when `Start` fails, unbounded output, hanging on inherited pipe descriptors from child processes, timeout cleanup races, and command-line leakage from stale `CommandLine`. Tests cover `cappedWriter` semantics and `drainExecSyncIO` timeout/delete behavior.
