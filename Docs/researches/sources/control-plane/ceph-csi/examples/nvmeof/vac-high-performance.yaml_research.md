## sources/control-plane/ceph-csi/examples/nvmeof/vac-high-performance.yaml

Purpose: Kubernetes `VolumeAttributesClass` example for the Ceph CSI NVMe-oF driver, named `high-performance`, showing how to apply high read/write IOPS and bandwidth limits through `storage.k8s.io/v1`.

Important API surface: `kind: VolumeAttributesClass`, `driverName: nvmeof.csi.ceph.com`, and string parameters `rwIosPerSecond` and `rwMbytesPerSecond`. The comment notes `v1beta1` for Kubernetes 1.33 compatibility, while the manifest uses `v1`.

Control flow and integration: The object is consumed by Kubernetes external-provisioner/controller modify flows and passed to the NVMe-oF Ceph CSI driver as mutable volume attributes. No local state is persisted by the manifest; persistence is the Kubernetes API object plus any driver-side QoS application to the NVMe-oF backend.

Dependencies and risks: Requires a cluster version exposing `VolumeAttributesClass` and a Ceph CSI NVMe-oF deployment that recognizes these keys. Values are strings and unit names are driver-specific, so typo or unit mismatch silently risks ineffective QoS. Test signal is example-level only: apply the manifest, bind it to a volume, then verify resulting NVMe-oF target limits.
