<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.yaml -->
# sources/control-plane/ceph-csi/api/deploy/ocp/scc.yaml

Purpose: embedded OpenShift SCC manifest for Ceph CSI.
Important surface: allows privileged containers, hostNetwork, hostDir volumes, hostPorts, hostPID, hostIPC, SYS_ADMIN, RunAsAny/seLinux/fsGroup/supplementalGroups, selected volume types, and service account users for RBD, CephFS, NFS, and NVMe-oF plugin/provisioners.
Control flow/state: rendered with `.Namespace` and optional `.Prefix` by `NewSecurityContextConstraintsYAML`.
Dependencies/integration: OpenShift SCC admission and service account names from deployment artifacts.
Risks/test signals: broad privileges are required for CSI but high impact; missing a service account blocks pods under SCC admission. Unit tests assert prefix/name/user-prefix behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.yaml -->
