<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/main.rs -->
# sources/cloud-native/fuse-overlayfs/src/main.rs

Purpose: binary entrypoint that parses configuration, initializes layers and FUSE, daemonizes if requested, and runs the filesystem session.

Important flow: parses args, initializes logging from `FUSE_OVERLAYFS_DEBUG_LOG` or env/default level, validates `lowerdir` and mountpoint, rejects redirect modes other than `off`, raises `RLIMIT_NOFILE`, warns on read-only `/proc`, opens workdir, initializes layers, builds fuser mount options and ACL from parsed options, creates `OverlayFs`, creates a `fuser::Session`, sets notifier for cache invalidation, daemonizes unless foreground, installs SIGUSR1 reporting, spawns and joins the FUSE session.

State and persistence: opens workdir/layer fds, mounts FUSE at mountpoint, may daemonize, writes logs, and SIGUSR1 reports node/inode stats. Dependencies include config/layer/overlay/sys modules and fuser. Risks include startup exits on missing options, workdir fd `-1` in read-only mode assumptions, daemonization timing, and signal logging fd lifetime. Test signal is integration tests that run the binary under mount scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/main.rs -->
