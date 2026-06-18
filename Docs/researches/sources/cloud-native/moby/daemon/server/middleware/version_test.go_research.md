# sources/cloud-native/moby/daemon/server/middleware/version_test.go

## Purpose
Tests API version middleware validation, effective version propagation, error messages, and response headers.

## Important APIs, Types, And Functions
Tests call `NewVersionMiddleware`, `WrapHandler`, and `httputils.VersionFromContext`.

## Control Flow
Constructor tests check valid defaults and invalid ranges. Version tests wrap a handler that reads the context version, then run missing, minimum, too-old, and too-new route versions. Header tests assert `Server`, `Api-Version`, and `Ostype` are set even when version validation fails.

## State And Persistence
Uses local `httptest.ResponseRecorder` and request objects. No daemon state is involved.

## Dependencies And Integration Points
Depends on daemon config API version constants, runtime GOOS, gotest assertions, and HTTP testing.

## Risks And Edge Cases
Tests reuse a recorder across subcases in one function, so header state is cumulative but acceptable for the assertions made. They do not cover malformed version strings.

## Test Signals
Failures indicate changes to supported API range validation, context propagation, or headers required by clients.
