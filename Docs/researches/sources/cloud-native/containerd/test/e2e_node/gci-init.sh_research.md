<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/gci-init.sh -->
# sources/cloud-native/containerd/test/e2e_node/gci-init.sh

- Purpose: Initializes Google Container-Optimized OS/GCI nodes for containerd e2e-node testing.
- Important functions: `configure_cgroup_mode` adjusts kubelet/containerd cgroup settings based on metadata-provided environment.
- Control flow: Load `/home/containerd/containerd-env` if present, configure cgroup mode, prepare kubelet and containerized mounter directories, and bind/mount required paths.
- State and persistence: Mutates host filesystem directories and kubelet/containerd runtime configuration on boot.
- Dependencies and integration: Used with the cloud-init `init.yaml` service chain and Kubernetes e2e node infrastructure.
- Risks: Depends on metadata/env file shape; host-level mount and kubelet changes must match image expectations.
- Test signals: Node joins with containerd and kubelet e2e tests pass.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/gci-init.sh -->
