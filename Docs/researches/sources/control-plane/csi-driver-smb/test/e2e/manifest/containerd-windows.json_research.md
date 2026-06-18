<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/containerd-windows.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/containerd-windows.json

Purpose: ACS Engine/vlabs template for Windows e2e clusters using containerd.

Important configuration: Kubernetes orchestrator release is parameterized/blank, `kubernetesConfig` sets `containerRuntime: containerd`, disables managed identity, and supplies a Windows containerd binary URL. One Windows agent pool uses `Standard_D4s_v3`, 128 GB OS disk, AvailabilitySet, and Windows OS type. Windows profile enables CSI proxy v1.1.1, SSH, and selects `2019-datacenter-core-ctrd-2104` image metadata.

Control flow: Consumed declaratively by cluster creation tooling; placeholders for SSH key and service principal are blank.

State and persistence behavior: Creates Azure infrastructure when used by the e2e environment.

Dependencies and integration points: Integrates with Windows CSI proxy, ACS Engine vlabs schema, Azure credentials, and Windows containerd artifacts.

Risks: Hardcoded image versions and binary URLs can age out. The placeholder admin password is unsuitable for production and must be replaced/handled by test tooling.

Test signals: Supports Windows containerd e2e lanes that exercise CSI proxy and HostProcess-related paths.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/containerd-windows.json -->
