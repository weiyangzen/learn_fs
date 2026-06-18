<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/init.yaml -->
# sources/cloud-native/containerd/test/e2e_node/init.yaml

- Purpose: Cloud-init config that installs and starts containerd on e2e nodes through systemd units.
- Important resources: `containerd-installation.service`, `containerd.service`, and `containerd.target`.
- Control flow: Fetch `containerd-configure-sh` from GCE metadata, chmod it, execute it, then start containerd with overlay module pre-load. `runcmd` stops existing containerd, reloads units, enables services, starts the target, and starts Docker if needed.
- State and persistence: Writes systemd unit files and enables services on the node.
- Dependencies and integration: Requires GCE metadata service, curl, systemd, overlay kernel module, and binaries installed under `/home/containerd/usr/local/bin`.
- Risks: Metadata script controls installation; bind-remounting `/home/containerd` as exec is security-sensitive; service ordering with Docker must be correct.
- Test signals: Active `containerd.target`, running containerd service, and Kubernetes e2e node success.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/test/e2e_node/init.yaml -->
