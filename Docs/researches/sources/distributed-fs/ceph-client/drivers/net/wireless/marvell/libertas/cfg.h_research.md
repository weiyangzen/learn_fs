## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.h

Purpose: this header declares the cfg80211-facing Libertas helpers exported from `cfg.c` to the rest of the driver.

Important APIs: allocation/registration/free are `lbs_cfg_alloc()`, `lbs_cfg_register()`, and `lbs_cfg_free()`. Event helpers are `lbs_send_disconnect_notification()` and `lbs_send_mic_failureevent()`. Scan lifecycle is `lbs_scan_done()` and `lbs_scan_deinit()`. Link teardown is `lbs_disconnect()`.

Control flow and integration: bus/core startup code allocates a `wireless_dev` before firmware details are known, then calls registration once firmware capability/region data are available. Command response/event paths use the notification helpers to report firmware events to cfg80211. Shutdown calls scan deinit/free to cancel work and unregister wiphy.

State and persistence: declarations operate on `struct lbs_private` and its `wdev`, scan, and association state. No state is defined in the header.

Risks and tests: prototypes must stay synchronized with cfg.c and callers. Test signals are successful link of core/bus modules and correct cleanup during probe failure, disconnect, and module removal.
