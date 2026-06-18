# sources/cloud-native/containerd/internal/cri/util/util_test.go

## Purpose
Tests the main CRI utility behavior in `util.go`.

## Important APIs, Types, And Functions
The tests exercise `GenerateUserString`, `GetPassthroughAnnotations`, and `IsShimTTRPCClosed`, using CRI `Int64Value`, path-style patterns, and wrapped ttrpc errors.

## Control Flow
Table-driven cases compare expected user strings/errors, annotation maps filtered by runtime patterns, and boolean recognition of closed shim ttrpc errors.

## State And Persistence
No persisted state. Tests use in-memory maps and errors.

## Dependencies And Integration Points
Uses Go testing, CRI runtime API types, errdefs, ttrpc, and testify assertions.

## Risks
The tests do not cover `BuildLabels`, namespace context helpers, timeout registration, invalid label logging, or malformed annotation patterns.

## Test Signals
Strong signal for user-string edge cases and annotation glob semantics, with partial coverage of shim error classification.
