# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.c

Purpose: Implements wl1251 power-save and ELP sleep/wakeup transitions.

Important APIs and functions: `wl1251_elp_work()`, `wl1251_ps_elp_sleep()`, `wl1251_ps_elp_wakeup()`, and `wl1251_ps_set_mode()`. Constants define a 5 ms delayed ELP entry and 100 ms ELP wake timeout.

Control flow: `wl1251_ps_elp_sleep()` queues delayed work unless station mode is active. The delayed work locks the device, skips if already in ELP or active, writes `ELPCTRL_SLEEP`, and marks `wl->elp`. Wakeup cancels delayed work, writes `ELPCTRL_WAKE_UP`, polls `ELPCTRL_WLAN_READY`, and clears `wl->elp`. `wl1251_ps_set_mode()` sends different ACX/command sequences for station power-save, idle, and active CAM.

State and persistence: Mutates volatile fields `wl->elp` and `wl->station_mode`, and programs firmware sleep authorization, beacon filtering, wake conditions, BET, PS mode, and disconnect templates. No persistent storage.

Dependencies and integration points: Called by TX work, IRQ work, config changes, scans, key changes, filter changes, BSS changes, and stop cleanup. Depends on ACX helpers and command helpers.

Risks: Wakeup polling is a FIXME replacement for IRQ-driven ready notification, so latency and timeout behavior matter. Mode transitions have multiple firmware steps and can leave partial state if an intermediate command fails. Delayed work cancellation must stay synchronized with `wl->mutex`.

Test signals: Power-save enable/disable, idle transitions, TX while asleep, IRQ wakeups, and scan-from-idle are key runtime checks. Timeout log `elp wakeup timeout` indicates hardware or bus wake failure.
