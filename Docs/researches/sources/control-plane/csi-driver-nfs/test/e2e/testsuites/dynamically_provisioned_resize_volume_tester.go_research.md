## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_resize_volume_tester.go

Purpose: verifies dynamic NFS PVC expansion is reflected in PVC request state and PV capacity. It first mounts and exercises the volume, then increases the requested storage by one GiB.

Important API: `DynamicallyProvisionedResizeVolumeTest.Run`. It creates a pod with dynamic volumes, waits for command success, reads the first PVC from the pod volume list, modifies `Spec.Resources.Requests["storage"]`, updates the PVC, sleeps 30 seconds, then compares the new PVC request and PV capacity.

State is Kubernetes PVC/PV storage size state. Dependencies include client-go, resource quantities, and the StorageClass default `AllowVolumeExpansion=true`. Risks include fixed sleep instead of polling resize conditions, string-based PV/PVC size comparison with `"Gi"` appended, ignoring errors on PV get, and only checking the first volume. Test signal covers controller expansion at a smoke-test level.
