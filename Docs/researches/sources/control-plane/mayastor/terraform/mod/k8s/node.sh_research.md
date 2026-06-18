# sources/control-plane/mayastor/terraform/mod/k8s/node.sh

Purpose: configures worker node kernel prerequisites and joins it to the kubeadm cluster.

Important APIs/types/functions: functions `addKernelModules` and `addHugePages`; conditionally skips host kernel setup inside LXC; loads `nbd` and `xfs`, optionally installs Ubuntu extra modules and loads `nvme-tcp`/`nvmet`, waits for `${master_ip}:6443`, and runs `kubeadm join`.

Control flow: under `set -ex`, host setup runs unless `/proc/1/environ` contains `container=lxc`; then it waits for API server and joins with token and unsafe CA skip.

State/persistence: writes hugepage sysctl, module-load config, loads kernel modules, installs packages, and joins Kubernetes node state.

Dependencies/integration: templated variables include hugepage count, master IP, token, and image name. Integrates with kubeadm config and repo package setup.

Risks: unsafe CA skip, image-name-specific NVMe module logic, and appending duplicate module/sysctl lines on reruns.

Test signals: node should join the cluster with required hugepages and storage modules available for Mayastor.
