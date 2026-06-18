# sources/control-plane/ceph-csi/deploy/nvmeof/kubernetes/csi-nvmeofplugin-provisioner.yaml

Purpose: static NVMe-oF controller/provisioner Deployment.

Important APIs/types/functions: single replica, `nvmeof-csi-provisioner` service account, main `csi-nvmeofplugin --controllerserver=true`, external-provisioner, resizer, attacher, and projected KMS token; main plugin drops all capabilities and is not privileged.

Control flow: sidecars communicate over `unix:///csi/csi-provisioner.sock`, perform leader-elected Kubernetes storage operations, and call the NVMe-oF CSI controller.

State and persistence behavior: ephemeral socket and key dirs; persistent state is Kubernetes storage API objects and Ceph/NVMe-oF backend state.

Dependencies and integration points: Ceph config, Ceph-CSI config, RBAC, OpenShift annotation, KMS token projection, and sidecar images.

Risks: no liveness Service/sidecar in this manifest unlike RBD/CephFS/NFS static provisioners. Single replica reduces HA. Hardcoded default namespace and canary image are sample-oriented.

Test signals: NVMe-oF provisioning, expansion, attach, and controller rollout tests.
