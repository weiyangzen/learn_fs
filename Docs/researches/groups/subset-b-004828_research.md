# subset-b-004828

Grouped research for Intel iwlwifi MLD files. Each section is source-tree aligned and bounded for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/fw.c

Purpose: Implements the MLD firmware bring-up, shutdown, and post-alive configuration path. It starts transport hardware, waits for UCODE_ALIVE_NTFY, loads PNVM, sends init PHY configuration, pushes runtime configuration commands, initializes MCC/regulatory state, and tears firmware down on error or stop.

Important APIs/types/functions: `iwl_mld_load_fw()`, `iwl_mld_start_fw()`, `iwl_mld_stop_fw()`, `iwl_mld_send_recovery_cmd()`, `iwl_mld_run_fw_init_sequence()`, `iwl_alive_fn()`, `iwl_mld_config_fw()`, `iwl_mld_send_tx_ant_cfg()`, RSS setup via `iwl_mld_send_rss_cfg_cmd()`, scan setup via `iwl_mld_config_scan()`, and alive timeout diagnostics in `iwl_mld_print_alive_notif_timeout()`.

Control flow: `iwl_mld_start_fw()` calls `iwl_mld_load_fw()`, which starts HW and runs the init sequence. The sequence registers an alive notification wait, starts regular ucode, validates alive response version and payload size, records SKU/error-table data, loads PNVM, sends `INIT_EXTENDED_CFG_CMD` and PHY config, and waits for `INIT_COMPLETE_NOTIF`. After loading, `iwl_mld_config_fw()` sends antenna, BT, SoC latency, LARI, thermal, RX queue, RSS, scan, power, LED, PPAG/SAR/SGOM/TAS/AP-type configuration, and recovery state if this is a hardware restart. Any post-load failure stops firmware before returning.

State/persistence: Maintains `mld->fw_status.running`, alive-derived firmware debug/error table addresses, transport debug IMR data, optional `mld->error_recovery_buf`, and firmware recovery DB exchange state. On stop it aborts notification waits, stops firmware debug collection, stops the device, cancels async notifications, and marks firmware not running.

Dependencies/integration: Uses transport start/stop, firmware runtime/debug TLVs, PNVM, PHY, power, MCC, LED, coexistence, regulatory, thermal, scan, RSS, and host command helpers. It assumes callers hold `wiphy->mtx` and relies on `iwl_mld_send_cmd_pdu()` from `hcmd.h`.

Risks: Alive payload version/length mismatches abort startup. RSS assumes more than one RX queue because queue 0 is skipped as fallback. Recovery command blob failures disconnect station interfaces. Many configuration steps are sequential, so one failed optional-looking subsystem can prevent driver start. Timeout handling reads low-level registers and triggers firmware debug collection.

Test signals: KUnit or integration tests should cover alive notification parsing versions 7/8, timeout/error paths, recovery buffer upload response handling, restart configuration, and startup failure cleanup. Runtime signals include successful `uCode started`, valid MCC initialization, LED configuration after firmware start, and absence of leaked notification waits after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/hcmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/hcmd.h

Purpose: Provides the central MLD host-command send wrappers used by the rest of the op-mode. It standardizes locking, D3 safety, RF-kill behavior, and PDU command construction around `iwl_trans_send_cmd()`.

Important APIs/types/functions: `iwl_mld_send_cmd()`, `__iwl_mld_send_cmd_with_flags_pdu()`, `iwl_mld_send_cmd_with_flags_pdu()`, `iwl_mld_send_cmd_pdu()`, and `iwl_mld_send_cmd_empty()`.

Control flow: Synchronous commands assert that `wiphy->mtx` is held, while async commands skip that lockdep assertion. With PM sleep enabled, sending any command after entering D3 warns and returns `-EIO`. Every command is marked `CMD_SEND_IN_RFKILL` because this op-mode does not support devices that must shut down immediately on RF-kill. The PDU macros construct a stack `iwl_host_cmd` with inferred data length when the caller omits an explicit length.

State/persistence: The helper does not own persistent state, but it gates command emission on `mld->fw_status.in_d3` and mutates `cmd->flags` before transport submission.

Dependencies/integration: Included broadly by firmware, interface, key, LED, MCC, low-latency, and link code. It depends on `struct iwl_mld`, `struct iwl_host_cmd`, command flags, and transport command semantics.

Risks: Async callers are responsible for lifetime of payload buffers. The varargs macro infers `sizeof(*(data))`, so pointer type mistakes can silently send a wrong length unless an explicit length is supplied. Allowing send-in-RF-kill is intentional for this hardware family but would be unsafe if reused for a different transport contract.

