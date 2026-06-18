<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux-vmss.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/linux-vmss.json

Purpose: ACS Engine/vlabs Linux VMSS cluster template for e2e runs.

Important configuration: Kubernetes 1.22, containerd, Azure network plugin, cloud controller manager, disabled Azure disk/file CSI addons, rate limits, `DelegateFSGroupToCSIDriver=true`, and admission plugins including `AlwaysPullImages`. The agent pool uses VMSS availability and `Standard_DS2_v2`.

Control flow: Declarative provisioning input with placeholders for DNS prefix, SSH key, client ID, and secret.

State and persistence behavior: Creates Azure VMSS-based Kubernetes resources when applied.

Dependencies and integration points: Intended for Linux e2e lanes, especially features needing FSGroup delegation coverage.

Risks: Version and distro defaults may become stale. Missing managed identity means service principal placeholders must be valid.

Test signals: Infrastructure signal for Linux VMSS e2e coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux-vmss.json -->
