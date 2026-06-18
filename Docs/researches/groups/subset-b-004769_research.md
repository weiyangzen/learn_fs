# subset-b-004769 Research

Grouped research for `subset-b-004769`, covering ath9k beaconing, channel-context/offchannel scheduling, common RX/init/debug/spectral helpers, DFS radar handling, Bluetooth coexistence, calibration, and dynamic ACK timeout code. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/beacon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/beacon.c

Purpose: Implements ath9k beacon generation, beacon queue programming, per-vif beacon slot ownership, CSA completion, SWBA tasklet handling, and mode-specific beacon timer setup for AP, mesh, IBSS, and station operation.

Important APIs/functions: `ath9k_beacon_assign_slot()`, `ath9k_beacon_remove_slot()`, `ath9k_beacon_ensure_primary_slot()`, `ath9k_csa_is_finished()`, `ath9k_csa_update()`, `ath9k_beacon_tasklet()`, `ath9k_beacon_config()`, and `ath9k_set_beacon()` are the external integration points. Internal helpers configure the beacon TXQ (`ath9k_beaconq_config()`), build beacon descriptors (`ath9k_beacon_setup()`), fetch mac80211 beacons and buffered multicast frames (`ath9k_beacon_generate()`), choose staggered slots, calculate TSF adjustment, and cache `struct ath_beacon_config`.

Control flow: mac80211 configuration calls cache beacon interval/DTIM/BMISS settings, updates `ATH_OP_BEACONS`, and dispatches to AP/IBSS/STA timer programming through common beacon helpers. On each SWBA, `ath9k_beacon_tasklet()` skips during reset, checks whether the prior beacon is still pending, handles stuck-beacon recovery and NF calibration hints, chooses the current slot, handles CSA completion, notifies the channel-context scheduler, regenerates and DMA maps the beacon skb, updates deferred slot-time changes, and posts the descriptor to the beacon queue. AP/mesh use staggered slots across `ATH_BCBUF`; station mode programs BMISS timers and does not transmit beacons.

State/persistence: State is in `sc->beacon` (`bbuf`, `bslot[]`, beacon queue, CAB queue, `bmisscnt`, slot-time update state, TX status flags), `ath_vif` (`av_bcbuf`, `av_bslot`, `tsf_adjust`, `chanctx`), `sc->cur_chan->beacon`, `common->op_flags`, and hardware interrupt masks/TSF/beacon registers. Beacon skb DMA mappings persist until regenerated or slot removal.

Dependencies/integration: Uses mac80211 beacon APIs, DMA mapping, ath9k TX descriptor/queue helpers, hardware beacon timers, channel context NoA insertion, CSA callbacks, power-save synchronization for IBSS joiners, and noise-floor recalibration from `calib.c`.

Risks: DMA unmap/free ordering for old beacon skb must stay exact. Slot re-enumeration adjusts TSF and can perturb multi-vif timing if `tsf_adjust` math is wrong. Missed-beacon thresholds interact with `nbcnvifs`, EDMA completion behavior, and channel-context beacon events. Zero beacon intervals are sanitized to avoid timer loops. CABQ flushing for multi-vif DTIMs can drop buffered multicast traffic by design.

Test signals: Verify AP/mesh beacon emission, multi-BSS staggered slots, IBSS creator/joiner synchronization, station BMISS interrupts, CSA completion, CAB traffic at DTIM, stuck-beacon reset path, NF recalibration after repeated misses, channel-context NoA IEs in generated beacons, and absence of DMA mapping leaks under vif add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/beacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.c

Purpose: Programs hardware Bluetooth coexistence for 2-wire, 3-wire, and MCI-capable ath9k chips, including GPIO routing, coexistence mode registers, WLAN/BT weight tables, enable/disable sequencing, and stomp policies.

Important APIs/functions: Exported entry points are `ath9k_hw_init_btcoex_hw()`, `ath9k_hw_btcoex_init_scheme()`, `ath9k_hw_btcoex_init_2wire()`, `ath9k_hw_btcoex_init_3wire()`, `ath9k_hw_btcoex_deinit()`, `ath9k_hw_btcoex_init_mci()`, `ath9k_hw_btcoex_set_weight()`, `ath9k_hw_btcoex_enable()`, `ath9k_hw_btcoex_disable()`, `ath9k_hw_btcoex_bt_stomp()`, and `ath9k_hw_btcoex_set_concur_txprio()`. Static weight tables encode AR9003 and MCI WLAN priorities for `ATH_BTCOEX_STOMP_*`.

Control flow: Scheme selection honors global `common->btcoex_enabled`, then picks MCI if available, otherwise 3-wire for AR9300+ or AR9285, and 2-wire for other AR9280+ parts. Init configures GPIO muxes and input requests. Hardware defaults build `bt_coex_mode`, `bt_coex_mode2`, and SoC mode3 fields. Enabling dispatches by scheme: 2-wire requests WLAN active output, 3-wire writes coex mode/weight registers and RX-clear GPIO output, and MCI writes MCI coex weights. Disabling clears `enabled`, resets MCI or legacy registers, and returns WLAN-active GPIO to output-low/simple output.

State/persistence: Persistent state lives in `ah->btcoex_hw`: scheme, GPIO numbers, cached register values, BT/WLAN weights, MCI state, AIC state, concurrency TX priority table, and `enabled`. Hardware state persists in GPIO mux/request ownership, AR_BT_COEX registers, AR_MCI weight registers, quiet/PCU fields, and pull-down/pull-up programming.

Dependencies/integration: Depends on silicon revision predicates, register macros, GPIO request/free helpers, MCI capability bits, debug logging, and higher-level BT coexistence policy code that chooses stomp type, duty cycle, scans, and antenna diversity.