Test signals: Compile-time coverage should exercise explicit and inferred PDU lengths. Runtime lockdep should flag synchronous command sends without `wiphy->mtx`, and PM tests should verify D3 command rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/hcmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.c

Purpose: Manages mac80211 virtual interfaces as firmware MAC contexts. It allocates/free firmware MAC IDs, builds `MAC_CONFIG_CMD` payloads by interface type, handles restart cleanup, tracks association side effects, and processes firmware notifications tied to VIF or link-level behavior.

Important APIs/types/functions: `iwl_mld_add_vif()`, `iwl_mld_rm_vif()`, `iwl_mld_mac_fw_action()`, `iwl_mld_cleanup_vif()`, `iwl_mld_set_vif_associated()`, `iwl_mld_get_fw_bss_vifs_ids()`, `iwl_mld_handle_probe_resp_data_notif()`, `iwl_mld_handle_datapath_monitor_notif()`, `iwl_mld_reset_cca_40mhz_workaround()`, and `iwl_mld_get_bss_vif()`.

Control flow: VIF add initializes `struct iwl_mld_vif`, allocates a firmware MAC ID except for NAN, and sends `MAC_CONFIG_CMD` add. MAC command construction fills common address/type/action fields, WiFi generation support, NIC ACK policy, and type-specific filters for STA, AP, monitor, P2P device, and IBSS. Remove sends a firmware remove action, clears the `fw_id_to_vif` RCU mapping, and cancels pending VIF-scoped notifications. Association updates all active links and recalculates multicast filtering.

State/persistence: `iwl_mld_vif` holds restart-cleaned fields such as firmware ID, AP STA, authorization, AP/IBSS active state, low latency causes, power-save state, CCA workaround state, and session protection. It also holds persistent pointers and workers for EMLSR, ROC, aux station, MLO scan deferral, and debugfs. Restart cleanup clears ROC, frees aux/internal link resources, invalidates inactive links, resets EMLSR active flags, and clears keys' hardware indices.

Dependencies/integration: Integrates mac80211 VIFs, firmware MAC context API, MLO link data, key cleanup, session protection, P2P NoA/probe response data, datapath monitor notifications, and multicast filter recalculation.

Risks: NAN is special-cased as unknown to firmware, so callers must not assume every VIF has a firmware ID. Probe-response data notification is explicitly not MLD-ready and rejects MLD VIFs. The 2.4 GHz 40 MHz CCA workaround mutates advertised HT/HE band capabilities and disconnects, so failure to reset on real disconnect would leave stale reduced capabilities. Cleanup warns if inactive links remain allocated unexpectedly.

Test signals: Add/remove VIF tests should validate `fw_id_to_vif` mappings and NAN bypass. Notification tests should cover invalid MAC IDs, P2P NoA length validation, CSA countdown updates, UAPSD misbehaving AP warnings, datapath monitor CCA reconnect flow, and CCA capability restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.h

Purpose: Defines the per-VIF MLD state model, EMLSR state/reason enums, VIF access helpers, valid-link iteration helpers, and interface-level function prototypes.

Important APIs/types/functions: `enum iwl_mld_cca_40mhz_wa_status`, `enum iwl_mld_emlsr_blocked`, `enum iwl_mld_emlsr_exit`, `struct iwl_mld_emlsr`, `struct iwl_mld_vif`, `iwl_mld_vif_from_mac80211()`, `iwl_mld_vif_to_mac80211()`, `iwl_mld_vif_fw_id_valid()`, `iwl_mld_link_dereference_check()`, `for_each_mld_vif_valid_link`, and `iwl_mld_link_from_mac80211()`.

Control flow: The header does not implement large flows, but its helpers shape all VIF/link traversal. Valid link pointers are RCU-dereferenced with lockdep checks against `wiphy->mtx`, while `for_each_mld_vif_valid_link` provides the common active link iteration pattern used in cleanup and link management.

State/persistence: `struct iwl_mld_vif` separates restart-cleaned fields from persistent fields. Restart-cleaned fields include firmware ID, session protection, AP station, authorization, AP STA count, AP/IBSS activity, low-latency causes, and last link activation time. Persistent fields include the owning `mld`, default link object, RCU link pointers, EMLSR workers/state, WoWLAN/debugfs data, ROC activity, aux station, and MLO scan work.

Dependencies/integration: Includes mac80211, MLD link/session/D3/time-event definitions, and exports prototypes used by mac80211, firmware notification, low-latency, key, MLO, and scan code.

Risks: `iwl_mld_vif_fw_id_valid()` warns and fails if `fw_id` is out of the fixed MAC index array; many consumers rely on this guard before indexing per-MAC arrays. EMLSR blocked/exit reasons are bitmasks consumed across MLO code, so new reasons must not collide. RCU link pointers must be accessed only under the expected lock or RCU context.

