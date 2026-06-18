# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.c

Purpose: Implements a wl12xx-specific ACX helper for configuring host interface behavior.

Important APIs and functions: `wl1271_acx_host_if_cfg_bitmap(struct wl1271 *wl, u32 host_cfg_bitmap)` allocates a `wl1271_acx_host_config_bitmap`, stores the bitmap little-endian, and sends `ACX_HOST_IF_CFG_BITMAP` through `wl1271_cmd_configure()`.

Control flow: Allocation, field fill, configure command, warning on failure, free, return status. It is called from wl12xx hardware init before memory configuration for wl128x, especially to enable RX FIFO and optional SDIO TX padding.

State and persistence: Does not store host state locally; programs firmware configuration. The requested bitmap comes from `main.c` according to chip quirks.

Dependencies and integration points: Depends on wlcore command and ACX infrastructure. Used by `wl12xx_hw_init()` in `main.c`.

Risks: Must be sent before memory configuration per comment in `main.c`; wrong order can break wl128x host interface behavior. Allocation failure and firmware command failure are propagated.

Test signals: wl128x boot/hw init success, RX FIFO operation, and TX blocksize padding behavior on SDIO-aligned chips.
