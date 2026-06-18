# subset-b-006225 Research

Grouped code research for the Ceph client copy of Linux mac80211 interface, key, LED, MLO link, hardware-registration, and mesh support files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/iface.c -->
# sources/distributed-fs/ceph-client/net/mac80211/iface.c

## Purpose
`iface.c` owns mac80211 virtual interface lifecycle and netdevice integration. It creates and removes `struct ieee80211_sub_if_data` instances, opens and stops netdev-backed and wireless-dev-only interfaces, switches interface types, handles monitor and AP VLAN special cases, manages per-interface workers and queues, updates multicast/filter/offload state, and coordinates teardown of keys, stations, channel contexts, MBSSID relationships, MLO links, and debugfs state.

## Important APIs, Types, And Functions
Important externally used functions include `ieee80211_do_open()`, `ieee80211_sdata_stop()`, `ieee80211_if_add()`, `ieee80211_if_remove()`, `ieee80211_remove_interfaces()`, `ieee80211_if_change_type()`, `ieee80211_recalc_txpower()`, `ieee80211_recalc_idle()`, `ieee80211_recalc_offload()`, `ieee80211_add_virtual_monitor()`, `ieee80211_del_virtual_monitor()`, `ieee80211_stop_mbssid()`, `ieee80211_vif_inc_num_mcast()`, `ieee80211_vif_dec_num_mcast()`, `ieee80211_vif_block_queues_csa()`, and `ieee80211_vif_unblock_queues_csa()`. The file defines netdevice ops for normal data interfaces, radiotap monitor interfaces, and 802.3 encapsulation-offload interfaces.

## Control Flow
Open starts in `ieee80211_open()`, validates addresses and concurrency, then calls `ieee80211_do_open()`. The first open starts the driver via `drv_start()`, turns on radio LEDs, configures monitor/offload state, adds the vif to the driver when appropriate, initializes default WMM/ERP state, increments filter counters, initializes hardware config on first interface, and marks `SDATA_STATE_RUNNING`. Stop flows through `ieee80211_stop()` and `ieee80211_do_stop()`: dependent AP VLANs and MBSSID partners are stopped first, scans/ROC/work items are cancelled, type-specific state machines are stopped, stations and keys are flushed, pending frames and TXQs are purged, driver interfaces are removed, idle/power/filter/offload state is recalculated, and hardware is stopped when the open count reaches zero.

Interface addition allocates either a netdevice or wireless-dev-only object, assigns a permanent MAC address, initializes default link data, frag cache, tailroom work, queues, rate masks, type-specific unions, debugfs, TXQs, and cfg80211 registration. Type changes either tear down/reinitialize a down interface or, when running, stop queues, stop and teardown state, call `drv_change_interface()`, rebuild type state, reopen, and wake queues.

## State And Persistence
Persistent runtime state lives in `ieee80211_local` interface lists and counters, `sdata->state`, `sdata->vif`, `sdata->wdev`, per-type `sdata->u.*` unions, `sdata->key_list`, pending SKB queues, TXQs, monitor lists, AP VLAN lists, MBSSID `tx_bss_conf` links, and MLO link pointers initialized through `ieee80211_link_init()`. The interface list is protected by RTNL, the wiphy mutex, `iflist_mtx`, and RCU according to the file-level locking contract. Stop paths use `synchronize_rcu()` and `synchronize_net()` to let TX/RX/key users drain before freeing.

## Dependencies And Integration Points
The file integrates with cfg80211 netdevice and wireless-dev registration, driver ops (`add_interface`, `remove_interface`, `change_interface`, `update_vif_offload`, `net_fill_forward_path`, `net_setup_tc`), channel-context helpers, station management, scan/ROC, IBSS/managed/mesh/OCB/NAN state machines, key teardown, debugfs, LED triggers, WME/rate setup, TX/RX aggregation management, MBSSID and AP VLAN code, and MLO link handling from `link.c`.

## Risks And Edge Cases
Lifecycle ordering is delicate: stations must be flushed before `drv_remove_interface()` so later STA notifications do not reference a removed vif; keys require forced `synchronize_net()` on stop because RX/TX may still hold RCU references; AP VLANs borrow state from the parent AP and must avoid driver callbacks; monitor mode can use either real or virtual monitor interfaces; offload netdev ops can change at runtime; powered MAC address changes are allowed only when no carrier, STA, ROC, scan, or connection operation is active. MLO teardown warns if valid links remain at interface stop, and runtime type changes reject MLD vifs.

