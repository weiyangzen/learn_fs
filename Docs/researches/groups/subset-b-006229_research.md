# Research: subset-b-006229 mac80211 NAN, OCB, offchannel, parsing, power, and rate control

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/nan.c -->
# sources/distributed-fs/ceph-client/net/mac80211/nan.c

Purpose: implements mac80211 NAN schedule handling for local NAN interfaces and peer NAN schedule installation. It bridges cfg80211 NAN schedule objects into mac80211 channel contexts, driver notifications, and NAN data interface carrier state.

Important APIs and functions: `ieee80211_nan_set_local_sched()` is the main local schedule update entry. It validates channel/blob limits, backs up the current schedule, maps requested schedule indexes to existing or newly allocated `ieee80211_nan_channel` objects, uses `ieee80211_nan_use_chanctx()` to claim shared channel contexts, sends `BSS_CHANGED_NAN_LOCAL_SCHED`, and rolls back on allocation or chanctx failures. `ieee80211_nan_sched_update_done()` completes deferred updates exported to drivers. Peer-side work is in `ieee80211_nan_set_peer_sched()`, `ieee80211_nan_init_peer_channel()`, `ieee80211_nan_init_peer_map()`, and `ieee80211_nan_free_peer_sched()`. Carrier gating uses `ieee80211_nan_has_common_slots()`, `ieee80211_nan_update_ndi_carrier()`, and `ieee80211_nan_update_peer_ndis_carrier()`.

Control flow: local schedule updates first remove or mark removed channels, then add/update channels, rebuild the slot schedule, notify the driver, and update all NAN data interface carriers unless the update is deferred. Deferred completion updates carriers, clears `deferred`, removes channels that were kept alive for peer notification ordering, recalculates SMPS, clears the removed bitmap, and reports completion to cfg80211.

State and persistence: state lives in `sdata->vif.cfg.nan_sched`, `sdata->u.nan.removed_channels`, `sta->sta.nan_sched`, chanctx pointers, and netdev carrier state. There is no durable storage; all state is in-kernel and protected by the wiphy lock plus RCU dereferences where needed.

Dependencies and integration points: depends on cfg80211 NAN structs, mac80211 channel context helpers, station lists, driver ops `drv_vif_cfg_changed()` and `drv_nan_peer_sched_changed()`, and cfg80211 completion notification. Integration risk is high around chanctx lifetime because peer maps store pointers into variable-length schedule arrays and local channels store `chanctx_conf` pointers.

Risks: rollback has to restore schedule arrays, availability blobs, channel contexts, and SMPS state consistently. Removing a local channel must rewrite all peer schedule pointers before compacting the peer channel array. Deferred NSS reductions intentionally delay SMPS recalculation, so missed completion would leave stale receive-chain requirements and carrier state.

Test signals: exercise local schedule add/update/remove, deferred updates, failure rollback from chanctx allocation, peer schedules with compatible and incompatible channels, peer map compaction after local removal, and NDI carrier transitions when common slots appear or disappear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/nan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ocb.c -->
# sources/distributed-fs/ceph-client/net/mac80211/ocb.c

Purpose: implements OCB mode lifecycle and peer station discovery for outside-the-context-of-a-BSS operation.

Important APIs and functions: `ieee80211_ocb_setup_sdata()` initializes the OCB timer, incomplete station list, and spinlock. `ieee80211_ocb_join()` claims the configured channel, sets link receive-chain and SMPS defaults, notifies BSS changes, marks the interface joined, queues housekeeping, and turns carrier on. `ieee80211_ocb_leave()` flushes stations, frees incomplete stations, releases the channel, purges queued skbs, clears offchannel state, and stops the timer. `ieee80211_ocb_rx_no_sta()` creates an incomplete `sta_info` for a newly observed peer when joined. `ieee80211_ocb_work()` drains the incomplete list and runs deferred housekeeping. `ieee80211_ocb_finish_sta()` moves a peer through AUTH, ASSOC, and AUTHORIZED states and initializes rate control.

