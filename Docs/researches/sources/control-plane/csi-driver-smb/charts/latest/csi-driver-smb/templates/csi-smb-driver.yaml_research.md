## sources/control-plane/csi-driver-smb/charts/latest/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the cluster-scoped `CSIDriver` object for SMB. It identifies the driver name, optional labels, and driver behavior to Kubernetes.

Important spec fields: `attachRequired: false`, `podInfoOnMount: true`, and `volumeLifecycleModes` containing `Persistent` plus conditional `Ephemeral` when `.Values.feature.enableInlineVolume` is true.

State is a Kubernetes storage.k8s.io/v1 CSIDriver object. Dependencies include values for driver name/labels and cluster support for CSI inline volumes. Risks include driver name changes breaking existing PVs/StorageClasses, enabling inline volume RBAC requirements, and cluster-scoped object ownership conflicts across releases. Test signal is Helm install and Kubernetes storage tests that require CSIDriver discovery.
