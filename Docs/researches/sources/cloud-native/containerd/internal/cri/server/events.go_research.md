
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events.go -->
# sources/cloud-native/containerd/internal/cri/server/events.go

## Purpose

This file implements CRI-server handling for containerd task, sandbox, OOM, and image events. It updates CRI in-memory stores, cleans up runtime tasks, emits CRI container event responses, and reconciles image metadata after image create/update/delete events.

## Important APIs, Types, and Functions

Key functions are `startSandboxExitMonitor`, `handleSandboxExit`, `startContainerExitMonitor`, `handleContainerExit`, `(*criEventHandler).HandleEvent`, `oomMetricsEventOccurred`, and `getPlatformFromSandboxID`. The `handleEventTimeout` constant limits event handling to ten seconds.

## Control Flow

The per-sandbox and per-container exit monitors wait on a `containerd.ExitStatus` channel or context cancellation. On exit, they build an event object, create a namespaced timeout context, look up the sandbox or container, and call the corresponding handler. Handler failures are logged and pushed into the event monitor backoff queue.

`handleSandboxExit` marks the sandbox not-ready, clears PID, records exit status and time, closes the sandbox stop channel, and emits a CRI stopped event. `handleContainerExit` attaches container IO if present, optionally checks cgroup OOM metrics for Linux exit code 137, deletes the task with NRI exit options and process kill, performs a task-service delete fallback on `NotFound` to avoid shim leaks, updates container status to exited, clears unknown state, stops the container store object, and emits a CRI stopped event.

`criEventHandler.HandleEvent` dispatches containerd events by concrete type. Task exits are matched first against containers by `ID`, then sandboxes. Task OOM updates container reason to `OOMKilled`. Image create/update/delete events call `UpdateImage`.

## State and Persistence Behavior

The file mutates in-memory sandbox and container store statuses. It deletes runtime task state and may call the containerd task service to remove stale shim records. It also drives image-store reconciliation through `UpdateImage`. CRI container event responses are placed on `containerEventsQ`; if status lookup fails, pod status may be nil while container status failures are logged.

## Dependencies and Integration Points

Dependencies include containerd client tasks, task-service API, containerd event types, cgroup v1/v2 metrics, sandbox and container stores, NRI, CRI runtime API, containerd `typeurl`, and platform lookup through `sandboxService.SandboxPlatform`. It integrates with the generic event monitor in `server/events`, image service update logic, and container stop/wait channels.

## Risks and Edge Cases

Event handling is serial in the monitor and uses a fixed timeout; slow task deletion can trigger retry and leak risks. `TaskExit.ID` is used to avoid treating exec exits as container exits. OOM detection has known races with systemd cgroup garbage collection and with asynchronous TaskOOM event handling. Task-service fallback handles one shim leak class but depends on correct `NotFound` classification. The code deliberately ignores missing containers/sandboxes because events can outlive store entries.

## Test Signals

Strong tests would cover monitor-generated exit events, backoff on handler failure, `TaskExit` dispatch to container versus sandbox, OOM reason update from both `TaskOOM` and cgroup metrics, task delete `NotFound` fallback to task-service delete, unknown-to-exited state transition, CRI event queue emission, and image event calls into `UpdateImage`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events.go -->
