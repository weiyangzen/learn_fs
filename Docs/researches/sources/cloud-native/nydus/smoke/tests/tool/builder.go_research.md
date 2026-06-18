# sources/cloud-native/nydus/smoke/tests/tool/builder.go

## Purpose
This helper wraps `nydus-image check` for smoke tests that need to validate generated bootstraps outside the higher-level `nydusify check` path.

## Important APIs, Types, And Functions
`CheckOption` contains `BuilderPath`. `CheckBootstrap` builds arguments `check --log-level error --bootstrap <path> -v`, runs the builder with `exec.CommandContext`, sends stdout/stderr to a logrus module writer, and returns errors to the caller.

## Control Flow
The function constructs CLI args, logs them at debug level, runs the command, logs failures with context, and returns nil on success.

## State And Persistence
It does not write files directly; it reads the bootstrap and emits log output.

## Dependencies And Integration Points
It integrates smoke tests with the `nydus-image` binary and is used by external backend tests after bootstrap generation/pull.

## Risks
It uses `context.Background` without timeout, so a hung builder can hang the test. It assumes `BuilderPath` is executable and compatible with the bootstrap format.

## Test Signals
Successful return is a bootstrap structural validation signal from `nydus-image check -v`.
