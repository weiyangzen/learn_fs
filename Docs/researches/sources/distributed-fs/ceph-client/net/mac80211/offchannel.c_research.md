# sources/distributed-fs/ceph-client/net/mac80211/offchannel.c

Purpose: coordinates remain-on-channel and offchannel management frame transmission, including software channel emulation, hardware ROC offload, cfg80211 notifications, and power-save handling while leaving the operating channel.

Important APIs and functions: cfg80211-facing entries are `ieee80211_remain_on_channel()`, `ieee80211_cancel_remain_on_channel()`, `ieee80211_mgmt_tx()`, and `ieee80211_mgmt_tx_cancel_wait()`. Driver callbacks are `ieee80211_ready_on_channel()` and `ieee80211_remain_on_channel_expired()`. Internal state is managed by `ieee80211_start_roc_work()`, `_ieee80211_start_next_roc()`, `ieee80211_roc_work()`, `ieee80211_hw_roc_start()`, `ieee80211_hw_roc_done()`, `ieee80211_cancel_roc()`, `ieee80211_roc_purge()`, and `ieee80211_roc_notify_destroy()`.

Control flow: requests allocate `ieee80211_roc_work`, assign cookies, and either start immediately or queue on `local->roc_list`. Compatible requests on the same sdata/channel may be coalesced. Hardware ROC uses driver `remain_on_channel` and waits for ready/expired callbacks. Software ROC stops queues, sends station nullfunc power-save frames, marks interfaces offchannel, changes `tmp_channel`, schedules delayed work, then restores channel, beaconing, queues, monitors, and idle state.

State and persistence: transient state lives in `local->roc_list`, work flags `started`, `notified`, `hw_begun`, `abort`, `on_channel`, cookies, pending management skb, `local->tmp_channel`, interface offchannel bits, beacon stopped bits, and dynamic power-save timers. It is not persistent beyond the queued operation.

Dependencies and integration points: ties cfg80211 ROC/mgmt-TX APIs to driver ops `remain_on_channel` and `cancel_remain_on_channel`, mac80211 TX, scan/deferred-scan logic, queue stop/wake reasons, station power save, beacon configuration, MLO link selection, CSA counter updates, and skb ACK tracking.

Risks: cancellation races with hardware callbacks are explicitly handled by flushing/canceling work, but combined ROC entries mean a cancellation can destroy more than one started operation. Management TX link/channel selection is complex for AP, station, mesh, P2P, NAN, and MLO cases. Software ROC must restore queues and channel configuration even after aborts and scan deferrals.

Test signals: coalesced ROC start/expiration ordering, cancellation before and after hardware ready, management TX on-channel versus offchannel for each interface type, MLO link selection, CSA counter mutation, no-ACK cookie handling, and suspend/purge cleanup paths.
