<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/resize-vagrant-root.sh -->
# sources/cloud-native/containerd/script/resize-vagrant-root.sh

- Purpose: Expands the root partition and filesystem for Vagrant-based Linux development/test machines.
- Important logic: Installs `cloud-utils-growpart` with `dnf` if `growpart` is absent, parses `df -T /`, calls `growpart`, then resizes either btrfs or xfs root filesystems.
- Control flow: Parse `/dev/<disk><partition>` roots, tolerate `NOCHANGE`, branch on filesystem type, and fail for unknown filesystems or device-mapper roots.
- State and persistence: Mutates the host partition table and root filesystem size.
- Dependencies and integration: Requires root privileges, `growpart`, `btrfs filesystem resize` or `xfs_growfs`, and Rocky/Fedora-like package management for the fallback install.
- Risks: Regex parsing only supports simple block devices; device-mapper/LVM is explicitly unsupported; running on an unexpected host can alter storage irreversibly.
- Test signals: Successful `growpart`/filesystem tool exits and post-run `df` size changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/resize-vagrant-root.sh -->
