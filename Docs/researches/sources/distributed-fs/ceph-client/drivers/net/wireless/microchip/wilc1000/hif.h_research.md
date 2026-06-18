# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/hif.h

Purpose: Declares WILC host-interface modes, state enums, scan/connect event contracts, firmware configuration parameter structs, per-vif HIF state, and public HIF command APIs.

Important APIs and types: Defines WILC operation modes (`IDLE`, `AP`, `STATION`, `GO`, `CLIENT`), `host_if_state`, `scan_event`, `conn_event`, bus type flags, MAC status values, `rf_info`, `cfg_param_attr`, `wilc_rcvd_net_info`, `wilc_user_scan_req`, `wilc_conn_info`, `wilc_remain_ch`, and `host_if_drv`. Function prototypes cover key management, scan/connect/disconnect, config, AP operations, station operations, power/multicast/ROC/frame registration, operation mode, statistics, tx power, WoWLAN, external auth, firmware async indications, join param parsing, default management key, and disconnect handling.

Control flow: This header defines the callback contracts used between `cfg80211.c` and `hif.c`: scan callbacks receive event and optional network info, connection callbacks receive connect/disconnect event and MAC status, remain-on-channel callbacks receive vif/cookie. `host_if_drv` embeds timers and request state used by HIF implementation.

State and persistence: `host_if_drv` is allocated per opened netdev and persists until host-interface deinit. It stores current HIF state, associated BSSID, scan/connect/ROC timers, pending callback data, and association response buffer. `cfg_param_attr` flags persist only for one configuration command.

Dependencies and integration points: Includes `linux/ieee80211.h` and `wlan_if.h`, and forward-declares WILC private/vif/join types. Used by `netdev.h`, `cfg80211.c`, and `hif.c`.

Risks: State enum ordering is used by comparisons such as "scanning through before connected"; inserting states can affect logic. Callback pointer lifetimes are cross-file and timer-driven, so callers must clear them during deinit/abort. Max probed SSIDs and concurrent interfaces are firmware limits.

Test signals: Compile coverage and runtime tests for every cfg80211 operation that maps to a HIF function, especially scan/connect timers, multi-interface operation, and async firmware indications.
