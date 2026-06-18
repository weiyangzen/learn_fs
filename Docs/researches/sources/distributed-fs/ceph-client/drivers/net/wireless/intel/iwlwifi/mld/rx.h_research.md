# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.h

Purpose: declares RX data-path entry points and defines the internal RX-queue synchronization payloads shared between queue-sync command senders and notification handlers.

Important APIs/types: `enum iwl_mld_internal_rxq_notif_type` currently has empty sync and DELBA notification types. `struct iwl_mld_internal_rxq_notif` is a packed firmware-echoed internal payload with type, cookie, reserved alignment, and variable payload. `struct iwl_mld_rx_queues_sync` stores wait queue, cookie, and bitmask state. Function declarations expose MPDU handling, RX queue sync command, sync notification handling, packet pass-through to mac80211, and PHY air sniffer notification handling.

Control flow: aggregation or teardown code can call `iwl_mld_sync_rx_queues()` to broadcast an internal message to all RX queues and wait until `iwl_mld_handle_rx_queues_sync_notif()` clears each queue bit. Normal notification dispatch calls `iwl_mld_rx_mpdu()` for MPDUs and sniffer handler for PHY air notifications.

State and persistence: the state structure is embedded in `struct iwl_mld`; it is a live synchronization primitive with a monotonic cookie and bitmask, not persistent storage.

Dependencies and integration: includes local `mld.h`, uses NAPI, firmware RX command buffers/packets, and mac80211 station/SKB types. DELBA payload integration is implemented in aggregation code.

Risks and test signals: the internal payload must remain DWORD-aligned because firmware echoes it opaquely. Cookie handling is the primary stale-notification guard. Tests should verify variable payload sizing and that all RX queue bits clear before wait completion.
