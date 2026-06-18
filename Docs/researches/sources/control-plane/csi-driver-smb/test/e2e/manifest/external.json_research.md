<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/external.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/external.json

Purpose: ACS Engine/vlabs Linux cluster template for an "external" e2e environment variant.

Important configuration: Kubernetes 1.22, Azure network plugin, containerd runtime, cloud controller manager, rate limits, `DelegateFSGroupToCSIDriver=true`, admission plugins including `AlwaysPullImages`, and disabled in-tree Azure disk/file CSI addons. One Linux agent pool uses `Standard_DS2_v2`; SSH key, client ID, and secret are placeholders.

Control flow: Declarative template consumed by cluster provisioning.

State and persistence behavior: Creates Azure cluster resources when used.

Dependencies and integration points: Supports e2e tests that depend on external driver deployment rather than built-in Azure CSI addons.

Risks: Kubernetes 1.22 and template schema may be old relative to current Azure support. Placeholders must be substituted correctly.

Test signals: Provides infrastructure for Linux e2e lanes with external CSI driver behavior and FSGroup delegation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/external.json -->
