# sources/cloud-native/moby/integration/container/health_test.go

Purpose: Tests healthcheck execution semantics: working directory inheritance, signal interaction, timeout process cleanup/logging, and start interval behavior.

Important APIs and flow: Tests create containers with `HealthConfig` fields and poll `ContainerInspect().State.Health`. `TestHealthCheckWorkdir` expects a shell healthcheck to run in `/foo`. `TestHealthKillContainer` toggles a file with `SIGUSR1` and ensures healthchecks continue after signals. `TestHealthCheckProcessKilled` expects timeout log text from a killed healthcheck. `TestHealthStartInterval` verifies fast `StartInterval` checks during `StartPeriod`, then normal `Interval` spacing after healthy. Helpers `pollForHealthCheckLog` and `pollForHealthStatus` centralize inspect polling.

State and dependencies: Uses container files under `/health` and `/tmp/health`, health log persistence, and time-sensitive polling. Windows is skipped where shell/signals do not apply.

Risks and signals: It catches regressions in health monitor scheduling, exec timeout handling, signal handling, and health status/log persistence.
