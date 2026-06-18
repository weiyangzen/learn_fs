# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/mon.c

Purpose: Implements WILC monitor-mode netdev support, including radiotap wrapping for received management frames and TX status callbacks, management TX from monitor frames, and monitor interface allocation/teardown.

Important APIs and functions: `wilc_wfi_monitor_rx()` delivers received/callback management frames to a monitor netdev with radiotap headers. `wilc_wfi_init_mon_interface()` allocates/registers an `ARPHRD_IEEE80211_RADIOTAP` netdev and links it to a real WILC netdev. `wilc_wfi_deinit_mon_interface()` unregisters it. Internal TX path functions include `wilc_wfi_mon_xmit()`, `mon_mgmt_tx()`, and `mgmt_tx_complete()`.

Control flow: RX checks monitor existence and running state, reads WILC host header metadata before the frame buffer to distinguish management TX callbacks from received frames, prepends the appropriate radiotap header, and injects via `netif_rx()`. Monitor TX strips the incoming radiotap header, special-cases broadcast deauth-style frames for local TX-status echo, routes management frames whose source equals BSSID through `wilc_wlan_txq_add_mgmt_pkt()`, and sends other frames through normal `wilc_mac_xmit()` on the real netdev.

State and persistence: `struct wilc_wfi_mon_priv` stores the backing real netdev. `wl->monitor_dev` persists while monitor mode is active. Allocated TX callback buffers persist until TX completion callback frees them.

Dependencies and integration points: Depends on cfg80211/netdev shared types, radiotap definitions, WILC host header flags (`HOST_HDR_OFFSET`, `WILC_PKT_HDR_OFFSET_FIELD`, `IS_MANAGMEMENT_CALLBACK`, `IS_MGMT_STATUS_SUCCES`), normal TX queue helpers, and `wilc_mac_xmit()` from `netdev.c`. Created/deleted by cfg80211 virtual interface operations.

Risks: RX reads `buff - HOST_HDR_OFFSET`, so callers must pass buffers with valid WILC host header space. Monitor TX returns error-like values from a `netdev_tx_t` path in some cases, which is not ideal for netdev semantics. Radiotap rate is hardcoded to 5. Management/data classification by source address equals BSSID is heuristic.

Test signals: Add/delete monitor interface, receive P2P/action/auth/probe frames, hostapd management TX callbacks, monitor-injected management frames, normal data forwarding through monitor, and teardown while monitor device exists are useful tests.
