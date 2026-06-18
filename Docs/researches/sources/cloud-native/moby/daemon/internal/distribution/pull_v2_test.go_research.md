# sources/cloud-native/moby/daemon/internal/distribution/pull_v2_test.go

## Purpose
Tests selected Registry v2 pull helpers.

## APIs, Control Flow, and Integration
`TestNoMatchesErr` validates platform formatting for default host platform and explicit Windows/arm64/v8 platform. `TestPullSchema2Config` starts an HTTP registry-like test server and verifies config blob fetch retry behavior: immediate success, one 500 then success, EOF/panic then success, and unauthorized responses that should not retry. `testNewPuller` builds a token-authenticated puller against the test server.

## State, Dependencies, and Risks
State is an in-process HTTP server and atomic request counter. Tests validate digest-verifying config fetch and retry classification, but not layer downloads, manifest list platform matching, refstore updates, rootfs mismatch, or temp-file resume.
