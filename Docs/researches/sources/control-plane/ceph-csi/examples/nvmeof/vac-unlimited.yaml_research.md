## sources/control-plane/ceph-csi/examples/nvmeof/vac-unlimited.yaml

Purpose: Kubernetes `VolumeAttributesClass` example for the NVMe-oF Ceph CSI driver that expresses unlimited QoS by setting multiple limit parameters to `"0"`.

Important API surface: `VolumeAttributesClass` named `unlimited`, `driverName: nvmeof.csi.ceph.com`, and parameters `rwIosPerSecond`, `rwMbytesPerSecond`, `rmBbytesPerSecond`, and `wmBbytesPerSecond`. The file documents the zero-as-unlimited convention.

Control flow and state: Kubernetes stores this as an API object and the CSI side interprets the class during volume attribute modification. There is no script or runtime loop in the file; it is declarative input to the driver and storage API.

Dependencies and risks: Depends on VAC support in Kubernetes and matching parameter parsing in the NVMe-oF driver. The `rmBbytesPerSecond`/`wmBbytesPerSecond` names look unusual compared with read/write abbreviations, so tests should verify the driver accepts them exactly. Test signal is practical: apply, attach to a volume, and inspect target-side throttling absence.
