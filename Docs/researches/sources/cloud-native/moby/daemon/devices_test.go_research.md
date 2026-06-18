# sources/cloud-native/moby/daemon/devices_test.go

## Purpose
Tests GPU vendor selection priority and error handling.

## Important APIs, Types, And Functions
- `TestGetFirstAvailableVendor` table-tests NVIDIA, AMD, nil vendor list, unknown vendors, and mixed vendor input.

## Control Flow
The test calls `getFirstAvailableVendor` for each vendor slice and asserts either the selected vendor or exact error string.

## State And Persistence
No state is changed.

## Dependencies And Integration Points
Covers `devices.go` and supports AMD CDI discovery logic that needs a known vendor from a CDI cache.

## Risks And Edge Cases
It does not test global driver registration or OCI spec mutation. Mixed-vendor expected result documents NVIDIA priority.

## Test Signals
Failures indicate changed vendor priority or incompatible error behavior for empty/unknown CDI vendor lists.
