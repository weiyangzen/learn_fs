# subset-b-006223 research

Grouped research report for mac80211 channel management, debugfs surfaces, driver operation wrappers, drop reasons, and EHT handling.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/chan.c -->
# sources/distributed-fs/ceph-client/net/mac80211/chan.c

## Purpose

`chan.c` owns mac80211 channel-context lifecycle and assignment. It lets multiple virtual interfaces and MLO links share compatible channel definitions, reserve future channel contexts for channel switch announcements, replace one context with another, and keep driver-visible channel context state synchronized with link/VLAN `bss_conf` pointers. The file is a core integration point between cfg80211 channel validation, mac80211 link state, station bandwidth/rate-control state, radar requirements, and low-level driver callbacks.

## Important APIs, Types, And Functions

The central local helper type is `struct ieee80211_chanctx_user_iter`, which iterates users of a `struct ieee80211_chanctx` across running interfaces, MLO links, reserved links, and NAN scheduled channels. The `for_each_chanctx_user_assigned`, `for_each_chanctx_user_reserved`, and `for_each_chanctx_user_all` macros build on `ieee80211_chanctx_user_iter_next()` and enforce a consistent notion of assigned versus future reserved users.

Public or cross-file entry points include `ieee80211_chanctx_num_assigned()`, `ieee80211_chanctx_refcount()`, `ieee80211_chanreq_identical()`, `ieee80211_is_radar_required()`, `ieee80211_recalc_chanctx_min_def()`, `ieee80211_free_chanctx()`, `ieee80211_recalc_chanctx_chantype()`, `ieee80211_recalc_smps_chanctx()`, `ieee80211_link_copy_chanctx_to_vlans()`, `ieee80211_link_reserve_chanctx()`, `ieee80211_link_unreserve_chanctx()`, `_ieee80211_link_use_channel()`, `ieee80211_link_use_reserved_context()`, `ieee80211_link_change_chanreq()`, `ieee80211_link_release_channel()`, `ieee80211_link_vlan_copy_chanctx()`, and the exported iterator APIs `ieee80211_iter_chan_contexts_atomic()` and `ieee80211_iter_chan_contexts_mtx()`.

Key helpers include `ieee80211_chanreq_compatible()`, `_ieee80211_chanctx_compatible()`, `ieee80211_find_chanctx()`, `ieee80211_find_or_create_chanctx()`, `ieee80211_alloc_chanctx()`, `ieee80211_add_chanctx()`, `ieee80211_del_chanctx()`, `ieee80211_assign_link_chanctx()`, `ieee80211_replace_chanctx()`, and `ieee80211_vif_use_reserved_switch()`.

## Control Flow

Normal channel use starts in `_ieee80211_link_use_channel()`. For active links it checks DFS/radar requirements through cfg80211, validates interface combinations, releases any current channel when not reconfiguring, finds or creates a compatible context, copies the requested `chanreq` into the link and AP VLANs, assigns the link to the driver via `drv_assign_vif_chanctx()`, clears temporary `will_be_used` state if an existing context was reused, and recalculates SMPS and radar state. Inactive links only update their stored `chanreq`.

Context sharing is compatibility-driven. `ieee80211_chanreq_compatible()` combines operational chandefs and AP chandefs, while `_ieee80211_chanctx_compatible()` folds a candidate request across all current users except an optional changing link. `ieee80211_find_chanctx()` skips exclusive and replacement contexts, marks a selected context `will_be_used`, updates its driver-facing chandef through `ieee80211_change_chanctx()`, and returns it for assignment.

Reservation flow starts with `ieee80211_link_reserve_chanctx()`. It tries an existing reservation-compatible context, otherwise creates a new context on an available radio, or builds an in-place replacement pair with `ieee80211_replace_chanctx()`. A later `ieee80211_link_use_reserved_context()` marks the reservation ready and either finalizes direct assignment/reassignment or enters `ieee80211_vif_use_reserved_switch()` for coordinated replacement. The replacement path validates that all users of the old context have reservations ready, optionally calls `drv_switch_vif_chanctx()` for driver-visible swaps, adds/removes driver channel contexts for ctx-less or reassign cases, updates all link pointers and AP VLAN pointers, notifies BSS bandwidth changes, recalculates tx power/chantype/SMPS/radar/min bandwidth, completes CSA work, and finally removes old contexts.

Bandwidth state is recalculated from actual users. `ieee80211_get_chanctx_max_required_bw()` collects max required width from assigned/reserved users and monitor interfaces; `__ieee80211_recalc_chanctx_min_def()` downgrades `conf.min_def` from the configured `def` where possible, except narrow S1G widths and radar-enabled contexts. `ieee80211_chan_bw_change()` updates per-link station bandwidth and calls rate control updates around driver context changes.

## State And Persistence

Channel contexts live in `local->chanctx_list` and are freed with RCU after list removal. Link state persists in `link->conf->chanctx_conf`, `link->conf->chanreq`, reservation fields (`reserved_chanctx`, `reserved`, `reserved_ready`, `reserved_radar_required`), radar state, SMPS mode, and AP VLAN copied `chanctx_conf`/`chanreq` pointers. Context state includes `conf.def`, `conf.ap`, `conf.min_def`, `conf.radar_enabled`, radio index, rx-chain counts, `mode`, `driver_present`, `will_be_used`, `replace_state`, and `replace_ctx`. This is runtime kernel state only; there is no disk persistence.

Most mutation requires the wiphy mutex (`lockdep_assert_wiphy()` is pervasive). Published link and context pointers use RCU access helpers and `rcu_assign_pointer()`, with atomic iterators guarded by `rcu_read_lock()`.

## Dependencies And Integration Points

This file depends on cfg80211 channel helpers (`cfg80211_chandef_*`, DFS checks, radio validation), mac80211 station/rate-control internals, AP VLAN/link structures, NAN scheduling data, WBRF add/remove hooks, and driver wrappers from `driver-ops.h` (`drv_add_chanctx`, `drv_change_chanctx`, `drv_remove_chanctx`, `drv_assign_vif_chanctx`, `drv_unassign_vif_chanctx`, `drv_switch_vif_chanctx`). It also feeds cfg80211 stop-interface handling when reservation finalization fails.