Risks: Revision-specific GPIO and polarity choices are fragile. `ath9k_hw_btcoex_set_weight()` indexes by stomp type and assumes callers pass values below `ATH_BTCOEX_STOMP_MAX`. Concurrent TX priority bit insertion must match weight register layout. Deinit frees GPIOs unconditionally, so scheme initialization must have assigned valid pins. MCI and non-MCI disable paths intentionally differ.

Test signals: Exercise AR9280 2-wire, AR9285/AR9300 3-wire, AR9462/AR9565 MCI, global disable, enable/disable cycles, stomp all/low/none/audio/FTP policies, concurrent TX priority override, GPIO ownership cleanup, and Bluetooth/WLAN throughput or scan coexistence behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.h

Purpose: Declares ath9k Bluetooth coexistence constants, scheme/stomp enums, MCI/AIC/coex hardware state structures, and hardware coexistence APIs.

Important APIs/types: GPIO constants describe AR9280 and AR9300 WLAN-active, BT-active, and BT-priority pins. Timing/duty-cycle thresholds cover default BT period, duty cycle, scan duty cycle, BMISS threshold, priority counters, RX wait, FTP stomp threshold, and max TX power limits. `enum ath_stomp_type` selects WLAN aggressiveness toward BT traffic. `enum ath_btcoex_scheme` selects none, 2-wire, 3-wire, or MCI. `struct ath9k_hw_mci` tracks MCI interrupts, GPM/scheduler buffers, WLAN channel bitmaps, calibration sequence, BT version/state, FTP stomp, concurrent TX, and recovery timestamp. `struct ath9k_hw_aic` stores antenna interference cancellation state and SRAM image. `struct ath_btcoex_hw` aggregates scheme, MCI/AIC, GPIO pins, cached coex register settings, weight arrays, and per-stomp TX priority.

Control flow: This header supplies the state layout consumed by `btcoex.c` and other ath9k MCI/AIC policy files. Callers initialize scheme and hardware state, choose 2-wire/3-wire/MCI init, update weights or stomp, then enable/disable coexistence around runtime policy decisions.

State/persistence: All persistent coexistence policy and hardware shadow registers are in `struct ath_btcoex_hw` under `struct ath_hw`. The header does not allocate or own memory, but its `gpm_buf` pointer and channel arrays are long-lived MCI state.

Dependencies/integration: Includes `hw.h`, uses AR9300 weight dimensions, ATH AIC channel count, and exported functions implemented in `btcoex.c`.

Risks: Enum ordering is ABI-like within the driver because weight arrays are indexed by `enum ath_stomp_type`. Structure fields are hardware-policy coupled; accidental reinitialization can lose MCI calibration or BT version state. No bounds helpers are declared for stomp indexes.

Test signals: Compile all BT coexistence configurations, validate MCI initialization state defaults, confirm stomp arrays have `ATH_BTCOEX_STOMP_MAX` entries, and verify feature-guarded call sites use declared APIs consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/btcoex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.c

Purpose: Provides common ath9k calibration support, centered on noise-floor calibration history, NF loading into baseband, calibration validity reset, and stuck-beacon interference handling.

Important APIs/functions: Exported APIs are `ath9k_hw_getchan_noise()`, `ath9k_hw_reset_calibration()`, `ath9k_hw_reset_calvalid()`, `ath9k_hw_start_nfcal()`, `ath9k_hw_loadnf()`, `ath9k_hw_getnf()`, `ath9k_init_nfcal_hist_buffer()`, and `ath9k_hw_bstuck_nfcal()`. Internal helpers compute median NF history (`ath9k_hw_get_nf_hist_mid()`), choose 2 GHz/5 GHz NF limits, read EEPROM NF thresholds, update history buffers, and sanitize raw readings.

Control flow: Calibration reset calls hardware setup, marks current calibration running, clears measurement signs, and resets sample count. NF start sets pending state, enables/disables baseband NF update, and triggers AGC NF. NF load writes cached/default/override NF values to `ah->nf_regs`, forces baseband load, waits up to 22.2 ms, optionally restarts an interrupted NF calibration, and restores max CCA power to `-50`. NF get refuses incomplete AGC NF, reads raw NF through hardware ops, clamps against per-band limits, warns on EEPROM threshold failures, updates per-chain median history, stores channel noisefloor, and updates `ah->noise`.

State/persistence: State lives in `ah->caldata`, `nfCalHist[]`, `cal_flags` (`NFCAL_PENDING`, `NFCAL_INTF`), `ah->cal_list*`, `ah->meas*`, `ah->cal_samples`, `ah->noise`, `chan->noisefloor`, `ah->nf_override`, and hardware AGC/NF registers. NF history persists per channel calibration data and smooths transient readings.

Dependencies/integration: Uses `hw.h`, `hw-ops.h`, Linux sort/export, EEPROM ops, ath debug categories, channel width helpers, register RMW buffering, and beacon stuck handling from `beacon.c`.

Risks: NF load timeout handling intentionally returns before restoring `-50` to avoid RX deafness from overlapping loads. Incorrect chainmask or HT40 gating can touch wrong NF registers. Interference mode bypasses max NF clamping after stuck beacons; failure to clear it would keep elevated NF. `nf_override` from debugfs directly affects baseband NF programming.

Test signals: Verify NF median updates, invalid-count warmup behavior, 2 GHz/5 GHz limits, HT20/HT40 chain handling, NF timeout path, forced override, stuck-beacon NF recalibration, calibration-valid reset on supported revisions, and stable RX sensitivity after repeated channel resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.h

Purpose: Declares ath9k calibration data structures, INI table helpers, calibration list macros, NF history limits, PA calibration state, and common calibration entry points.

Important APIs/types: `struct ar5416IniArray` wraps register initialization tables with rows/columns and access macros. `INIT_CAL()` and `INSERT_CAL()` build a circular list of `struct ath9k_cal_list`. `enum ath9k_cal_state` defines inactive, waiting, running, and done states. `struct ath9k_percal_data` supplies hardware calibration callbacks and sample counts. `struct ath9k_nfcal_hist` stores five NF readings, current index, private median NF, and invalid warmup count. `struct ath9k_pacal_info` tracks PA calibration offset and skip counters.

