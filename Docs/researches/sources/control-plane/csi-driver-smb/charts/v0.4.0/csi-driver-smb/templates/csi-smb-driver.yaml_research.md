## sources/control-plane/csi-driver-smb/charts/v0.4.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.4.0 SMB CSIDriver object with `storage.k8s.io/v1beta1` and fixed name.

State is beta cluster-scoped driver metadata. Dependencies are clusters still serving the beta API. Risks include API removal on modern Kubernetes and no attach/lifecycle flags. Test signal is install success and driver discovery.
