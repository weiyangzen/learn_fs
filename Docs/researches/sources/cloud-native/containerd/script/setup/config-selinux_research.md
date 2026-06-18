<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-selinux -->
# sources/cloud-native/containerd/script/setup/config-selinux

- Purpose: Sets the host SELinux mode for containerd test hosts according to the `SELINUX` environment variable.
- Important behavior: No-ops if `getenforce` and `setenforce` are unavailable; supports `Disabled`, `Enforcing`, and `Permissive`.
- Control flow: For disabled mode, set permissive and unmount `/sys/fs/selinux` if mounted. For enforcing/permissive, mount selinuxfs if needed and call `setenforce`.
- State and persistence: Mutates kernel SELinux runtime state and the selinuxfs mount, but does not edit persistent distribution config files.
- Dependencies and integration: Requires SELinux utilities, mount privileges, and callers that set `SELINUX`.
- Risks: Missing `SELINUX` under `set -u` fails; unmounting selinuxfs can surprise other processes; unsupported values exit hard.
- Test signals: Final `getenforce` output and subsequent containerd CRI SELinux tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/script/setup/config-selinux -->
