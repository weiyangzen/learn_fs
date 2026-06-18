# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/debugfs.c

Purpose: Adds wl12xx-specific firmware statistics files under debugfs.

Important APIs and functions: Macro `WL12XX_DEBUGFS_FWSTATS_FILE()` defines many field readers over `struct wl12xx_acx_statistics`. `wl12xx_debugfs_add_files()` creates a module directory, `fw_stats` directory, and registers statistic files for tx, rx, dma, isr, wep, pwr, mic, aes, event, ps, and rxpipe groups.

Control flow: At debugfs init, create directories and add each firmware stat file through wlcore debugfs macros. Reads are handled by generated wlcore/debugfs helpers.

State and persistence: Debugfs exposes volatile firmware statistics snapshots stored in wlcore stats buffers. It does not persist data.

Dependencies and integration points: `wl12xx_ops.debugfs_init` points here. Depends on `wlcore/debugfs.h`, `wlcore/wlcore.h`, and the statistics layout in `acx.h`.

Risks: No explicit error handling for failed debugfs directory/file creation, consistent with debugfs being optional. Field definitions must match `struct wl12xx_acx_statistics`.

Test signals: Presence and readability of `/sys/kernel/debug/.../wl12xx/fw_stats/*` files after device init, and plausible changing counters under RX/TX/PS activity.