## Risks

The highest-risk behavior is coordinated replacement state. `IEEE80211_CHANCTX_WILL_BE_REPLACED` and `IEEE80211_CHANCTX_REPLACES_OTHER` must stay paired, and all early failures must unreserve links and restore driver contexts correctly. Another risk is stale AP VLAN channel pointers; the code intentionally copies/clears them while the AP link context is still valid. Compatibility calculations rely on all users being visible to the iterator, including NAN and reserved users. Driver callback failures are mixed with `assign_on_failure` and reconfig paths, so callers must understand when mac80211 commits state despite driver errors. A test signal worth watching is that `ieee80211_if_write_link_handler()` in the nearby netdev debugfs code has a typed-data mismatch that could affect link-level debugfs controls that eventually call channel/link operations.

## Test Signals

Useful coverage includes MLO active-link switching, CSA reservation completion for station/AP/mesh/IBSS/OCB, context sharing with AP bandwidth changes and TDLS wider bandwidth, radar-required scan/channel use combinations, monitor interface on/off with `NO_VIRTUAL_MONITOR`, driver failures from add/assign/switch channel-context callbacks, AP VLAN channel release/copy races, NAN scheduled channels, and repeated reserve/unreserve cycles that trigger in-place replacement cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debug.h -->
# sources/distributed-fs/ceph-client/net/mac80211/debug.h

## Purpose

`debug.h` centralizes mac80211 debug logging macros. It gates subsystem-specific debug output behind Kconfig symbols and provides uniform prefixes for interface, link, link ID, and wiphy messages. It is used by mac80211 code that wants compile-time selectable debug traces without hand-coding `pr_debug()`, `wiphy_debug()`, or interface names repeatedly.

## Important APIs, Types, And Functions

The file defines boolean compile-time flags such as `MAC80211_OCB_DEBUG`, `MAC80211_IBSS_DEBUG`, `MAC80211_PS_DEBUG`, `MAC80211_HT_DEBUG`, mesh-related debug flags, `MAC80211_TDLS_DEBUG`, `MAC80211_STA_DEBUG`, and `MAC80211_MLME_DEBUG`. With `CONFIG_MAC80211_VERBOSE_DEBUG` enabled it declares `__sdata_info()`, `__sdata_dbg()`, `__sdata_err()`, and `__wiphy_dbg()` and routes the `_sdata_*` and `_wiphy_dbg` macros to those helpers. Otherwise the macros map to `wiphy_info`, `wiphy_dbg`, `wiphy_err`, and their `struct wiphy` variants.

The main consumer-facing macros are `sdata_info`, `sdata_err`, `sdata_dbg`, `link_info`, `link_err`, `link_err_once`, `link_id_info`, `link_dbg`, and specialized families such as `ht_dbg`, `ibss_dbg`, `ps_dbg`, `mpl_dbg`, `mpath_dbg`, `mhwmp_dbg`, `msync_dbg`, `mcsa_dbg`, `mps_dbg`, `tdls_dbg`, `sta_dbg`, `mlme_dbg`, and `mlme_link_id_dbg`.

## Control Flow

There is no runtime control flow beyond macro expansion. At compile time, each specialized macro embeds a boolean debug flag into `_sdata_dbg()` or `_link_id_dbg()`. In verbose-debug builds, helper functions can decide whether to print and can include richer interface context. In normal builds, output routes directly to wiphy logging helpers and the `print` argument controls debug printing. Link macros derive `sdata` and `link_id` from `struct ieee80211_link_data`; `link_err_once()` uses `net_ratelimit()` to suppress repeated errors.

## State And Persistence

The file stores no state. It reads stable fields such as `sdata->local->hw.wiphy`, interface names, and link IDs only when a macro is evaluated. Compile-time Kconfig settings determine which calls remain meaningful. There is no persistence.

## Dependencies And Integration Points

It depends on `ieee80211_i.h` for mac80211 internal types and on kernel wiphy logging helpers. Other files in this group use these macros for reservation failures and driver operation diagnostics, especially `chan.c` and broader MLME/channel-switch code.

## Risks

Because this is macro-heavy, side-effecting macro arguments must be avoided by callers. Debug category flags are compile-time choices, so missing Kconfig coverage can make expected traces silent. Link macros assume valid `link` or `sdata` pointers and are not defensive beyond their own formatting decisions. `link_err_once()` is global-ratelimit based and can hide repeated per-link failures during stress.

## Test Signals

Build coverage should include verbose and non-verbose debug configurations plus individual debug-category Kconfig combinations. Runtime signals are correct prefixes for interface/link messages, no format warnings from `__printf` declarations, and no unexpected evaluation warnings when macros are compiled out or debug flags are false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs.c -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs.c

## Purpose

`debugfs.c` builds the PHY-level mac80211 debugfs tree under the wiphy debugfs directory. It exposes read-only hardware and queue state, low-level driver statistics, and several writable diagnostic controls for AQM/AQL, airtime accounting, forced TX status, hw flag testing, and suspend/resume reset.

## Important APIs, Types, And Functions

The externally visible API is `debugfs_hw_add(struct ieee80211_local *local)`, declared in `debugfs.h`. `mac80211_format_buffer()` is a shared debugfs formatting helper used by key and station debugfs files. Local file operations are generated with `DEBUGFS_READONLY_FILE*` macros and `struct debugfs_short_fops`.

Important read/write handlers include `aqm_read()`/`aqm_write()`, `airtime_flags_read()`/`airtime_flags_write()`, `aql_pending_read()`, `aql_txq_limit_read()`/`aql_txq_limit_write()`, `aql_enable_read()`/`aql_enable_write()`, `force_tx_status_read()`/`force_tx_status_write()`, optional `reset_write()`, `hwflags_read()`/`hwflags_write()`, `misc_read()`, `queues_read()`, and generated low-level stats readers such as `stats_dot11ACKFailureCount_read()`.