## Test Signals
Useful signals include cfg80211/mac80211 interface create/open/stop/delete tests across station, AP, AP VLAN, monitor, mesh, OCB, NAN, and P2P modes; syzkaller coverage of open/stop/type-change races; lockdep/RCU debug during netdev unregister; tests for monitor filter counters and virtual monitor creation; AP VLAN and MBSSID dependent shutdown tests; MAC-address change while powered; encapsulation-offload toggling with monitor presence and frag threshold; and hardware restart/unregister tests that verify queues, keys, stations, and work items are drained.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/iface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/key.c -->
# sources/distributed-fs/ceph-client/net/mac80211/key.c

## Purpose
`key.c` implements mac80211 key allocation, installation, replacement, hardware offload negotiation, default-key selection, teardown, key iteration, replay/MIC statistics, WoWLAN GTK rekey helpers, and MLO link activation/deactivation handling for keys. It is the core bridge between cfg80211 key operations, mac80211 software crypto, per-station/per-link key state, and driver `set_key()` offload.

## Important APIs, Types, And Functions
Important APIs include `ieee80211_key_alloc()`, `ieee80211_key_link()`, `ieee80211_key_free()`, `ieee80211_key_free_unused()`, `ieee80211_set_tx_key()`, `ieee80211_set_default_key()`, `ieee80211_set_default_mgmt_key()`, `ieee80211_set_default_beacon_key()`, `ieee80211_remove_link_keys()`, `ieee80211_free_key_list()`, `ieee80211_free_keys()`, `ieee80211_free_sta_keys()`, `ieee80211_reenable_keys()`, `ieee80211_iter_keys()`, `ieee80211_iter_keys_rcu()`, `ieee80211_delayed_tailroom_dec()`, `ieee80211_gtk_rekey_notify()`, `ieee80211_get_key_rx_seq()`, `ieee80211_set_key_rx_seq()`, `ieee80211_gtk_rekey_add()`, `ieee80211_key_mic_failure()`, `ieee80211_key_replay()`, and `ieee80211_key_switch_links()`. Internal helpers handle tailroom counters, hardware enable/disable, pairwise rekey barriers, key identity checks, and replacement in RCU-protected pointers.

## Control Flow
Allocation validates the key index, allocates `struct ieee80211_key` plus key material, initializes cipher-specific IV/ICV sizes, replay counters or PN/RSC state from optional sequence input, and prepares crypto transforms for CCMP/GCMP/GMAC/CMAC. Linking finds the old key in station PTK/GTK, link GTK, or interface default slots; rejects cipher switches; accepts identical reinstallations with `-EALREADY`; assigns `local`, `sdata`, `sta`, unique `color`, and SPP A-MSDU flags; increments tailroom need; and calls `ieee80211_key_replace()`. Replacement disables old hardware offload, optionally enables new hardware offload, updates RCU key pointers, default-key pointers, station fast RX/TX state, and the per-interface key list. Free paths replace the key with NULL, synchronize with packet paths, remove debugfs entries, update tailroom counters, and free crypto transforms with `kfree_sensitive()`.

## State And Persistence
Key state persists in `struct ieee80211_key`: owner pointers, key list node, internal flags, cipher-specific PN/TKIP/CMAC/GMAC/GCMP state, replay/MIC counters, debugfs entries, color, and `ieee80211_key_conf`. Interface state persists in `sdata->key_list`, `sdata->keys[]`, default unicast keys, per-link `gtk[]`, default multicast/mgmt/beacon keys, station `ptk[]`, link-station `gtk[]`, and crypto tailroom counters. Hardware offload state is represented by `KEY_FLAG_UPLOADED_TO_HARDWARE`; tainted keys are kept from use during unsafe rekey/resume transitions.

