## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_collocated_pod_tester.go

Purpose: verifies multiple dynamically provisioned NFS-backed pods can run concurrently, optionally forcing later pods onto the same node as the first one.

Important API: `DynamicallyProvisionedCollocatedPodTest.Run`. It creates each pod with dynamic PVCs, optionally sets `NodeSelector` to `{"name": nodeName}` after the first pod, creates the pod, waits for running state, and records `Spec.NodeName` for later colocation.

State is live running pods and PVC/PV resources left until deferred cleanup. Dependencies are `PodDetails.SetupWithDynamicVolumes`, `TestPod.SetNodeSelector`, and Kubernetes scheduler/node labels. Risks include assuming nodes carry a `name` label matching `Spec.NodeName`, not verifying actual file writes after pods run, and cleanup being delayed until all pods are running. Test signal is useful for RWX-like concurrent mount scheduling but weaker for data correctness.
