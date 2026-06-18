<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/timer.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/timer.c

Purpose: Contains shared Tulip media-monitoring timer/work handlers for generic media-table devices, Macronix chips, and COMET chips.

Important APIs and functions: `tulip_media_task()` is a workqueue callback scheduled by `tulip_timer()` in `tulip_core.c`; it inspects CSR12 and media-table leaves, switches media when link beat is missing, checks MII duplex, and completes deferred TX timeout recovery. `mxic_timer()` is a minimal periodic Macronix negotiation-status timer. `comet_timer()` polls COMET PHY link status, updates carrier state, and reschedules itself every two seconds.

Control flow: The timer itself schedules work for generic Tulip chips so media transitions do not run directly in timer context. Type 0 and 4 leaves check CSR12 link-sense bits and may cycle `tp->cur_index` to another non-FD media leaf. Type 1 and 3 MII leaves call `tulip_check_duplex()`. At the end, if `tp->timeout_recovery` was set by `tulip_tx_timeout()`, the task calls `tulip_tx_timeout_complete()` under `tp->lock`.

State and persistence: Uses `tp->timer`, `tp->media_work`, `tp->cur_index`, `tp->mtable`, `tp->timeout_recovery`, `dev->if_port`, carrier state, and CSR6/CSR12. State is volatile runtime hardware and driver state.

Dependencies and integration: Depends on `tulip_select_media()`, `tulip_check_duplex()`, `tulip_restart_rxtx()`, and `tulip_tx_timeout_complete()`. Timer functions are selected through `tulip_tbl[]` in `tulip_core.c`.

Risks: Media-table leaf interpretation is hardware-specific. Incorrect link-sense polarity can cause media flapping. The task mixes carrier updates, media switching, and TX timeout recovery, so locking order with interrupt and close paths matters. `mod_timer()` is used to synchronize with interrupt-side timer changes.

Test signals: Validate media cycling with multi-leaf EEPROM tables, MII link loss and restoration, carrier on/off transitions, timeout recovery from scheduled work, COMET duplex polling, and close/suspend races with pending media work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/timer.c -->
