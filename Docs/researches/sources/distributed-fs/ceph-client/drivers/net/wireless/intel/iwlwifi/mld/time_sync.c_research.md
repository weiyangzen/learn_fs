# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/time_sync.c

Purpose: Implements MLD time-synchronization support for 802.11v timing measurement and FTM frames, pairing queued SKBs with firmware timestamp notifications and reporting adjusted PTP timestamps to mac80211.

Important APIs and functions: `iwl_mld_time_sync_config()` configures the single supported peer/protocol set. `iwl_mld_time_sync_fw_config()` sends firmware configuration. `iwl_mld_deinit_time_sync()` tears down RCU state and queued frames. `iwl_mld_time_sync_frame()` intercepts matching timing/FTM frames. `iwl_mld_handle_time_msmt_notif()` and `iwl_mld_handle_time_sync_confirm_notif()` attach RX/TX timestamps and deliver frames/status.

Control flow: Configuration rejects a different active peer, validates protocol bits, replaces existing state, and sends firmware config. Matching frames are queued on `time_sync->frame_list`. Notification handlers find the first queued SKB matching peer address and dialog token, dropping older unmatched SKBs, convert firmware 10 ns timestamp pairs to adjusted PTP nanoseconds under `ptp_data.lock`, write hardware timestamp fields, and call `ieee80211_rx_napi()` or `ieee80211_tx_status_ext()`.

State and persistence: `struct iwl_mld_time_sync_data` is RCU-protected and stores peer address, active protocol mask, and queued SKBs. Deinit purges the queue and frees via RCU. No durable persistence.

Dependencies and integration points: Depends on MLD command dispatch, PTP adjustment helper, mac80211 frame classifiers/status APIs, SKB queues, RCU, and firmware WNM timing measurement config/notification ABI.

Risks: Firmware supports one peer only; attempts to configure another active peer return `-ENOBUFS`. Queue matching assumes notifications arrive in frame order and drops unmatched queued frames. Dequeue occurs while an RCU read lock is held; teardown must purge safely. Missing notifications leak queued frames until deinit or a later mismatch drains them.

Test signals: Cover peer reconfiguration, invalid protocol mask, FW config failure, RX and TX notification timestamp conversion, dialog-token mismatch drop, missing state notification warning, queue purge on deinit, and concurrent frame enqueue/deinit behavior.
