# sources/control-plane/csi-driver-nfs/charts/v4.10.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

Purpose: Optional Deployment for the external snapshot-controller.

Important APIs/types/functions: `apps/v1` `Deployment`; Helm gate `.Values.externalSnapshotter.enabled`; values for name, labels, annotations, replicas, priority class, resources, image, imagePullSecrets, and controller scheduling.

Control flow: Renders only when enabled. It creates a rolling-update Deployment with `minReadySeconds: 15`, Linux nodeSelector, optional controller affinity/tolerations, leader election args, and a security context dropping all capabilities.

State and persistence: Controller runtime state is leader-election leases and updates to VolumeSnapshot* resources.

Dependencies and integration points: Requires snapshot CRDs and RBAC from `rbac-snapshot-controller.yaml`.

Risks: Duplicates platform snapshot-controller if one already exists; uses controller scheduling values instead of separate snapshotter scheduling knobs. Test signals: render enabled/disabled and create a VolumeSnapshot.