Control flow: RX path enqueues unrecognized peers under `incomplete_lock`; the interface work item later promotes them under the wiphy lock. Housekeeping is timer-driven every 60 seconds and expires inactive peers after 240 seconds.

State and persistence: state is `sdata->u.ocb.joined`, `wrkq_flags`, `housekeeping_timer`, `incomplete_stations`, station table entries, carrier state, and the link channel context. No state persists across leave or device teardown.

Dependencies and integration points: uses station allocation/insertion/freeing, rate control initialization, `ieee80211_link_use_channel()` and release, BSS change notifications, netdev carrier, and mac80211 work/timer infrastructure.

Risks: station creation is capped by global `local->num_sta`, but there is no LRU eviction, so heavy peer churn can drop new peers. Incomplete station handling spans RX, spinlocks, and wiphy work; leave must free entries that were not inserted. `ieee80211_ocb_finish_sta()` returns an RCU-protected station and callers must release RCU, which is easy to misuse.

Test signals: join/leave channel acquisition failure, duplicate station insertion races, station expiry after inactivity, incomplete-list cleanup on leave, and carrier/timer behavior across rapid join/leave cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/ocb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/offchannel.c -->
# sources/distributed-fs/ceph-client/net/mac80211/offchannel.c

Purpose: coordinates remain-on-channel and offchannel management frame transmission, including software channel emulation, hardware ROC offload, cfg80211 notifications, and power-save handling while leaving the operating channel.

Important APIs and functions: cfg80211-facing entries are `ieee80211_remain_on_channel()`, `ieee80211_cancel_remain_on_channel()`, `ieee80211_mgmt_tx()`, and `ieee80211_mgmt_tx_cancel_wait()`. Driver callbacks are `ieee80211_ready_on_channel()` and `ieee80211_remain_on_channel_expired()`. Internal state is managed by `ieee80211_start_roc_work()`, `_ieee80211_start_next_roc()`, `ieee80211_roc_work()`, `ieee80211_hw_roc_start()`, `ieee80211_hw_roc_done()`, `ieee80211_cancel_roc()`, `ieee80211_roc_purge()`, and `ieee80211_roc_notify_destroy()`.

Control flow: requests allocate `ieee80211_roc_work`, assign cookies, and either start immediately or queue on `local->roc_list`. Compatible requests on the same sdata/channel may be coalesced. Hardware ROC uses driver `remain_on_channel` and waits for ready/expired callbacks. Software ROC stops queues, sends station nullfunc power-save frames, marks interfaces offchannel, changes `tmp_channel`, schedules delayed work, then restores channel, beaconing, queues, monitors, and idle state.

State and persistence: transient state lives in `local->roc_list`, work flags `started`, `notified`, `hw_begun`, `abort`, `on_channel`, cookies, pending management skb, `local->tmp_channel`, interface offchannel bits, beacon stopped bits, and dynamic power-save timers. It is not persistent beyond the queued operation.

Dependencies and integration points: ties cfg80211 ROC/mgmt-TX APIs to driver ops `remain_on_channel` and `cancel_remain_on_channel`, mac80211 TX, scan/deferred-scan logic, queue stop/wake reasons, station power save, beacon configuration, MLO link selection, CSA counter updates, and skb ACK tracking.

Risks: cancellation races with hardware callbacks are explicitly handled by flushing/canceling work, but combined ROC entries mean a cancellation can destroy more than one started operation. Management TX link/channel selection is complex for AP, station, mesh, P2P, NAN, and MLO cases. Software ROC must restore queues and channel configuration even after aborts and scan deferrals.

Test signals: coalesced ROC start/expiration ordering, cancellation before and after hardware ready, management TX on-channel versus offchannel for each interface type, MLO link selection, CSA counter mutation, no-ACK cookie handling, and suspend/purge cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/offchannel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/parse.c -->
# sources/distributed-fs/ceph-client/net/mac80211/parse.c

