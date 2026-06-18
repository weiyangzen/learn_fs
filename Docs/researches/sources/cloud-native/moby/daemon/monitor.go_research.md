# sources/cloud-native/moby/daemon/monitor.go

## Purpose
This file handles containerd lifecycle events for containers and exec processes, updates Docker container state, checkpoints state, emits events, restarts containers, and handles auto-removal.

## Important APIs, Types, And Functions
Key methods are `setStateCounter`, `handleContainerExit`, `ProcessEvent`, `autoRemove`, and `shouldIgnoreExitEventWithLock`. It uses container state, restart manager, containerd task/process APIs, health monitor hooks, metrics, backend removal config, and event logging.

## Control Flow
`ProcessEvent` resolves the container and switches on event type. OOM marks `OOMKilled` and checkpoints. Main process exit delegates to `handleContainerExit`; exec exit updates `ExecConfig`, closes streams, deletes the process asynchronously, and emits `exec_die`. Start/pause/resume external events update state, health, metrics, checkpoints, and Docker events. `handleContainerExit` ignores networking setup failures and duplicate exits, deletes the task, waits briefly for streams, resets state, chooses restart behavior, cleans up resources, checkpoints, emits `die`, and optionally schedules restart after the restart-manager wait channel.

## State, Persistence, And Dependencies
The file mutates `container.State`, `RestartCount`, exec command stores, health monitor state, metrics counters, stream state, and container checkpoints through `CheckpointTo`. It also calls daemon cleanup, container removal, and container start paths. Dependencies include containerd client/error/status types, Docker event/action constants, restartmanager, and daemon config.

## Integration Points
This is a central integration point between containerd events and Docker's persisted container model, API-visible state, event stream, metrics, restart policy, health checks, and auto-remove behavior.

## Risks And Edge Cases
Duplicate exit events are hard to classify; the code checks current state and live task status instead of timestamps because system time can move backward. Restart processing uses goroutines and must handle daemon startup completion, shutdown, manual stops/restarts, and failed restarts. Lock ordering is important: `autoRemove` is deferred until after unlocking. External starts may race with non-Docker task deletion and handle NotFound specially.

## Test Signals
No direct tests are in this work item. Behavior is likely covered by daemon lifecycle integration tests. The code has explicit logging around duplicate exits, cleanup failures, and restart errors.