Control flow: Hardware-specific init code declares per-calibration objects, initializes them with these macros, starts/reset calibrations through `ath9k_hw_reset_calibration()`, and manages NF through the exported functions implemented in `calib.c`.

State/persistence: The header defines persistent per-device/per-channel calibration containers but does not allocate them. NF history length, invalid warmup length, min/max sample constants, and PA skip limits are compile-time behavioral constants.

Dependencies/integration: Includes `hw.h` and is used by hardware calibration, reset, debugfs NF dumps, and channel change paths.

Risks: The circular list macro assumes callers initialize `cal_list_last` correctly. INI macros cast table storage to `u32 *` and rely on rectangular arrays. `NUM_NF_READINGS` is six, representing control and extension chains, so callers must gate extension readings on HT40.

Test signals: Compile coverage for all hardware families, calibration list insertion order, NF history initialization, NF dump formatting, and channel-width-specific NF register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/calib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/channel.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/channel.c

Purpose: Implements ath9k channel changing, optional multi-channel channel-context scheduling, offchannel scan/remain-on-channel operations, queue management during context switches, P2P Notice of Absence generation, and P2P power-save timer handling.

Important APIs/functions: Always-built APIs include `ath_chanctx_init()` and `ath_chanctx_set_channel()`. Under `CONFIG_ATH9K_CHANNEL_CONTEXT`, key APIs include `ath_is_go_chanctx_present()`, `ath_chanctx_check_active()`, `ath_chanctx_event()`, beacon event wrappers, `ath_offchannel_next()`, `ath_roc_complete()`, `ath_scan_complete()`, `ath_chanctx_set_next()`, `ath9k_offchannel_init()`, `ath9k_init_channel_context()`, `ath9k_deinit_channel_context()`, `ath9k_is_chanctx_enabled()`, queue stop/wake helpers, `ath9k_beacon_add_noa()`, P2P callbacks, and P2P timer init/deinit.

Control flow: `ath_set_channel()` updates old survey stats, resolves the internal channel, resets survey in-use state, calls `ath_reset()`, updates old NF, and enables DFS radar or spectral channel-scan triggering. The channel-context state machine consumes beacon prepare/sent, TSF timer, beacon receive, authorization, switch, assignment, unassignment, and multi-channel enable events. It schedules switches after beacons or half beacon intervals, sets backup software timers, updates NoA, queues `chanctx_work`, and performs the actual switch under `sc->mutex`. Offchannel scan/RoC code advances scan indexes, sends probe requests, times channel dwell, reports mac80211 scan/RoC completion, and returns to an operating context.

State/persistence: State spans `sc->cur_chan`, `sc->next_chan`, `sc->chanctx[]`, `sc->offchannel.chan`, `sc->sched` timers/flags/timestamps, `sc->offchannel` scan/RoC fields, per-context `vifs`, `active`, `assigned`, `stopped`, `txpower`, `flush_timeout`, TSF snapshots, queued AC lists, and `ath_vif` NoA/P2P fields. Hardware persistence includes current channel, TSF, gen timer, RX filter, and queue stop/wake state. Survey state is stored in `sc->survey[]` and `sc->cur_survey`.

Dependencies/integration: Integrates with cfg80211 chandefs, mac80211 channel contexts, scan and RoC callbacks, ath reset/TX/flush/power-save helpers, beacon tasklet events, DFS/spectral scan, hardware gen timers, aggregation sleep/wakeup, and P2P NoA parsing/updating.

Risks: The state machine is timing-sensitive and relies on spinlocks, workqueues, timers, and mutex boundaries. Switching must stop queues, flush TX, send PS nullfunc frames, snapshot TSF, reset hardware when chandef changes, and wake queues only when safe. Offchannel pending/wait flags can otherwise strand scans or RoC. NoA duration/index updates must match beacon timing. P2P timer shares the hardware gen timer path with channel switching.

Test signals: Multi-channel AP+STA/P2P GO+client operation, offchannel scan across active contexts, RoC ready/expire/cancel/abort, queue stop/wake ordering, PS nullfunc transmission, TSF adjustment after beacon receive, NoA IE contents, spectral chanscan trigger, DFS radar filter enable, and regressions under association/disassociation or vif removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/channel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.c

Purpose: Provides shared ath9k/ath9k-common beacon timer calculations for station, IBSS, and AP modes.

Important APIs/functions: `ath9k_cmn_beacon_config_sta()` fills `struct ath9k_beacon_state` for station BMISS/sleep timers. `ath9k_cmn_beacon_config_adhoc()` prepares IBSS SWBA timing. `ath9k_cmn_beacon_config_ap()` prepares AP/mesh staggered SWBA timing. `ath9k_get_next_tbtt()` is the core helper that advances TSF by a fudge factor and software beacon response time, then rounds to the next beacon interval.

Control flow: STA configuration is skipped with `-EPERM` until `ATH_OP_PRIM_STA_VIF` is set. It computes next TBTT and DTIM from current TSF, clamps BMISS threshold to 1..15, selects a 100 ms sleep duration rounded to beacon/DTIM periods, and sets TSF out-of-range threshold. IBSS converts interval to usec, chooses first TBTT directly for creators or next TBTT for joiners, and toggles SWBA in `ah->imask`. AP divides the beacon interval by buffer count for staggered SWBA and toggles SWBA similarly.

State/persistence: Mutates `struct ath_beacon_config` (`intval`, `nexttbtt`) and `ah->imask`; station mode also fills a caller-supplied `struct ath9k_beacon_state` consumed by hardware timer programming.

Dependencies/integration: Used by `beacon.c`, depends on `common.h`, hardware TSF reads, `ATH_OP_PRIM_STA_VIF`, and ath debug logging.

