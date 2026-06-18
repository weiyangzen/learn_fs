# sources/cloud-native/moby/client/utils_test.go

## Purpose
Tests platform JSON encoding and race safety for cancelable read closers.

## APIs, Types, And Functions
`TestEncodePlatforms` checks `encodePlatforms` with OCI platform values. `TestNewCancelReadCloserRace` exercises `newCancelReadCloser` with concurrent cancellation, reading, and closing behavior.

## Control Flow, State, And Integration
The platform test compares JSON output. The race test uses contexts and readers to ensure cancel-triggered close does not race or panic while reads are active. State is limited to test-local readers and goroutines.

## Risks And Test Signals
Signals are important because `newCancelReadCloser` protects log and stream APIs from goroutine leaks and data races. Running tests with `-race` would increase confidence in the concurrency path.