Purpose: parses 802.11 management information elements into `struct ieee802_11_elems`, including legacy, HT/VHT/HE/EHT/UHR, mesh, CSA, MBSSID, and multi-link overlays.

Important APIs and functions: `ieee802_11_parse_elems_full()` allocates a flexible parse object, prepares MBSSID or MLO profile parsing, parses outer elements, overlays non-transmitted BSS or per-STA profile elements, defragments reconfiguration/EPCS MLEs, and returns the embedded `ieee802_11_elems`. `_ieee802_11_parse_elems_full()` is the central IE loop. `ieee80211_parse_extension_element()` handles extension IDs for HE/EHT/UHR and MLO markers. `ieee80211_parse_tpe()` parses transmit power envelope variants. `ieee802_11_find_bssid_profile()`, `ieee80211_prep_mle_link_parse()`, and `ieee80211_mle_get_sta_prof()` support MBSSID/MLO profile overlay. `ieee80211_parse_bitrates()` maps supported-rate IE bytes to band bitrate masks.

Control flow: the parser initializes scratch space at three times input length, records original IE pointers, optionally builds a merged non-transmitted profile or defragmented MLO basic element, parses the outer IE stream with duplicate and size checks, then parses inherited inner/profile elements as overrides.

State and persistence: parse results are heap allocated with scratch storage embedded after the result object; callers own and free the returned pointer. Most element pointers refer either to the original frame buffer or scratch defragmentation/profile storage. CRC state is accumulated only for requested filtered elements.

Dependencies and integration points: depends on cfg80211 element iterators, element validation helpers, CRC32, KUnit export visibility, mesh/rate/wme/mac80211 headers, and wireless frame constants. Consumers throughout mac80211 rely on parse flags and pointer lifetimes.

Risks: pointer lifetime is tied to the returned allocation and original frame buffer; callers must not keep pointers after freeing or after skb lifetime ends. Duplicate-element handling is selective and must match standards expectations. MLO and MBSSID overlay paths share scratch space, so bounds and non-inheritance checks are critical.

Test signals: malformed/truncated IE endings, duplicate singleton IEs, extension element size validation, MBSSID profile matching and DTIM override, MLE defragmentation and per-link profile parsing, TPE count/category variants, and bitrate mask translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/pm.c -->
# sources/distributed-fs/ceph-client/net/mac80211/pm.c

Purpose: implements mac80211 suspend preparation and WoWLAN wakeup reporting.

Important APIs and functions: `__ieee80211_suspend()` is the main suspend path used by mac80211. `ieee80211_sched_scan_cancel()` stops scheduled scans unless WoWLAN any-trigger keeps them alive. `ieee80211_report_wowlan_wakeup()` exports driver wakeup reporting to cfg80211.

Control flow: suspend marks `local->suspending`, cancels scans, DFS CAC, ROC work, and virtual monitor, tears down BA sessions unless WoWLAN any-trigger is active, stops queues, synchronizes networking, flushes queues and workqueue, deletes timers, and then either delegates to `drv_suspend()` for WoWLAN or removes driver-created interfaces and stops the device. Resume is intentionally handled elsewhere through reconfiguration.

State and persistence: transient state includes `local->suspending`, `quiescing`, `suspended`, `wowlan`, queue stop reasons, BA block flags, dynamic power-save flags/timers, station auth/assoc progress, and driver interface presence. No durable state is written.

Dependencies and integration points: depends on scan, DFS, ROC purge, monitor removal, BA teardown, managed-mode quiesce, driver suspend/remove/stop operations, queue control, net synchronization, LED/mesh headers, and cfg80211 WoWLAN reporting.

Risks: memory barriers are used so timers and other paths observe suspending/quiescing state in order. Error returns from `drv_suspend()` must restore queue state and BA flags. WoWLAN power-save handling can otherwise leave firmware active after resume if TX woke it during suspend.