Risks: Units differ by mode: `beacon_interval` is in TU, while `intval` and `nexttbtt` are programmed in usec. Incorrect `bc_buf` or zero intervals can break SWBA cadence. BMISS threshold clamping affects roaming and false disconnect behavior.

Test signals: Station association BMISS timers, DTIM sleep alignment, IBSS creator and joiner beacon start, AP multi-BSS staggered SWBA interval, and interrupt mask toggling when beacons are enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.h

Purpose: Declares the shared beacon timer configuration APIs used by ath9k front-end code.

Important APIs/types: Forward declares `struct ath_beacon_config` and declares `ath9k_cmn_beacon_config_sta()`, `ath9k_cmn_beacon_config_adhoc()`, and `ath9k_cmn_beacon_config_ap()`.

Control flow: The header forms the compile-time contract between mode-specific beacon code and common timer math. Station callers pass an output `ath9k_beacon_state`; AP/IBSS callers mutate the beacon config and hardware interrupt mask through implementation side effects.

State/persistence: No direct state; all persistent state is in `ath_hw`, `ath_beacon_config`, and caller-provided timer structures.

Dependencies/integration: Included through `common.h` and consumed by `beacon.c` and shared ath9k code.

Risks: It has no include guard in this snapshot, relying on inclusion discipline. API users must respect TU/usec unit conversions performed by the implementation.

Test signals: Build coverage for all beacon modes and static analysis for duplicate inclusion or missing prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-beacon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.c

Purpose: Implements common debugfs readers and RX statistic accounting shared by ath9k components.

Important APIs/functions: Exported functions are `ath9k_cmn_debug_modal_eeprom()`, `ath9k_cmn_debug_base_eeprom()`, `ath9k_cmn_debug_stat_rx()`, `ath9k_cmn_debug_recv()`, and `ath9k_cmn_debug_phy_err()`. File operations expose `modal_eeprom`, `base_eeprom`, `recv`, and `phy_err`.

Control flow: EEPROM readers allocate fixed buffers, call `ah->eep_ops->dump_eeprom()` with base/modal selection, copy data to user, and free. RX stat accounting increments all-packet/byte counts, descriptor error counts, and per-PHY-error buckets when `rs_phyerr` is in range. Debugfs read paths format accumulated common RX counters or named PHY error counters into temporary buffers and return them through `simple_read_from_buffer()`.

State/persistence: Persistent stats live in caller-owned `struct ath_rx_stats`. Debugfs files hold private data pointers to `ath_hw` or `ath_rx_stats`; buffers are per-read allocations only.

Dependencies/integration: Depends on debugfs, EEPROM ops, `struct ath_rx_status`, PHY error enum values, and exported common debug declarations. `debug.c` registers these files under the ath9k debugfs directory.

Risks: Fixed output buffers can truncate future expanded counter sets. Stat increments are not locked here, so readers can observe racing updates. EEPROM dump size assumptions must match hardware implementation.

Test signals: Read debugfs EEPROM files on supported cards, inject RX statuses for CRC/decrypt/MIC/PHY errors, verify per-PHY counters, and confirm disabled common-debug builds compile to inline no-ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.h

Purpose: Defines shared RX statistics and conditional debug helper prototypes/no-op stubs for ath9k common debug support.

Important APIs/types: `struct ath_rx_stats` records aggregate RX packets/bytes, CRC/decrypt/MIC/PHY errors, delimiter/decrypt-busy errors, per-PHY-error counters, length/OOM/rate/fragment drops, beacon/fragments, and spectral sample counters. Under `CONFIG_ATH9K_COMMON_DEBUG`, prototypes expose EEPROM and RX debugfs helpers; otherwise static inline no-ops preserve call sites.

Control flow: RX paths update `ath_rx_stats` directly or through `ath9k_cmn_debug_stat_rx()`. Debug initialization registers files only when common debug is built.

State/persistence: This header defines the persistent RX stats structure embedded in ath9k debug stats. It does not synchronize updates.

Dependencies/integration: Requires PHY error constants and `struct ath_rx_status` from ath9k hardware headers; included by `common.h` and `debug.h`.

Risks: Counter width is `u32`, so long-lived systems can wrap. No-op stubs mean tests must cover both debug-enabled and debug-disabled builds.

Test signals: Compile matrix with and without `CONFIG_ATH9K_COMMON_DEBUG`, RX counter increments, spectral sample good/error accounting, and debugfs output consistency with structure fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.c

Purpose: Initializes common mac80211 channel/rate tables and HT capability data for ath9k devices.

Important APIs/functions: `ath9k_cmn_init_channels_rates()` allocates and installs 2 GHz/5 GHz supported band channel/rate tables. `ath9k_cmn_setup_ht_cap()` fills `struct ieee80211_sta_ht_cap` from hardware capabilities and chainmasks. `ath9k_cmn_reload_chainmask()` refreshes HT capabilities after chainmask changes.

Control flow: Static channel tables define calibrated 2 GHz channels 1..14 and selected 5 GHz UNII/middle band channels, with `hw_value` used as the private channel array index. Legacy rate table includes CCK and OFDM rates plus half/quarter support flags. Init copies tables into devm-allocated memory only for bands advertised by `ah->caps.hw_caps`. HT setup enables 20/40, SMPS, SGI40, DSSS/CCK40, optional LDPC/SGI20/STBC, chooses max streams by silicon revision, counts active TX/RX chains, sets TX MCS mismatch bits, and fills RX MCS masks.

State/persistence: Populates `common->sbands[]` channel/rate/HT capability fields. Allocations are devm-managed against `ah->dev`.

Dependencies/integration: Used during hardware registration with mac80211. Depends on revision predicates, capability bits, `ath9k_cmn_count_streams()`, and cfg80211/mac80211 band/rate structures.

Risks: `hw_value` must remain aligned with `ATH9K_NUM_CHANNELS` and `ah->channels[]`; a build-time assertion checks total count. Revision-to-stream mapping is hardware-specific. Partial allocation failure can leave one band initialized before returning `-ENOMEM`.

