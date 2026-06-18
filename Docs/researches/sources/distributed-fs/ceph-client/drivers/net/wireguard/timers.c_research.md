# sources/distributed-fs/ceph-client/drivers/net/wireguard/timers.c

Purpose: Implements per-peer WireGuard timers for handshake retransmission, delayed keepalive, new-handshake retry after silence, zeroing stale key material, and persistent keepalives.

Important APIs and functions: `wg_timers_init()` and `wg_timers_stop()` initialize and synchronously stop all timers/work. Event hooks include `wg_timers_data_sent()`, `wg_timers_data_received()`, `wg_timers_any_authenticated_packet_sent()`, `wg_timers_any_authenticated_packet_received()`, `wg_timers_handshake_initiated()`, `wg_timers_handshake_complete()`, `wg_timers_session_derived()`, and `wg_timers_any_authenticated_packet_traversal()`. Expiry handlers include retransmit, send keepalive, new handshake, zero key material, queued zero-key work, and persistent keepalive.

Control flow: Authenticated data sent starts a new-handshake watchdog. Data received schedules a keepalive unless one is already pending, in which case it marks the need for another. Any authenticated send/receive cancels opposing timers. Handshake initiation schedules retransmit with jitter. Handshake completion cancels retransmit and records walltime. Session derivation schedules key zeroing after three reject windows. Retransmit expiry either retries and clears endpoint source or gives up, purges staged packets, and schedules key zeroing. Zero-key expiry queues work on the handshake send workqueue with a peer ref.

State and persistence: Mutates per-peer timer pending state, handshake attempt count, `timer_need_another_keepalive`, `sent_lastminute_handshake`, walltime last handshake, staged packet queue, endpoint source cache, and key material. Runtime-only.

Dependencies and integration points: Depends on peer/device state, send queueing, socket source clearing, Noise key clearing, workqueues, timers, random jitter, and netdev running state.

Risks: Timer callbacks run asynchronously against peer removal; `mod_peer_timer()` checks `netif_running()` and `is_dead` under RCU. `wg_timers_stop()` must delete timers synchronously and flush clear-peer work. Retry limits and jitter affect both liveness and network noise.

Test signals: Handshake retry/give-up, endpoint source clearing on retry, staged packet purge after max attempts, data receive keepalive behavior, data sent new-handshake watchdog, persistent keepalive interval, key zeroing after session age, peer removal while timers pending, and walltime last-handshake reporting via netlink.
