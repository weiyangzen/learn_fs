# sources/cloud-native/moby/hack/make/test-integration

## Purpose
Runs the main Go integration test suite.

## Important APIs and Types
Sources `.integration-test-helpers` and calls the standard integration runner.

## Control Flow, State, and Persistence
The script delegates daemon setup, filter setup, suite binary building, environment isolation, execution, and cleanup to shared helpers.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `hack/make/.integration-*`, Go test tooling, and a runnable daemon. Risks are inherited from shared helpers: stale daemon state, incorrect filters, and environment loss. The suite's pass/fail result is the validation signal.
