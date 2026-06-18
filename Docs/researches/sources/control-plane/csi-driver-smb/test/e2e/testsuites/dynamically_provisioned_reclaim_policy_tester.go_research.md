# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go

## Purpose
This testsuite validates SMB dynamic provisioning behavior for Kubernetes reclaim policies and SMB driver `onDelete` behavior.

## Important APIs, Types, And Functions
`DynamicallyProvisionedReclaimPolicyTest` holds the e2e dynamic driver, a list of `VolumeDetails`, a concrete `*smb.Driver`, and storage-class parameters. `Run` is the entry point.

## Control Flow
For each volume, it provisions a PVC/PV pair, defers StorageClass deletion manually, calls PVC cleanup, then checks retain behavior. If the PV reclaim policy is `Retain`, it waits for `Released`, deletes the bound PV, and invokes `smb.Driver.DeleteVolume` directly to remove backing SMB data.

## State, Persistence, And Dependencies
State is Kubernetes PV/PVC lifecycle and backend SMB directories. Unlike most tests, it uses the in-process SMB driver to delete backing storage after retained PV cleanup.

## Integration Points
The suite’s global `smbDriver` is passed into this test. It integrates Kubernetes reclaim-policy behavior with SMB driver DeleteVolume semantics.

## Risks And Test Signals
Direct driver cleanup bypasses Kubernetes controller flow and assumes `VolumeHandle` remains valid. StorageClass cleanup is manual because the cleanup returned by setup is ignored. Signals are PVC deletion, PV phase/deletion, and direct DeleteVolume success.
