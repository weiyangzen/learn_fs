# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-snapshot-controller.yaml

Purpose: Optional external snapshot-controller Deployment for 4.11.0.

Important APIs/types/functions: `Deployment` gated by `.Values.externalSnapshotter.enabled`; snapshot-controller image settings, replicas, labels/annotations, priority class, resources, imagePullSecrets, and controller scheduling values.

Control flow: Renders a Linux Deployment with leader election args and `minReadySeconds: 15`; optional affinity/tolerations follow controller settings.

State and persistence: Runtime leader-election leases and updates to VolumeSnapshot resources.

Dependencies and integration points: Snapshot CRDs and RBAC snapshot-controller template.

Risks: Can duplicate an existing cluster snapshot-controller and uses shared controller scheduling knobs. Test signals: enabled render, controller startup, and VolumeSnapshot reconcile.
