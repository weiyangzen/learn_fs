## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/dynamically_provisioned_pod_with_multiple_pv.go

Purpose: validates one pod can consume multiple dynamically provisioned PVs. It is used by the top-level test that creates six PVCs and mounts them into a single pod.

Important API: `DynamicallyProvisionedPodWithMultiplePVsTest.Run`. For each pod definition, it calls `SetupWithDynamicMultipleVolumes`, defers all PVC/StorageClass cleanup, creates the pod, defers pod cleanup, and waits for command success.

State is a set of StorageClasses/PVCs/PVs and a single consuming pod. Dependencies include `specs.go` logic that decides between filesystem mounts and raw block device setup based on `VolumeMode`. Risks include creating one StorageClass per volume, which is heavier than needed, and validating only command success on the first mount path unless the command checks all mounts. Test signal covers multi-volume attachment/mount plumbing.