Test signals: Build and lockdep coverage should verify helper use under `wiphy->mtx`. Unit tests around EMLSR transitions can assert that blocked and exit reason bits map cleanly into policy decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/iface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.c

Purpose: Translates mac80211 key operations into firmware `SEC_KEY_CMD` add, remove, and modify operations. It computes firmware key flags and station masks for pairwise, group, AP, STA, MLO, IGTK, and BIGTK cases.

Important APIs/types/functions: `iwl_mld_add_key()`, `iwl_mld_remove_key()`, `iwl_mld_update_sta_keys()`, `iwl_mld_remove_ap_keys()`, `iwl_mld_track_bigtk()`, `iwl_mld_beacon_protection_enabled()`, plus internal helpers `iwl_mld_get_key_flags()`, `iwl_mld_get_key_sta_mask()`, `iwl_mld_add_key_to_fw()`, and `iwl_mld_remove_key_from_fw()`.

Control flow: Add/remove computes a station mask and key flags, handles IGTK replacement limits, sends `SEC_KEY_CMD` add/remove unless resuming from WoWLAN, updates `key->hw_key_idx`, and tracks IGTK/BIGTK pointers in the link. AP group keys target internal multicast/broadcast stations depending on key index; STA group keys use the AP STA. Per-link keys use a single link station ID, while non-link pairwise keys use the full station mask. Station mask changes send firmware MODIFY commands for pairwise keys when station links change.

State/persistence: Tracks one firmware-installed IGTK per link (`mld_link->igtk`), two BIGTK pointers per STA link, global `mld->num_igtks`, and mac80211 `key->hw_key_idx` as the indicator that a key is in firmware. During WoWLAN resume, firmware is assumed to have already handled rekey state.

Dependencies/integration: Depends on mac80211 key/cipher structures, MLD VIF/link/STA mappings, internal AP broadcast/multicast station allocation, and the datapath firmware key API.

Risks: Returning zero station mask drops or rejects operations; missing internal AP STAs prevent AP group key installation. Firmware supports fewer concurrent IGTKs than mac80211 can expose, requiring replacement logic. TKIP MIC key offsets must match nl80211 layout. Resume shortcuts assume firmware key state is authoritative after WoWLAN.

Test signals: Tests should cover station mask computation for AP group, STA group, pairwise MLO, and link-specific keys; IGTK replacement and max-count behavior; BIGTK tracking; WoWLAN resume no-op behavior; and pairwise key MODIFY during link station remapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.h

Purpose: Declares the MLD key-management API and provides the restart cleanup iterator that invalidates mac80211 key hardware indices.

Important APIs/types/functions: `iwl_mld_add_key()`, `iwl_mld_remove_key()`, `iwl_mld_remove_ap_keys()`, `iwl_mld_update_sta_keys()`, `iwl_mld_cleanup_keys_iter()`, `iwl_mld_track_bigtk()`, and `iwl_mld_beacon_protection_enabled()`.

Control flow: The inline cleanup iterator is called by VIF restart cleanup and marks each key as not present in hardware with `STA_KEY_IDX_INVALID`. The rest of the header exposes key add/remove/update hooks used mainly by mac80211 callback code and station/link lifecycle code.

State/persistence: No independent state is stored in the header. Its APIs mutate key hardware indices, link IGTK/BIGTK pointers, AP early keys, and firmware key table state in `key.c` callers.

Dependencies/integration: Includes `mld.h`, mac80211, and firmware STA definitions. It forms the boundary between `mac80211.c`, `iface.c`, AP code, and the key firmware command implementation.

Risks: Any cleanup path that forgets `iwl_mld_cleanup_keys_iter()` may leave mac80211 believing keys remain installed after restart. Callers must honor the invariant that key update operations happen with wiphy locking and valid VIF/STA/link mappings.

Test signals: Restart/recovery tests should ensure all keys have invalid hardware indices after VIF cleanup and that reconfiguration later reinstalls keys through the normal `set_key` path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.c

Purpose: Registers and drives the optional Linux LED class device for MLD hardware, translating brightness changes into firmware `LEDS_CMD` commands.

Important APIs/types/functions: `iwl_mld_leds_init()`, `iwl_mld_led_config_fw()`, `iwl_mld_leds_exit()`, `iwl_led_brightness_set()`, and `iwl_mld_send_led_fw_cmd()`.

Control flow: Initialization reads `iwlwifi_mod_params.led_mode`, accepts default/RF-state mode, rejects unsupported values, and maps blink to RF-state with an error. It allocates a LED name, sets a brightness callback, optionally uses the mac80211 radio LED trigger, and registers with the LED class. Brightness changes send async firmware LED commands only when firmware is running. Firmware reconfiguration replays current brightness after firmware start.

