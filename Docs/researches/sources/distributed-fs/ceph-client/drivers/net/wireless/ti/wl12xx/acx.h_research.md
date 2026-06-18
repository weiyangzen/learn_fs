# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/acx.h

Purpose: Defines wl12xx ACX event masks, host interface bitmap command structure, and firmware statistics layout used by debugfs and wlcore.

Important APIs and types: `WL12XX_ACX_ALL_EVENTS_VECTOR`, `WL12XX_INTR_MASK`, `struct wl1271_acx_host_config_bitmap`, many `wl12xx_acx_*_statistics` structs, aggregate `struct wl12xx_acx_statistics`, and `wl1271_acx_host_if_cfg_bitmap()`.

Control flow: Header only. The event mask constants are used by boot interrupt setup, and statistics structs are used for debugfs field extraction.

State and persistence: Describes firmware statistics snapshots and interrupt mask bits. No local storage.

Dependencies and integration points: Includes wlcore core and ACX headers. Tied to `debugfs.c`, `acx.c`, and `main.c`.

Risks: Statistics structure layout must match firmware ACX statistics response exactly; debugfs fields will report nonsense if offsets drift. Interrupt mask constants determine which firmware interrupts reach the host.

Test signals: Debugfs firmware stats reads, event interrupt delivery, and wl128x host interface configuration.