## Dependencies And Integration Points
The file depends on AES CCM/GCM/GMAC/CMAC helpers, TKIP/WEP/WPA software paths, `driver-ops.h` for `drv_set_key()` and default unicast key updates, station aggregation and fast-RX/TX helpers, debugfs key reporting, AP VLAN inheritance, WoWLAN state, cfg80211 GTK rekey notifications, RCU and wiphy locking, and MLO link state from `link.c`. Drivers can inspect uploaded keys through `ieee80211_iter_keys()`/`ieee80211_iter_keys_rcu()`.

## Risks And Edge Cases
Key handling is concurrency-sensitive: RCU readers can see keys while replacement is in progress, so teardown must synchronize before freeing. Tailroom counters intentionally over-allocate during roaming to avoid expensive zero-to-one transitions and WARNs in software crypto, but mismatched increments/decrements surface as stop-time WARNs. Pairwise rekey without Extended Key ID taints the old key, blocks BA, tears down aggregation, and may flush queues if the driver cannot safely replace PTK0. AP VLAN GTKs are not uploaded because drivers do not know VLAN interfaces. Per-link keys are only uploaded for active links, and `ieee80211_key_switch_links()` must disable/enable hardware state when active links change.

## Test Signals
Tests should cover all supported ciphers, initial sequence import/export, duplicate reinstall rejection, cipher-switch rejection, default unicast/multicast/mgmt/beacon key changes, AP VLAN behavior, station PTK Extended Key ID rekey, hardware `set_key()` failures (`-ENOSPC`, `-EOPNOTSUPP`, fatal errors), SW crypto control rejection, WoWLAN GTK rekey add/notify, replay/MIC counter updates, delayed tailroom decrement during roaming, key iteration under RCU, link add/remove key switching, and lockdep/RCU validation under concurrent TX/RX and station removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/key.h -->
# sources/distributed-fs/ceph-client/net/mac80211/key.h

## Purpose
`key.h` defines mac80211 internal key data structures, constants, state enums, and prototypes used by key installation, software crypto, hardware offload, station management, link management, and debugfs. It is the internal contract for `key.c` and all users that need to store, dereference, switch, free, or report keys.

## Important APIs, Types, And Functions
The header defines `NUM_DEFAULT_KEYS`, `NUM_DEFAULT_MGMT_KEYS`, `NUM_DEFAULT_BEACON_KEYS`, and `INVALID_PTK_KEYIDX`. `enum ieee80211_internal_key_flags` carries `KEY_FLAG_UPLOADED_TO_HARDWARE` and `KEY_FLAG_TAINTED`. `enum ieee80211_internal_tkip_state`, `struct tkip_ctx`, and `struct tkip_ctx_rx` describe TKIP phase/key-cache state. `struct ieee80211_key` embeds owner pointers, list membership, flags, cipher-specific state unions for TKIP, CCMP, AES-CMAC, AES-GMAC, GCMP, and generic PN tracking, optional debugfs pointers, a key color, and trailing `struct ieee80211_key_conf` with variable-length key material.

## Control Flow
The header itself has no executable control flow, but its layout drives all key paths. Callers allocate a key with `ieee80211_key_alloc()`, attach it with `ieee80211_key_link()`, mark PTK TX use with `ieee80211_set_tx_key()`, update defaults through the default-key helpers, remove per-link or per-interface keys through the free helpers, and re-enable or switch hardware offload through `ieee80211_reenable_keys()` and `ieee80211_key_switch_links()`. The delayed tailroom work callback is declared here for interface initialization in `iface.c`.

## State And Persistence
The central persistent object is `struct ieee80211_key`, which lives until the key is unlinked and RCU/network readers have drained. Cipher unions preserve replay counters, packet numbers, TKIP phase state, and precomputed crypto transforms. The key color is used to distinguish fragments or cached state across replacements. Because `ieee80211_key_conf` is last and contains key material, allocation size and free paths must treat it as sensitive variable-length storage.

## Dependencies And Integration Points
The header includes Linux list/crypto/RCU types, ARC4 and AES-CBC-MAC crypto headers, and public `<net/mac80211.h>`. It forward-declares `ieee80211_local`, `ieee80211_sub_if_data`, `ieee80211_link_data`, and `sta_info`, keeping the full definitions in `ieee80211_i.h` and station headers. It is included by key management, MLO link teardown, interface teardown, station cleanup, and crypto/debugfs code.

