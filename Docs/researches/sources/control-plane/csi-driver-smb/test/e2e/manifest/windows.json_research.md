<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/windows.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/windows.json

Purpose: ACS Engine/vlabs template for Windows e2e clusters using the default Windows runtime path.

Important configuration: Kubernetes orchestrator release is blank/parameterized. One Windows agent pool uses `Standard_D2s_v3`, 128 GB OS disk, AvailabilitySet, and Windows OS. Windows profile enables CSI proxy v1.0.2, SSH, and selects AKS Windows Server 2019 core image metadata. Linux master profile and service principal placeholders are included.

Control flow: Declarative cluster provisioning input.

State and persistence behavior: Creates Azure Windows Kubernetes infrastructure when used.

Dependencies and integration points: Supports Windows e2e tests that exercise CSI proxy SMB mount/unmount and Windows path behavior.

Risks: Hardcoded CSI proxy and Windows image versions may be stale. The embedded example password must be replaced by secure provisioning.

Test signals: Infrastructure support for Windows e2e lanes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/windows.json -->