State/persistence: Stores the LED class device in `mld->led`, including allocated `led.name`, default trigger, current brightness, and max brightness. Exit unregisters and frees the name, then nulls it.

Dependencies/integration: Depends on Linux LED class, mac80211 radio LED trigger, MLD firmware command helpers, module LED mode parameters, and the firmware long-group LED command.

Risks: LED commands are async, so payload lifetime relies on transport command-copy semantics. Firmware command attempts before `fw_status.running` are warned/rejected. Unsupported blink mode is silently downgraded after logging, which may surprise users expecting blink behavior.

Test signals: Build configurations with and without `CONFIG_IWLWIFI_LEDS` should compile. Runtime checks include LED registration success, brightness toggles producing firmware commands only while running, replay after firmware restart, and clean unregister/free on op-mode stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.h

Purpose: Provides the LED subsystem interface for MLD and compiles it out cleanly when LED support is disabled.

Important APIs/types/functions: `iwl_mld_leds_init()`, `iwl_mld_leds_exit()`, and `iwl_mld_led_config_fw()`, with static inline no-op versions when `CONFIG_IWLWIFI_LEDS` is not set.

Control flow: Callers can unconditionally invoke LED init, exit, and firmware replay hooks. The header maps those calls either to real implementations in `led.c` or no-op/stub behavior.

State/persistence: With LED support disabled, no LED state is allocated or mutated. With support enabled, state resides in `mld->led` and is managed by `led.c`.

Dependencies/integration: Includes `mld.h` and is consumed by firmware startup and op-mode lifecycle code.

Risks: The no-op `iwl_mld_leds_init()` always returns success, so tests must consider both build-time variants. Any future LED caller should remain valid when support is compiled out.

Test signals: Compile both `CONFIG_IWLWIFI_LEDS=y` and disabled configurations. In disabled builds, op-mode start/stop should not require LED class symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.c

Purpose: Manages firmware link contexts for each mac80211 BSS/link configuration. It adds/removes/activates/deactivates links, packs link configuration commands, handles missed beacon and beacon filter notifications, and computes link quality grades for MLO/EMLSR policy.

Important APIs/types/functions: `iwl_mld_add_link()`, `iwl_mld_remove_link()`, `iwl_mld_activate_link()`, `iwl_mld_deactivate_link()`, `iwl_mld_change_link_in_fw()`, `iwl_mld_handle_missed_beacon_notif()`, `iwl_mld_cancel_missed_beacon_notif()`, `iwl_mld_link_set_associated()`, `iwl_mld_get_link_grade()`, `iwl_mld_get_chan_load()`, `iwl_mld_get_chan_load_by_others()`, and `iwl_mld_handle_beacon_filter_notif()`.

Control flow: Link add allocates or reuses link state, allocates a firmware link ID, maps it with RCU, and sends `LINK_CONFIG_CMD` add. Change builds a modify command with MAC/PHY IDs, local addresses, active state, rates, protection, QoS, beacon/DTIM, HE/MU-EDCA/BSS color, RU blocking, and nontransmitted BSSID fields. Activation marks active, sends active modify, and records activation time; deactivation cancels session protection, frees probe response data, sends inactive modify, and cancels link-scoped notifications. Remove sends firmware remove and clears mappings. Missed beacon notifications can trigger connection loss, CQM beacon loss, MLO scan, or EMLSR exit depending on thresholds and second-link loss.

State/persistence: Owns `struct iwl_mld_link` firmware ID, active flag, queue parameters, channel context pointer, HE RU 2 MHz block, IGTK/BIGTK pointers, internal broadcast/multicast/monitor stations, average beacon energy, early AP keys, silent deactivation flag, and RCU probe response data. Link grade is derived, not persisted except beacon energy and channel-load inputs.

Dependencies/integration: Integrates with mac80211 BSS configs, MLD VIFs, PHY contexts, TLC/rate constants, MLO/EMLSR policy, session protection, AP beacon/NoA handling, firmware MAC configuration, and cfg80211 BSS load elements.

Risks: Link command packing depends on valid channel context for rates and PHY ID. Silent deactivation is subtle and only intended around CSA with quiet in EMLSR. Channel load from QBSS elements can be absent or invalid; defaults differ by band. Link grading assumes valid RSSI/band/width and adjusts 6 GHz RSSI. Missed beacon thresholds have several branches that can disconnect or merely warn when RX data continues.

Test signals: KUnit exports cover missed beacon handling and link grading. Tests should exercise add/remove rollback, active state failure rollback, QoS/rate/protection modify masks, EMLSR missed beacon exits, channel-load fallback, puncturing subchannel counts, and beacon filter average energy updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.h

