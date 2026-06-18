# sources/control-plane/csi-driver-smb/test/e2e/testsuites/testsuites.go

## Purpose
This is the shared e2e resource helper library for SMB CSI tests. It wraps Kubernetes StorageClass, PV, PVC, Pod, Deployment, and Secret creation/cleanup, validates dynamic provisioning results, and provides polling/logging utilities.

## Important APIs, Types, And Functions
Key wrappers include `TestStorageClass`, `TestPreProvisionedPersistentVolume`, `TestPersistentVolumeClaim`, `TestDeployment`, `TestPod`, and `TestSecret`. Constructors include `NewTestStorageClass`, `NewTestPersistentVolumeClaim`, `NewTestPersistentVolumeClaimWithDataSource`, `NewTestDeployment`, `NewTestPod`, and `NewTestSecret`. Important methods include `Create`, `Cleanup`, `WaitForBound`, `ValidateProvisionedPersistentVolume`, `DeleteBoundPersistentVolume`, `DeleteBackingVolume`, `WaitForSuccess`, `WaitForRunning`, `WaitForFailure`, `WaitForFailedMountError`, `SetupVolume`, `SetupRawBlockVolume`, `SetupCSIInlineVolume`, `SetupVolumeMountWithSubpath`, `PollForStringInPodsExec`, and `DeletePodAndWait`.

## Control Flow
StorageClass/PV/PVC helpers create resources through client-go and validate expected capacity, access modes, claim references, reclaim policy, mount options, and topology/affinity. PVC cleanup deletes the claim, removes PV finalizers for CSI delete cases as a workaround, waits for PV deletion under Delete reclaim policy, and waits for PVC disappearance. Pod/Deployment helpers generate Linux or Windows pod specs, attach volumes, create resources, wait for pod states, collect logs, and delete resources. Exec polling launches goroutines per pod and aggregates errors.

## State, Persistence, And Dependencies
All state is Kubernetes API state plus backend volume state. `DeleteBackingVolume` calls `smb.Driver.DeleteVolume` directly. The file depends heavily on Kubernetes e2e framework packages, `client-go`, CSI types, SMB driver types, Ginkgo/Gomega, and Kubernetes image utilities.

## Integration Points
The individual testsuite runners and suite specs depend on this file for all resource operations. It integrates with kubelet events for FailedMount detection, kubectl exec via e2e framework, and Deployment utilities.

## Risks And Test Signals
Risks include mutating PV finalizers, hard-coded Windows images/tolerations, fixed timeouts, direct kubelet event reason matching, and helper argument order in `waitForPersistentVolumeClaimDeleted` being easy to misuse. The strongest signals are PVC/PV object validation, pod phase transitions, Deployment readiness, log collection, and exec output polling.
