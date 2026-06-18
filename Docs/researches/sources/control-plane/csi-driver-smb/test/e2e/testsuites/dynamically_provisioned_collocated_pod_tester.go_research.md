# sources/control-plane/csi-driver-smb/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go

## Purpose
This testsuite validates that multiple dynamically provisioned SMB volumes can be used by pods, optionally forcing later pods onto the same node as the first pod.

## Important APIs, Types, And Functions
`DynamicallyProvisionedCollocatedPodTest` contains `CSIDriver`, `Pods`, `ColocatePods`, and storage-class parameters. `Run` is the sole entry point.

## Control Flow
The runner provisions volumes and pods one-by-one. When `ColocatePods` is true and a previous pod has established `nodeName`, it sets a node selector `{"name": nodeName}` on the next pod. Each pod is created, cleanup is deferred, and `WaitForRunning` confirms that it is live rather than waiting for command completion.

## State, Persistence, And Dependencies
State is Kubernetes resources plus the in-memory `nodeName` captured from the first scheduled pod. It depends on shared pod/PVC helpers and assumes nodes expose a `name` label matching `pod.Spec.NodeName`.

## Integration Points
Specs use this to exercise multi-pod or same-node behavior for SMB mounts. It integrates with dynamic provisioning and scheduler placement.

## Risks And Test Signals
The node selector can be brittle because Kubernetes commonly uses `kubernetes.io/hostname` rather than `name`. The test signal is pod Running state; it does not validate file contents or concurrent writes directly in this runner.