## Risks And Edge Cases
`struct ieee80211_key` mixes RCU-visible pointers, wiphy-mutex-protected flags, spinlock-protected TKIP TX state, and sensitive key material. Any layout change can affect variable-length allocation, debugfs expectations, or software crypto. The key index constants define the valid split among data, management, and beacon keys; off-by-one errors here can corrupt default-key selection. `INVALID_PTK_KEYIDX` intentionally points to a NULL PTK slot and must remain outside the valid active PTK key IDs used for Extended Key ID.

## Test Signals
Header-level validation is mostly compile-time: all users must agree on struct layout, constants, and prototypes. Runtime signals come from key allocation/free tests for every cipher, Extended Key ID PTK tests, per-link GTK tests, debugfs key visibility, RCU/key iteration tests, and memory-sanitizer checks that sensitive key storage is released through the intended free path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/led.c -->
# sources/distributed-fs/ceph-client/net/mac80211/led.c

## Purpose
`led.c` implements optional `CONFIG_MAC80211_LEDS` trigger support for mac80211 devices. It provides RX, TX, association, radio, and throughput LED triggers; allocates trigger names; registers/unregisters LED triggers; exports trigger-name lookup helpers for drivers; and runs a timer-driven throughput blink policy based on driver-provided throughput thresholds.

## Important APIs, Types, And Functions
Public functions include `ieee80211_led_assoc()`, `ieee80211_led_radio()`, `ieee80211_alloc_led_names()`, `ieee80211_free_led_names()`, `ieee80211_led_init()`, `ieee80211_led_exit()`, and `ieee80211_mod_tpt_led_trig()`. Exported driver-facing helpers include `__ieee80211_get_radio_led_name()`, `__ieee80211_get_assoc_led_name()`, `__ieee80211_get_tx_led_name()`, `__ieee80211_get_rx_led_name()`, and `__ieee80211_create_tpt_led_trigger()`. Static activation/deactivation callbacks maintain atomic active counters, and `tpt_trig_timer()` computes blink timing from traffic deltas.

## Control Flow
Name allocation builds trigger names from `wiphy_name()` plus `rx`, `tx`, `assoc`, and `radio` suffixes. `ieee80211_led_init()` initializes active counters, assigns activation callbacks, and registers each named trigger, freeing failed names. If a throughput trigger was created by a driver, it registers that trigger too. Association/radio updates emit `LED_FULL` or `LED_OFF` only when the corresponding trigger has active users. TX/RX one-shot blinking is inlined in `led.h`. Throughput accounting accumulates bytes through inline helpers, samples once per second, converts deltas to Kbit/s, chooses a blink table entry, and calls `led_trigger_blink()`. `ieee80211_mod_tpt_led_trig()` starts or stops the timer based on radio/work/connected bits and the driver-requested mask.

## State And Persistence
LED state is stored in `struct ieee80211_local`: trigger objects, allocated names, atomic active counters, and optional `struct tpt_led_trigger`. Throughput trigger state persists in the allocated trigger object: name, blink table pointer/length, desired and active type masks, previous traffic count, running flag, timer, and back-pointer to `local`. No state persists beyond hardware unregister; `ieee80211_led_exit()` unregisters triggers and frees the throughput trigger, while `ieee80211_free_led_names()` frees name strings.

## Dependencies And Integration Points
The file depends on the kernel LED trigger subsystem, timers/jiffies, `wiphy_name()`, and mac80211 lifecycle hooks in `main.c` and `iface.c`. Interface idle/radio state calls `ieee80211_mod_tpt_led_trig()`, RX/TX paths call inline byte counters or blink helpers from `led.h`, and drivers can expose trigger names to platform LED configuration through the exported lookup functions.

## Risks And Edge Cases
LED support is optional; callers must tolerate NULL names when allocation or registration fails. Throughput trigger creation warns if called more than once. The blink table is driver-owned const data, so it must outlive the trigger. Byte counters are plain integer fields updated from TX/RX paths while sampled by a timer, so they are approximate rather than strongly synchronized. Timer shutdown uses `timer_delete_sync()` to avoid use-after-free, and throughput blinking is suppressed when the radio bit is inactive even if other wanted states are set.

