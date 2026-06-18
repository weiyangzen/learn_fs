# sources/cloud-native/moby/integration/secret/main_test.go

## Purpose
Package harness for secret integration tests. It configures tracing, initializes the execution environment, ensures frozen Linux images, and provides `setupTest` for environment protection/cleanup.

## Important APIs, Types, And Functions
`TestMain` calls tracing setup, `environment.New`, `environment.EnsureFrozenImagesLinux`, environment printing, `m.Run`, span status on non-zero exit, shutdown, and `os.Exit`. `setupTest` starts a span, protects the environment, and schedules cleanup.

## Control Flow
Suite setup runs once, while each secret test calls `setupTest` before creating a swarm or client.

## State And Persistence Behavior
Global `testEnv` and `baseContext` are package state. Cleanup clears environment resources after each test.

## Dependencies And Integration Points
Integrates secret tests with Moby environment utilities, frozen image management, and OpenTelemetry.

## Risks
Environment/image setup failure aborts all secret tests. Cleanup correctness is important because swarm tests create daemon and cluster state.

## Test Signals
No direct functional assertions; setup errors and non-zero exit are reflected in tracing.
