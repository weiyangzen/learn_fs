# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/values.yaml

Purpose: default values for the CephFS Helm chart, covering RBAC/service accounts, cluster config, KMS config, logging, `CSIDriver`, nodeplugin, provisioner, storage/snapshot/group-snapshot classes, optional Secret creation, `ceph.conf`, and internal socket/configmap names.

Important APIs/types/functions: no code APIs; the exported interface is the chart value schema. Key knobs include `csiConfig`, `encryptionKMSConfig`, `CSIDriver.fsGroupPolicy`, `nodeplugin.forcecephkernelclient`, kernel/fuse mount options, `provisioner.deployController`, sidecar images, `storageClass.fsName`, CephFS secret refs, and `driverName: cephfs.csi.ceph.com`.

Control flow: Helm templates consume these defaults to conditionally render service accounts, RBAC, DaemonSet/Deployment sidecars, metrics Services, StorageClass, SnapshotClass, GroupSnapshotClass, KMS/config ConfigMaps, and optional Secret.

State and persistence behavior: persistent configuration is Kubernetes object state plus CephFS subvolumes/snapshots created later by the driver. Secret values are disabled by default but include placeholder credentials when enabled.

Dependencies and integration points: integrates with Kubernetes CSI sidecars, CephFS mounters, Vault/KMS config, Prometheus metrics, kubelet plugin paths, and the Ceph-CSI `cephcsi` binary flags.

Risks: placeholder cluster IDs, filesystem names, and secrets must be replaced. `logLevel: 5` is verbose by default. Enabling generated Secrets with plaintext values is unsafe outside examples. Mount/kernel/fuse options can override runtime behavior globally. `externallyManagedConfigmap` shifts responsibility to the operator.

Test signals: mainly validated through Helm rendering, chart install tests, and CephFS e2e coverage that exercises provisioning, expansion, snapshots, and mount options.