## Control Flow

`debugfs_hw_add()` exits if the wiphy debugfs directory is absent, creates `keys`, creates top-level files such as `total_ps_buffered`, `wep_iv`, `rate_ctrl_alg`, `queues`, `misc`, `hwflags`, `force_tx_status`, `aql_enable`, `aql_pending`, `aqm`, `airtime_flags`, `aql_txq_limit`, `aql_threshold`, and creates a `statistics` subdirectory. If `CONFIG_MAC80211_DEBUG_COUNTERS` is enabled, it exposes direct u32 counters; driver stats are always exposed through files that call `drv_get_stats()` under `wiphy_lock()`.

Writable handlers parse small user buffers. `aqm_write()` adjusts global fq limits/quantum. `aql_txq_limit_write()` parses AC/low/high limits, acquires the wiphy lock, updates global AQL limits, and updates stations that still match the old defaults. `aql_enable_write()` toggles the static key used to disable/enable AQL. `hwflags_write()` allows changing the `IEEE80211_HW_STRICT` bit through `strict=...`. `reset_write()` takes RTNL and wiphy locks, calls mac80211 suspend/resume internals, and shuts down all interfaces on resume failure.

## State And Persistence

The debugfs files expose runtime-only fields on `ieee80211_local`: hardware config flags and power levels, WEP IV, fq queue state, AQL counters/limits, airtime flags, pending queues, stop reasons, forced TX status, and optional debug counters. Writes mutate live in-memory behavior and are not persisted across module/device restart.

Locking is mixed by state: fq stats use `fq.lock`, queue stop reasons use `queue_stop_reason_lock`, AQL station limit propagation uses the wiphy lock, and driver statistics use `wiphy_lock()`. Simple scalar writes such as `force_tx_status` and `airtime_flags` are direct debug/test knobs.

## Dependencies And Integration Points

This file depends on debugfs, `ieee80211_i.h`, `driver-ops.h`, `rate.h`, mac80211 fq/AQL structures, PM suspend/resume internals, and optional debug-counter Kconfig. Other debugfs files rely on `mac80211_format_buffer()`. Key debugfs directories created here are consumed by `debugfs_key.c`.

## Risks

Writable debugfs controls can materially change runtime behavior. AQL and AQM inputs have range checks only where explicitly implemented; very large limits or quantum values are accepted. `hwflags_write()` appears inverted by label (`strict=0` sets `STRICT`, `strict=1` clears it), so callers need to verify intended semantics. The reset path is invasive and can shut down all interfaces after resume failure. Statistics and queue reads must avoid buffer overrun as enum sizes evolve; `BUILD_BUG_ON` protects hardware flag name coverage.

## Test Signals

Tests should mount/read debugfs with `CONFIG_MAC80211_DEBUGFS`, verify each file appears under the wiphy directory, exercise AQL/AQM writes with valid and invalid buffers, check station AQL defaults are propagated only when matching old defaults, test reset under `CONFIG_PM`, validate `hwflags` formatting after flag enum changes, and confirm `drv_get_stats()` failures are propagated to readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs.h -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs.h

## Purpose

`debugfs.h` is the small public-internal header for PHY-level mac80211 debugfs support. It lets the rest of mac80211 add hardware debugfs entries and use the common formatting helper when debugfs support is compiled in, while compiling to no-ops when it is disabled.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `debugfs_hw_add(struct ieee80211_local *local)` and `mac80211_format_buffer(char __user *userbuf, size_t count, loff_t *ppos, char *fmt, ...)` with `__printf(4, 5)` checking. Without debugfs, it provides an empty inline `debugfs_hw_add()` and does not expose the formatter.

## Control Flow

There is no runtime control flow in the header. Compile-time selection determines whether callers link to real debugfs code or no-op stubs.

## State And Persistence

No state is stored. The real implementation mutates debugfs dentries and runtime debug knobs in `debugfs.c`; this header only declares the interface.

## Dependencies And Integration Points

It includes `ieee80211_i.h` for `struct ieee80211_local`. `debugfs.c`, `debugfs_key.c`, and `debugfs_sta.c` depend on the formatter declaration when debugfs is enabled. mac80211 initialization code can call `debugfs_hw_add()` without surrounding its call in Kconfig conditionals.

## Risks

The fallback only stubs `debugfs_hw_add()`. Code that uses `mac80211_format_buffer()` must itself be compiled only under debugfs-enabled paths. A mismatch here would be a build failure rather than a runtime bug.

## Test Signals

Build both `CONFIG_MAC80211_DEBUGFS=y` and disabled configurations. The disabled build should have no unresolved references to `mac80211_format_buffer()`, and the enabled build should preserve printf-format checking for all formatter users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.c -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.c

## Purpose

`debugfs_key.c` exposes per-key mac80211 debugfs diagnostics under the PHY `keys` directory. It reports key configuration, cipher suite, packet number state, replay/error counters, raw key bytes, interface association, and default-key symlinks.

## Important APIs, Types, And Functions

The exported functions are `ieee80211_debugfs_key_add()`, `ieee80211_debugfs_key_remove()`, `ieee80211_debugfs_key_update_default()`, `ieee80211_debugfs_key_remove_mgmt_default()`, and `ieee80211_debugfs_key_remove_beacon_default()`. Macro families `KEY_READ`, `KEY_CONF_READ`, `KEY_OPS`, and `KEY_CONF_OPS` generate many read-only files for `keylen`, `keyidx`, `hw_key_idx`, `flags`, and `ifindex`.

Cipher-specific handlers include `key_algorithm_read()`, `key_tx_spec_read()`/`key_tx_spec_write()`, `key_rx_spec_read()`, `key_replays_read()`, `key_icverrors_read()`, `key_mic_failures_read()`, and `key_key_read()`.

## Control Flow

