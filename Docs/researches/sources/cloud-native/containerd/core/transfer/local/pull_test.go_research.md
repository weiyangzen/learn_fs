# sources/cloud-native/containerd/core/transfer/local/pull_test.go

## Purpose
This file unit-tests platform and snapshotter matching for pull-time unpack selection.

## Important APIs, Types, and Functions
`TestGetSupportedPlatform` builds supported `unpack.Platform` entries and checks `getSupportedPlatform` results for exact platform/snapshotter, no-match, and default snapshotter fallback cases.

## Control Flow
Each table case calls `getSupportedPlatform`, asserts the boolean match, verifies nil platform behavior on no match, and checks snapshotter and matcher compatibility on match.

## State and Persistence
No persistence. Inputs are in-memory platform matchers and unpack configurations.

## Dependencies and Integration Points
Uses `platforms`, `transfer.UnpackConfiguration`, `unpack.Platform`, and `defaults.DefaultSnapshotter`. The behavior feeds `pull.go` and `import.go` unpack decisions.

## Risks
The test set covers representative Linux/default cases but not multiple non-default snapshotter ordering beyond fallback preference.

## Test Signals
Confirms exact snapshotter match, default fallback, platform mismatch rejection, and nil platform on failed match.
