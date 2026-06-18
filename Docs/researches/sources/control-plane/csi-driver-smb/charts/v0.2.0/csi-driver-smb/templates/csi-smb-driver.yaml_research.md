## sources/control-plane/csi-driver-smb/charts/v0.2.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the SMB CSIDriver object for chart v0.2.0. Like v0.1.0, it uses `storage.k8s.io/v1beta1` and hard-codes `smb.csi.k8s.io`.

State is the beta CSIDriver object. Dependencies are Kubernetes clusters that still support v1beta1 CSIDriver. Risks include modern API removal and missing explicit lifecycle mode fields. Test signal is successful Helm install and driver discovery on older clusters.