`ieee80211_debugfs_key_add()` first checks that the PHY-level `keys` directory exists. It assigns a monotonically increasing static numeric directory name, records it in `key->debugfs.cnt`, creates the key directory, and, for station keys, creates a symlink back to the station debugfs directory. It then creates files for configuration fields, cipher algorithm, TX/RX PN state, replay/error counters, raw key material, and interface name.

`key_tx_spec_write()` rejects WEP, returns unsupported for TKIP, and accepts a 48-bit hex PN for CCMP/CMAC/BIP/GCMP families by atomically setting `key->conf.tx_pn`. Readers select different key union fields depending on cipher: TKIP IV32/IV16 arrays, CCMP/GCMP per-TID RX PN arrays including group slot, AES-CMAC/GMAC management PN, and replay/error counters. `ieee80211_debugfs_key_update_default()` recreates default unicast/multicast symlinks under an interface debugfs directory while holding the wiphy lock.

## State And Persistence

The debugfs tree mirrors runtime key objects. `key->debugfs.dir`, `stalink`, and `cnt` track dentries/symlink identity. Reads expose live key counters and packet numbers. Writes can mutate the key transmit PN for selected ciphers, which directly affects encryption/replay sequencing behavior. The static `keycount` only monotonically assigns debugfs names within the module lifetime and is not persisted.

## Dependencies And Integration Points

This file depends on `ieee80211_i.h`, `key.h`, `debugfs.h`, and `debugfs_key.h`. It consumes the PHY `local->debugfs.keys` directory created by `debugfs_hw_add()`. It links station keys to `debugfs_sta.c` station directories and interface default-key symlinks to netdev debugfs directories.

## Risks

The raw `key` file exposes key bytes through debugfs, so access controls and debugfs availability matter. TX PN writes are powerful test hooks and can create replay/security anomalies if used on a live link. `keycount` is static and not synchronized beyond normal mac80211/wiphy serialization expectations; unusual concurrent key creation should still be reviewed. Cipher switch statements must be updated for new cipher suites or they silently return empty data/default behavior.

## Test Signals

Coverage should create/remove keys for WEP, TKIP, CCMP, GCMP, AES-CMAC, and BIP-GMAC/CMAC, verify directories and station/default symlinks, read PN/replay/error files for each cipher, write boundary TX PN values including `2^48 - 1` and `2^48`, and confirm remove paths clear dentries without leaving stale default symlinks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.h -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.h

## Purpose

`debugfs_key.h` declares the internal mac80211 key debugfs lifecycle API and provides no-op stubs for non-debugfs builds. It isolates key management code from direct Kconfig conditionals.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `ieee80211_debugfs_key_add()`, `ieee80211_debugfs_key_remove()`, `ieee80211_debugfs_key_update_default()`, `ieee80211_debugfs_key_remove_mgmt_default()`, and `ieee80211_debugfs_key_remove_beacon_default()`. Without debugfs, the same functions are inline empty stubs.

## Control Flow

There is no runtime logic in the header. Compile-time selection either wires key lifecycle events to real debugfs updates or drops them.

## State And Persistence

No state is held in the header. The real implementation stores dentry pointers in key and interface debugfs fields and reflects live key state only.

## Dependencies And Integration Points

The prototypes require `struct ieee80211_key` and `struct ieee80211_sub_if_data` to be visible to includers. Key installation/removal/default-key code can call these helpers unconditionally. The implementation depends on the `debugfs.c` PHY keys directory.

## Risks

The no-op stubs mean non-debugfs builds lose all key visibility, which is expected. Any caller that relies on side effects beyond diagnostics would be wrong. Type visibility must be maintained by includers because this header does not include all defining headers itself.

## Test Signals

Build with debugfs enabled and disabled. Enabled builds should update per-key directories and default symlinks; disabled builds should compile out all debugfs side effects with no behavior changes to key installation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.c -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.c

## Purpose

`debugfs_netdev.c` creates and manages debugfs directories for mac80211 virtual interfaces and MLO links. It exposes common rate-control masks, interface state, per-link tx power and SMPS, station/AP/IBSS/mesh-specific diagnostics, TSF controls, active-link controls, and hooks for driver-owned per-vif/per-link debugfs files.

## Important APIs, Types, And Functions

The lifecycle APIs are `ieee80211_debugfs_remove_netdev()`, `ieee80211_debugfs_rename_netdev()`, `ieee80211_debugfs_recreate_netdev()`, `ieee80211_link_debugfs_add()`, `ieee80211_link_debugfs_remove()`, `ieee80211_link_debugfs_drv_add()`, and `ieee80211_link_debugfs_drv_remove()`. Internal wrapper helpers `ieee80211_if_read_sdata()`, `ieee80211_if_write_sdata()`, `ieee80211_if_read_link()`, and `ieee80211_if_write_link()` route debugfs operations through `wiphy_locked_debugfs_read/write()`.

Macro families generate file operations for sdata and link fields: `IEEE80211_IF_FILE*` and `IEEE80211_IF_LINK_FILE*`. Notable writable handlers include `ieee80211_if_parse_smps()`, `ieee80211_if_parse_tkip_mic_test()`, `ieee80211_if_parse_beacon_loss()`, `ieee80211_if_parse_uapsd_queues()`, `ieee80211_if_parse_uapsd_max_sp_len()`, `ieee80211_if_parse_tdls_wider_bw()`, `ieee80211_if_parse_tsf()`, and `ieee80211_if_parse_active_links()`.

## Control Flow

`ieee80211_debugfs_add_netdev()` creates `netdev:<name>`, stores it in `sdata->vif.debugfs_dir`, aliases the default link directory to it, creates a `stations` subdirectory, adds interface-type-specific files, and adds default-link files for non-MLD vifs. `ieee80211_debugfs_recreate_netdev()` removes and recreates this tree, then re-invokes driver debugfs hooks if the vif is in the driver.

`add_files()` always adds `flags` and `state`, adds common rate/AQM files for non-monitor types, then dispatches by iftype: station files include BSSID/AID/beacon timeout, TKIP MIC test injection, beacon-loss trigger, U-APSD controls, TDLS wider bandwidth, valid/active links, and dormant links; AP files include PS/multicast counters, TKIP MIC test, and multicast-to-unicast; AP VLAN exposes multicast station count; IBSS/mesh expose TSF; mesh adds stats and configuration directories.

