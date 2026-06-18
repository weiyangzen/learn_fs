# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/debug.c

Purpose: Debugfs implementation for CW1200 runtime state, firmware counters, and optional WSM frame dumps.

Important APIs and functions: Provides `cw1200_debug_init` and `cw1200_debug_release`. Debugfs files include `status`, `counters`, and writable `wsm_dumps`. Show helpers render join mode, interface mode, queue state, link maps, firmware identity, power-save state, WSM command state, and debug counters.

Control flow: `cw1200_debug_init` allocates `cw1200_debug_priv`, creates a `cw1200` directory under the wiphy debugfs directory, and creates files. Reading `status` snapshots driver fields and queue/link maps. Reading `counters` calls `wsm_get_counters_table`. Writing `wsm_dumps` toggles `priv->wsm_enable_wsm_dumps`.

State and persistence: Debug counters live in `struct cw1200_debug_priv` and reset on driver initialization. Debugfs files are removed recursively during release. `wsm_dumps` persists only for the current device instance.

Dependencies and integration: Depends on debugfs, seq_file, WSM MIB counter reads, queue structures, CW1200 join/link enums, and debug increment helpers in `debug.h`.

Risks: Status reads inspect many fields without uniform locking; output is diagnostic and may be slightly racy. `cw1200_debug_init` does not check each `debugfs_create_file` result. Counter reads require firmware command responsiveness.

Test signals: Mount debugfs and read all files during idle, scan, joined STA, AP mode, and teardown. Toggle `wsm_dumps` and verify BH TX/RX hex dumps appear only when enabled.
