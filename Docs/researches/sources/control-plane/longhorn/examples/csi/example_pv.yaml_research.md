<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/examples/csi/example_pv.yaml -->
# sources/control-plane/longhorn/examples/csi/example_pv.yaml

Purpose: static CSI PersistentVolume example binding an existing Longhorn volume to a PVC and pod.

Important APIs/types/functions: defines `PersistentVolume` with CSI driver `driver.longhorn.io`, `volumeHandle: existing-longhorn-volume`, fsType `ext4`, volume attributes, a bound PVC using `volumeName`, and an nginx pod mounting `/data`.

Control flow: Kubernetes binds the PVC to the static PV, CSI attaches/mounts the existing Longhorn volume, and the pod liveness probe checks `/data/lost+found`.

State and persistence: existing Longhorn volume data is exposed through the PV; reclaim policy is Delete in this example.

Dependencies/integration points: depends on a pre-existing Longhorn volume named by `volumeHandle`, CSI attach/mount, and ext4 filesystem.

Risks/test signals: wrong handle or filesystem causes mount failures; Delete reclaim can remove an existing volume unexpectedly. Test signals are PV/PVC bound state, pod mount success, and Longhorn UI/API volume association.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/examples/csi/example_pv.yaml -->
