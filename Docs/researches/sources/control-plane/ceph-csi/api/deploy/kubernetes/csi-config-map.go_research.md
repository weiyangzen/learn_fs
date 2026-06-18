<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/csi-config-map.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/csi-config-map.go

Purpose: shared data model for generated CSI config-map JSON.
Important APIs/types: `ClusterInfo`, `CephFS`, `RBD`, `NFS`, and `ReadAffinity` structs with JSON tags; embeds Kubernetes `corev1.SecretReference` for controller/node secret references.
Control flow/state: pure type definitions, no functions or persistence.
Dependencies/integration: consumed by cephfs/rbd/nfs `NewCSIConfigMap*` helpers and external automation building `config.json`.
Risks/test signals: zero values serialize into config JSON when callers pass uninitialized fields; struct tags form a compatibility contract with driver config parsing. Tests in subpackages verify only basic rendering, not semantic config validity.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/csi-config-map.go -->
