# sources/cloud-native/moby/integration/volume/main_test.go

## Purpose
Package-level harness for volume integration tests.

## Important APIs, Types, And Functions
- `TestMain` configures tracing, initializes environment, ensures frozen images, prints environment details, runs tests, and exits.
- `setupTest` starts a per-test span, protects baseline daemon resources, and registers cleanup.

## Control Flow
Initialization is performed once before all tests. Each test calls `setupTest` to get a traced context and cleanup behavior.

## State And Persistence
Stores package globals for the environment and base context. Cleanup removes unprotected volumes, containers, images, networks, and plugins after each test.

## Dependencies And Integration Points
Uses `internal/testutil`, `environment`, OpenTelemetry, and frozen-image setup. Volume tests rely heavily on busybox availability.

## Risks And Edge Cases
Harness failure prevents all package tests. Cleanup is critical because volume tests create named and anonymous volumes that would otherwise interfere with later cases.

## Test Signals
Successful package initialization supplies a working API client and cleanup-managed environment for volume tests.