Test signals: suspend with no open interfaces, WoWLAN success/error/deferred-disconnect returns, active auth/assoc cleanup, BA session blocking and restoration on driver error, scheduled scan keep/cancel behavior, and queue/timer quiescence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rate.c -->
# sources/distributed-fs/ceph-client/net/mac80211/rate.c

Purpose: provides the mac80211 software rate-control framework: algorithm registration/selection, per-station lifecycle calls, TX-status feedback dispatch, fallback rate selection, user rate-mask enforcement, and rate table publication to drivers.

Important APIs and functions: exported registration functions are `ieee80211_rate_control_register()` and `ieee80211_rate_control_unregister()`. Runtime entry points include `rate_control_rate_init()`, `rate_control_rate_init_all_links()`, `rate_control_tx_status()`, `rate_control_rate_update()`, `rate_control_get_rate()`, `ieee80211_get_tx_rates()`, `rate_control_set_rates()`, `ieee80211_init_rate_ctrl_alg()`, `rate_control_deinitialize()`, and `ieee80211_check_rate_mask()`.

Control flow: initialization chooses an algorithm by requested name, module parameter, or built-in default unless the hardware owns rate control. Per-station initialization obtains the current channel band and invokes algorithm `rate_init`. TX status is serialized by `sta->rate_ctrl_lock` and dispatched to `tx_status_ext` or legacy `tx_status`. TX rate selection first handles low/min/basic-rate cases, skips software algorithms for hardware RC, calls the algorithm when available, then fills/fixes driver rate arrays and masks them against user and station capabilities.

State and persistence: global algorithm state is `rate_ctrl_algs` under `rate_ctrl_mutex`; per-hw state is `local->rate_ctrl`; per-station state is `sta->rate_ctrl_priv`, `sta->rate_ctrl_lock`, `WLAN_STA_RATE_CONTROL`, and RCU-published `sta->rates`. Settings are in module parameter and per-sdata rate masks.

Dependencies and integration points: integrates with `struct rate_control_ops`, debugfs, station/channel context state, driver callbacks `drv_link_sta_rc_update()` and `drv_sta_rate_tbl_update()`, S1G special handling, TX skb control blocks, and RCU-managed station rate tables.

Risks: MLO is explicitly unsupported for software rate control in this path. Mask fixups across legacy/HT/VHT can silently fall back when user masks conflict with supported/basic rates. RCU rate table publication assumes the documented non-concurrent caller contract.

Test signals: algorithm duplicate register/unregister, algorithm fallback selection, hardware-RC bypass, user mask conflicts with basic rates, non-data/no-ACK fallback rates, HT/VHT mask transitions, S1G defaults, and driver rate table update notifications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rate.h -->
# sources/distributed-fs/ceph-client/net/mac80211/rate.h

Purpose: declares the internal mac80211 rate-control interface shared by core TX/station code and rate-control algorithms.

Important APIs and types: `struct rate_control_ref` stores selected `rate_control_ops` and private algorithm data. Function declarations cover rate lookup, TX status, per-link/per-station initialization and updates, rate-mask validation, algorithm initialization/deinitialization, and Minstrel module init/exit. Inline helpers wrap algorithm per-station allocation/free and debugfs setup.

Control flow: users allocate per-station algorithm state through `rate_control_alloc_sta()`, add debugfs through `rate_control_add_sta_debugfs()`, and free via `rate_control_free_sta()`. `rate_control_add_debugfs()` creates the top-level `rc` debugfs directory, `name` file, and algorithm-specific debugfs entries when debugfs and an algorithm hook are present.

State and persistence: the header itself stores no state, but it defines access to `sta->rate_ctrl_lock`, `sta->rate_ctrl_priv`, `local->debugfs.rcdir`, and the selected algorithm reference. Debugfs entries are runtime-only.

