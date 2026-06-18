# sources/cloud-native/ostree/src/switchroot/ostree-prepare-root.c

Purpose: initramfs/systemd prepare-root implementation. It turns the physical root mounted at a sysroot path into an OSTree deployment root, supports composefs/transient root configuration, prepares `/etc`, `/usr`, `/sysroot`, and `/var`, writes boot metadata, and leaves systemd to switch root.

Important APIs/functions: `sysroot_is_configured_ro()` reads repo config with `GKeyFile`. `resolve_deploy_path()` uses `otcore_get_ostree_target()` to parse the kernel command line, validates the target symlink, resolves the deployment, and journals deployment device/inode/path. `main()` parses `SYSROOT [KERNEL_CMDLINE]`, loads `prepare-root.conf`, loads `RootConfig`, mounts composefs or legacy bind root via `otcore_mount_rootfs()`, mounts transient/persistent `/etc` via `otcore_mount_etc()`, handles `/usr` hotfix overlay, binds physical root to future `/sysroot`, detaches old sysroot, prepares `/var`, writes `OTCORE_RUN_BOOTED` metadata, moves `/sysroot.tmp` to target, and optionally remounts `/sysroot` read-only.

Control flow: after config and target resolution, all later operations assume cwd is the deployment directory. Composefs is attempted first; legacy bind mount is fallback. Metadata is accumulated in a `GVariantBuilder` and written to `/run/ostree-booted` before final move. `/boot` is intentionally not mounted here; generator handles it.

State/persistence: heavily mutates mount namespace and writes `/run/ostree` directories plus `OTCORE_RUN_BOOTED` metadata. It may leave `/sysroot` read-only by configuration and ensures `/var` and `/etc` mutability through bind/overlay mounts.

Dependencies/integration: GLib/GIO option/keyfile/variant APIs, libglnx, libostree core/private APIs, `otcore` rootfs helpers, systemd journal IDs, Linux mount/umount semantics, and `ostree-mount-util.h`.

Risks: this is boot-critical code with many privileged mount operations. Composefs, transient root, readonly sysroot, and hotfix overlays interact; signed composefs forbids `/usr` hotfix overlay. It relies on symlink deployment targets and correct kernel cmdline/config. Errors exit the process, which fails boot preparation.

Test signals: `tests-unit-container/test-prepare-root.sh` directly exercises legacy prepare-root in a podman container, verifies `/run/ostree-booted`, `/etc` and `/usr` mountpoints, default readonly sysroot config, default config fallback, `etc.transient`, and that `/boot` is not mounted by prepare-root.
