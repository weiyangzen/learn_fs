<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/e2e_test.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/e2e_test.go

Purpose: top-level Ginkgo/Kubernetes e2e harness for BeeGFS CSI driver-specific and upstream storage suites.
Important APIs/functions: flag registration for dynamic/static BeeGFS paths, global `beegfsDriver` and `beegfsDynamicDriver`, `SynchronizedBeforeSuite`, `SynchronizedAfterSuite`, `Describe`, and `Test`.
Control flow/state: before-suite loads a clientset, checks for orphaned mounts, reads the active driver ConfigMap, unmarshals `PluginConfig`, and injects per-filesystem configs into both driver objects. after-suite archives service logs before checking orphaned mounts again. `Test` creates the report directory and runs Ginkgo.
Dependencies/integration: depends on Kubernetes e2e framework, Ginkgo/Gomega, testing manifests FS, BeeGFS e2e utilities, and `csi-beegfs-config.yaml` ConfigMap data.
Risks/test signals: global mutable driver state relies on Ginkgo synchronized ordering; failure before log archival can reduce diagnostics; orphan-mount checks require SSH/provider setup and at least two nodes. Suite success includes no orphaned mounts before or after.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/e2e_test.go -->