Dependencies and integration points: includes mac80211 internals, station info, driver ops, skbuff/netdevice headers, and conditionally exposes `rcname_ops`. It also abstracts `CONFIG_MAC80211_RC_MINSTREL` so callers can invoke Minstrel init/exit regardless of build option.

Risks: inline helpers assume `sta->rate_ctrl` is valid. Debugfs helpers must tolerate missing algorithms or directories. Because this is internal glue, signature changes affect station lifecycle, TX, debugfs, and algorithm modules together.

Test signals: build with and without `CONFIG_MAC80211_DEBUGFS` and `CONFIG_MAC80211_RC_MINSTREL`, station alloc/free lifecycle, debugfs creation/removal, and algorithm-less hardware-RC configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.c -->
# sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.c

Purpose: implements the Minstrel HT/VHT software rate-control algorithm for mac80211, including rate grouping, probability/throughput estimation, sampling, retry table construction, capability updates, and registration as `minstrel_ht`.

Important APIs and functions: the `rate_control_ops mac80211_minstrel_ht` hooks are `minstrel_ht_tx_status()`, `minstrel_ht_get_rate()`, `minstrel_ht_rate_init()`, `minstrel_ht_rate_update()`, `minstrel_ht_alloc_sta()`, `minstrel_ht_free_sta()`, `minstrel_ht_alloc()`, `minstrel_ht_free()`, optional debugfs hooks, and `minstrel_ht_get_expected_throughput()`. Module entry/exit are `rc80211_minstrel_init()` and `rc80211_minstrel_exit()`. Core internals include `minstrel_ht_update_caps()`, `minstrel_ht_update_stats()`, `minstrel_ht_refill_sample_rates()`, `minstrel_ht_update_rates()`, `minstrel_ht_set_rate()`, `minstrel_calc_retransmit()`, and `minstrel_ht_get_tp_avg()`.

Control flow: allocation initializes contention/retry defaults, CCK/OFDM lookup tables, update interval, and randomized sample table. Capability updates rebuild supported HT/VHT/legacy groups from station bandwidth, SGI, SMPS, LDPC/STBC, VHT MCS map, and configured `minstrel_vht_only`. TX status accumulates per-rate attempts/successes, AMPDU length, and sample counters; periodically it recalculates filtered probabilities, sorted throughput/probability winners, sample buckets, retry counts, AMSDU limit, and publishes a new `ieee80211_sta_rates` table. `get_rate` injects one probe rate at `MINSTREL_SAMPLE_INTERVAL` when appropriate.

State and persistence: per-hw `minstrel_priv` stores hardware pointer, retry/segment parameters, legacy rate indexes, update interval, and optional fixed debugfs index. Per-station `minstrel_ht_sta` stores supported bitmaps, per-group stats, best rate indexes, sample queues, AMPDU averages, overheads, flags, and packet counters. State is in-memory and reset on capability updates or station recreation.

Dependencies and integration points: depends on rate framework callbacks, station capabilities, aggregation recalculation, RCU rate table publication via `rate_control_set_rates()`, random bytes for sampling, module parameters, debugfs, and mac80211 duration helpers.

Risks: this code is performance-sensitive and statistics-driven; subtle arithmetic or indexing errors can degrade throughput rather than fail loudly. VHT/HT group indexing, invalid VHT MCS filtering, legacy fallback, SMPS downgrades, and sample bucket maintenance all depend on consistent encoded `MI_RATE()` values. Debugfs fixed rate can override adaptive behavior.

Test signals: VHT/HT/legacy capability matrices, static/dynamic SMPS, short preamble CCK, bandwidth and SGI combinations, TX status with legacy status arrays and `rate_info` arrays, AMPDU and non-AMPDU feedback, sample scheduling, retry-count bounds, expected throughput, fixed-rate debugfs override, and rate table publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.h -->
# sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.h

Purpose: defines Minstrel HT/VHT constants, encoded rate helpers, data structures, and cross-file declarations used by the algorithm and debugfs renderer.

