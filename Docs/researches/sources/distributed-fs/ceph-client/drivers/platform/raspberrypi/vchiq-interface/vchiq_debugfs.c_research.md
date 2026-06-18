# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_debugfs.c

Purpose: Debugfs integration for VCHIQ global state and per-client controls. It exposes a global VCHIQ state dump plus per-instance use count and trace toggle files.

Important APIs, types, and functions: `debugfs_usecount_show()` prints `vchiq_instance_get_use_count()`. `debugfs_trace_show()` and `debugfs_trace_write()` read and set per-instance trace using `vchiq_instance_get_trace()` and `vchiq_instance_set_trace()`. `vchiq_dump_show()` delegates to `vchiq_dump_state()`. `vchiq_debugfs_init()` creates `/sys/kernel/debug/vchiq/state` and `clients/`; `vchiq_debugfs_add_instance()` creates a pid-named directory with `use_count` and `trace`; `vchiq_debugfs_remove_instance()` and `vchiq_debugfs_deinit()` clean up. Stub functions are provided when `CONFIG_DEBUG_FS` is off.

Control flow: platform probe calls `vchiq_debugfs_init()`. Each `/dev/vchiq` open calls `vchiq_debugfs_add_instance()`, and release removes that instance directory. Writes to a client's `trace` file accept first characters `Y/y/1` and `N/n/0`.

State and persistence: static dentries track the top-level VCHIQ directory and clients directory. Per-instance dentry is stored in the instance debugfs node. Debugfs contents are runtime-only and disappear on unload.

Dependencies and integration points: depends on Linux debugfs, seq_file helpers, VCHIQ arm/core getters, and cdev open/release lifecycle.

Risks: `debugfs_trace_write()` copies one byte regardless of `count`; zero-length writes can still attempt copy and should be reviewed. No explicit validation is done for top-level directory creation failures, relying on debugfs tolerance. Per-client directories are named only by pid, so pid reuse is acceptable only because directories are removed on close.

Test signals: with debugfs enabled, verify state dump while services are active, per-client directories on open/close, trace toggling propagation to services, invalid trace writes being ignored, and no-op behavior with `CONFIG_DEBUG_FS=n`.
