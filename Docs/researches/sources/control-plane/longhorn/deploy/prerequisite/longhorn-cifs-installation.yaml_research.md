<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-cifs-installation.yaml -->
# sources/control-plane/longhorn/deploy/prerequisite/longhorn-cifs-installation.yaml

Purpose: node-wide helper DaemonSet for installing `cifs-utils`, enabling Longhorn backup targets or workflows that require CIFS support on every node.

Important APIs/types/functions: defines an `apps/v1` `DaemonSet` with a privileged init container running `nsenter --mount=/proc/1/ns/mnt -- bash -c <cmd>` and a pause container to keep the pod present.

Control flow: each node enters the host mount namespace, detects distro family from `/etc/os-release`, then runs `apt-get`, `zypper`, or `yum` commands to install `cifs-utils`. The init container prints success or failure, then the pause container holds the DaemonSet pod.

State and persistence: mutates host OS package state outside Kubernetes. Kubernetes only stores the DaemonSet/pod status; the installed package remains on the node image or filesystem until manually changed.

Dependencies/integration points: depends on host package managers, network access to package repositories, `sudo`, `bash`, `nsenter`, and privileged host namespace access. It integrates with Longhorn backupstore support that needs CIFS mounting.

Risks/test signals: running package managers from a pod is distro-sensitive, non-idempotent under partial failures, and can drift immutable nodes. Test signals are DaemonSet rollout, init container logs, `mount.cifs` availability on every node, and backup target mount tests.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-cifs-installation.yaml -->
