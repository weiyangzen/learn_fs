# sources/control-plane/rook/pkg/operator/k8sutil/pvc_test.go

## Purpose
This test verifies conditional PVC expansion behavior.

## Important APIs, Types, and Functions
`TestExpandPVCIfRequired()` creates a desired/current PVC and storage class in a fake controller-runtime client, varies current and desired sizes, toggles `AllowVolumeExpansion`, calls `ExpandPVCIfRequired()`, then re-reads the PVC.

## Control Flow, State, and Persistence
All persistence is in the fake client object store. The same PVC object is reused across table cases with request size and storage-class expansion flags updated before each run.

## Dependencies and Integration Points
It uses Kubernetes PVC/storage-class APIs, resource quantity parsing, controller-runtime fake client, and testify.

## Risks
The assertion uses string comparison (`tc.currentPVCSize <= tc.desiredPVCSize`) to decide expected behavior, which happens to work for these values but is not a general quantity comparison. The test ignores the boolean return from `ExpandPVCIfRequired()`.

## Test Signals
Signals cover no-op equal size, successful growth when allowed, shrink ignored, and growth blocked when storage class expansion is false.
