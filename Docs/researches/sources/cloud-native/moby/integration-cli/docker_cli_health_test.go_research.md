# sources/cloud-native/moby/integration-cli/docker_cli_health_test.go

Purpose: integration coverage for Docker healthcheck configuration, runtime health transitions, health log inspection, CLI overrides, timeout behavior, JSON-form health commands, and unset environment variable handling.

Important APIs/types/functions: `DockerCLIHealthSuite`, helper `waitForHealthStatus`, helper `getHealth`, `TestHealth`, and `TestUnsetEnvVarHealthCheck`. It uses `container.HealthStatus` and `container.Health` from API types.

Control flow: `TestHealth` builds an image with a healthcheck that reads `/status`, creates/runs containers, waits for transitions from `starting` to `healthy`, removes/touches files through exec to force unhealthy/healthy transitions, inspects health status/logs, disables checks via CLI and Dockerfile, enables checks on an image with `HEALTHCHECK NONE`, tests timeout output, and validates JSON-form command parsing. The env-var test runs a healthcheck with an unset env var and waits for healthy.

State and persistence: health configuration is stored in image/container config. Runtime health status, failing streak, and logs are stored in container state and retrieved via inspect. Containers and test images are removed by cleanup paths.

Dependencies and integration points: Linux busybox, Docker build, `docker inspect`, `docker exec`, health monitor scheduling, stop signal handling, and API health structs.

Risks: health tests are timing-sensitive by design and poll every 100ms. `waitForHealthStatus` has a TODO noting questionable assertion logic around previous state. Short intervals and timeouts can be flaky on overloaded systems.

Test signals: failures indicate broken healthcheck parsing, scheduling, state transitions, failing streak accounting, timeout handling, inspect serialization, or CLI/Dockerfile healthcheck override semantics.
