# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csidriver-crd.yaml

Purpose: renders the Kubernetes `CSIDriver` object for the RBD driver.

Important APIs/types/functions: object name comes from `.Values.driverName`; spec sets `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy`, and `seLinuxMount`.

Control flow: installed once per driver name so Kubernetes can discover CSI driver capabilities and pass pod context to node publish operations.

State and persistence behavior: cluster-scoped Kubernetes API object. It affects scheduling/mount behavior but stores no driver data.

Dependencies and integration points: consumed by kubelet, external-attacher, Kubernetes storage controllers, and Ceph-CSI node publish logic that expects pod info.

Risks: driver name must match sidecar flags and StorageClass `provisioner`. Incorrect `fsGroupPolicy` or `seLinuxMount` changes security semantics for mounted volumes.

Test signals: Kubernetes CSI conformance, chart rendering, and e2e pod mount tests expose mismatches.
