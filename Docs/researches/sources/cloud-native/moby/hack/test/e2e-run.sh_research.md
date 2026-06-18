# sources/cloud-native/moby/hack/test/e2e-run.sh

## Purpose
End-to-end test runner wrapper for newer and legacy integration suites.

## Important APIs and Types
Defines `run_test_integration`, `run_test_integration_suites`, `run_test_integration_legacy_suites`, and `test_env`.

## Control Flow, State, and Persistence
The script constructs a test environment, runs selected suite binaries or legacy suites, and propagates results. It centralizes environment variables needed by e2e tests rather than relying on the caller's shell.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on built test binaries, daemon/client binaries, and e2e environment variables. Risks include inconsistent behavior with `hack/make` helpers, missing cleanup between suites, and stale legacy suite assumptions. E2E CI lanes validate it.
