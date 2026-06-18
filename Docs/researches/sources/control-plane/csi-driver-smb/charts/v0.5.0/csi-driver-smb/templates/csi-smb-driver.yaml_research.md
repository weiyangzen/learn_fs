## sources/control-plane/csi-driver-smb/charts/v0.5.0/csi-driver-smb/templates/csi-smb-driver.yaml

Purpose: renders the v0.5.0 SMB CSIDriver object. It still uses `storage.k8s.io/v1beta1` with fixed name `smb.csi.k8s.io`.

State is beta cluster metadata. Dependencies are Kubernetes versions supporting the beta API. Risks include incompatibility with newer Kubernetes and lack of attach/lifecycle declarations. Test signal is chart install and CSI driver discovery.
