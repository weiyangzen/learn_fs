# sources/cloud-native/moby/integration/plugin/logging/main_test.go

## Purpose
Package harness for logging plugin integration tests. It initializes tracing, environment, frozen Linux images, and package globals.

## Important APIs, Types, And Functions
`TestMain` calls `testutil.ConfigureTracing`, `environment.New`, `environment.EnsureFrozenImagesLinux`, prints the environment, runs tests, marks span status for non-zero exit, and exits.

## Control Flow
Suite initialization happens once before tests. Tests use `baseContext` and `testEnv` directly or through helpers.

## State And Persistence Behavior
Maintains global `testEnv` and `baseContext`; no per-test helper is defined here.

## Dependencies And Integration Points
Integrates logging plugin tests with Moby's environment and tracing utilities.

## Risks
Failure to load frozen images prevents the package from running. Tests must manage their own environment cleanup because this file does not provide a `setupTest` wrapper.

## Test Signals
No direct behavioral assertions; setup failures and non-zero package exit are reflected in tracing.
