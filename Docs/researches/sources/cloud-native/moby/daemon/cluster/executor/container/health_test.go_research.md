# Research: sources/cloud-native/moby/daemon/cluster/executor/container/health_test.go

## sources/cloud-native/moby/daemon/cluster/executor/container/health_test.go

Purpose: validates that `controller.checkHealth` reacts only to unhealthy container health events for the matching task/container. It is Unix-only through `!windows`.

The test constructs an in-memory daemon event service, a task with swarm task labels, and a controller. It starts `checkHealth` in a goroutine, logs synthetic container events, and asserts that running, healthy, and die events are ignored while `ActionHealthStatusUnhealthy` produces `ErrContainerUnhealthy`.

State is in-memory channels and event subscriptions. Integration points include daemon `EventsService`, `LogContainerEvent`, Engine event actions, and controller event filtering by container name. Risks covered are false-positive health failures and missed unhealthy events. Gaps include service-binding activation on healthy events, behavior when the event stream closes, and shutdown after unhealthy detection.
