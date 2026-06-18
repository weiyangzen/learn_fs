<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/uninstall-driver.sh -->
# Research: sources/control-plane/csi-driver-smb/deploy/uninstall-driver.sh

- Purpose: shell helper that removes SMB CSI manifests for a requested version from either GitHub raw URLs or the local `./deploy` tree.
- Important APIs/types/functions: Bash with `set -euo pipefail`; accepts version as `$1`, optional local mode as `$2`, computes `repo`, appends version subdirectory for non-master, and runs `kubectl delete --ignore-not-found` for controller, node, Windows node, CSIDriver, and RBAC manifests.
- Control flow: resolve version/repo, print uninstall status, delete resources in dependency-tolerant order, and exit on unexpected command errors.
- State and persistence behavior: deletes Kubernetes API objects but does not clean remote SMB data, PV reclaim artifacts, Secrets, or host mount residue beyond what Kubernetes finalizers/DaemonSet teardown handle.
- Dependencies/integration points: requires kubectl context, network access for raw GitHub unless local mode is used, and file names matching the deploy tree for the requested version.
- Risks: hostprocess Windows manifest is not deleted explicitly; deleting manifests can leave PVs, mounts, or external SMB subdirectories depending on reclaim policy and workload state.
- Test signals: run against a test cluster and confirm target resources disappear with `kubectl get`; `--ignore-not-found` makes repeated runs idempotent for listed files.

<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/deploy/uninstall-driver.sh -->
