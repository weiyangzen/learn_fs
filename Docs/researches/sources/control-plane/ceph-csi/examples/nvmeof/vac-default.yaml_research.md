# sources/control-plane/ceph-csi/examples/nvmeof/vac-default.yaml

Purpose: example NVMe-oF `VolumeAttributesClass` providing default QoS-like parameters.

Important fields and flow: VAC `default` uses driver `nvmeof.csi.ceph.com` and sets `rwIosPerSecond: "5000"`.

State, dependencies, and integration: applied to PVCs through Kubernetes VAC support to modify NVMe-oF volume attributes.

Risks and test signals: requires Kubernetes VAC API support and driver-side parameter handling. Reattachment or modification tests should confirm the I/O parameter is honored.