## Test Signals
Useful checks include builds with and without `CONFIG_MAC80211_LEDS`, trigger registration failure injection, driver calls to exported name helpers, RX/TX blink activity only when active counters are nonzero, association/radio LED transitions, throughput blink table threshold selection, timer start/stop on connected/work/radio transitions, and unregister/free under device removal with timers enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/led.h -->
# sources/distributed-fs/ceph-client/net/mac80211/led.h

## Purpose
`led.h` is the internal abstraction layer for mac80211 LED support. It exposes lightweight TX/RX and throughput accounting helpers to hot paths while compiling them to no-ops when LED support is disabled, and it declares the lifecycle and state-change functions implemented in `led.c`.

## Important APIs, Types, And Functions
The always-visible inline helpers are `ieee80211_led_rx()`, `ieee80211_led_tx()`, `ieee80211_tpt_led_trig_tx()`, and `ieee80211_tpt_led_trig_rx()`. Under `CONFIG_MAC80211_LEDS`, the header declares `ieee80211_led_assoc()`, `ieee80211_led_radio()`, `ieee80211_alloc_led_names()`, `ieee80211_free_led_names()`, `ieee80211_led_init()`, `ieee80211_led_exit()`, and `ieee80211_mod_tpt_led_trig()`. Without LED support, those functions become empty inlines.

## Control Flow
TX/RX blink helpers check the corresponding atomic active counter before calling `led_trigger_blink_oneshot()` with `MAC80211_BLINK_DELAY`. Throughput helpers check `tpt_led_active` and add byte counts to the throughput trigger counters. The rest of the lifecycle control flow is delegated to `led.c`; this header ensures callers do not need conditional compilation around each LED update site.

## State And Persistence
The header does not own storage, but it directly accesses `ieee80211_local` LED trigger fields and atomic active counters. Throughput byte counters accumulate in `local->tpt_led_trigger` until sampled by the timer in `led.c`. When LED support is disabled, no LED state is read or updated.

## Dependencies And Integration Points
The header includes list, spinlock, LED subsystem headers, and `ieee80211_i.h` for `struct ieee80211_local`. It is used by RX/TX paths, interface/radio state logic, and hardware allocation/registration cleanup. It hides `CONFIG_MAC80211_LEDS` from most callers and keeps hot-path overhead to atomic reads plus simple counter updates when enabled.

## Risks And Edge Cases
Because inline helpers are used from hot paths, they must remain cheap and must not sleep. Throughput helpers assume `local->tpt_led_trigger` exists when `tpt_led_active` is nonzero, which is established by registration ordering in `led.c`. Any future change to activation ordering must preserve that invariant. Disabled LED builds should be tested because many functions become no-ops and unused fields may otherwise hide build issues.

## Test Signals
Compile coverage with `CONFIG_MAC80211_LEDS=y` and `n` is the primary signal. Runtime tests should confirm TX/RX paths do not crash before trigger activation, throughput byte counters increment only while active, and callers can invoke lifecycle/state helpers unconditionally in both configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/link.c -->
# sources/distributed-fs/ceph-client/net/mac80211/link.c

## Purpose
`link.c` implements multi-link operation (MLO) link object setup, teardown, valid-link changes, AP VLAN link mirroring, and active-link switching for station vifs. It manages the relationship between `struct ieee80211_sub_if_data`, per-link `struct ieee80211_link_data`, per-link `struct ieee80211_bss_conf`, driver `change_vif_links`/`change_sta_links` callbacks, channel contexts, keys, stations, and debugfs.

## Important APIs, Types, And Functions
Public functions include `ieee80211_apvlan_link_setup()`, `ieee80211_apvlan_link_clear()`, `ieee80211_link_setup()`, `ieee80211_link_init()`, `ieee80211_link_stop()`, `ieee80211_vif_set_links()`, `ieee80211_set_active_links()`, and `ieee80211_set_active_links_async()`. Static helpers include `ieee80211_update_apvlan_links()`, `ieee80211_tear_down_links()`, `ieee80211_free_links()`, `ieee80211_check_dup_link_addrs()`, `ieee80211_set_vif_links_bitmaps()`, `ieee80211_vif_update_links()`, and `_ieee80211_set_active_links()`.

