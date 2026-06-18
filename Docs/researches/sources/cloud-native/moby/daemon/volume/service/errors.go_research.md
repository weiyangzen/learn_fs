# sources/cloud-native/moby/daemon/volume/service/errors.go

## Purpose
Typed error definitions and operation wrapper for volume service/store failures.

## Important APIs, Types, And Functions
Defines `errVolumeInUse`, `errNoSuchVolume`, and `errNameConflict`; marker types `conflictError` and `notFoundError`; `OpErr` with `Error`, `Cause`, and `Unwrap`; classifiers `IsInUse`, `IsNotExist`, and `IsNameConflict`.

## Control Flow
Store methods wrap driver/store failures in `OpErr` with operation/name/ref context. Classifiers use `errors.Is` and legacy `Cause()` recursion to match typed sentinel errors through wrappers.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by API service methods to map internal errors to errdefs conflict/not-found responses and by tests to assert correct behavior.

## Risks
Error message formatting includes refs and is user-visible. Maintaining both `Unwrap` and legacy `Cause` support matters for existing error utilities.

## Test Signals
Store and service tests assert `IsInUse`, `IsNotExist`, `IsNameConflict`, conflict errdefs, and formatted operation errors.
