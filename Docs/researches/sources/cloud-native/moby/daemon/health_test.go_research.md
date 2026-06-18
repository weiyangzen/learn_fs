# sources/cloud-native/moby/daemon/health_test.go

Purpose: unit tests for healthcheck state machine and probe validation.

Important APIs and control flow: `reset` installs a fresh starting health state. `TestNoneHealthcheck` verifies `initHealthMonitor` leaves `State.Health` nil when healthcheck type is `NONE`. `TestHealthStates` creates an event service and container replica DB, then drives `handleProbeResult` directly through starting, unhealthy, healthy, retries, and start-period scenarios while asserting emitted `health_status` events and failing streak values. `TestCmdProbeEmptyCommand` calls `cmdProbe.run` with `Test: []string{"CMD"}` and expects a "has no command" error before any daemon dependency is needed.

State, dependencies, and risks: tests avoid real exec by directly invoking result handling except for the empty-command validation. They depend on event channel timing and a temporary container view DB. Coverage is strong for transition rules and event emission but does not exercise monitor timers, exec startup/timeout behavior, limited output truncation, or in-memory commit failure handling.
