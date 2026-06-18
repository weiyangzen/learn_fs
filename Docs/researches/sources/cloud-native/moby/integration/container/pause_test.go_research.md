# sources/cloud-native/moby/integration/container/pause_test.go

Purpose: Pause/unpause API tests for state transitions, events, Windows unsupported behavior, and stopping a paused container.

Important APIs and flow: `TestPause` runs a container, records daemon time, pauses and unpauses it, inspects `State.Paused`, then consumes `Events` filtered by container and expects pause/unpause actions through `getEventActions`. `TestPauseFailsOnWindowsServerContainers` expects not implemented for Windows process isolation. `TestPauseStopPausedContainer` pauses then stops a Linux container and waits for stopped state.

State and dependencies: Uses cgroup freezer/pause support, daemon event stream, and inspect state. Skips Windows process isolation or cgroup-driver none cases.

Risks and signals: It guards correct state persistence and event emission for pause workflows. Failures can indicate broken cgroup integration, event stream ordering, or stop handling for paused containers.
