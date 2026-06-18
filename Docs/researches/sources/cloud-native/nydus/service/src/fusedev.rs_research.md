# sources/cloud-native/nydus/service/src/fusedev.rs

Purpose: implements the FUSE-backed Nydus daemon. It creates a `FuseSession`, runs threaded `/dev/fuse` request loops, exposes a `FusedevFsService` implementing `FsService`, supports live upgrade/failover, and creates the configured VFS backend.

Important APIs/types: `FuseOp`/`FuseOpWrapper` track in-flight FUSE requests, `FuseServer` wraps a `Server<Arc<Vfs>>` plus channel, `FusedevNotifier` and `FuseSysfsNotifier` send resend/flush notifications, `FusedevFsService` owns the session/VFS/backend collection/upgrade manager, `FusedevDaemon` implements `NydusDaemon`, and public helpers are `create_fuse_daemon` and `create_vfs_backend`.

Control flow: `create_fuse_daemon` canonicalizes the mountpoint, starts the daemon FSM thread, optionally mounts an initial backend, mounts the FUSE session, emits `Mount` and `Start`, stores the calculated FUSE connection id, and hands the fuse fd to `UpgradeManager`. `start` launches `threads_cnt` `fuse_server` threads; each handles messages until session shutdown and wakes the controller on exit. `umount` shuts down and wakes the session; `stop` just wakes; `wait` joins state-machine and service threads.

State and persistence: daemon state is an atomic `i32`; service state includes FUSE connection id, failover policy, session fd, VFS, mounted backend collection, inflight operation wrappers, and optional upgrade manager. Upgrade save/restore is delegated to `upgrade::fusedev_upgrade`, including VFS bytes and held fuse fd.

Dependencies and integration: depends on `fuse-backend-rs` transport/server/VFS APIs, RAFS inode walking, `mio::Waker`, sysfs/procfs FUSE connection files, `nix` device major/minor helpers, `FsService` defaults, and daemon FSM. It integrates with API status through `export_inflight_ops` and backend collection.

Risks: FUSE shutdown paths are timing-sensitive; connection-id calculation depends on platform mount metadata; failover resend first tries `/dev/fuse` then sysfs, and flush/resend availability varies by kernel. Recursive invalidation logs child failures but continues. `is_crashed` depends on both residual mount and API socket state.

Test signals: unit tests cover sysfs base paths, notifier connection reference behavior, and Linux FUSE connection-id calculation on existing/nonexistent paths. Broader behavior is exercised by smoke API mount/remount tests.