Link debugfs for MLO creates `link-<id>`, adds link address and tx-power files, and station SMPS controls where applicable. Driver link debugfs is added through `drv_link_add_debugfs()` and removed by deleting/recreating the link directory without driver data.

## State And Persistence

The file stores dentry pointers in `sdata->vif.debugfs_dir`, `sdata->deflink.debugfs_dir`, `sdata->debugfs.subdir_stations`, and `link->debugfs_dir`. Reads expose live `sdata`, `vif`, `bss_conf`, queue, mesh, TSF, and link-mask state. Writes can change SMPS requests, inject TKIP MIC failure frames, synthesize beacon loss, adjust U-APSD settings, prohibit/allow TDLS wider bandwidth, reset/set/offset TSF through driver ops, and call `ieee80211_set_active_links()`.

Most sdata/link file access uses wiphy-locked debugfs helpers. AQM reads take `local->fq.lock`. TSF operations call driver wrappers and recalculate DTIM.

## Dependencies And Integration Points

This file depends on debugfs, netdevice and cfg80211 types, mac80211 rate/driver ops, mesh Kconfig, active-link management, station debugfs directories, and driver debugfs callbacks. It is called by interface/link lifecycle paths and by `driver-ops.c` when adding/removing driver-side debugfs entries.

## Risks

The most concrete implementation risk is in `ieee80211_if_write_link_handler()`: it declares `struct ieee80211_if_write_sdata_data *d = data` even though `ieee80211_if_write_link()` passes `struct ieee80211_if_write_link_data`. Because both structures contain a function pointer followed by a pointer, this may compile but calls a link write parser through an incompatible function pointer type and passes the link pointer as if it were `sdata`; link write files such as `smps` should be tested carefully. Writable debugfs entries can trigger live protocol behavior, including MIC failure frames, beacon loss, TSF mutation, and active-link changes. Directory recreation can drop driver debugfs entries if lifecycle ordering is wrong.

## Test Signals

Coverage should create/remove/rename/recreate netdev debugfs for station, AP, AP VLAN, IBSS, mesh, monitor, NAN, MLD and non-MLD cases; add/remove MLO link directories; verify driver debugfs hooks are re-added after recreation; exercise `active_links`, `smps`, `tsf`, `tkip_mic_test`, `beacon_loss`, U-APSD, and mesh config files with valid/invalid input; and run KASAN/lockdep while writing link-level files to catch the handler type mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.h -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.h

## Purpose

`debugfs_netdev.h` declares the internal lifecycle interface for virtual-interface and link debugfs directories. It lets interface/link management code update debugfs state unconditionally while compiling to stubs when mac80211 debugfs support is disabled.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `ieee80211_debugfs_remove_netdev()`, `ieee80211_debugfs_rename_netdev()`, `ieee80211_debugfs_recreate_netdev()`, `ieee80211_link_debugfs_add()`, `ieee80211_link_debugfs_remove()`, `ieee80211_link_debugfs_drv_add()`, and `ieee80211_link_debugfs_drv_remove()`. Without debugfs, all are inline no-ops.

## Control Flow

No runtime control flow exists in the header. The Kconfig branch determines whether netdev/link lifecycle events manipulate debugfs or do nothing.

## State And Persistence

No state is stored here. The implementation stores dentry pointers in sdata/link structures and exposes runtime state only.

## Dependencies And Integration Points

It includes `ieee80211_i.h` for `struct ieee80211_sub_if_data` and `struct ieee80211_link_data`. `driver-ops.c` uses the driver add/remove declarations to refresh driver-owned debugfs during interface and MLO link changes. Interface creation/removal code uses the netdev functions.

## Risks

No-op stubs hide all debugfs lifecycle effects in non-debugfs builds, which is expected. Callers must not depend on debugfs side effects for correctness. The header keeps declarations separated from implementation details, so signature drift between header and implementation would be caught at build time.

## Test Signals

Build with debugfs enabled and disabled. Runtime checks in enabled builds should confirm dentry pointers are set/cleared on netdev and link lifecycle events and driver debugfs entries are refreshed across link changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.c -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.c

## Purpose

`debugfs_sta.c` creates station and per-link-station debugfs diagnostics. It exposes station flags, AID, PS buffering, last sequence numbers, AQM/AQL/airtime state, aggregation session controls, driver-buffered TIDs, driver-owned station debugfs, and HT/VHT/HE/EHT capability decoders.

## Important APIs, Types, And Functions

The lifecycle APIs are `ieee80211_sta_debugfs_add()`, `ieee80211_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_add()`, `ieee80211_link_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_drv_add()`, and `ieee80211_link_sta_debugfs_drv_remove()`. Station file handlers include `sta_flags_read()`, `sta_num_ps_buf_frames_read()`, `sta_last_seq_ctrl_read()`, `sta_aqm_read()`, `sta_airtime_read()`/`sta_airtime_write()`, `sta_aql_read()`/`sta_aql_write()`, and `sta_agg_status_read()`/`sta_agg_status_write()`.

Per-link-station handlers include `link_sta_addr_read()`, `link_sta_ht_capa_read()`, `link_sta_vht_capa_read()`, `link_sta_he_capa_read()`, and `link_sta_eht_capa_read()`. Macros generate file operations and simple counters for station and link-station fields.

## Control Flow

`ieee80211_sta_debugfs_add()` creates a station directory named by MAC address under the interface `stations` directory, tolerating failure due to a documented remove/add race for the same address. It adds station-level files, optional AQL controls if the wiphy advertises the AQL extended feature, `driver_buffered_tids`, and driver station debugfs via `drv_sta_add_debugfs()`.