Test signals: Device registration for 2 GHz only, 5 GHz only, dual-band, HT-capable and legacy chips, chainmask reload after antenna changes, and mac80211 visible rates/MCS masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.h

Purpose: Declares common ath9k initialization helpers for channel/rate tables and HT capability setup.

Important APIs: `ath9k_cmn_init_channels_rates()`, `ath9k_cmn_setup_ht_cap()`, and `ath9k_cmn_reload_chainmask()`.

Control flow: Driver probe code initializes supported bands, then HT capability setup is run per supported band and can be re-run when chainmasks change.

State/persistence: No direct state; callers pass `ath_common`, `ath_hw`, and mac80211 HT capability structures mutated by the implementation.

Dependencies/integration: Included by `common.h`, used by ath9k and ath9k_htc style common initialization.

Risks: Header is minimal and has no explicit include guard in this snapshot; duplicate inclusion is expected through controlled includes.

Test signals: Build coverage and device registration checks for visible channels/rates/HT capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.c

Purpose: Implements spectral scan FFT sample parsing, validation, relayfs output, debugfs controls, and hardware trigger/configuration helpers.

Important APIs/functions: Exported APIs are `ath_cmn_process_fft()`, `ath9k_cmn_spectral_scan_trigger()`, `ath9k_cmn_spectral_scan_config()`, `ath9k_cmn_spectral_init_debug()`, and `ath9k_cmn_spectral_deinit_debug()`. Internal handlers validate HT20 and HT20/40 max-index/magnitude metadata, construct `fft_sample_ht20` or `fft_sample_ht20_40` TLVs, compensate for missing/extra MAC bytes, and write samples to a relay channel.

Control flow: RX processing accepts only radar/false-radar/spectral PHY errors with the spectral bit set. If relay buffers are full, it reports the frame as consumed without parsing. It chooses HT20 or HT40 parsing from the current chandef, scans the raw report for FFT sample boundaries, validates metadata, fixes the single-sample short/extra-byte cases when possible, emits TLVs, increments good/error spectral sample counters, and mixes bin data into the kernel randomness pool. Debugfs `spectral_scan_ctl` reads/writes mode strings (`disable`, `background`, `chanscan`, `manual`, `trigger`). Trigger enables PHYRADAR/PHYERR RX filters, reconfigures hardware, and calls the hardware spectral trigger op.

State/persistence: State lives in `struct ath_spec_scan_priv`: `ah`, relay channel pointer, current `spectral_mode`, and `spec_config` fields (`enabled`, `endless`, `short_repeat`, `count`, `period`, `fft_period`). Persistent debugfs files control config; relayfs buffers persist until deinit.

Dependencies/integration: Uses `linux/relay.h`, `linux/random.h`, spectral common TLV definitions, ath hardware ops (`spectral_scan_trigger`, `spectral_scan_config`), power-save ops, RX stats macros, debugfs, and channel scan triggering from `channel.c`.

Risks: FFT reports can be malformed by hardware byte insertion/deletion; parser recovery is intentionally conservative. Buffer-full conditions drop processing. Spectral and DFS both use PHY error paths and cannot be used concurrently during DFS radar detection. TX99 disables spectral control. User debugfs writes directly affect hardware scan mode and RX filter.

Test signals: HT20 and HT40 FFT reports, single-sample correction cases, malformed/truncated reports, relay buffer full handling, debugfs mode/config writes, channel-scan trigger on channel change, spectral disabled under TX99, and RX stats for good/error samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.h

Purpose: Defines spectral scan modes, hardware FFT report layouts, per-device spectral scan state, max-magnitude/index helpers, and conditional spectral API declarations.

Important APIs/types: `enum spectral_mode` defines disabled, background, manual, and channel-scan modes. `struct ath_radar_info`, `ath_ht20_mag_info`, `ath_ht20_fft_packet`, `ath_ht20_40_mag_info`, and `ath_ht20_40_fft_packet` document PHY report tails and FFT metadata. `struct ath_spec_scan_priv` carries hardware pointer, relay channel, current mode, and hardware spectral config. Inline helpers decode max magnitude, signed max index, HT20/HT40 index mappings, and bitmap weight. Conditional declarations expose spectral init/deinit, trigger/config, and RX FFT processing.

Control flow: The implementation uses the structures for parsing but warns that full packet structs are reference-only because the MAC can vary sample byte counts. Callers initialize debug, configure mode, trigger scans, and feed spectral PHY error payloads through `ath_cmn_process_fft()`.

State/persistence: Persistent state is the `ath_spec_scan_priv` embedded in the driver softc. Constants define expected sample lengths and maximum stack buffer size.

Dependencies/integration: Includes `../spectral_common.h` for TLV and bin counts; depends on ath common/hardware types through included users.

Risks: Signed max-index decoding is subtle and bounds-clamps invalid values to zero. HT40 index remapping assumes lower/upper half layout. Feature-disabled builds turn most functions into no-ops; notably `ath9k_cmn_spectral_scan_config()` has no stub in this snapshot, so callers must be feature-gated.

Test signals: Compile with and without `CONFIG_ATH9K_COMMON_SPECTRAL`, max-index helper unit coverage for negative/positive bins, HT20/HT40 sample length constants, and real spectral TLV consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common-spectral.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.c

Purpose: Supplies shared ath9k and ath9k_htc helpers for RX acceptance/post-processing, RX rate/RSSI translation, TX crypto key type selection, channel conversion, stream counting, TX power updates, and hardware key cache initialization.

Important APIs/functions: Exported APIs include `ath9k_cmn_rx_accept()`, `ath9k_cmn_rx_skb_postprocess()`, `ath9k_cmn_process_rate()`, `ath9k_cmn_process_rssi()`, `ath9k_cmn_get_hw_crypto_keytype()`, `ath9k_cmn_get_channel()`, `ath9k_cmn_count_streams()`, `ath9k_cmn_update_txpow()`, and `ath9k_cmn_init_crypto()`.

