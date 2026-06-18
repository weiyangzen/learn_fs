# sources/control-plane/csi-driver-nfs/charts/v3.1.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: v3.1.0 CSIDriver registration with optional inline ephemeral volume support.

Important APIs/types/functions: `storage.k8s.io/v1` `CSIDriver`; values `.Values.driver.name`, `.Values.feature.enableInlineVolume`, and `.Values.feature.enableFSGroupPolicy`.

Control flow: Always emits `Persistent` lifecycle mode. Adds `Ephemeral` mode when inline volume support is enabled and adds `fsGroupPolicy: File` when FSGroup support is enabled.

State and persistence: Persists driver capabilities in cluster storage API state.

Dependencies and integration points: Must align with node/controller driver flags and kubelet support for CSI inline volumes.

Risks: Advertising unsupported `Ephemeral` behavior could let pods request inline NFS volumes that the driver or cluster cannot satisfy. Test signals: dry-run, CSIDriver inspection, fsGroup mount test, and optional inline volume pod test.