Purpose: Defines per-link state for MLD VIFs and declares link lifecycle, notification, channel-load, and link-grade APIs.

Important APIs/types/functions: `struct iwl_probe_resp_data`, `struct iwl_mld_link`, `iwl_mld_cleanup_link()`, `NORMALIZE_PERCENT_TO_255`, and prototypes for link add/remove/activate/deactivate/change, missed beacon handling, association update, link grade, channel load, and beacon filter notification handling.

Control flow: The inline cleanup helper frees RCU probe response data, clears restart-cleaned link fields, and frees internal broadcast, multicast, and monitor STAs if allocated. It is used during firmware restart and VIF cleanup before links are reused or freed.

State/persistence: `struct iwl_mld_link` intentionally separates restart-cleaned fields from state that survives restart. Firmware ID, active flag, EDCA params, channel context, RU block, and key pointers are reset on restart. Internal STAs, RSSI event history, AP early keys, average beacon energy, silent deactivation, and probe response data are outside that group but cleanup still frees relevant dynamic resources.

Dependencies/integration: Includes mac80211, MLD root state, STA state, datapath notification structures, AP key flows, P2P NoA data, and MLO policies.

Risks: Cleanup must be called before freeing or reusing link state, otherwise RCU probe data or internal station IDs can leak. AP early key capacity is fixed at six entries. `NORMALIZE_PERCENT_TO_255` multiplies by 256/100, so callers should expect a 0..256 style scale, not a strict 0..255 maximum.