## Control Flow
`ieee80211_vif_set_links()` calls `ieee80211_vif_update_links()`, which allocates new link containers, snapshots old link/conf pointers, removes pointers for deleted links, initializes added links, checks duplicate link addresses, tears down removed links and their keys, updates valid/dormant/active bitmaps, calls `drv_change_vif_links()` for non-AP-VLAN vifs, refreshes AP VLAN child links for APs, and handles rollback on errors. Link initialization fills `link_conf`, assigns addresses/BSSID for AP/AP_VLAN links, initializes work items for CSA/color/DFS, sets power defaults, installs RCU pointers, and adds debugfs for non-default links. Active-link switching is station-only: it validates usable links, optionally switches through an overlapping active link, changes driver vif links, releases channels for removed links, assigns channels for added links, recalculates station aggregates, changes station links, switches per-link key hardware offload, notifies link info for added links, and finally updates `vif.active_links`.

## State And Persistence
Persistent state includes `sdata->link[]`, `sdata->vif.link_conf[]`, `sdata->deflink`, allocated `link_container` objects, `vif.valid_links`, `vif.dormant_links`, `vif.active_links`, `sdata->desired_active_links`, AP VLAN `wdev.valid_links` and per-link addresses, per-link work items, channel contexts, and per-link keys. Removed links are detached with RCU pointer clearing, stopped, synchronized, and then freed after key lists are destroyed.

## Dependencies And Integration Points
The file depends on MLO definitions in `<net/mac80211.h>` and `ieee80211_i.h`, driver ops for vif/station link changes and link activation capability, key removal/switching from `key.c`, managed-mode link setup/stop and QoS helpers, TDLS teardown, channel-context assignment/release, CSA/color/DFS work callbacks, debugfs netdev link entries, AP VLAN state from `iface.c`, and station aggregation recalculation.

## Risks And Edge Cases
Rollback is only partial after some state changes: once keys are removed from deleted links, the code explicitly cannot undo that. Active-link switching contains warnings for driver failures that are hard to recover from after internal state is advanced. Channel assignment for newly active links is forced not to fail from mac80211's perspective, relying on driver recovery if hardware fails. AP links are always treated as active, station active links are limited initially, and duplicate per-link MAC addresses are rejected. Async active-link changes are ignored for stopped or non-station vifs and are skipped during reconfiguration.

## Test Signals
Tests should cover adding/removing valid links, dormant-link validation, AP VLAN link propagation with and without 4-address stations, duplicate link address rejection, driver `change_vif_links()` failure rollback, link teardown key movement/freeing, station active-link switch with overlapping and non-overlapping masks, TDLS/channel release on deactivation, key hardware offload switch on link activation, async active-link work cancellation on stop, and lockdep/RCU checks during concurrent station/link updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/main.c -->
# sources/distributed-fs/ceph-client/net/mac80211/main.c

## Purpose
`main.c` is the mac80211 core allocation, registration, hardware configuration, notifier, restart, and module lifecycle file. It allocates `ieee80211_hw`/`ieee80211_local`, validates driver ops and advertised capabilities, initializes default cfg80211/wiphy/mac80211 state, registers hardware with cfg80211, creates default interfaces, handles global filter and channel configuration, dispatches BSS/link/vif change notifications, processes queued RX/TX-status frames, and unregisters/frees all core resources.

## Important APIs, Types, And Functions
Driver-facing exported APIs include `ieee80211_alloc_hw_nm()`, `ieee80211_register_hw()`, `ieee80211_unregister_hw()`, `ieee80211_free_hw()`, `ieee80211_restart_hw()`, and emulated channel-context callbacks `ieee80211_emulate_add_chanctx()`, `ieee80211_emulate_remove_chanctx()`, `ieee80211_emulate_change_chanctx()`, and `ieee80211_emulate_switch_vif_chanctx()`. Internal important functions include `ieee80211_configure_filter()`, `ieee80211_hw_config()`, `ieee80211_hw_conf_chan()`, `ieee80211_hw_conf_init()`, `ieee80211_bss_info_change_notify()`, `ieee80211_vif_cfg_change_notify()`, `ieee80211_link_info_change_notify()`, `ieee80211_reset_erp_info()`, `ieee80211_handle_queued_frames()`, restart work, IP address notifiers, cipher-suite initialization, and module init/exit.

