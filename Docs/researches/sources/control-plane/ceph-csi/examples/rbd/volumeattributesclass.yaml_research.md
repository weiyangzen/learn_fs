## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass.yaml

Purpose: RBD QoS `VolumeAttributesClass` example for volume-level read/write IOPS and bandwidth limits, primarily documented for `rbd-nbd`.

Important API surface: VAC `qos-vac`, `driverName: rbd.csi.ceph.com`, active `baseIops: "1000"`, and commented parameters for max/base read/write IOPS, bytes/sec, per-GiB scaling, and `baseVolSizeBytes`.

Control flow and state: Kubernetes persists this class and passes attributes to CSI modify-volume. The RBD driver computes limits from base values and optional size-scaling parameters, then applies QoS through the supported mounter/backend path.

Dependencies and risks: Currently noted as supporting `rbd-nbd`; krbd may require cgroup VAC instead. Missing max values or per-GiB parameters change scaling behavior. Test by applying to different-sized PVCs and checking effective rbd-nbd QoS limits.
