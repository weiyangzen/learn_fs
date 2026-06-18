<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.go

Purpose: renders the Kubernetes `CSIDriver` object for the NFS CSI driver.
Important APIs/functions: `CSIDriverValues`, `CSIDriverDefaults`, `NewCSIDriver`, and `NewCSIDriverYAML`; embeds `csidriver.yaml`, templates `.Name`, and unmarshals into `storagev1.CSIDriver`.
Control flow/state: parse/execute template on each call; no persistent state.
Dependencies/integration: used by automation that wants typed Kubernetes objects or YAML for installing the driver.
Risks/test signals: default driver name is part of the external CSI identity contract; changing attach/podInfo/fsGroup/seLinux settings in YAML changes cluster behavior. Unit tests catch basic rendering/unmarshal failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.go -->
