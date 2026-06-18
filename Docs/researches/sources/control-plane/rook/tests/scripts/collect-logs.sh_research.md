<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/collect-logs.sh -->
# sources/control-plane/rook/tests/scripts/collect-logs.sh

Purpose: diagnostic log collector for Rook/Ceph test clusters. It captures Ceph status, Kubernetes resources, pod logs, CR descriptions, secrets, block device state, and host journals.

Important APIs and control flow: environment variables select cluster namespace, operator namespace, additional namespace, and output directory. The script runs Ceph commands through `rook-ceph-tools`, builds a namespace list, then for each namespace captures lists/descriptions/logs for pods, deployments, jobs, daemonsets, ConfigMaps, PVCs, and StorageClasses. It dumps Secrets as YAML, iterates all CRDs to describe namespace-scoped custom resources, and collects `kubectl get all`, `lsblk`, `dmesg`, and `journalctl`.

State, persistence, and integration: creates a filesystem log tree under `LOG_DIR` and reads sensitive cluster state. Dependencies include `kubectl`, toolbox deployment, `sudo`, and systemd journal access. Risks include collecting secret contents in plaintext, failures when resource kinds are absent, and large unbounded logs. Test signals are the presence of populated diagnostics for post-failure triage rather than pass/fail assertions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/collect-logs.sh -->
