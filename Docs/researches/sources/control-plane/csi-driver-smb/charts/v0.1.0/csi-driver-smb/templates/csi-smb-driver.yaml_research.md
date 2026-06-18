## sources/control-plane/csi-driver-smb/charts/v0.1.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the early SMB `CSIDriver` object for chart v0.1.0. It uses `storage.k8s.io/v1beta1` and hard-codes name `smb.csi.k8s.io`.

Important behavior is minimal: declare the CSIDriver and driver name without later fields such as attachRequired, podInfoOnMount, or lifecycle modes. State is a cluster-scoped beta API object. Dependencies are Kubernetes versions that still serve v1beta1 CSIDriver. Risks include incompatibility with modern clusters where v1beta1 is removed and lack of explicit inline/persistent lifecycle signaling. Test signal is Helm install on older clusters.
