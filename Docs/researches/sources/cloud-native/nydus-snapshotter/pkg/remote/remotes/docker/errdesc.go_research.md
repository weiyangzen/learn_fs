# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/errdesc.go

## Purpose
Registers Docker distribution error descriptors and exposes descriptor lookup by group or globally.

## Important APIs, Types, And Functions
`Register`, `GetGroupNames`, `GetErrorCodeGroup`, `GetErrorAllDescriptors`, and variables such as `ErrorCodeUnknown`, `ErrorCodeUnsupported`, `ErrorCodeUnauthorized`, `ErrorCodeDenied`, `ErrorCodeUnavailable`, and `ErrorCodeTooManyRequests`.

## Control Flow
Package initialization calls `Register` for standard `errcode` descriptors. `Register` assigns monotonically increasing numeric codes, panics on duplicate values or codes, updates maps by code, value, and group, and returns the assigned `ErrorCode`. Query functions sort group names and descriptors by value.

## State And Persistence
Maintains process-global maps and `nextCode`, guarded by `registerLock` for registration. State is in memory only.

## Dependencies And Integration Points
Consumed by `errcode.go` for string/marshal behavior and by registry error decoding in fetch paths.

## Risks And Edge Cases
Registration panics on duplicates, which is acceptable during init but risky for dynamic extension. `GetErrorCodeGroup` sorts the backing slice in place, so callers should not rely on previous group order.

## Test Signals
No dedicated tests in this subset. Runtime coverage appears through JSON error decoding in fetcher tests.
