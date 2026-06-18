# sources/cloud-native/overlayfs-tools/config.h

Purpose: central static configuration for overlayfs-tools.

Important APIs/types/functions: defines `PACKAGE_VERSION` as `v0.1.0` and `MOUNT_TAB` as `/proc/mounts`.

Control flow: compile-time constants only.

State and persistence: no state. `MOUNT_TAB` controls where fsck/mount detection reads live mount information.

Dependencies/integration: included by common, fsck, mount, and related code; Meson also passes `OVERLAYFS_TOOLS_VERSION` separately for version output.

Risks: `PACKAGE_VERSION` may diverge from Meson project version; actual `version()` uses `OVERLAYFS_TOOLS_VERSION`, so this macro may be stale or unused. Hard-coded `/proc/mounts` is Linux-specific.

Test signals: version command and mount-detection tests expose configuration mismatches.
