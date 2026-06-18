# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.c

Purpose: central receive-notification dispatcher for MLD firmware events. It separates data/RSS fast paths from table-driven notifications, validates firmware payload versions and sizes, handles selected sync notifications immediately, and queues async notifications onto wiphy work with object-aware cancellation.

Important APIs/functions: `iwl_mld_rx()`, `iwl_mld_rx_rss()`, `iwl_mld_async_handlers_wk()`, `iwl_mld_cancel_async_notifications()`, `iwl_mld_cancel_notifications_of_object()`, and `iwl_mld_delete_handlers()`. The visible `iwl_mld_rx_handlers[]` table maps command ids to handlers, contexts, payload size/version tables, object types, and cancellation functions. Static handlers cover MFUART, MU-MIMO group updates, CSA start/error, and beacon manager state.

Control flow: the primary RX entry checks MPDU, frame-release, RX queue sync, and sniffer notifications before falling back to `iwl_mld_rx_notif()`. The dispatcher scans the handler table, validates version and payload length, calls sync handlers inline, or steals the RX buffer page into an async list and queues `async_handlers_wk`. After dispatch it wakes notification waiters and records debug time points. Async work splices the pending list under a spinlock, then runs handlers under wiphy work context. Cancellation scans pending async entries by object type and object id.

State and persistence: owns `mld->async_handlers_list`, `mld->async_handlers_lock`, `mld->async_handlers_wk`, notification wait state, and `mld->ibss_manager`. State is in memory and is purged on cancellation/removal.

Dependencies and integration: integrates nearly every MLD submodule: scan, MCC, session protection, link, TX/RX, TLC, aggregation, thermal, ROC, stats, coexistence, time sync, FTM, NAN, and MLO. It depends on firmware command metadata for notification version lookup.

Risks and test signals: handler ordering matters for hot notifications; async handlers can be observed after later sync notifications; page stealing requires exactly one owner and proper freeing; version validation fallback appears inverted-risk-prone and should be covered by KUnit/fuzzed payload size cases. Tests should cover object cancellation for scan/ROC/NAN/STA/link, duplicate ROC cancellation races, RSS queue bounds, and handler table version coverage.
