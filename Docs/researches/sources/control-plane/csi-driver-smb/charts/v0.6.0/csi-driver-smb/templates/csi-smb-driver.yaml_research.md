## sources/control-plane/csi-driver-smb/charts/v0.6.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.6.0 SMB CSIDriver object. It remains on `storage.k8s.io/v1beta1` and fixed driver name `smb.csi.k8s.io`.

State is beta cluster-scoped driver metadata. Dependencies are Kubernetes versions still serving v1beta1. Risks include install failure on newer clusters and missing explicit attach/lifecycle fields. Test signal is driver discovery after Helm install.
