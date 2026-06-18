## sources/control-plane/csi-driver-nfs/test/e2e/testsuites/testsuites.go

Purpose: implements the shared Kubernetes object lifecycle for the NFS e2e tests. It creates and deletes StorageClasses, PVCs, Pods, Deployments, validates bound PVs, polls pod exec output, removes finalizers, and exposes CSI-specific cleanup hooks.

Important APIs include `TestStorageClass`, `TestPersistentVolumeClaim`, `TestPod`, `TestDeployment`, `NewTestPersistentVolumeClaim`, `generatePVC`, `WaitForBound`, `ValidateProvisionedPersistentVolume`, `NewTestPod`, `SetupVolume`, `SetupRawBlockVolume`, `Create`, `WaitForSuccess`, `WaitForRunning`, `NewTestDeployment`, `PollForStringInPodsExec`, `DeletePodAndWait`, `DeleteBackingVolume`, `SetupVolumeMountWithSubpath`, and `SetupCSIInlineVolume`.

State is live cluster state plus cached object pointers on the test structs. Dependencies include client-go, Kubernetes e2e framework helpers, deployment/pod/pv utilities, `kubectl` exec wrapper, CSI `DeleteVolumeRequest`, and NFS controller server. Risks include patching away PV finalizers as a workaround, process-level `context.Background` for backing deletion, fixed timeouts, direct field indexing into node affinity, and Linux node selectors in pod/deployment templates. Test signal is broad because failures here reflect lifecycle and cleanup correctness across all scenarios.
