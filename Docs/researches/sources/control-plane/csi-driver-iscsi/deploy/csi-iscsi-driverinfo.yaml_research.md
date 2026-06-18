## sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-driverinfo.yaml

Purpose: declares the CSI driver object for Kubernetes.

Control flow is Kubernetes declarative configuration: a `storage.k8s.io/v1` `CSIDriver` named `iscsi.csi.k8s.io` with `attachRequired: false` and both `Persistent` and `Ephemeral` lifecycle modes. There is no executable logic or local persistence.

Integration points are kubelet, external sidecars, and the node plugin DaemonSet. Risks include advertising ephemeral support even though controller operations are unimplemented and node-only behavior depends on volume attributes; attach is disabled so controller publish is skipped. Test signal is Pluto API-version checks and install script `kubectl apply`.