Control flow: RX acceptance filters descriptor errors while allowing decrypt/MIC/keymiss cases that mac80211 can process, normalizes keymiss handling for CCMP only, flags failed FCS/decrypt/MIC conditions, and handles TKIP MIC stripping/error reporting. Postprocess removes hardware padding, marks decrypted frames by descriptor key index or IV key ID, and forces software decrypt for management frames when configured. Rate processing maps HT and legacy hardware rates to mac80211 RX status. RSSI processing skips aggregate subframes without signal, reports per-chain signal, and low-pass filters beacon RSSI for ANI. Channel conversion maps cfg80211 width/band to internal `channelFlags`.

State/persistence: Mutates RX status flags, skb data pointer/length, `common->last_rssi`, `ah->stats.avgbrssi`, `ah->channels[]`, regulatory max power, and key cache contents. Crypto state uses `common->keymap`, `tkip_keymap`, `ccmp_keymap`, `keymax`, and `crypt_caps`.

Dependencies/integration: Depends on mac80211 RX/TX status formats, ath hardware descriptors, channel width helpers, regulatory TX power helpers, and hardware key reset.

Risks: Padding removal uses header length and skb length checks; mistakes corrupt frames. Keymiss/decrypt logic is security-sensitive. RSSI chain indexing compresses active chains and must match chainmask. Channel `hw_value` must match internal array indexes. TX power readback can differ from requested due to regulatory clamping.

Test signals: RX error matrix for CRC/decrypt/MIC/keymiss, TKIP MIC stripped vs reported, management software crypto, HT/legacy/short-preamble rates, half/quarter bandwidth, per-chain RSSI, channel width flags, TX power clamping, and key cache reset at init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.h

Purpose: Central common header for ath9k shared code, pulling in mac80211, ath core, hardware ops, and common init/beacon/debug/spectral headers while defining shared RSSI, aggregation, beacon config, and helper prototypes.

Important APIs/types: Defines block-ack buffer sizing constants, RSSI low-pass filter macros, `IEEE80211_MS_TO_TU()`, and `struct ath_beacon_config`. Declares common RX processing, crypto, channel, stream count, TX power, and crypto initialization functions.

Control flow: Driver RX/TX/channel/beacon code includes this header to get consistent helper contracts and shared macros. RSSI macros update filtered beacon RSSI only above threshold and convert fixed-point EP values back to integer RSSI.

State/persistence: `struct ath_beacon_config` is embedded in channel context state and persists beacon interval, DTIM, BMISS, creator/enabled flags, next TBTT, and programmed interval. Other macros operate on caller-owned state.

Dependencies/integration: Includes `../ath.h`, `hw.h`, `hw-ops.h`, and other ath9k common headers; exposes interfaces implemented in `common.c`.

Risks: Macro side effects require careful argument use. Beacon config stores mixed units (`beacon_interval` in TU, `intval` in usec after configuration). Header fan-in makes it sensitive to include-order changes.

Test signals: Build all common consumers, RSSI filter behavior, beacon config unit handling, and include dependency cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.c

Purpose: Implements ath9k debugfs and ethtool statistics, hardware register diagnostics, mutable debug knobs, and debug statistic accounting.

Important APIs/functions: External/stat APIs include `ath9k_debug_sync_cause()`, `ath9k_debug_stat_ant()`, `ath_debug_stat_interrupt()`, `ath_debug_stat_tx()`, `ath_debug_stat_rx()`, `ath9k_get_et_strings()`, `ath9k_get_et_sset_count()`, `ath9k_get_et_stats()`, `ath9k_deinit_debug()`, and `ath9k_init_debug()`. Debugfs operations cover `debug`, `ani`, `bt_ant_diversity`, `antenna_diversity`, `dma`, `interrupt`, `xmit`, `queues`, `misc`, `reset`, `regidx`, `regval`, `regdump`, `dump_nfcal`, `btcoex`, `ack_to`, `wow`, `tpc`, and `nf_override`.

Control flow: Init creates the `ath9k` debugfs directory under the wiphy, initializes DFS/tx99/spectral/common debug files, and registers per-feature files. Read paths format current driver or hardware state, often waking hardware before register access and restoring power state after. Write paths parse user input and mutate driver state: debug mask, ANI enable, BT antenna diversity, user reset, selected register index/value, WOW, TPC, and NF override. Ettool stats copy fixed names and fill totals plus per-AC TX and RX counters.

State/persistence: Debug stats live in `sc->debug.stats` and include interrupt, TX, RX, DFS, antenna, and reset counters. Debugfs mutable state includes `common->debug_mask`, `common->disable_ani`, `common->bt_ant_diversity`, `sc->debug.regidx`, `sc->force_wow`, `ah->tpc_enabled`, and `ah->nf_override`; register writes persist in hardware.

Dependencies/integration: Uses debugfs, seq_file, vmalloc, mac80211 wiphy debugfs, ath power-save helpers, reset work, tx/queue structures, common debug and spectral/DFS init, btcoex/tx99/WOW feature code, calibration NF history, and ethtool stats callbacks.

Risks: Debugfs is operationally powerful: arbitrary register write, forced reset, NF override, and TPC/ANI toggles can destabilize live hardware. Most counters are unsynchronized `u32`. `regdump` skips hard-coded register holes and allocates based on revision. User reset must avoid shutdown invalid state. NF override validates only non-positive values down to `-120`.

Test signals: Debugfs file presence under feature matrices, read/write validation errors, power-state wake/restore around register access, ethtool string/count alignment, reset write queuing, NF override immediate load, counter increments from IRQ/TX/RX paths, and debugfs teardown closing spectral relay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.h

Purpose: Defines ath9k debugfs/statistics structures, reset reason enum, counter macros, debug API prototypes, and no-op stubs for feature-disabled builds.

