## sources/control-plane/csi-driver-nfs/test/e2e/dynamic_provisioning_test.go

Purpose: declares the main Ginkgo e2e scenarios for NFS dynamic provisioning. It builds `PodDetails`, `VolumeDetails`, and typed testsuite structs to exercise StorageClass parameters, mount options, read-only mounts, pod restart persistence, reclaim policy behavior, multiple PVs, subpath mounts, inline volumes, delete-retain/archive modes, and resizing.

Important flow: `BeforeEach` runs `test/utils/check_driver_pods_restart.sh`, then stores the framework client and namespace. Each `It` case constructs a testsuite such as `DynamicallyProvisionedCmdVolumeTest`, `CollocatedPodTest`, `DeletePodTest`, `ReclaimPolicyTest`, or `ResizeVolumeTest` and calls `Run(ctx, cs, ns)`.

State is cluster-level: StorageClasses, PVCs, PVs, Pods, Deployments, and the test NFS server share. Dependencies include `e2e_suite_test.go` globals for storage parameters and driver/server constants. Risks include long-running pods requiring cleanup defers, hard-coded `default` secret namespace, Windows command conversion only for selected commands, and a restart check that logs but no longer fails. Test signal is high because this file is the scenario matrix for real provisioning.
