## sources/control-plane/csi-driver-nfs/test/e2e/driver/nfs_driver.go

Purpose: implements the generic e2e PV driver interfaces for the NFS CSI driver. `InitNFSDriver` reads `NFS_CSI_DRIVER` and falls back to `nfs.DefaultDriverName`, making tests usable with alternate provisioner names.

Important APIs: `NFSDriver`, `normalizeProvisioner`, `GetDynamicProvisionStorageClass`, `GetPreProvisionStorageClass`, `GetPersistentVolume`, and `GetParameters`. StorageClass methods create generated names from namespace and driver name; PV creation builds a CSI PV with size, fs type, volume handle, optional node stage secret, and the legacy `pv.kubernetes.io/provisioned-by` annotation.

State is generated Kubernetes object metadata and environment-dependent driver name. Dependencies include the NFS package constants, Kubernetes core/storage APIs, resource parsing, and klog. Risks include a typo in the pre-provisioned PV generateName, inconsistent normalization in `GetPreProvisionStorageClass`, and unused/default Azure-like `skuName` parameters. Test signal comes from all e2e suites that instantiate `driver.InitNFSDriver`.
