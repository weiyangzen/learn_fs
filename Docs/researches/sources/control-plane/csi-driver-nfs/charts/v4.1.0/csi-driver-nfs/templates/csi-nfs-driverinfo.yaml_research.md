# sources/control-plane/csi-driver-nfs/charts/v4.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v4.1.0 CSIDriver registration.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; driver name and feature gates for inline volumes and FSGroup policy.

Control flow: Same GA CSIDriver flow as v4.0.0: persistent mode always, optional ephemeral mode, optional `fsGroupPolicy: File`.

State and persistence: Cluster driver capability state.

Dependencies and integration points: Controller/node driver `--drivername`, StorageClass provisioner, kubelet volume handling.

Risks: Capability flags must match actual driver support and target Kubernetes version. Test signals: server-side dry-run and workload tests for fsGroup and optional inline volumes.
