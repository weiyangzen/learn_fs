## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/rbac-csi-smb.yaml

Purpose: renders service accounts and RBAC for SMB CSI controller and node components when enabled by values. It covers external provisioner, external resizer, and optional node secret access for inline volumes.

Important resources: controller and node ServiceAccounts, `smb-external-provisioner-role` with PV/PVC/StorageClass/CSI node/node/event/lease/secret reads, provisioner binding, `smb-external-resizer-role` with PV/PVC status/event/lease privileges, resizer binding, and conditional node secret role/binding when inline volumes are enabled.

State is cluster-scoped RBAC plus namespace service accounts. Dependencies include release namespace, sidecar permission requirements, and `.Values.rbac.name`. Risks include broad secret `get` permissions, cluster role naming collisions across releases, missing RBAC when service accounts are externally managed, and inline-volume secret access exposure. Test signal is provisioning/resizing failures with RBAC denial events.
