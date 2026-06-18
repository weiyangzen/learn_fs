# sources/cloud-native/cri-o/server/version_test.go

## Purpose
Tests the server CRI `Version` method.

## Important APIs, Types, And Functions
Ginkgo spec calls `sut.Version(context.Background(), nil)` using the shared server fixture.

## Control Flow
Setup constructs the mocked server, then the test verifies no error, non-nil response, non-empty CRI version and runtime name, and runtime API version equal to `v1`.

## State And Persistence
Uses temporary server fixture state only.

## Dependencies And Integration Points
Exercises `version.go` through the real server object but mocked storage/config dependencies.

## Risks And Test Signals
Does not assert exact `RuntimeVersion`, `Version`, or `RuntimeName` values. The duplicate runtime-name assertion likely meant to check runtime-version.
