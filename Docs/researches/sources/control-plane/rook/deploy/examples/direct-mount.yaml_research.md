<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/direct-mount.yaml -->
# sources/control-plane/rook/deploy/examples/direct-mount.yaml

Purpose: privileged toolbox-style Deployment for directly mounting Ceph devices/filesystems from a pod using host kernel facilities.
Important APIs/types/functions: `Deployment` `rook-direct-mount`, image `docker.io/rook/ceph:master`, command `/usr/local/bin/toolbox.sh`, `serviceAccountName: rook-ceph-default`, `hostNetwork: true`, privileged root security context, hostPath mounts `/dev`, `/sys/bus`, `/lib/modules`, Rook mon secret, and mon endpoints ConfigMap.
Control flow: Kubernetes starts a privileged pod with host device and module access; the Rook toolbox entrypoint can run Ceph commands and direct mount/map operations using injected mon endpoints and secrets. State is operational and host-level; persistent data remains in Ceph, while pod state is ephemeral. Dependencies are Rook mon secret/configmap and host kernel modules. Risks: broad host/device privilege, `master` image tag drift, hostNetwork requirement, and secret exposure. Test signals: pod Running, Ceph CLI authenticates, `rbd map` or CephFS mount works, and cleanup unmaps devices.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/direct-mount.yaml -->
