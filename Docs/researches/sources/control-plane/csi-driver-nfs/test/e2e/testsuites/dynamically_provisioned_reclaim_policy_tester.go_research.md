## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_reclaim_policy_tester.go

Purpose: validates dynamic PV behavior for `Delete` and `Retain` reclaim policies. It provisions volumes, deletes the PVC through the common cleanup path, then performs policy-specific checks.

Important API: `DynamicallyProvisionedReclaimPolicyTest.Run`. For `Delete`, `tpvc.Cleanup` waits for PV deletion. For `Retain`, the test waits for the PV to enter `Released`, deletes the bound PV manually, and intentionally skips backing NFS directory cleanup because the in-process controller cannot resolve the test cluster NFS service.

State is PV/PVC lifecycle state and, for Retain, potentially retained backing directories. Dependencies include the NFS controller server type, though actual `DeleteBackingVolume` is commented out. Risks include leaked backing data for Retain tests, reliance on PV phase transitions, and one-volume-at-a-time execution. Test signal covers Kubernetes reclaim policy integration.
