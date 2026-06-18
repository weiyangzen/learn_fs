## sources/control-plane/csi-driver-smb/charts/v0.3.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.3.0 beta CSIDriver for SMB. It remains `storage.k8s.io/v1beta1` with hard-coded name `smb.csi.k8s.io`.

State is a cluster-scoped beta object. Dependencies are older Kubernetes versions and Helm install ordering. Risks include API removal in newer clusters and lack of explicit attach/lifecycle settings. Test signal is successful chart install and driver discovery.
