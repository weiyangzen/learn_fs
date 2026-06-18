# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/init.h

Purpose: Declares the wl1251 initialization entry points implemented by `init.c`.

Important APIs and types: Exposes `wl1251_hw_init()`, plus stage-level helpers for hardware encryption config, templates, RX config, PHY config, beacon filter, PTA, energy detection, beacon/broadcast config, power authorization, and memory config. It depends on `struct wl1251` from `wl1251.h`.

Control flow: This header itself has no runtime control flow. It provides callable init stages, but production startup primarily enters through `wl1251_hw_init()` from `main.c`.

State and persistence: No state is stored here. The declarations imply mutation of the `struct wl1251` instance and firmware/device state by their implementations.

Dependencies and integration points: Included by `init.c` and by the core driver where initialization is invoked. It forms a narrow contract between the mac80211 core startup path and the ACX/firmware initialization sequence.

Risks: Because many stage functions are public within the driver, later code could call them out of order. Most stages assume earlier boot and wakeup state is valid.

Test signals: Compile coverage catches signature drift. Runtime validation comes from `wl1251_op_start()` successfully completing firmware boot and init.