`ieee80211_link_sta_debugfs_add()` places link-specific files directly in the station directory for non-MLO stations, or under `link-<id>` for valid-links MLO stations. It adds address for MLO links, capability decoders, and RX duplicate/fragment counters. Driver link-station debugfs is added separately, and removal recreates the directory without driver data for MLO link-station entries.

Aggregation control uses `wiphy_locked_debugfs_read/write()`. Reads print RX/TX BA session state per TID. Writes parse `tx start [timeout=N] <tid>`, `tx stop <tid>`, or `rx stop <tid>` style commands and call BA session start/stop helpers.

## State And Persistence

Station directories are runtime debugfs dentries stored in `sta->debugfs_dir` and `link_sta->debugfs_dir`. Reads expose live station flags, queues, AQL/airtime counters, aggregation state, and capability structures populated during association. Writes can reset airtime accounting, change per-station AQL limits, and start/stop aggregation sessions. No data is persisted beyond object lifetime.

Locking is per data type: fq stats use `local->fq.lock`, airtime and AQL limits use `active_txq_lock[ac]` for reads/resets, aggregation state uses the wiphy lock, and debugfs directory lifecycle follows station/link lifecycle serialization.

## Dependencies And Integration Points

This file depends on debugfs, `ieee80211_i.h`, `sta_info.h`, `driver-ops.h`, and capability helper macros from IEEE 802.11 headers. It is integrated with netdev debugfs station directories, driver debugfs hooks, BA aggregation management, AQL scheduling, rate/AQM queue structures, and HE/EHT capability parsing in files such as `eht.c`.

## Risks

The capability formatters are large and mirror evolving standards bit layouts; new capability bits can be missed or decoded incorrectly. The station add path documents a race where a new station with the same address may appear before the old debugfs directory is removed. `ieee80211_link_sta_debugfs_remove()` sets `sta->debugfs_dir = NULL` when removing the non-MLO default link directory alias, which requires lifecycle ordering to avoid losing the station directory unexpectedly. Writable aggregation and AQL controls can perturb live traffic and should remain debug-only.

## Test Signals

Tests should cover station add/remove races with repeated same-MAC association, MLO and non-MLO station link directories, driver debugfs add/remove recreation, AQL feature-present/absent paths, airtime reset behavior, aggregation command parsing and error cases, and sample HT/VHT/HE/EHT capability dumps for known capability fixtures. Lockdep/KASAN runs are useful while removing stations during debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.h -->
# sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.h

## Purpose

`debugfs_sta.h` declares station and link-station debugfs lifecycle helpers, with no-op stubs for non-debugfs builds. It lets station lifecycle and driver-operation code add/remove debugfs entries without direct Kconfig branching.

## Important APIs, Types, And Functions

With `CONFIG_MAC80211_DEBUGFS`, it declares `ieee80211_sta_debugfs_add()`, `ieee80211_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_add()`, `ieee80211_link_sta_debugfs_remove()`, `ieee80211_link_sta_debugfs_drv_add()`, and `ieee80211_link_sta_debugfs_drv_remove()`. Without debugfs, all are inline empty functions.

## Control Flow

There is no runtime logic in the header. Compile-time Kconfig controls whether callers reach the implementation in `debugfs_sta.c`.

## State And Persistence

The header stores no state. The implementation stores debugfs dentries in station and link-station objects and exposes live runtime state only.

## Dependencies And Integration Points

It includes `sta_info.h` for `struct sta_info` and `struct link_sta_info`. `driver-ops.c` uses driver add/remove helpers during MLO station link changes. Station lifecycle code can call add/remove helpers unconditionally.

## Risks

The no-op stubs must remain behavior-free; callers must not require debugfs side effects for station correctness. Signature mismatches between header and implementation would be build-time failures.

## Test Signals

Build both debugfs and non-debugfs configurations. Enabled builds should create station/link debugfs entries and driver subentries; disabled builds should compile and run station lifecycle paths without debugfs references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/debugfs_sta.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/driver-ops.c -->
# sources/distributed-fs/ceph-client/net/mac80211/driver-ops.c

## Purpose

`driver-ops.c` implements non-inline mac80211 wrappers around selected low-level driver callbacks. These wrappers enforce mac80211 state checks, locking expectations, tracepoints, fallback behavior, debugfs hook management, MLO link handling, and driver-present bookkeeping for channel contexts.

## Important APIs, Types, And Functions

Implemented wrappers include `drv_start()`, `drv_stop()`, `drv_add_interface()`, `drv_change_interface()`, `drv_remove_interface()`, `drv_sta_state()`, `drv_sta_set_txpwr()`, `drv_link_sta_rc_update()`, `drv_conf_tx()`, `drv_get_tsf()`, `drv_set_tsf()`, `drv_offset_tsf()`, `drv_reset_tsf()`, `drv_assign_vif_chanctx()`, `drv_unassign_vif_chanctx()`, `drv_switch_vif_chanctx()`, `drv_ampdu_action()`, `drv_link_info_changed()`, `drv_set_key()`, `drv_change_vif_links()`, and `drv_change_sta_links()`.

## Control Flow

Most functions begin with `might_sleep()` and `lockdep_assert_wiphy()`, validate `IEEE80211_SDATA_IN_DRIVER` through `check_sdata_in_driver()`, emit a `trace_drv_*` event, call the optional or required driver operation, emit a return trace, and then update mac80211 bookkeeping. `drv_start()` sets `local->started` before invoking the driver start op, using a memory barrier so RX can proceed, and rolls back on error. `drv_stop()` calls the stop op, drains the tasklet by disable/enable, then clears `started`.

Interface wrappers block invalid AP VLAN/monitor cases, set/clear `IEEE80211_SDATA_IN_DRIVER`, and add/remove driver debugfs entries. Station-state handling supports both the modern `sta_state` callback and fallback `sta_add`/`sta_remove` transitions between AUTH and ASSOC, including rate-table upload after successful fallback add.

Channel-context wrappers skip emulated monitor assignment cases, ignore inactive links, validate `driver_present`, and call assign/unassign/switch operations. `drv_switch_vif_chanctx()` updates `driver_present` on new/old contexts after successful swap mode. MLO link-change wrappers remove driver debugfs for links being removed before calling the driver and add it back for links being added after success, except during reconfig/resume.