Important APIs and types: macros include `MINSTREL_SCALE`, `MINSTREL_FRAC()`, `MINSTREL_TRUNC()`, EWMA/noise-filter coefficients, group counts, `MI_RATE()`, `MI_RATE_IDX()`, `MI_RATE_GROUP()`, sample counts, and sample interval. Main structs are `minstrel_priv`, `mcs_group`, `minstrel_rate_stats`, `minstrel_mcs_group_data`, `minstrel_sample_category`, and `minstrel_ht_sta`. Exports include bitrate arrays, `minstrel_mcs_groups[]`, `minstrel_ht_add_sta_debugfs()`, and `minstrel_ht_get_tp_avg()`.

Control flow: the header shapes how `.c` encodes rates into a 16-bit group/index value, stores per-rate probability and retry state, organizes sample queues by type, and shares the station data with debugfs.

State and persistence: all structs describe runtime in-memory state. `minstrel_rate_stats` keeps current-period, last-period, and historical attempts/success counters plus filtered probabilities. `minstrel_ht_sta` keeps per-station selected rates and supported groups until the station is freed or capabilities are rebuilt.

Dependencies and integration points: relies on Linux bitfield helpers and mac80211/cfg80211 constants supplied by including C files. It is included by both the algorithm and debugfs implementation, so layout changes affect debugfs output and rate-selection state.

Risks: group-count constants and array dimensions must stay synchronized with `minstrel_mcs_groups[]`. Encoded rate bitfield widths constrain maximum group/rate indexes. Debugfs accesses these structs directly, so concurrent/statistical fields should remain readable without needing extra ownership assumptions beyond mac80211 rate-control locking conventions.

Test signals: compile-time array/group count checks, encoded rate round trips, fixed-point probability math, struct layout users in debugfs, and builds with/without debugfs enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht_debugfs.c -->
# sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht_debugfs.c

Purpose: exposes per-station Minstrel HT/VHT rate-control statistics through debugfs in human-readable and CSV formats.

Important APIs and functions: `minstrel_ht_add_sta_debugfs()` creates `rc_stats` and `rc_stats_csv` files. `minstrel_ht_stats_open()` and `minstrel_ht_stats_csv_open()` allocate a fixed 32 KiB buffer and render a snapshot. `minstrel_stats_read()` serves that buffer; `minstrel_stats_release()` frees it. `minstrel_ht_stats_dump()` and `minstrel_ht_stats_csv_dump()` format each supported rate. `minstrel_ht_is_sample_rate()` marks rates currently queued for sampling.

Control flow: opening a debugfs file snapshots `struct minstrel_ht_sta` into a temporary buffer, iterating CCK first, then HT groups before CCK, then remaining groups. Each row labels mode, guard interval, stream count, best-rate markers A-D, max-prob marker P, sample marker S, MCS/legacy name, encoded index, airtime, max throughput, average throughput, probability, retries, last attempts/successes, historical totals, and packet/sample counters.

State and persistence: debugfs data is generated on open and stored in `struct minstrel_debugfs_info` until release. It does not mutate rate-control state, except that it reads live counters without producing persistent artifacts.

Dependencies and integration points: depends on `rc80211_minstrel_ht.h` structs and helpers, debugfs file operations, module ownership, and simple read helpers. It is installed through Minstrel's `add_sta_debugfs` rate-control op.

Risks: the renderer uses `sprintf()` into a fixed 32 KiB allocation and only warns after rendering if the buffer was exceeded, so future group/rate growth can become a memory corruption risk unless converted to bounded formatting. It reads live stats without explicit locking in this file, so output can be inconsistent during concurrent updates, though it is diagnostic-only.

Test signals: opening both debugfs files for stations with legacy-only, HT, and VHT rates; buffer size with all groups supported; CSV row shape; best/prob/sample markers; and cleanup on open allocation failure or file release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/rc80211_minstrel_ht_debugfs.c -->
