# sources/control-plane/ceph-csi/deploy/csi-config-map-sample.yaml

Purpose: annotated sample `ceph-csi-config` ConfigMap showing cluster config and cluster-mapping JSON shapes.

Important APIs/types/functions: documents `clusterID`, `monitors`, RBD options (`netNamespaceFilePath`, `radosNamespace`, `mirrorDaemonCount`, node-publish secret), CephFS options (`subvolumeGroup`, mount options, rados namespace), NFS namespace path, read affinity labels, and DR mappings for cluster IDs, RBD pool IDs, and CephFS FSC IDs.

Control flow: operators copy/modify this data for real deployments; driver pods read it from mounted ConfigMap.

State and persistence behavior: sample only, but when applied it persists cluster connection metadata in Kubernetes.

Dependencies and integration points: StorageClass/SnapshotClass `clusterID` must match entries here; read-affinity and network namespace settings affect node operations.

Risks: sample JSON contains placeholders and illustrative ellipses, so it is not directly valid production JSON as-is. Adding rados namespaces to active configs can break existing volume metadata lookup.

Test signals: config parsing and provisioning/mount workflows.