Test signals: Restart cleanup tests should validate internal STA freeing and RCU pointer clearing. Link-state tests should confirm that fields intended to survive restart are not accidentally zeroed by `CLEANUP_STRUCT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.c

Purpose: Detects latency-sensitive VO/VI traffic and toggles firmware low-latency mode per MAC context. It also coordinates low-latency state with P2P client power settings and EMLSR retry behavior.

Important APIs/types/functions: `iwl_mld_low_latency_init()`, `iwl_mld_low_latency_free()`, `iwl_mld_low_latency_restart_cleanup()`, `iwl_mld_vif_update_low_latency()`, `iwl_mld_low_latency_update_counters()`, `iwl_mld_low_latency_stop()`, `iwl_mld_low_latency_restart()`, `iwl_mld_calc_low_latency()`, and `iwl_mld_send_low_latency_cmd()`.

Control flow: Data path calls `iwl_mld_low_latency_update_counters()` with packet header, STA, and RX/TX queue. QoS data packets with VO/VI TIDs increment per-queue/per-MAC counters and schedule work at 500 ms cadence. The worker sums counters by MAC, enables low latency immediately above threshold, disables only after the 10 second active period expires below threshold, then iterates active interfaces and updates VIF low-latency causes. State changes send `LOW_LATENCY_CMD`; P2P clients also update MAC power and retry EMLSR when enabling.

State/persistence: Allocates per-RX-queue counter arrays with spinlocks. Maintains per-MAC window start times, latest per-MAC low-latency result, global timestamp, delayed work, and a stopped flag. VIF low-latency causes are bitfields in `iwl_mld_vif`.

Dependencies/integration: Depends on mac80211 QoS headers/TIDs, MLD STA/VIF mappings, firmware MAC configuration commands, power management, MLO/EMLSR helpers, and wiphy delayed work.

Risks: Counter updates run in data-path context and must use spinlocks. `sta` and VIF mappings must be valid; invalid firmware IDs or queue IDs are dropped with warnings. Work is suppressed during hardware restart and stopped during driver stop. Thresholds are constants, so behavior may be sensitive to traffic bursts and queue count.

Test signals: Tests should simulate VO/VI and non-VO/VI packets, threshold crossing, delayed disable after active window expiry, restart cleanup counter reset, stop/restart behavior, command failure rollback of VIF cause bits, and P2P client power/EMLSR side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.h

Purpose: Defines low-latency detection state, cause bits, packet counters, and public low-latency lifecycle/update APIs.

Important APIs/types/functions: `struct iwl_mld_low_latency_packets_counters`, `enum iwl_mld_low_latency_cause`, `struct iwl_mld_low_latency`, and prototypes for init/free/restart cleanup, VIF update, counter update, stop, and restart.

Control flow: The header defines the data contract used by data-path calls and worker code. Cause bits allow multiple independent sources, such as traffic, debugfs, and VIF type, to request low latency without clearing each other accidentally.

State/persistence: Packet counters are cacheline-aligned and protected by spinlocks. The main state stores delayed work, timestamps, per-MAC windows/results, allocated counters, and stop status.

Dependencies/integration: Relies on `NUM_MAC_INDEX_DRIVER`, `struct iwl_mld`, mac80211 headers, and VIF-level low latency cause storage.

Risks: Cause bits must remain unique bit values. The per-MAC arrays must stay in sync with firmware MAC ID array sizes. Counter allocation size depends on transport RX queue count.

Test signals: Compile-time and runtime tests should confirm array bounds with firmware ID validation, independent cause-bit set/clear behavior, and safe counter updates across all RX queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mac80211.c

Purpose: Implements the `struct ieee80211_ops` adapter for the MLD op-mode. It exposes device capabilities to mac80211/cfg80211, starts and stops firmware for mac80211, manages VIF/channel/station/key/scan/AP/ROC/NAN callbacks, and connects user-visible wireless operations to the lower MLD firmware modules.

Important APIs/types/functions: `iwl_mld_register_hw()`, `iwl_mld_recalc_multicast_filter()`, `iwl_mld_mac80211_start()`, `iwl_mld_mac80211_stop()`, VIF callbacks, channel context callbacks, `iwl_mld_mac80211_link_info_changed()`, `iwl_mld_mac80211_vif_cfg_changed()`, `iwl_mld_mac80211_sta_state()`, `iwl_mld_mac80211_set_key()`, scan callbacks, CSA callbacks, MLO link callbacks, FTM/timestamp/NAN hooks, and the exported `iwl_mld_hw_ops` table.

Control flow: Registration verifies firmware command/notification preconditions, sets addresses, channels, security, PM/WoWLAN, antennas, radiotap, hardware flags, wiphy capabilities, MLO/HE/EHT features, and data sizes before `ieee80211_register_hw()`. Start resumes from D3 when possible, performs restart cleanup if needed, starts firmware, and emits debug time points. Stop cancels deferred TXQ work, optionally stops firmware, clears restart state, and warns on leftover scan UIDs. Interface callbacks create/remove VIFs and default links, track monitor/P2P/NAN singletons, and modify interface type by remove/add. Channel context callbacks allocate PHY IDs, send PHY commands, assign contexts to links, activate links when safe, and deactivate/remove on unassign. Station state transitions add STAs, configure TLC, update link stations, set AP STA, handle authorization, block/unblock EMLSR for TDLS/throughput, and update AP beacon filters. Key callbacks filter unsupported ciphers, allocate PTK PN tracking, store AP early keys, and delegate firmware key operations.

State/persistence: Mutates most top-level MLD state: `fw_status`, monitor state, scan status, multicast filter command, used PHY IDs, VIF/link/STA mappings, AP STA authorization, EMLSR state/work, TDLS count effects, PTK PN state, antenna masks, and WoWLAN/runtime PM state. Multicast filter data is allocated in prepare and installed in configure. TXQs not yet allocated are queued on `txqs_to_add`.

Dependencies/integration: This is the main integration point for mac80211/cfg80211, firmware start/configuration, VIF/link/key/STA/AP/scan/D3/TLC/aggregation/ROC/MLO/NAN/FTM/time-sync/stats/thermal-related modules, transport queue state, and Linux networking offload features.

Risks: This file coordinates many ordering-sensitive flows: restart cleanup must precede mac80211 reconfiguration, session protection assumes callback ordering around association, channel switch swap/reassign has rollback paths, MLO link activation can wait for link STA firmware state, and AP keys may arrive before AP internal STAs. FIPS disables ciphers/WiFi7 features. Multicast filter memory ownership crosses prepare/configure callbacks. A-MSDU aggregation is restricted to IPv4 and matching checksum offload capability.

Test signals: Broad mac80211 integration tests should cover registration capability flags, start/stop/restart, VIF add/remove/change, channel context assign/unassign/switch rollback, STA state up/down including TDLS and AP station counts, key add/remove including unsupported ciphers and PN allocation, scan start/cancel races, multicast filter ownership, CSA EMLSR exit behavior, WoWLAN suspend/resume, antenna set/get, and NAN/FTM/timestamp callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mac80211.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mac80211.h

Purpose: Declares the small public surface from the mac80211 adapter module to the rest of MLD.

Important APIs/types/functions: `iwl_mld_register_hw()` and `iwl_mld_recalc_multicast_filter()`.

Control flow: `iwl_mld_register_hw()` is called during op-mode start after NVM, scan command, LED, and low-latency setup are ready. `iwl_mld_recalc_multicast_filter()` is called when association state or multicast configuration changes and resends the stored multicast filter to associated station VIFs.

State/persistence: No state is defined here. The declared functions mutate `mld->hw`, `mld->wiphy`, and multicast filter state in `mac80211.c`.

Dependencies/integration: Includes `mld.h` and is used by op-mode startup and interface association code.

Risks: The narrow header helps keep the large mac80211 callback table private. Callers must still ensure the MLD object is initialized enough for registration or multicast command replay.

Test signals: Linkage/build tests should catch accidental signature drift. Runtime registration and multicast update behavior are covered through `mac80211.c` integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mac80211.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.c

Purpose: Handles MCC/regulatory communication with firmware and converts firmware channel profiles into cfg80211 regulatory domains.

Important APIs/types/functions: `iwl_mld_get_regdomain()`, `iwl_mld_init_mcc()`, `iwl_mld_update_changed_regdomain()`, `iwl_mld_handle_update_mcc()`, and internal helpers `iwl_mld_update_mcc()`, `iwl_mld_copy_mcc_resp()`, `iwl_mld_get_current_regdomain()`, and `iwl_mld_apply_last_mcc()`.

Control flow: `iwl_mld_update_mcc()` sends `MCC_UPDATE_CMD` with alpha2/source and expects a response SKB. `iwl_mld_copy_mcc_resp()` validates payload length based on channel count before copying. `iwl_mld_get_regdomain()` parses the response through NVM regulatory helpers, records MCC source, and updates puncturing allowance for applicable RF types. Init first replays an existing wiphy regdomain if present; otherwise it gets current firmware regdomain and optionally overrides with BIOS MCC. CHUB update notifications are ignored for WiFi source while associated, otherwise they fetch a new regdomain and install it if changed.

State/persistence: Updates `mld->mcc_src`, wiphy regulatory domain, and `IEEE80211_HW_DISALLOW_PUNCTURING` flag based on BIOS/firmware policy. Temporary firmware MCC responses and parsed regdomains are allocated and freed by caller flow.

Dependencies/integration: Depends on firmware MCC commands/notifications, host command response SKBs, `iwl_parse_nvm_mcc_info()`, cfg80211 regulatory APIs, BIOS MCC data, UEFI puncturing policy, and active interface iteration.

Risks: MCC response length validation is critical because channel array length is firmware-controlled. `regulatory_set_wiphy_regd_sync()` can fail init. Ignoring WiFi MCC updates while associated avoids regulatory churn but can defer changes. Puncturing policy is conditional on RF type and BIOS permissions.

Test signals: Tests should cover malformed response lengths, zero MCC warnings, changed status handling, replay of previous regdomain source, BIOS MCC override, associated WiFi-source notification ignore, regulatory set failures, and puncturing flag toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.h

Purpose: Declares the MLD MCC/regulatory API used by firmware startup and notification handling.

Important APIs/types/functions: `iwl_mld_init_mcc()`, `iwl_mld_handle_update_mcc()`, `iwl_mld_update_changed_regdomain()`, and `iwl_mld_get_regdomain()`.

Control flow: The header exposes initialization, async notification handling, on-demand changed-regdomain update, and direct regdomain fetch by alpha2/source.

State/persistence: State changes occur in `mcc.c`: wiphy regdomain, MCC source, and puncturing flags. The API contract notes that returned regdomains must be freed by the caller.

Dependencies/integration: Consumed by firmware startup and notification modules, and depends on cfg80211 regulatory types plus firmware MCC source enums from included MLD context.

Risks: Callers of `iwl_mld_get_regdomain()` own the returned pointer and must handle `ERR_PTR`/NULL. Most calls require `wiphy->mtx`, enforced in implementation.

Test signals: Build tests should catch type/signature drift; regulatory integration tests should confirm init and notification callers handle allocation and error returns correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.c

Purpose: Defines the MLD op-mode module and its transport-facing `iwl_op_mode_ops`. It registers the `iwlmld` op-mode, constructs/destructs the main MLD object, configures transport command groups, starts initial firmware to read NVM, registers mac80211 hardware, and handles transport callbacks for queues, RF-kill, errors, dumps, reset, and power-off.

Important APIs/types/functions: module init/exit `iwl_mld_init()`/`iwl_mld_exit()`, `iwl_construct_mld()`, `iwl_op_mode_mld_start()`, `iwl_op_mode_mld_stop()`, `iwl_mld_configure_trans()`, firmware runtime ops, command-name group arrays `iwl_mld_groups`, queue callbacks, `iwl_mld_nic_error()`, `iwl_mld_sw_reset()`, `iwl_mld_dump_error()`, `iwl_mld_restart_nic()`, and `iwl_mld_ops`.

Control flow: Module init registers the op-mode. Start allocates `ieee80211_hw` with private op-mode plus MLD storage, initializes MLD structures/work, constructs firmware runtime, reads BIOS/UEFI policy, configures regulatory and transport settings, starts firmware under RTNL and wiphy locks with retries, reads NVM, flushes async handlers, stops firmware, initializes LED/scan/low-latency, registers mac80211 HW, initializes debugfs/thermal/PTP, and returns op-mode. Stop removes PTP/LED/thermal, stops low-latency/time-sync under wiphy lock, unregisters mac80211, frees firmware runtime and allocations, leaves transport op-mode, and frees HW.

State/persistence: Initializes and frees top-level persistent state in `struct iwl_mld`: transport/config/firmware/HW pointers, fw runtime, notification waits, async handler list/work, TXQ add list/work, RX queue sync waitqueue, NVM data, scan command, low-latency counters, LED, thermal, PTP, multicast filter, channel survey, and error recovery buffer. Error paths set `fw_status.in_hw_restart`, `do_not_dump_once`, scan abort state, and error recovery buffer for later firmware recovery.

Dependencies/integration: Integrates Linux module lifecycle, iwlwifi op-mode registry, transport configuration, UEFI/BIOS tables, firmware runtime debug, mac80211 HW registration, NVM parsing, LED/scan/low-latency/thermal/PTP/time-sync subsystems, and all command group name tables used by transport/debug.

Risks: Start error unwinding must free only initialized resources and leave transport op-mode. Initial firmware is started only to obtain NVM, then stopped before mac80211 registration. Command group arrays must remain sorted for binary search. Queue-full handling for unmapped internal queues stops all mac80211 queues. Error/restart paths must abort scan before restart to satisfy mac80211.

Test signals: Tests should cover op-mode start failure at each allocation/init stage, firmware load retry and NVM read failure, stop cleanup idempotence, command group lookup coverage, queue full/not-full mapping, RF-kill updates, NIC error dump/restart behavior, SW reset restart gating, and PM powered-off handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.h

Purpose: Defines the top-level MLD op-mode data structure, global module parameters, cleanup/reset helpers, firmware lifecycle prototypes, firmware-ID allocation macro, notification handler contracts, band/rate conversion helpers, and debug/test exports.

Important APIs/types/functions: `struct iwl_mld`, `CLEANUP_STRUCT`, `iwl_cleanup_mld()`, `struct iwl_mld_mod_params`, `IWL_OP_MODE_GET_MLD`, `IWL_MAC80211_GET_MLD`, firmware lifecycle prototypes, RF-kill setters, antenna helpers, band conversion helpers, `struct iwl_rx_handler`, `struct iwl_notif_struct_size`, `IWL_MLD_ALLOC_FN`, `iwl_mld_fw_id_to_link_conf()`, `iwl_mld_mac80211_ac_to_fw_tx_fifo()`, `iwl_mld_get_lmac_id()`, and `iwl_mld_error_before_recovery()`.

Control flow: The header codifies the resource lifecycle described in its documentation: MLD owns VIF/link/STA mappings, restart-sensitive fields are grouped for zeroing, and async firmware notifications can be tied to object instances. `iwl_cleanup_mld()` zeroes restart-cleaned top-level and scan state, clears D3 state, and resets low-latency runtime counters. The allocation macro finds an unused RCU mapping slot, optionally randomized, with array size adjusted for station/link firmware capability limits.

State/persistence: `struct iwl_mld` is the central persistent state object. Restart-cleaned fields include firmware link/VIF/TXQ mappings, used PHY IDs, IGTK count, monitor data, netdetect, P2P/NAN VIF pointers, and BT activity. Persistent fields include transport/config/firmware/HW/wiphy pointers, capabilities arrays, NVM data, firmware runtime, notification wait/list/work, thermal work, firmware status/rfkill flags, power budget, MAC addresses, scan/survey, WoWLAN, LED, MCC source, puncturing policy, BA sessions, RXQ sync, deferred TXQ list/work, recovery buffer, multicast filter, antenna masks, rate version, low-latency state, thermal/PTP/time-sync/FTM data, and station mapping that survives restart.

Dependencies/integration: Pulls together iwl transport/op-mode, firmware runtime and command APIs, mac80211, notification, scan, RX, thermal, low-latency, PTP, time-sync, FTM, NAN, and constants. Its types are included by nearly every MLD source file.

Risks: Because this header is widely included, layout or helper changes have large blast radius. Restart grouping must be maintained carefully: putting a field in the wrong group can either leak stale firmware state across restart or erase state needed for recovery. `IWL_MLD_ALLOC_FN` uses compile-time type checks and RCU pointer arrays; misuse with an unexpected type would be dangerous. The exported KUnit symbol name `global_iwl_mld_goups_size` appears misspelled and consumers must match it.

Test signals: KUnit should validate allocation macro behavior under full tables, restart cleanup field boundaries, band/rate conversions, LMAC selection with and without CDB, firmware ID lookup bounds checks, and notification handler registration/cancellation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mld.h -->
