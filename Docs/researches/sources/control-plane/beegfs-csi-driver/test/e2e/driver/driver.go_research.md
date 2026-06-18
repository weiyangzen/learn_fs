<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/driver/driver.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/driver/driver.go

Purpose: BeeGFS implementation of Kubernetes storage e2e `TestDriver`, `DynamicPVTestDriver`, and pre-provisioned driver interfaces.
Important APIs/types/functions: `baseBeegfsDriver`, `BeegfsDriver`, `BeegfsDynamicDriver`, `GetDriverInfo`, `PrepareTest`, `GetDynamicProvisionStorageClass`, `CreateVolume`, `GetPersistentVolumeSource`, `SetStorageClassParams`, `SetFSIndex`, `SetFSIndexForRDMA`, and `SetPerFSConfigs`.
Control flow/state: driver instances hold mutable `perFSConfigs`, `fsIndex`, and optional extra StorageClass parameters. Dynamic provisioning emits StorageClasses with `sysMgmtdHost` and `volDirBasePath`; pre-provisioned volumes create CSI PV sources whose handle is a BeeGFS URL built from selected FS config and static path.
Dependencies/integration: integrates with BeeGFS operator API config, `pkg/beegfs.NewBeegfsURL`, Kubernetes e2e storage framework, and CSI driver name `beegfs.csi.netapp.com`.
Risks/test signals: `fsIndex` is intentionally unchecked and panics/fails if tests set it out of range; mutable extra parameters must be unset after tests; capability flags control which upstream Kubernetes suites actually run. Compile-time interface assertions are the first signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/driver/driver.go -->
