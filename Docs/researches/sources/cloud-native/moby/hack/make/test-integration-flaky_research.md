# sources/cloud-native/moby/hack/make/test-integration-flaky

## Purpose
Runs integration tests marked or selected as flaky, usually with repeat/retry behavior.

## Important APIs and Types
Uses `.integration-test-helpers`, `TESTFLAGS`, repeat controls, and flaky test filters.

## Control Flow, State, and Persistence
The script configures filters for flaky tests and executes them through the same daemon and environment isolation used by the main integration bundle.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on the integration helper library and test naming conventions. Risks include stale flaky classification, repeat loops masking deterministic failures, and long runtime. CI flaky lane behavior and failure reproduction are the signals.