Important APIs/types: `enum ath_reset_type` names reset causes. Counter macros `TX_STAT_INC`, `RX_STAT_INC`, `RESET_STAT_INC`, `ANT_STAT_INC`, and `ANT_LNA_INC` update stats when debugfs is enabled. `struct ath_interrupt_stats`, `ath_tx_stats`, `ath_rx_rate_stats`, `ath_airtime_stats`, `ath_antenna_stats`, `ath_stats`, and `ath9k_debug` define the persistent debug state. Function prototypes cover debug init/deinit, IRQ/TX/RX/antenna/sync stats, ethtool stats, and per-station debugfs.

Control flow: Runtime paths increment stats through macros and helper functions. Debugfs init exposes those stats; ethtool callbacks serialize a subset. Station statistics are separately gated by `CONFIG_ATH9K_STATION_STATISTICS`.

State/persistence: `struct ath9k_debug` is embedded in `ath_softc` and persists the debugfs dentry, selected register index, and stats for the device lifetime. All counters are `u32` except ethtool exports as `u64`.

Dependencies/integration: Includes `hw.h` and `dfs_debug.h`; used widely by TX, RX, reset, IRQ, antenna diversity, DFS, and station code.

Risks: Counter macros compile to no-ops without debugfs, so code must not depend on side effects. Reset enum ordering must match `debug.c` display arrays. Per-queue stats index by hardware queue number and assume mapped queues exist.

Test signals: Compile with debugfs and station statistics enabled/disabled, reset cause display coverage, ethtool stat count matches string table, and no side-effect dependencies on stat macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug_sta.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug_sta.c

Purpose: Adds per-station debugfs files for aggregation state and received rate statistics.

Important APIs/functions: `ath_debug_rate_stats()` updates per-station RX rate counters. `ath9k_sta_add_debugfs()` creates `node_aggr` and `node_recv` files. Static file readers format TID aggregation window state and HT/legacy receive counts.

Control flow: RX data frames call `ath_debug_rate_stats()`, which finds the station by source address under RCU, maps the RX status to HT, CCK, or OFDM buckets, and increments HT20/HT40/SGI/LGI or legacy preamble/rate counters. `node_aggr` verifies HT support, then locks each TID TXQ and prints active BA window fields. `node_recv` prints MCS counters when HT is supported, then legacy CCK/OFDM counters based on current band.

State/persistence: Per-station state lives in `struct ath_node`: `rx_rate_stats`, aggregation TID state, max AMPDU, MPDU density, station pointer, and softc pointer. Debugfs files hold private pointers to `ath_node`.

Dependencies/integration: Requires mac80211 station lookup/debugfs hooks, ath TX aggregation structures, `debug.h` rate stats, and RX status processing from common paths.

Risks: Station lifetime must outlive debugfs private data as managed by mac80211. Rate index assumptions differ for 2 GHz OFDM (`rate_idx - 4`) and 5 GHz. Aggregation readers lock TXQs but stats increments are unsynchronized.

Test signals: Per-station debugfs creation/removal, HT and non-HT station output, RX frames at all MCS/legacy rates, 2 GHz OFDM index adjustment, and aggregation state during active BA sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/debug_sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.c

Purpose: Processes ath9k DFS/radar PHY error payloads, filters false radar pulses, detects chirping signatures, feeds the DFS pattern detector, and reports radar to mac80211.

Important APIs/functions: Public API is `ath9k_dfs_process_phyerr()`. Internal helpers parse FFT max bins for chirp detection (`ath9k_check_chirping()`), convert hardware duration units to microseconds, postprocess bandwidth/RSSI/duration into `struct pulse_event`, and call the `dfs_pattern_detector`.

Control flow: RX code calls `ath9k_dfs_process_phyerr()` for PHY errors. Non-radar PHY errors, zero data length, invalid bandwidth info, and unusable RSSI are counted and discarded. The last three bytes of the payload provide pulse BW info and primary/extension durations. RSSI is sanitized from signed 8-bit hardware values. Primary, extension, or dual-channel events choose the correct duration and RSSI. Width is converted to usec; pulses in chirp-width range are checked against a sequence of FFT max-bin deltas. Accepted pulses are sent to the pattern detector for the primary channel and, in HT40 extension cases, again for the extension frequency offset by +/-20 MHz. Detector matches call `ieee80211_radar_detected()`.

State/persistence: Uses `sc->dfs_detector`, `sc->dfs_prev_pulse_ts`, `sc->debug.stats.dfs_stats`, `ah->curchan`, and current channel flags. No allocation occurs in this file.

Dependencies/integration: Depends on `dfs_pattern_detector`, mac80211 radar notification, ath RX status, channel helpers, `dfs_debug.h` counters, and hardware-specific DFS payload layout.

Risks: DFS correctness is regulatory-sensitive. Payload parsing assumes at least three trailer bytes after nonzero `rs_datalen`; malformed shorter packets would be risky. Chirp detection tolerances and HT40 primary/extension swaps affect false positives/negatives. DFS and spectral share PHY error reports.

Test signals: Radar PHY errors for primary, extension, and dual-channel pulses; signed RSSI discard cases; invalid BW info and zero length; chirp and non-chirp FCC pulse patterns; HT40 plus/minus frequency mapping; detector match leading to mac80211 radar notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.h

Purpose: Declares the DFS radar PHY-error processing entry point and provides a no-op stub when certified DFS support is not built.

Important APIs: `ath9k_dfs_process_phyerr(struct ath_softc *sc, void *data, struct ath_rx_status *rs, u64 mactime)` is available under `CONFIG_ATH9K_DFS_CERTIFIED`.

Control flow: RX PHY error paths can call this unconditionally when included; the implementation is compiled only for certified DFS builds, otherwise the inline stub drops the event.

State/persistence: No direct state. The implementation uses `ath_softc` DFS detector and debug stats.

Dependencies/integration: Includes `../dfs_pattern_detector.h` and relies on ath softc/RX status declarations from including contexts.

