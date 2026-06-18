## sources/control-plane/csi-driver-nfs/test/e2e/driver/driver.go

Purpose: defines the e2e driver abstraction used by NFS CSI storage tests. `PVTestDriver` composes dynamic provisioning and pre-provisioned volume capabilities so higher-level test suites can create StorageClasses and PVs without hard-coding driver implementation details.

Important APIs are `DynamicPVTestDriver.GetDynamicProvisionStorageClass`, `PreProvisionedVolumeTestDriver.GetPersistentVolume`, `GetPreProvisionStorageClass`, and shared helper `getStorageClass`. The helper fills default reclaim policy `Delete`, default binding mode `Immediate`, and always enables `AllowVolumeExpansion`.

State is Kubernetes object state represented in memory until tests call the API server. Dependencies are core/v1 and storage/v1 Kubernetes APIs. Integration points are `nfs_driver.go` and every testsuite setup method in `test/e2e/testsuites`. Risks include defaulting expansion to true for all StorageClasses and passing caller-provided parameter maps by reference. Test signal is indirect through dynamic provisioning, reclaim, resize, and topology scenarios.
