# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v4.10.0 CSIDriver manifest.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; driver name plus inline-volume and FSGroup feature gates.

Control flow: Renders persistent lifecycle mode, optional ephemeral mode, optional `fsGroupPolicy: File`, and `attachRequired: false`.

State and persistence: Cluster-scoped CSI driver capability object.

Dependencies and integration points: Must match StorageClasses, snapshot classes, and controller/node driver args.

Risks: Capability mismatch can cause kubelet scheduling/mount failures. Test signals: dry-run and workload mount tests for fsGroup/inline options.
