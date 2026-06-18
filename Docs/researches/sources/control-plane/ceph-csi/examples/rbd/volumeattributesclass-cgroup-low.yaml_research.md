## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup-low.yaml

Purpose: Low-tier cgroup v2 QoS `VolumeAttributesClass` for RBD.

Important API surface: VAC `cgroup-qos-low`, RBD CSI driver name, 500 read/write IOPS, and 50 MiB/s read/write bandwidth in byte-per-second parameters.

Control flow and state: The class is declarative Kubernetes state that the RBD driver interprets during volume attribute modification, applying limits through cgroup v2 for krbd-mapped devices.

Dependencies and risks: Requires the same cgroup/VAC/driver prerequisites as the other cgroup examples. Incorrect node cgroup mode or mounter choice can make limits ineffective. Test with fio inside a Pod and compare measured throughput against limits.
