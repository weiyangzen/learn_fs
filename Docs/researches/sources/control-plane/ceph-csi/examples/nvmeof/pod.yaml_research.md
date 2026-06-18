# sources/control-plane/ceph-csi/examples/nvmeof/pod.yaml

Purpose: baseline NVMe-oF filesystem PVC consumer pod.

Important fields and flow: Pod `csi-nvmeof-demo-pod` runs nginx and mounts PVC `nvmeof-pvc` at `/var/lib/www/html`.

State, dependencies, and integration: depends on `pvc.yaml` and the NVMe-oF StorageClass/gateway configuration.

Risks and test signals: pod readiness validates attach, NVMe connection, filesystem mount, and publish path.