## State And Persistence

The wrappers mutate live runtime state: `local->started`, `sdata->flags`, `sta->uploaded` in fallback paths, channel `driver_present`, and driver debugfs subdirectories for vifs, links, and link stations. No persistent storage is used.

## Dependencies And Integration Points

This file depends on `net/mac80211.h`, mac80211 internal state, tracepoints, `driver-ops.h`, `debugfs_sta.h`, and `debugfs_netdev.h`. It is called broadly from channel management, interface lifecycle, station lifecycle, key management, TSF debugfs, aggregation, and MLO active-link code.

## Risks

Wrappers are correctness gates between mac80211 and drivers. Missing `check_sdata_in_driver()` checks can call drivers for removed interfaces; over-strict checks can suppress needed cleanup during reconfig failure. `drv_start()` temporarily sets `started` before driver success, so error paths and concurrent RX assumptions depend on the barrier and rollback. Debugfs recreation in `drv_remove_interface()` must not run for the virtual monitor interface. MLO link debugfs remove/add ordering must match driver link-change success/failure or stale driver files can remain. FIPS gating in `drv_set_key()` prevents driver key programming entirely.

## Test Signals

Test with drivers that implement and omit optional callbacks, fallback station add/remove paths, reconfig/resume link-change paths, inactive MLO links, monitor and AP VLAN edge cases, FIPS enabled key setting, channel-context switch modes, and tracepoint expectations. Fault injection in driver callbacks should verify state rollback and debugfs lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/driver-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/driver-ops.h -->
# sources/distributed-fs/ceph-client/net/mac80211/driver-ops.h

## Purpose

`driver-ops.h` is the main inline wrapper layer for mac80211-to-driver callbacks. It normalizes locking assertions, tracepoints, optional-callback fallback returns, AP VLAN remapping, interface-in-driver checks, FIPS restrictions, MLO active-link filtering, debugfs hook stubs, and channel-context driver-present bookkeeping.

## Important APIs, Types, And Functions

The header defines `check_sdata_in_driver()` and `get_bss_sdata()`, declares non-inline wrappers implemented in `driver-ops.c`, and implements many inline wrappers including `drv_tx()`, PM wrappers, `drv_config()`, `drv_vif_cfg_changed()`, multicast/filter configuration, scan/sched-scan wrappers, stats/key sequence helpers, threshold/coverage/antenna/ring parameter wrappers, station add/remove/statistics/rate update wrappers, debugfs driver hook wrappers, channel-context add/remove/change wrappers, AP start/stop, channel-switch callbacks, IBSS join/leave, TX queue wake scheduling, TDLS/NAN/PMSR/TWT/offload wrappers, link activation/TTLM checks, and `drv_set_eml_op_mode()`.

## Control Flow

The common pattern is: assert sleeping/locking where required, map AP VLAN sdata to the owning AP with `get_bss_sdata()`, check the interface is in the driver when applicable, emit a tracepoint, call the driver op only if present, return a default (`0`, `false`, or `-EOPNOTSUPP`) when absent, and emit a return trace. Some wrappers intentionally do not take wiphy assertions because they are used in TX-fast or callback contexts (`drv_tx()`, selected buffered-frame helpers).

Channel context inline wrappers call `add_chanctx`, `remove_chanctx`, and `change_chanctx`, setting or checking `ctx->driver_present`. Debugfs hook wrappers exist only under `CONFIG_MAC80211_DEBUGFS`; otherwise `drv_vif_add_debugfs()` is a no-op and related declarations are absent. `drv_wake_tx_queue()` marks TXQs dirty during reconfig instead of waking them immediately.

## State And Persistence

The header itself stores no persistent state, but inline wrappers mutate live runtime fields such as channel context `driver_present`, TXQ `IEEE80211_TXQ_DIRTY`, and driver-visible configuration. No disk persistence exists.

## Dependencies And Integration Points

It includes FIPS, `net/mac80211.h`, `ieee80211_i.h`, and trace definitions. It is included by almost every mac80211 subsystem that calls drivers, including this group’s `chan.c`, `debugfs.c`, `debugfs_netdev.c`, `debugfs_sta.c`, and `eht.c`.

## Risks

Because wrappers encode driver callback contracts, default return values are semantically important. A missing optional callback may mean success for some operations and unsupported for others. Several NAN wrappers call `check_sdata_in_driver(sdata)` without using the boolean result, so they warn but still call the driver; callers must know this behavior. `drv_set_tid_config()` and `drv_reset_tid_config()` assume corresponding ops exist and do not check optionality. Trace arguments must stay valid even when optional callbacks are absent. FIPS checks in key/rekey paths can make behavior differ by system policy.

## Test Signals

Build coverage should exercise debugfs and non-debugfs variants, PM and non-PM variants, IPv6 variant wrappers, and optional-driver callback combinations. Runtime tests should check lockdep assertions, tracepoint emission, AP VLAN remapping, reconfig TXQ dirty marking, absent callback return codes, channel-context `driver_present` transitions, FIPS key/rekey suppression, and MLO active-link filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/driver-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/drop.h -->
# sources/distributed-fs/ceph-client/net/mac80211/drop.h

## Purpose

`drop.h` defines mac80211-specific RX drop reasons and the bitwise `ieee80211_rx_result` type. It gives RX handlers precise drop/error return values that can be converted into kernel skb drop reason space while still allowing sparse to distinguish handler results from ordinary integers.

## Important APIs, Types, And Functions

The file defines `typedef unsigned int __bitwise ieee80211_rx_result`, the macro list `MAC80211_DROP_REASONS_UNUSABLE(R)`, internal enum `___mac80211_drop_reason`, public enum `mac80211_drop_reason`, and the predicate `RX_RES_IS_UNUSABLE(result)`.

