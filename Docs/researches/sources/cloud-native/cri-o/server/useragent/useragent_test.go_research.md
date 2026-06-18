# sources/cloud-native/cri-o/server/useragent/useragent_test.go

## Purpose
Tests the high-level `useragent.Get` function.

## Important APIs, Types, And Functions
Ginkgo spec under `Useragent/Get` calls `useragent.Get()`.

## Control Flow
The test asserts no error and verifies the result contains `cri-o`, `os`, and `arch`.

## State And Persistence
Read-only test; no filesystem state.

## Dependencies And Integration Points
Depends on live build/version metadata through `internal/version.Get(false)`.

## Risks And Test Signals
Good smoke signal for basic User-Agent assembly. It does not assert Go version presence, token order, semver normalization, or invalid token filtering.