## Control Flow
Allocation validates mandatory driver ops and channel-context mode, creates a wiphy, initializes wiphy flags/features/default management frame stypes, allocates and initializes `ieee80211_local`, station state, locks, lists, TXQs, AQL, scan/ROC/restart/filter/dynamic-PS work, tasklets, SKB queues, LED names, and defaults. Registration validates queue/channel/NAN/TDLS/MLO/capability constraints, derives default channel definition and supported capability signals, sets interface modes and cipher suites, computes scan IE lengths, creates the ordered workqueue, initializes WEP, LEDs, TXQ flows, rate control, optional sband copies, registers the wiphy, adds debugfs/rate-control debugfs, optionally creates a default station interface, and registers IPv4/IPv6 address notifiers. Unregistration kills tasklets, unregisters notifiers, removes interfaces, tears down TXQ flows and work, clears pending frames, deinitializes rate control, unregisters wiphy, destroys workqueue, exits LEDs, and frees scan requests. Freeing destroys locks/IDRs/station state, LED names, copied bands, and the wiphy.

## State And Persistence
`main.c` initializes and persists most `ieee80211_local` core state: wiphy pointer, ops, hardware config, emulated channel-context flag, interface lists, monitor list, multicast list, filter counters/flags, channel contexts, scan/ROC state, restart work, PS work/timer, TXQ/AQL state, pending queues, tasklets, ack-status IDR, software scan request, workqueue, LED state, rate control, copied supported-band masks, and notifier blocks. Hardware config is held in `local->hw.conf`, while cfg80211-visible capabilities live in `hw->wiphy`.

## Dependencies And Integration Points
The file is the integration hub for cfg80211/wiphy registration, driver ops, interface handling from `iface.c`, station state, rate control, WEP/software crypto, mesh init/stop, LED support, debugfs, scan/ROC/DFS/channel-context helpers, TX/RX paths, inet/inet6 address notifiers for ARP/IPv6 offload updates, drop reason registration, and module init/exit. BSS/link/vif change notifiers abstract old `bss_info_changed` drivers and newer split `vif_cfg_changed`/`link_info_changed` drivers.

## Risks And Edge Cases
Registration contains many capability invariants: MLO drivers must provide modern link callbacks and cannot use chanctx emulation; HT/VHT/HE/EHT/UHR dependencies and queue counts must line up; FIPS forbids RC4 and rejects SW_CRYPTO_CONTROL drivers without explicit cipher suites; scan IE length is subtracted from driver limits and can underflow conceptually if drivers advertise too little; channel-context emulation forbids multi-channel combinations. Restart freezes queues and RX, cancels scans/ROC/work, synchronizes packet processing, and shuts down all interfaces if reconfiguration fails. Error labels in registration must unwind only resources already initialized.

## Test Signals
High-value tests include driver registration failure injection for each validation gate, FIPS cipher-suite behavior, MLO capability validation, chanctx emulation config changes, default interface creation, wiphy register/unregister loops under lockdep/KASAN, hardware restart during scan/CSA/ROC, IPv4/IPv6 notifier updates while associated, BSS/link/vif notification routing for legacy and split drivers, tasklet queued RX/TX-status handling, LED/rate-control/debugfs cleanup, and module init/exit drop-reason registration coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh.c -->
# sources/distributed-fs/ceph-client/net/mac80211/mesh.c

## Purpose
`mesh.c` implements core 802.11s mesh interface behavior for mac80211: mesh identity matching, peer-link acceptance state, recent multicast cache, mesh information element builders, beacon/probe response construction, mesh start/stop lifecycle, mesh housekeeping/root timers, fast mesh TX, mesh address/header construction, management-frame handling, channel switch announcement processing/forwarding, and mesh per-interface initialization/teardown.

