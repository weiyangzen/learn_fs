## sources/cloud-native/moby/integration-cli/docker_cli_service_health_test.go

Purpose: validates swarm task lifecycle integration with container health checks. `TestServiceHealthRun` confirms an initially healthy service task becomes failed when its health check turns unhealthy. `TestServiceHealthStart` confirms an unhealthy-at-start task remains in `TaskStateStarting` until the health check passes.

Important APIs are `cli.BuildCmd` with inline Dockerfiles, `d.GetServiceTasks`, `d.GetTask`, `d.Cmd("inspect", "--format=...")`, and `container.ErrContainerUnhealthy`. Control flow builds custom busybox images with `HEALTHCHECK`, creates a service, polls task state and container health, mutates `/status` with `docker exec`, then asserts swarm task states.

State lives in built images, swarm task status, and container health state. Dependencies include Linux-only busybox behavior, health-check timing, swarm executor errors, and `defaultReconciliationTimeout`. Risks are timing flakes around health transitions and large retry values masking failures. Test signals are `healthy/unhealthy`, failing streaks, `TaskStateStarting`, `TaskStateRunning`, `TaskStateFailed`, and the expected unhealthy-container error.