Risks: Feature-disabled builds silently ignore radar processing, so regulatory behavior depends on build configuration and hardware flags. Callers must still ensure RX filters are configured appropriately.

Test signals: Compile with and without `CONFIG_ATH9K_DFS_CERTIFIED`, radar RX path invocation, and absence of unresolved symbols in non-DFS builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.c

Purpose: Exposes DFS detector and pool statistics through debugfs and provides a debugfs trigger to simulate radar detection.

Important APIs/functions: `ath9k_dfs_init_debug()` creates `dfs_stats` and `dfs_simulate_radar`. `read_file_dfs()` formats hardware DFS support, detector availability, per-wiphy pulse stats, detector region, and global pool stats. `write_file_dfs()` resets per-device DFS stats only when a magic value is written. `write_file_simulate_radar()` calls `ieee80211_radar_detected()`.

Control flow: Debug init registers files under `sc->debug.debugfs_phy`. Reading stats pulls current pool stats from `sc->dfs_detector->get_stats()`. Writing `0x80000000` to `dfs_stats` clears `sc->debug.stats.dfs_stats`; other values are accepted but ignored. Writing any data to `dfs_simulate_radar` reports radar to mac80211.

State/persistence: Uses a file-static `dfs_pool_stats` snapshot and persistent `sc->debug.stats.dfs_stats`. Debugfs files hold `ath_softc` as private data.

Dependencies/integration: Depends on debugfs, DFS detector pool stats, mac80211 radar notification, `debug.h` stats, and build-time `CONFIG_ATH9K_DFS_DEBUGFS`.

Risks: Simulated radar is a powerful test hook that can trigger channel availability behavior. Stats reset uses a magic value to avoid accidental reset but has no locking. File-static pool stats are overwritten on reads.

Test signals: Debugfs presence, stats output with and without detector, magic reset behavior, simulated radar triggering cfg80211/mac80211 radar handling, and pool stat formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.h

Purpose: Defines DFS debug statistics and conditional debugfs/stat increment hooks.

Important APIs/types: `struct ath_dfs_stats` records pulse totals, non-DFS pulse reports, detected pulses, datalen/RSSI/BW discards, primary/extension/dual-channel PHY errors, processed pulses, and radar detections. `DFS_STAT_INC(sc, c)` increments stats when `CONFIG_ATH9K_DFS_DEBUGFS` is enabled; otherwise it compiles to a no-op. `ath9k_dfs_init_debug()` is declared or stubbed similarly.

Control flow: `dfs.c` increments counters through `DFS_STAT_INC()` throughout the radar filtering pipeline. `debug.c` calls `ath9k_dfs_init_debug()` during debugfs setup.

State/persistence: Stats are embedded in `sc->debug.stats.dfs_stats`. No direct allocation or synchronization is defined here.

Dependencies/integration: Includes `hw.h`, forward-declares `ath_softc`, and references `ath_dfs_pool_stats` from the shared DFS detector.

Risks: Counter no-ops in disabled builds mean DFS logic cannot rely on side effects. Unsynchronized `u32` counters can race or wrap. External declaration of global pool stats must match detector implementation.

Test signals: Compile with/without DFS debugfs, per-counter increments from radar path, debugfs initialization stubbing, and stats reset/read behavior through `dfs_debug.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dfs_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.c

Purpose: Implements dynamic ACK timeout estimation for ath9k, using TX status timestamps and received ACK timestamps to tune ACK/CTS timeout and slot time for long-distance or reduced-rate channels.

Important APIs/functions: Exported APIs are `ath_dynack_sample_tx_ts()`, `ath_dynack_sample_ack_ts()`, `ath_dynack_node_init()`, `ath_dynack_node_deinit()`, and `ath_dynack_reset()`. `ath_dynack_init()` initializes the feature but is not exported in this file. Internal helpers compute max timeout by channel width, EWMA station timeout, SIFS by PHY/rate mode, BSSID-mask ACK filtering, hardware timeout programming, and aggregate max timeout across nodes.

Control flow: TX completion sampling ignores disabled dynack and NO_ACK frames. XRETRY on association/auth frames is treated as late ACK: hardware timeout is raised to the channel max, station timeout is invalidated, and recomputation is delayed. Otherwise TX timestamp, duration, destination/source, and adjusted legacy duration are pushed into a ring buffer. ACK RX sampling filters by BSSID mask and pushes timestamps into a second ring. `ath_dynack_compute_to()` pairs TX and ACK ring heads, computes ACK propagation time after TX duration, bounds it below channel max, updates the matching station's EWMA `ackto`, and periodically recomputes the hardware timeout as the maximum station timeout. Reset clears rings, sets all nodes to max timeout, and programs hardware.

State/persistence: State lives in `ah->dynack`: enabled flag, qlock, node list, station TX ring, ACK ring, current `ackto`, and delayed recompute jiffies `lto`. Each `ath_node` stores `ackto` and a list node. Hardware state is ACK timeout, CTS timeout, and slottime registers.

Dependencies/integration: Depends on mac80211 station lookup, ath TX/RX status timestamps, channel width helpers, rate flags, hardware timeout setters, BSSID mask state, and `NL80211_FEATURE_ACKTO_ESTIMATION`.

Risks: Ring pairing is heuristic and can mismatch ACKs under heavy traffic or multiple peers. List updates require `qlock`; station lifetime must pair node init/deinit. Late-ACK behavior can hold maximum timeout for `LATEACK_DELAY`. Slottime derives from timeout with `(to - 3) / 2`, so invalid small values would be unsafe, though computed bounds avoid that.

Test signals: Enable/disable dynack, station add/remove, long-distance ACK timeout convergence, late ACK on auth/assoc, HT40/normal/half/quarter max timeout selection, BSSID mask filtering, ring wrap behavior, and hardware ACK/CTS/slottime programming after reset and recompute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.c -->
