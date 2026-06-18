# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.h

Purpose: Declares rtl8192de dynamic-management entry points.

Important APIs/types: Exposes `rtl92de_dm_init()` and `rtl92de_dm_watchdog()`.

Control flow: Header-only declaration for initialization and periodic watchdog scheduling.

State and persistence: No local state; declared functions mutate `rtl_priv` DM and hardware registers.

Dependencies and integration: Included by rtl8192de `dm.c`, `hw.c`, and module ops setup. Requires `struct ieee80211_hw` declarations from surrounding includes.

Risks: Header guard uses `__RTL92C_DM_H__`, a naming carryover that is harmless unless colliding with another included header.

Test signals: Compile coverage and ops wiring to DM init/watchdog.
