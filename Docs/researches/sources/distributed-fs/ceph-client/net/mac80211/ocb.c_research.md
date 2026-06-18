# sources/distributed-fs/ceph-client/net/mac80211/ocb.c

Purpose: implements OCB mode lifecycle and peer station discovery for outside-the-context-of-a-BSS operation.

Important APIs and functions: `ieee80211_ocb_setup_sdata()` initializes the OCB timer, incomplete station list, and spinlock. `ieee80211_ocb_join()` claims the configured channel, sets link receive-chain and SMPS defaults, notifies BSS changes, marks the interface joined, queues housekeeping, and turns carrier on. `ieee80211_ocb_leave()` flushes stations, frees incomplete stations, releases the channel, purges queued skbs, clears offchannel state, and stops the timer. `ieee80211_ocb_rx_no_sta()` creates an incomplete `sta_info` for a newly observed peer when joined. `ieee80211_ocb_work()` drains the incomplete list and runs deferred housekeeping. `ieee80211_ocb_finish_sta()` moves a peer through AUTH, ASSOC, and AUTHORIZED states and initializes rate control.

Control flow: RX path enqueues unrecognized peers under `incomplete_lock`; the interface work item later promotes them under the wiphy lock. Housekeeping is timer-driven every 60 seconds and expires inactive peers after 240 seconds.

State and persistence: state is `sdata->u.ocb.joined`, `wrkq_flags`, `housekeeping_timer`, `incomplete_stations`, station table entries, carrier state, and the link channel context. No state persists across leave or device teardown.

Dependencies and integration points: uses station allocation/insertion/freeing, rate control initialization, `ieee80211_link_use_channel()` and release, BSS change notifications, netdev carrier, and mac80211 work/timer infrastructure.

Risks: station creation is capped by global `local->num_sta`, but there is no LRU eviction, so heavy peer churn can drop new peers. Incomplete station handling spans RX, spinlocks, and wiphy work; leave must free entries that were not inserted. `ieee80211_ocb_finish_sta()` returns an RCU-protected station and callers must release RCU, which is easy to misuse.

Test signals: join/leave channel acquisition failure, duplicate station insertion races, station expiry after inactivity, incomplete-list cleanup on leave, and carrier/timer behavior across rapid join/leave cycles.
