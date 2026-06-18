<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/driver/smb_driver.go -->
# sources/control-plane/csi-driver-smb/test/e2e/driver/smb_driver.go

Purpose: SMB-specific implementation of the e2e test driver interfaces.

Important APIs/types/functions: `SMBDriverNameVar` (`SMB_CSI_DRIVER`) overrides the provisioner. `SMBDriver` stores the driver name. `InitSMBDriver` defaults to `smb.DefaultDriverName` and logs the selected driver. `normalizeProvisioner` replaces `/` with `-` for generated object names. Methods build dynamic StorageClasses, pre-provisioned StorageClasses, and CSI PersistentVolumes. `GetParameters` returns default `skuName: Standard_LRS`.

Control flow: Dynamic and pre-provisioned StorageClass methods compose namespace/provisioner into `GenerateName` and delegate to `getStorageClass`. `GetPersistentVolume` defaults reclaim policy to Retain, optionally sets `NodeStageSecretRef`, and adds the legacy provisioner annotation.

State and persistence behavior: Pure Kubernetes object construction; cluster persistence occurs in testsuites.

Dependencies and integration points: Integrates package SMB constants, Kubernetes API types, resource parsing, and e2e tests. The PV attributes and secret references connect test objects to node/controller behavior.

Risks: `GetPreProvisionStorageClass` does not normalize provisioner in `generateName`, unlike dynamic and PV paths, so provisioner names containing `/` could produce invalid generated names. A spelling typo in `preprovsioned` affects generated PV names only.

Test signals: Exercised by all e2e dynamic/pre-provisioned tests but not unit-tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/driver/smb_driver.go -->
