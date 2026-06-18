# sources/distributed-fs/ceph-client/net/mac80211/rate.c

Purpose: provides the mac80211 software rate-control framework: algorithm registration/selection, per-station lifecycle calls, TX-status feedback dispatch, fallback rate selection, user rate-mask enforcement, and rate table publication to drivers.

Important APIs and functions: exported registration functions are `ieee80211_rate_control_register()` and `ieee80211_rate_control_unregister()`. Runtime entry points include `rate_control_rate_init()`, `rate_control_rate_init_all_links()`, `rate_control_tx_status()`, `rate_control_rate_update()`, `rate_control_get_rate()`, `ieee80211_get_tx_rates()`, `rate_control_set_rates()`, `ieee80211_init_rate_ctrl_alg()`, `rate_control_deinitialize()`, and `ieee80211_check_rate_mask()`.

Control flow: initialization chooses an algorithm by requested name, module parameter, or built-in default unless the hardware owns rate control. Per-station initialization obtains the current channel band and invokes algorithm `rate_init`. TX status is serialized by `sta->rate_ctrl_lock` and dispatched to `tx_status_ext` or legacy `tx_status`. TX rate selection first handles low/min/basic-rate cases, skips software algorithms for hardware RC, calls the algorithm when available, then fills/fixes driver rate arrays and masks them against user and station capabilities.

State and persistence: global algorithm state is `rate_ctrl_algs` under `rate_ctrl_mutex`; per-hw state is `local->rate_ctrl`; per-station state is `sta->rate_ctrl_priv`, `sta->rate_ctrl_lock`, `WLAN_STA_RATE_CONTROL`, and RCU-published `sta->rates`. Settings are in module parameter and per-sdata rate masks.

Dependencies and integration points: integrates with `struct rate_control_ops`, debugfs, station/channel context state, driver callbacks `drv_link_sta_rc_update()` and `drv_sta_rate_tbl_update()`, S1G special handling, TX skb control blocks, and RCU-managed station rate tables.

Risks: MLO is explicitly unsupported for software rate control in this path. Mask fixups across legacy/HT/VHT can silently fall back when user masks conflict with supported/basic rates. RCU rate table publication assumes the documented non-concurrent caller contract.

Test signals: algorithm duplicate register/unregister, algorithm fallback selection, hardware-RC bypass, user mask conflicts with basic rates, non-data/no-ACK fallback rates, HT/VHT mask transitions, S1G defaults, and driver rate table update notifications.
