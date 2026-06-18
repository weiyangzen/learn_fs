# sources/control-plane/csi-driver-nfs/charts/v4.11.0/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: 4.11.0 controller Deployment with provisioner, resizer, optional snapshotter, liveness probe, and NFS plugin.

Important APIs/types/functions: Same template structure as v4.10.0; values drive strategy, images, service account, scheduling, resources, snapshot flags, and NFS driver arguments.

Control flow: Host-networked pod uses controller affinity logic, starts sidecars against the CSI socket, conditionally includes `csi-snapshotter`, and runs privileged NFS with mount/delete/snapshot options.

State and persistence: CSI socket, host pod mounts, PV/PVC/VolumeSnapshot state, events, and leases.

Dependencies and integration points: RBAC, CSIDriver, kubeletDir, sidecar image versions, and optional snapshot APIs.

Risks: Same operational risks as v4.10.0, with image tag bump to NFS plugin 4.11.0. Test signals: upgrade smoke, provision/resize/snapshot workflows.
