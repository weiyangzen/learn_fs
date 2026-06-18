# sources/cloud-native/moby/daemon/pkg/oci/caps/utils_other.go

## Purpose
This non-Linux file provides a no-op capability initializer for platforms without Linux capabilities.

## Important APIs, Types, And Functions
`initCaps()` is defined under build tag `!linux` and intentionally does nothing.

## Control Flow
Calls to shared capability APIs on non-Linux platforms leave `allCaps` and `knownCaps` at zero values.

## State, Persistence, And Dependencies
No state is initialized and there are no dependencies.

## Integration Points
This allows the shared caps package to compile on Windows and other non-Linux targets while Linux-only callers are build constrained elsewhere.

## Risks And Edge Cases
If shared capability APIs are used unexpectedly on non-Linux, empty/nil capability state may lead to empty results or nil map behavior. Current usage expects Linux-specific capability manipulation.

## Test Signals
No direct tests in this subset.
