<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_windows.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/config_windows.go

Purpose: Windows host directory search layout for Docker registry config.

Important APIs/types/functions: `hostPaths(root, host)` mirrors Unix but strips `:` characters because Windows paths cannot contain colons.

Control flow: if `hostDirectory` changed the host, it checks the colon-stripped sanitized name; then checks the colon-stripped literal host and `_default`.

State and persistence: path construction only.

Dependencies and integration points: used by `HostDirFromRoot` on Windows for `hosts.toml` and certificate discovery.

Risks: stripping colons can cause name collisions that are impossible on Unix. IPv6 address directory names may be less readable and potentially ambiguous.

Test signals: resolver test has a Windows-specific branch when constructing expected host config directories.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_windows.go -->
