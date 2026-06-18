<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-iscsi-selinux-workaround.yaml -->
# sources/control-plane/longhorn/deploy/prerequisite/longhorn-iscsi-selinux-workaround.yaml

Purpose: Fedora/RHEL-style SELinux workaround that grants `iscsid_t` `dac_override` capability needed by Longhorn iSCSI flows on affected systems.

Important APIs/types/functions: defines a privileged DaemonSet whose init container uses `nsenter` into the host mount namespace and runs `rpm`, writes a temporary CIL module, applies it with `semodule -vi`, and deletes the temporary file.

Control flow: each node checks for `policycoreutils` via `rpm -q`; if available, it writes `(allow iscsid_t self (capability (dac_override)))` into `/tmp/local_longhorn.cil`, installs it, reports status, then leaves a pause container running.

State and persistence: mutates host SELinux policy module state. Kubernetes stores only DaemonSet and pod status; SELinux policy persists independently on the host.

Dependencies/integration points: depends on SELinux-enabled RPM distributions, `policycoreutils`, `semodule`, `bash`, and privileged host namespace access. It integrates with host `iscsid` access for Longhorn volumes.

Risks/test signals: applies a host security policy exception and is inapplicable outside Fedora-like systems. Test signals are init logs, `semodule -l` on hosts, absence of SELinux AVC denials for Longhorn iSCSI operations, and successful attach/mount under enforcing SELinux.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/deploy/prerequisite/longhorn-iscsi-selinux-workaround.yaml -->
