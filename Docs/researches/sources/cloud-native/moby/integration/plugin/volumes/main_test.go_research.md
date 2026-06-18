# sources/cloud-native/moby/integration/plugin/volumes/main_test.go

## Purpose
Package harness for volume plugin integration tests. It configures tracing, initializes environment, ensures frozen Linux images, and exposes shared globals.

## Important APIs, Types, And Functions
`TestMain` uses `testutil.ConfigureTracing`, `environment.New`, `environment.EnsureFrozenImagesLinux`, OpenTelemetry spans, `testEnv.Print`, `m.Run`, and process exit.

## Control Flow
Suite setup runs once, then tests execute with global `baseContext` and `testEnv`.

## State And Persistence Behavior
Maintains package-level environment and base context. No per-test setup helper is provided here.

## Dependencies And Integration Points
All volume plugin tests depend on this file for environment discovery, tracing, and frozen image availability.

## Risks
Environment or image setup failure aborts the package. Tests need to manage daemon cleanup explicitly.

## Test Signals
No direct assertions beyond setup failure handling and non-zero exit tracing.
