# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/ps.h

Purpose: Declares wl1251 power-save and ELP helpers.

Important APIs and types: Provides prototypes for `wl1251_ps_set_mode()`, `wl1251_ps_elp_sleep()`, `wl1251_ps_elp_wakeup()`, and `wl1251_elp_work()`. Uses `enum wl1251_station_mode` and `struct wl1251`.

Control flow: No control flow in the header. It defines the interface for code paths that need to wake firmware before touching registers or queue delayed sleep after work.

State and persistence: Header has no state. Implementations mutate `wl->elp`, `wl->station_mode`, and firmware PS state.

Dependencies and integration points: Included by `main.c`, `tx.c`, and `ps.c`, making power management part of both mac80211 callbacks and data-path work.

Risks: Callers must already understand locking expectations; most runtime callers hold `wl->mutex`. Calling wake/sleep out of sequence can race with delayed work.

Test signals: Compile coverage and runtime ELP transitions in TX, IRQ, scan, and config flows.