`MAC80211_DROP_REASONS_UNUSABLE` lists many `RX_DROP_U_*` values for MIC failures, replay, bad MMIE, duplicate/spurious frames, decrypt/key/cipher failures, invalid AMSDU/802.3 frames, unprotected robust management/action frames, malformed/runt management/data/control/BAR frames, mesh-specific failures, port-control mismatches, unknown stations/actions, and no-link cases.

## Control Flow

There is no runtime control flow beyond macro expansion and the `RX_RES_IS_UNUSABLE()` predicate. The two-enum design first creates untyped internal constants anchored to `SKB_CONSUMED`, `SKB_NOT_DROPPED_YET`, and the mac80211 unusable drop subsystem base, then casts the public enum values to `ieee80211_rx_result`.

## State And Persistence

No mutable state exists. Values are compile-time constants that become return values and skb drop reason inputs elsewhere.

## Dependencies And Integration Points

It depends on `<net/dropreason.h>` for `SKB_DROP_REASON_SUBSYS_MAC80211_UNUSABLE`, `SKB_DROP_REASON_SUBSYS_SHIFT`, masks, and skb consumed/not-dropped constants. RX path files include this header to return `RX_CONTINUE`, `RX_QUEUED`, or specific unusable drop reasons and to test whether a result belongs to the unusable subsystem.

## Risks

The macro list is an ABI-like diagnostic surface. Reordering or inserting values changes numeric drop reason meanings unless coordinated with drop-reason expectations. The comment marker near the trailing backslash is a maintenance guard; new reasons must be inserted before it. Sparse bitwise typing helps catch misuse but only where sparse is run. `RX_RES_IS_UNUSABLE()` relies on subsystem mask layout matching the internal enum base.

## Test Signals

Build with sparse to catch `ieee80211_rx_result` misuse. Runtime RX tests should verify specific malformed/security/drop cases map to expected `RX_DROP_U_*` values and that `kfree_skb_reason()` or tracing reports mac80211 subsystem reasons. Compile tests should cover additions to the reason list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/drop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/eht.c -->
# sources/distributed-fs/ceph-client/net/mac80211/eht.c

## Purpose

`eht.c` handles selected IEEE 802.11be EHT behavior in mac80211. It parses EHT capability IEs into per-link station capability state and processes protected EHT EML Operating Mode Notification action frames for MLD peers, forwarding accepted changes to the driver and replying with a notification response.

## Important APIs, Types, And Functions

The exported functions are `ieee80211_eht_cap_ie_to_sta_eht_cap()` and `ieee80211_rx_eml_op_mode_notif()`. The local helper `ieee80211_send_eml_op_mode_notif()` builds the response action frame. The code uses `struct ieee80211_sta_eht_cap`, `struct ieee80211_eht_cap_elem`, `struct ieee80211_eml_params`, `struct link_sta_info`, `struct sta_info`, and driver wrapper `drv_set_eml_op_mode()`.

## Control Flow

Capability parsing starts by zeroing `link_sta->pub->eht_cap`, rejecting absent EHT IEs or unsupported local iftype capability, computing the variable MCS/NSS size from the peer HE/EHT capabilities, optionally computing PPE threshold length from the EHT PPE header, validating all lengths against `eht_cap_len`, copying fixed capability fields, copying only the advertised MCS/NSS bytes into a zeroed destination structure, copying PPE thresholds if present, and setting `has_eht`. It then recalculates `cur_max_bandwidth` and station bandwidth. On 2.4 GHz only, it maps EHT max MPDU length bits into aggregate max AMSDU length and calls `ieee80211_sta_recalc_aggregates()`.

`ieee80211_rx_eml_op_mode_notif()` first requires an MLD vif, rejects mutually invalid eMLSR/eMLMR control combinations, requires local iftype extended capabilities and a valid RX link, and looks up the transmitting station in the BSS. For eMLSR it verifies local support, accounts for link bitmap and optional parameter update length, validates padding/transition delay values, and updates the station EML capability delay bits. For eMLMR it verifies support, validates MCS map count and total optional length, checks every RX/TX MCS map entry is within range, and copies the map into `eml_params`. If either mode is active it reads the link bitmap and ensures it is a subset of active links. It then calls `drv_set_eml_op_mode()` and sends a response only on driver success.

## State And Persistence

The file mutates runtime station/link state: EHT capability structures, `link_sta->cur_max_bandwidth`, `link_sta->pub->bandwidth`, `link_sta->pub->agg.max_amsdu_len`, `sta->sta.eml_cap` delay fields, and driver EML operation mode state. No persistence exists. Received frame contents are validated against skb length before optional fields are consumed.

## Dependencies And Integration Points

It depends on mac80211 internal station/link structures, cfg80211 iftype extended capabilities, EHT/HE size helpers (`ieee80211_eht_mcs_nss_size`, `ieee80211_eht_ppe_size`), bandwidth helpers (`ieee80211_sta_cap_rx_bw`, `ieee80211_sta_cur_vht_bw`), aggregate recalculation, protected EHT action frame definitions, TX path `ieee80211_tx_skb()`, and driver callback `set_eml_op_mode` through `driver-ops.h`.

## Risks

Length accounting is security-critical because EHT capabilities and EML notifications contain variable optional fields. The code carefully validates lengths before reads, but future field additions could break offsets. EML notification handling updates `sta->sta.eml_cap` before the driver callback; if the driver rejects the mode change, delay fields may already be changed. The response copies optional bytes from the request after masking unsupported control bits, so opt_len calculation must match the request format exactly. Capability parsing depends on the associated HE capability IE for MCS/NSS sizing.

## Test Signals

Tests should parse EHT capability IEs with absent local support, truncated fixed fields, truncated MCS/NSS, PPE present with too-short headers, oversized PPE, 2.4 GHz MPDU length variants, and 6 GHz/5 GHz MPDU cases. EML notification tests should cover non-MLD rejection, invalid mode combinations, invalid link status, missing station, unsupported local eMLSR/eMLMR, malformed optional lengths, out-of-range delay/MCS values, inactive link bitmaps, driver callback failure, and successful response frame generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/eht.c -->
