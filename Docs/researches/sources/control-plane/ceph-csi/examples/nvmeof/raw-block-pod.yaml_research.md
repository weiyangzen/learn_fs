# sources/control-plane/ceph-csi/examples/nvmeof/raw-block-pod.yaml

Purpose: example pod consuming an NVMe-oF raw block PVC.

Important fields and flow: Pod `pod-with-raw-block-volume` runs CentOS sleep and maps PVC `raw-block-pvc` to `/dev/xvda` through `volumeDevices`.

State, dependencies, and integration: paired with `raw-block-pvc.yaml` to validate block-mode NVMe-oF publishing.

Risks and test signals: block PVC must exist and attach successfully. Device visibility in the container is the primary signal.
