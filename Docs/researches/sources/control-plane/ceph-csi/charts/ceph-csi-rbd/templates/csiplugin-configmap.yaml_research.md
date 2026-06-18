# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/csiplugin-configmap.yaml

Purpose: renders the Ceph-CSI cluster configuration ConfigMap unless externally managed.

Important APIs/types/functions: gated by `not .Values.externallyManagedConfigmap`; writes `config.json` from `toJson .Values.csiConfig` and `cluster-mapping.json` from `toJson .Values.csiMapping`.

Control flow: driver pods mount this ConfigMap and read cluster monitors, per-driver network namespace paths, read-affinity config, RBD mirror counts, and disaster-recovery cluster/pool/filesystem mappings.

State and persistence behavior: Kubernetes ConfigMap persists cluster connection metadata. It does not hold Ceph auth secrets.

Dependencies and integration points: integrated with nodeplugin/provisioner mounts, `configMapName`, optional `configMapKey`, and Ceph-CSI internal config loading.

Risks: empty default config means no usable Ceph cluster until operators populate values or manage the ConfigMap externally. Cluster IDs must match StorageClass/SnapshotClass parameters and should remain immutable.

Test signals: driver startup, provisioning attempts, and config reload behavior validate this object.
