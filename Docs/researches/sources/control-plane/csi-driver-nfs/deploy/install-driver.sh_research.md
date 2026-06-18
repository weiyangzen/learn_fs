# sources/control-plane/csi-driver-nfs/deploy/install-driver.sh

Purpose: shell installer for applying the NFS CSI driver manifests from either upstream raw GitHub URLs or the local `./deploy` directory.

Important APIs/types/functions: the script uses Bash with `set -euo pipefail`, accepts `ver` as the first argument defaulting to `master`, and switches to local manifests when the second argument contains `local`. It builds `repo=https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/$ver/deploy`, appends `/$ver` for non-master versions, then runs `kubectl apply` for RBAC, CSIDriver, controller, and node manifests. If the second argument contains `snapshot`, it also applies snapshot CRDs, snapshot-controller RBAC, and snapshot-controller deployment.

Control flow: argument parsing selects remote versus local source, then the script applies core objects in dependency order before optional snapshot objects. Any failed `kubectl apply` aborts because of `set -e`.

State and persistence: the script persists Kubernetes objects into the target cluster and has no local state. Remote mode depends on the current contents of the selected upstream branch/tag.

Dependencies and integration points: requires `kubectl` context access, network access for remote raw manifests unless local mode is used, and a deploy tree matching the selected version. It is the operational entry point for all YAML files in this subset.

Risks: the local mode check is substring-based and tied to the second argument, so argument ordering matters. Remote `master` installs mutable canary manifests. Snapshot install does not separately verify CRD readiness before deploying the controller.

Test signals: run in a disposable cluster with `local snapshot`, verify all expected objects, create a sample PVC and snapshot, and confirm rerunning the script is idempotent.
