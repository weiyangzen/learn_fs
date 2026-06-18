## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-medium.yaml

Purpose: Medium-tier cgroup v2 QoS `VolumeAttributesClass` for RBD.

Important API surface: VAC `cgroup-qos-medium`, `driverName: rbd.csi.ceph.com`, 1000 read/write IOPS, and 100 MiB/s read/write bandwidth.

Control flow and state: Kubernetes stores the class and passes attributes to the RBD CSI driver for cgroup-backed I/O throttling. The object itself has no controller loop.

Dependencies and risks: Needs cgroup v2, RBD CSI support, and compatible sidecars. Numeric values are strings; unit mistakes or unsupported keys can lead to unthrottled volumes. Test by switching a volume between low/medium/high classes and observing I/O changes.
