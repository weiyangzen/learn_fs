<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/install-driver.sh -->
# Research: sources/control-plane/csi-driver-smb/deploy/install-driver.sh

- Purpose: shell helper that installs SMB CSI driver manifests for a requested version from GitHub raw URLs or local deploy files, with a selectable Windows mode.
- Important APIs/types/functions: Bash with `set -euo pipefail`; accepts version `$1` defaulting to `master`, optional `$2` containing `local` and/or `hostprocess`; applies RBAC, CSIDriver, controller, Linux node, and either Windows CSI-proxy or HostProcess node manifest.
- Control flow: compute deploy repository path, append version for non-master, apply resources in dependency order with `kubectl apply`, then select Windows manifest based on `windowsMode`.
- State and persistence behavior: creates Kubernetes resources and may cause node pods to create host plugin directories/sockets. It does not create StorageClasses, Secrets, or SMB server state.
- Dependencies/integration points: kubectl, current cluster context, raw.githubusercontent.com access unless local mode is requested, deploy file naming conventions, and Windows mode compatibility with the cluster.
- Risks: applying remote `master` is mutable; local mode depends on cwd; the hostprocess mode requires supported Windows nodes; install applies both Linux and Windows node manifests even in single-OS clusters.
- Test signals: command exit code, resource rollout in kube-system, CSIDriver existence, and a smoke PVC mount.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/install-driver.sh -->
