<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/linux.json

Purpose: ACS Engine/vlabs Linux cluster template for older/default Linux e2e runs.

Important configuration: Kubernetes 1.17, managed identity, cloud controller manager, Azure network plugin, containerd, cloud-provider rate limits, disabled Azure disk/file CSI addons, one VMSS Ubuntu 18.04 agent pool, and placeholders for DNS prefix, SSH key, client ID, and secret.

Control flow: Declarative template consumed by provisioning scripts.

State and persistence behavior: Creates Azure Linux Kubernetes infrastructure when used.

Dependencies and integration points: Supports compatibility e2e runs on older Kubernetes/containerd/Ubuntu combinations.

Risks: Kubernetes 1.17 and Ubuntu 18.04 are old and may no longer be supported in modern Azure environments. Placeholder substitution is required.

Test signals: Legacy Linux e2e infrastructure coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux.json -->
