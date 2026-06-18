## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-high.yaml

Purpose: High-tier cgroup v2 QoS `VolumeAttributesClass` for RBD.

Important API surface: `VolumeAttributesClass` named `cgroup-qos-high`, `driverName: rbd.csi.ceph.com`, and parameters `maxReadIops`, `maxWriteIops`, `maxReadBps`, `maxWriteBps` set to 2000 IOPS and 200 MiB/s.

Control flow and state: Kubernetes stores the VAC and the CSI modify-volume path passes attributes to RBD CSI. For krbd, limits are expected to apply at the cgroup v2 `io.max` layer for the container/device.

Dependencies and risks: Requires Kubernetes VAC support, controller-modify and node-publish secrets in the StorageClass, cgroup v2 nodes, and driver support for these keys. Test by applying the class to a volume and measuring throttled I/O.
