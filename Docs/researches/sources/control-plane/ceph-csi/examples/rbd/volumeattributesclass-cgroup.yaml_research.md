## sources/control-plane/ceph-csi/examples/rbd/volumeattributesclass-cgroup.yaml

Purpose: General cgroup v2 QoS `VolumeAttributesClass` example for krbd RBD volumes.

Important API surface: VAC `cgroup-qos-vac`, RBD driver name, and four `io.max`-style parameters: `maxReadIops`, `maxWriteIops`, `maxReadBps`, and `maxWriteBps`. Comments define positive-integer values and byte units.

Control flow and state: The class is applied through Kubernetes volume attribute modification; RBD CSI uses the values to set cgroup limits at node publish/modify time for krbd-mapped devices.

Dependencies and risks: Requires cgroup v2 and driver support for cgroup QoS, plus StorageClass secrets for modify/publish. Does not apply to all mounters equally. Test by inspecting cgroup `io.max` and running workload I/O benchmarks.