## Important APIs, Types, And Functions
Important functions include `mesh_action_is_path_sel()`, `ieee80211s_init()`, `ieee80211s_stop()`, `mesh_matches_local()`, `mesh_peer_accepts_plinks()`, `mesh_accept_plinks_update()`, `mesh_sta_cleanup()`, `mesh_rmc_init()`, `mesh_rmc_free()`, `mesh_rmc_check()`, mesh IE builders such as `mesh_add_meshconf_ie()`, `mesh_add_meshid_ie()`, `mesh_add_rsn_ie()`, HT/VHT/HE/EHT capability/operation builders, `ieee80211_mesh_root_setup()`, `ieee80211_mesh_xmit_fast()`, `ieee80211_fill_mesh_addresses()`, `ieee80211_new_mesh_header()`, `ieee80211_mbss_info_change_notify()`, `ieee80211_start_mesh()`, `ieee80211_stop_mesh()`, `ieee80211_mesh_finish_csa()`, `ieee80211_mesh_csa_beacon()`, `ieee80211_mesh_rx_queued_mgmt()`, `ieee80211_mesh_work()`, `ieee80211_mesh_init_sdata()`, and `ieee80211_mesh_teardown_sdata()`.

## Control Flow
Mesh startup increments filter/allmulti requirements, sets mesh protocol IDs and sync ops, schedules housekeeping/root work, enables beaconing, updates mesh power-save state, builds the beacon, notifies the driver of beacon/HT/rate/interval changes, and brings carrier up. Beacon building allocates a `beacon_data` block and temporary SKB, constructs management header/head IEs including CSA when active, then constructs tail IEs for rates, RSN, HT/VHT/HE/EHT, mesh ID/config, awake window, and vendor data. Mesh work processes queued path discovery, housekeeping, proactive root frames, TSF drift adjustment, and deferred BSS changes. RX management dispatch handles beacons/probe responses for neighbor updates and CSA, probe requests for probe response generation, self-protected peering frames, HWMP path selection frames, and spectrum-management CSA action frames. Stop flushes stations, keys, mesh paths, beacon data, power-save buffers, timers, work flags, and filter counters.

## State And Persistence
Persistent mesh state lives in `sdata->u.mesh`: mesh ID/config, protocol IDs, accepting-plinks flag, peer/path counters, recent multicast cache pointer, path tables, timers, work flags, preq queue, power-save broadcast buffer, sync state, RCU beacon pointer, CSA settings pointer, CSA role/TTL/pre_value, security/vendor IE data, and mesh sequence number. A global `rm_cache` kmem cache backs recent multicast cache entries and is lazily initialized. Beacon data is RCU-published and replaced/freed with `kfree_rcu()`.

## Dependencies And Integration Points
The file depends on mesh path tables/HWMP (`mesh_pathtbl`, `mesh_hwmp`), peering (`mesh_plink`), mesh power save/sync helpers, WME, driver link-info notifications, cfg80211 channel/DFS/CSA validation, rate/capability IE builders from HT/VHT/HE/EHT code, station management, key cleanup, TX fast path helpers, SKB/wireless status APIs, and interface worker dispatch in `iface.c`. It also integrates with module lifecycle through `ieee80211s_stop()` in `main.c`.

## Risks And Edge Cases
Mesh code is state-machine heavy. Beacon rebuild failure reuses the old beacon where possible, but startup fails if the initial beacon cannot be built. Recent multicast cache allocation failure allows forwarding rather than dropping duplicates. Mesh CSA validation must reject unsupported, DFS-required without userspace DFS, repeated `pre_value`, too-high TTL, or identical channel switches while still forwarding valid CSA frames with decremented TTL. Probe response generation copies current beacon head/tail under RCU. Fast TX is bypassed for multicast, nolearn, sleeping peers, non-Ethernet-II payloads, status-request sockets, insufficient headroom, missing next hop, and non-operational aggregation.

## Test Signals
Useful tests include mesh join/leave cycles, beacon content inspection for mesh ID/config/rates/RSN/HT/VHT/HE/EHT/vendor IEs, peer matching with mismatched mesh config/basic rates/channel/security, recent multicast duplicate suppression and expiry, mesh path discovery/root timer behavior, probe request/response handling, fast TX eligibility and fallback, CSA beacon/action processing including DFS and TTL/pre_value rejection, beacon rebuild on BSS changes, stop cleanup of timers/beacon/path/STA/key state, and lockdep/RCU/KASAN coverage during concurrent mesh RX and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mac80211/mesh.c -->
