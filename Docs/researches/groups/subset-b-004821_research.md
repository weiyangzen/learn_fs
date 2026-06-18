# Research: subset-b-004821

Grouped source research for the Intel iwlwifi DVM thermal/TX/ucode path and shared firmware API/ACPI subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.c

Purpose: Implements DVM thermal throttling, including legacy power-index throttling, advanced thermal-index state transitions, CT-kill entry/exit, mac80211 queue stop/wake, and temperature-triggered HT/TX-stream restrictions.

Important APIs and functions: `iwl_tt_is_low_power_state()`, `iwl_tt_current_power_mode()`, `iwl_ht_enabled()`, `iwl_check_for_ct_kill()`, `iwl_tx_ant_restriction()`, `iwl_tt_enter_ct_kill()`, `iwl_tt_exit_ct_kill()`, `iwl_tt_handler()`, `iwl_tt_initialize()`, and `iwl_tt_exit()` are the public entry points. Static handlers include legacy and advanced state machines, CT-kill timers, and workqueue callbacks.

Control flow: Temperature updates queue `tt_work`, which dispatches to the legacy or advanced handler. Legacy mode maps temperature bands to `IWL_TI_0`, `IWL_TI_1`, `IWL_TI_2`, or `IWL_TI_CT_KILL` and updates the power mode. Advanced mode consults per-state transition tables, applies restriction-table effects such as HT disable, and then updates firmware power mode. CT-kill can be entered immediately for forced firmware card-state notifications or delayed through a 300 ms waiting timer; while in CT-kill a 5 second timer toggles `CSR_UCODE_DRV_GP1_REG_BIT_CT_KILL_EXIT` to wake firmware for temperature checks. Exit notifications cancel the timer, clear critical state, and wake queues.

State and persistence: Mutates `priv->thermal_throttle` state, `advanced_tt`, `tt_power_mode`, dynamic restriction/transition tables, CT-kill toggle, and two timers. It also sets/clears `STATUS_CT_KILL`, stops/wakes mac80211 queues, updates `priv->temperature`, and touches RXON staging flags for HT mode. State is runtime-only and rebuilt by `iwl_tt_initialize()`.

Dependencies and integration points: Depends on DVM private state in `dev.h`, command constants in `commands.h`, mac80211 queue APIs, transport MMIO access, power-management updates through `iwl_power_update_mode()`, statistics requests, RXON HT helpers, and driver workqueues/timers. It integrates with firmware card-state notifications and temperature statistics handling.

Risks: CT-kill state changes cross workqueue, timer, and mutex contexts, so teardown must cancel timers/work before freeing advanced tables. The advanced transition indexing assumes `IWL_TI_STATE_MAX` table geometry matches allocations. Failing `iwl_power_update_mode()` rolls back state and status bits. HT flag edits happen before the mutex-protected firmware update and must remain consistent with RXON commit paths. Temperature thresholds differ between legacy and advanced modes.

Test signals: Exercise legacy and advanced throttling across every threshold, CT-kill forced entry/exit notifications, delayed CT-kill timer entry, CT-kill exit polling, failed power update rollback, HT disable/restore in advanced state 2, queue stop/wake with mac80211 registered, teardown while timers/work are pending, and allocation failure fallback to legacy throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.h

Purpose: Defines DVM thermal throttling constants, states, restriction/transition structures, management state, and public thermal-throttling APIs.

Important APIs and types: `enum iwl_antenna_ok` models allowed antenna/stream use. `enum iwl_tt_state` defines normal, two throttled, and CT-kill states. `struct iwl_tt_restriction` encodes TX/RX stream and HT permissions. `struct iwl_tt_trans` encodes temperature ranges and next states. `struct iwl_tt_mgmt` stores current state, advanced-mode flag, power mode, optional previous temperature, tables, CT-kill toggle, and timers. Public prototypes expose current mode queries, restrictions, CT-kill handlers, initialization, and cleanup.

Control flow: This header has no executable flow; it is the ABI between DVM core code, TX/rate-control decisions, power management, and `tt.c` implementation.

State and persistence: The header owns no storage but defines the runtime `priv->thermal_throttle` layout. No durable persistence exists; state is reconstructed at driver start and cleaned at exit.

Dependencies and integration points: Includes DVM `commands.h` for thermal thresholds and power indices. Consumers use these declarations to gate HT support, choose TX antenna restrictions, and react to firmware CT-kill/card-state signals.

Risks: Changing enum order or struct layout can break table indexing in `tt.c`. `tt_previous_temp` exists only under `CONFIG_IWLWIFI_DEBUG`, so code must not rely on it outside that configuration. Timer fields require correct lifetime management by the implementation.

Test signals: Compile both debug and non-debug builds, advanced and legacy thermal configs, and all users of `iwl_ht_enabled()` and `iwl_tx_ant_restriction()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tx.c

Purpose: Implements DVM transmit command construction, frame enqueue, hardware crypto setup, per-station power-save accounting, aggregation queue lifecycle, TX completion processing, compressed block-ack processing, and firmware status accounting.

Important APIs and functions: `iwlagn_tx_skb()` is the main skb transmit path. Aggregation entry points are `iwlagn_tx_agg_start()`, `iwlagn_tx_agg_oper()`, `iwlagn_tx_agg_stop()`, and `iwlagn_tx_agg_flush()`. Completion handlers are `iwlagn_rx_reply_tx()` and `iwlagn_rx_reply_compressed_ba()`. Helpers build basic TX flags, rate fields, hardware crypto fields, allocate/deallocate AMPDU queues, translate firmware rates/statuses, and count status failures.

Control flow: TX starts by selecting the RXON context and station ID, appending NoA data to probe responses when present, allocating an `iwl_device_tx_cmd`, filling length/security/basic/rate fields, and storing context/command pointers in `IEEE80211_SKB_CB`. Under `sta_lock`, QoS frames receive driver sequence numbers from `tid_data`; aggregated frames are routed to the per-TID aggregation queue while non-aggregated frames use the mac80211 queue. Successful enqueue advances per-TID sequence state and increments pending client frame counters for non-aggregation traffic. Aggregation start allocates a hardware queue and either starts immediately or waits for the old queue to drain. Stop and flush disable firmware queues only when the transport had actually enabled aggregation. TX replies reclaim TFDs, update `next_reclaimed`, unblock pending ADDBA/DELBA flows, free stored device commands, translate status to mac80211, and deliver skbs to `ieee80211_tx_status_skb()`. Compressed BA notifications reclaim all frames before the BA SSN and report aggregate ack information on the first skb.

State and persistence: Mutates `priv->tid_data[sta][tid]` sequence, `next_reclaimed`, aggregation state, SSN, txq ID, and `wait_for_ba`; `agg_q_alloc`; `queue_to_mac80211`; `agg_tids_count`; station pending frame counters; rate-control fields in `lq_sta`; TX status statistics; `passive_no_rx`; `last_seq_ctl`; and queued `tx_flush` work. All state is runtime queue/session state and must be reset by station/queue teardown.

Dependencies and integration points: Depends on mac80211 TX metadata and status APIs, iwl transport allocation/enqueue/reclaim/free functions, station table helpers, DVM RXON contexts, link-quality command submission, BT coexistence parameters, firmware command layouts from `commands.h`, and aggregation callbacks into mac80211.

Risks: `info->control` is invalid after command ownership is stored, so later code must only use saved driver data/status fields. Aggregation state is subtle: queue drain transitions must compare SSN and `next_reclaimed` correctly or mac80211 BA callbacks happen too early. Error paths can leak allocated aggregation queues if `iwl_sta_tx_modify_enable_tid()` fails after queue allocation. Completion processing assumes firmware frame counts, SSNs, and queue IDs are coherent. `TX_STATUS_FAIL_PASSIVE_NO_RX` stops all queues and requires later recovery. Hardware crypto key formatting must match cipher-specific firmware expectations.

Test signals: Cover data, management, BAR, probe response with NoA, RF-kill drop, missing station drop, hardware crypto for CCMP/TKIP/WEP, QoS sequence assignment, AMPDU enqueue validation, aggregation start immediate/deferred, stop during starting/on/draining states, flush, single-frame TX replies, aggregated failure requiring BAR, compressed BA success, passive-channel no-RX queue stop, RF-kill flush work scheduling, and per-status statistic counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/ucode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/ucode.c

Purpose: Handles DVM firmware alive transitions and init-ucode calibration, including calibration command setup, BT/WiMAX coexistence bootstrap, queue-to-TX-FIFO enablement, ALIVE notification wait, and calibration result capture.

Important APIs and functions: `iwl_init_alive_start()` sends initial calibration configuration and optional BT environment setup. `iwl_send_prio_tbl()` and `iwl_send_bt_env()` program BT coexistence tables/environment. `iwl_load_ucode_wait_alive()` starts a selected firmware image and waits for `REPLY_ALIVE`. `iwl_run_init_ucode()` runs init firmware, waits for calibration complete, stores calibration results, and stops the device. Static helpers prepare XTAL and temperature-offset calibrations, disable WiMAX coexistence, enable AC/IPAN TX queues, and parse alive/calibration notifications.

Control flow: Init firmware flow registers a wait for calibration result/complete notifications, calls `iwl_load_ucode_wait_alive(IWL_UCODE_INIT)`, sends init-alive calibration setup, waits up to two seconds for calibration completion, then stops the transport regardless of success. Alive loading changes `priv->cur_ucode`, registers a one-second ALIVE wait, starts firmware through the transport, validates the alive response, delays briefly for rfkill outside WoWLAN, calls `iwl_alive_notify()`, and rolls back `cur_ucode` on failure. `iwl_alive_notify()` marks transport firmware alive, enables default or IPAN queues to TX FIFOs, clears passive/queue-stop state, disables WiMAX coexistence, sends XTAL calibration when needed, and sends saved calibration results.

State and persistence: Updates `priv->cur_ucode`, `priv->ucode_loaded`, `device_pointers.error_event_table`, `device_pointers.log_event_table`, `passive_no_rx`, and `transport_queue_stop`; stores calibration data through `iwl_calib_set()`. Calibration data persists in driver memory for later runtime firmware use, not across reloads.

Dependencies and integration points: Depends on `iwl_trans_start_fw()`, `iwl_trans_fw_alive()`, notification wait infrastructure, DVM command send helpers, NVM calibration fields, firmware capability flags, BT coexistence commands, transport queue enable APIs, calibration storage helpers, and runtime/init firmware images.

Risks: Notification waits must be removed on start/setup failure to avoid stale callbacks. `cur_ucode` and `ucode_loaded` need rollback on failed alive or post-alive setup. Queue-to-FIFO arrays differ for PAN/IPAN firmware and SKU capability. Temperature-offset calibration has v1/v2 layouts and fallback defaults. Init ucode always stops the device, so callers must not assume firmware remains loaded after calibration.

Test signals: Firmware start failure, ALIVE timeout, invalid alive response, post-alive command failure, init image absent, calibration result accumulation until complete, temp-offset v1/v2/default paths, XTAL skipped by `no_xtal_calib`, PAN/IPAN queue mapping, BT coexistence enabled/disabled, and cleanup of notification waits on every error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/ucode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.c

Purpose: Reads Intel Wi-Fi ACPI methods and DSM functions into `iwl_fw_runtime` regulatory, SAR, TAS, geo, PPAG, PHY-filter, and feature-policy state.

Important APIs and functions: Exports `iwl_acpi_get_dsm_object()`, `iwl_acpi_get_dsm()`, `iwl_acpi_get_tas_table()`, `iwl_acpi_get_mcc()`, `iwl_acpi_get_pwr_limit()`, `iwl_acpi_get_eckv()`, `iwl_acpi_get_wrds_table()`, `iwl_acpi_get_ewrd_table()`, `iwl_acpi_get_wgds_table()`, `iwl_acpi_get_ppag_table()`, `iwl_acpi_get_phy_filters()`, `iwl_acpi_get_guid_lock_status()`, `iwl_acpi_get_wbem()`, and `iwl_acpi_get_dsbr()`. Static helpers locate/evaluate ACPI methods, parse Wi-Fi-domain packages, parse chain tables, and cache DSM integer values.

Control flow: Method readers call `iwl_acpi_get_object()`, select the Wi-Fi package by revision and expected size/range, validate element types and revisions, then copy values into firmware runtime tables. WRDS/EWRD parse SAR profiles across multiple revisions and sub-band counts. WGDS selects the highest supported geo revision, handles variable profile counts for newer revisions, and fills missing bands from 5 GHz data. PPAG handles rev 0, rev 1-4, and rev 5 sizes. DSM loading first queries the validity bitmap, then caches supported fixed-size functions into `fwrt->dsm_values` and `dsm_funcs_valid`.

State and persistence: Populates runtime caches: DSM revision/source/values, TAS selection and block list, MCC, default power limit, external clock, reduced-power flags, SAR profiles, geo profiles/revision/source, PPAG flags/chains/source, PHY filter config, UEFI GUID lock status, WBEM, and DSBR values. The data is platform firmware policy cached in driver memory.

Dependencies and integration points: Depends on Linux ACPI object APIs, Intel ACPI method names and GUID, `iwl_fw_runtime` storage, BIOS/regulatory helper routines such as `iwl_bios_get_ppag_flags()` and `iwl_bios_print_ppag()`, SAR/geo regulatory definitions, and exported-symbol consumers in MVM/MLD runtime code.

Risks: ACPI packages are externally supplied and must be type/size checked before indexing; a known issue exists in `iwl_acpi_get_pwr_limit()` where it compares an element value with `ACPI_TYPE_INTEGER` instead of checking the element type. Revision fallback must not accept a package with the wrong table revision. DSM buffer parsing pads/truncates little-endian values and can silently lose high bits. Some methods return `-ENOENT` for optional policy, while others use nonzero enabled values, so callers must distinguish absence from disabled.

Test signals: Systems with absent ACPI handles, malformed packages, each WRDS/EWRD/WGDS/PPAG revision, variable WGDS profile counts, DSM query with sparse validity bits, integer and buffer DSM returns, invalid DSM sizes, TAS enabled/disabled/blocklist limits, China-only WRDD MCC, PHY filter loading, GUID lock status, WBEM/DSBR revision mismatch, and `CONFIG_ACPI` disabled stubs from the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.h

Purpose: Defines Intel Wi-Fi ACPI method names, package sizing constants, DSM constants, feature masks, product-reset structures, and CONFIG_ACPI-dependent prototypes/stubs for firmware runtime ACPI policy loading.

Important APIs and types: Method constants include `WRDS`, `EWRD`, `WGDS`, `WRDD`, `SPLC`, `ECKV`, `PPAG`, `WTAS`, `WPFC`, `GLAI`, `WBEM`, and `DSBR`. Size macros describe SAR, geo, PPAG, TAS, PHY-filter, lock-status, WBEM, and DSBR package layouts by revision. Prototypes expose all `iwl_acpi_get_*()` readers; no-ACPI inline stubs return `-ENOENT`, default power limit zero, or WGDS `1` as appropriate.

Control flow: Header-only flow is compile-time selection between real ACPI implementations and stubs. Callers can use the same API surface regardless of kernel ACPI support.

State and persistence: No direct storage; it defines constants used to fill `struct iwl_fw_runtime` fields in `acpi.c`. Platform policy persists in BIOS/ACPI, not in this header.

Dependencies and integration points: Includes Linux ACPI, firmware regulatory/image headers, and transport declarations. It is shared by iwlwifi firmware runtime, regulatory, MVM/MLD feature setup, and platform reset/control code.

Risks: Package-size macros must match BIOS specifications and the parser's fixed indexing. The no-ACPI return conventions are part of caller behavior and inconsistent returns can change feature defaults. `struct iwl_dsm_internal_product_reset_cmd` is packed and must match DSM payload expectations.

Test signals: Compile with and without `CONFIG_ACPI`, validate all package-size macros against parser loops, exercise caller handling of no-ACPI stubs, and test DSM product-reset payload packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/alive.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/alive.h

Purpose: Defines firmware ALIVE notifications, debug pointer layouts, SKU/platform metadata, card-state flags, init-flow extension command, radio-version notification, and firmware error-recovery command ABI.

Important APIs and types: `struct iwl_alive_ntf_v3`, `iwl_alive_ntf_v7`, and `iwl_alive_ntf` represent versioned ALIVE payloads with LMAC/UMAC debug data, SKU, IMR, and platform ID. `struct iwl_lmac_alive`, `iwl_umac_alive`, and debug-address structs expose firmware error/event/log pointers. Enums define firmware type/subtype, card-state flags, extended init flags, and error-recovery flags.

Control flow: No executable flow; these structures are consumed by firmware loading and notification handlers to validate firmware state, collect debug addresses, and decide rfkill/card-state handling.

State and persistence: Header owns no state. ALIVE payload values become runtime device pointers and capability metadata in driver state.

Dependencies and integration points: Used by `commands.h` legacy `UCODE_ALIVE_NTFY`, DVM and MVM firmware startup, debug dump collection, card-state notification handling, and recovery command submission.

Risks: Versioned structs have different LMAC counts and trailing fields; handlers must use firmware API version/capability before casting. Status constants (`0xCAFE`/`0xDEAD`) and rfkill bits are firmware ABI. Debug addresses are device SRAM offsets and must not be treated as host pointers.

Test signals: Parse alive v3/v7/current notifications, dual-LMAC devices, rfkill flag handling, IMR enabled/disabled, platform ID presence, init extended cfg command submission, card-state CT-kill/rfkill flags, and error-recovery command flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/alive.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/binding.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/binding.h

Purpose: Defines firmware binding-context commands and time-quota allocation commands for associating MAC contexts with PHY contexts and scheduler airtime quotas.

Important APIs and types: `struct iwl_binding_cmd_v1` and `iwl_binding_cmd` carry binding ID/color, action, up to three MAC IDs, PHY ID, and optional LMAC ID. `IWL_BINDING_CMD_SIZE_V1` supports old firmware sizing. `struct iwl_time_quota_cmd_v1` and `iwl_time_quota_cmd` carry up to four binding quota entries, with v2 adding low-latency flags from `enum iwl_quota_low_latency`.

Control flow: No local execution. Runtime MAC/PHY context code sends add/modify/remove binding commands and then time-quota commands so firmware can schedule active roles.

State and persistence: No driver state here. Firmware stores binding and quota state until modified or removed.

Dependencies and integration points: Includes firmware file/image headers and relies on context ID/color/action definitions from `context.h`. Used by MVM context management, multi-MAC operation, CDB dual-band scheduling, and low-latency policy.

Risks: Binding table limits (`MAX_MACS_IN_BINDING`, `MAX_BINDINGS`) must match firmware. v1/v2 command size selection is required for older firmware. Quotas are absolute TU values and incorrect balancing can starve contexts.

Test signals: Add/modify/remove bindings on single and dual LMAC devices, v1/v2 command version selection, zero/auxiliary fourth quota on non-CDB, low-latency TX/RX flags, and quota saturation at `IWL_MVM_MAX_QUOTA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/binding.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/cmdhdr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/cmdhdr.h

Purpose: Defines host-command header formats, command ID packing helpers, sequence-number queue/index extraction, generic command response, and calibration PHY database payload structures.

Important APIs and types: `SEQ_TO_QUEUE()`, `QUEUE_TO_SEQ()`, `SEQ_TO_INDEX()`, and `INDEX_TO_SEQ()` encode/decode driver sequence values. `iwl_cmd_opcode()`, `iwl_cmd_groupid()`, `iwl_cmd_version()`, and `iwl_cmd_id()` pack/unpack wide command IDs. `struct iwl_cmd_header` is the short header; `struct iwl_cmd_header_wide` adds length and version. `struct iwl_calib_res_notif_phy_db`, `iwl_phy_db_cmd`, and `iwl_cmd_response` define common payloads.

Control flow: Inline helpers are used when building host commands, routing responses, and reclaiming TX frames from sequence fields.

State and persistence: Header owns no state. Sequence values carry transient TX queue/index and unsolicited notification bits across firmware responses.

Dependencies and integration points: Central to transport, DVM TX completion, firmware notification dispatch, calibration PHY database setup, and all command group APIs.

Risks: Bitfield macros assume queue IDs fit five bits and TFD indices fit eight bits. Short vs wide command headers must match firmware group/version negotiation. `SEQ_RX_FRAME` bit distinguishes unsolicited notifications and direct responses.

Test signals: Command ID round trips, queue/index sequence round trips, unsolicited notification dispatch, wide-header command submission, calibration PHY DB variable-length payloads, and generic response status parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/cmdhdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/coex.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/coex.h

Purpose: Defines Bluetooth coexistence firmware command and notification ABI, including coexistence modes, enabled modules, channel inhibition, reduced TX power, activity grading, LUT selection, and profile notifications.

Important APIs and types: `struct iwl_bt_coex_cmd`, `iwl_bt_coex_reduced_txp_update_cmd`, `iwl_bt_coex_ci_cmd`, `iwl_bt_coex_prof_old_notif`, and `iwl_bt_coex_profile_notif` are the main wire structures. Enums define LUT type, coexistence mode, module bits, BT activity grading, CI compliance, and BT coexistence subcommand IDs.

Control flow: No executable flow. Runtime coexistence code sends configuration/reduced-power/CI commands and consumes profile notifications to adapt Wi-Fi behavior under BT activity.

State and persistence: Header owns no state; firmware maintains coexistence configuration and reports current BT profile. Driver may cache interpreted activity/loss values elsewhere.

Dependencies and integration points: Used by legacy command IDs in `commands.h`, BT coexistence management in DVM/MVM, regulatory/SAR power interactions, and channel/PHY configuration.

Risks: `BITS(nb)` is a local helper name that can collide if included in broad scopes. Old and new profile notification layouts differ substantially. Reduced TX power encodes enable bit and station ID in one field. Loss arrays are band/chain indexed and depend on `COEX_NUM_BAND` and `COEX_NUM_CHAINS`.

Test signals: Enable/disable coexistence modes and modules, reduced TX power per station, CI primary/secondary bitmaps, old profile notification v4/v5 parsing, new profile loss arrays, and high BT traffic adaptation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/coex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/commands.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/commands.h

Purpose: Provides the central firmware command namespace: command groups, legacy opcodes, system subcommands, and statistics subcommands used by iwlwifi host-command dispatch.

Important APIs and types: `enum iwl_mvm_command_groups` assigns group IDs such as legacy, system, MAC config, PHY ops, datapath, scan, location, BT coexistence, regulatory/NVM, debug, and statistics. `enum iwl_legacy_cmds` maps legacy opcodes for ALIVE, scan, station/key, TX, scheduler, MAC/PHY context, time events, LED, link quality, statistics, RX, BT, D3/WoWLAN, debug, and multicast filtering. `enum iwl_system_subcmd_ids` and `iwl_statistics_subcmd_ids` define grouped newer commands.

Control flow: No executable flow; all host command construction and notification dispatch depend on these numeric IDs.

State and persistence: Header owns no state. The numeric values are persistent firmware ABI and must remain stable for supported firmware images.

Dependencies and integration points: Cross-references structures from many API headers (`alive.h`, `binding.h`, `d3.h`, `datapath.h`, `debug.h`, `filter.h`, `led.h`, scan/rx/tx/etc.). Used by transport command submission, notification wait registration, debug tooling, DVM and MVM operation modes.

Risks: Opcode reuse and version-specific payload selection are easy to mismatch. Some legacy IDs document several payload versions. `LONG_GROUP` and `IWL_ALWAYS_LONG_GROUP` interaction in command headers must be preserved. Adding commands in the wrong group can break firmware routing.

Test signals: Compile all command users, validate command IDs against firmware TLV API versions, exercise notification dispatch for legacy and grouped commands, and run firmware init/runtime flows that touch ALIVE, TX, scan, statistics, debug, D3, and datapath commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/commands.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/config.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/config.h

Purpose: Defines firmware configuration payloads for DQA enablement, TX antenna configuration, PHY calibration control, PHY-specific filter configuration, PHY configuration command versions, and DC2DC flags.

Important APIs and types: `struct iwl_dqa_enable_cmd`, `iwl_tx_ant_cfg_cmd`, `iwl_calib_ctrl`, `iwl_phy_specific_cfg`, `iwl_phy_cfg_cmd_v1`, and `iwl_phy_cfg_cmd_v3` are the main command payloads. `enum iwl_calib_cfg` enumerates calibration bitmap bits for XTAL, temperature, voltage, PAPD, TX power, DC, filters, IQ, sensitivity, chain noise, antenna coupling, DAC, ABS, and AGC.

Control flow: No local flow; callers build these structs before sending DQA, TX antenna, and PHY configuration commands.

State and persistence: No state here. Firmware persists configuration until reset or replacement command; calibration bitmaps determine firmware calibration behavior.

Dependencies and integration points: Used by firmware startup, NVM/radio configuration, ACPI WPFC filter ingestion, and command IDs in `commands.h`/datapath APIs.

Risks: Calibration bitmaps must match firmware expectations exactly. `iwl_phy_cfg_cmd_v3` extends v1 with PHY filters, so version negotiation is required. Filter chain order is LMAC1 A/B then LMAC2 A/B.

Test signals: DQA command on supported firmware, valid TX antenna masks, PHY configuration v1/v3 selection, all calibration bitmap combinations used by init/runtime firmware, ACPI WPFC filter propagation, and DC2DC flag commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/context.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/context.h

Purpose: Defines common firmware context ID/color encoding and add/modify/remove actions for PHY, MAC, binding, and related context commands.

Important APIs and types: `enum iwl_ctxt_id_and_color` defines ID and color bit positions/masks plus invalid values. `FW_CMD_ID_AND_COLOR()` packs IDs and colors. `enum iwl_ctxt_action` defines invalid, add, modify, and remove operations. `IWL_LMAC_24G_INDEX` and `IWL_LMAC_5G_INDEX` identify LMAC roles.

Control flow: Header-only packing definitions are used when constructing context-related host commands.

State and persistence: No state. Encoded values identify firmware runtime objects and are often used to prevent stale references after object recreation.

Dependencies and integration points: Consumed by binding, MAC, PHY, station, and security key context APIs across MVM/MLD and firmware context management.

Risks: ID/color packing assumes 8-bit fields. Newer firmware may use `FW_CTXT_ID_INVALID` without color, so callers must choose the invalid representation by firmware generation. Wrong action values can leak or destroy firmware contexts.

Test signals: Pack/unpack context IDs/colors, add/modify/remove lifecycle for MAC/PHY/binding contexts, invalid context handling on old and new firmware, and dual-LMAC context placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/d3.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/d3.h

Purpose: Defines D0i3/D3 manager, protocol offload, WoWLAN pattern/config/key/status, wake packet, and D3-end firmware ABI.

Important APIs and types: `struct iwl_d3_manager_config` sets sleep and wake flags. Protocol offload structs v1/v2/v3 small/large/v4 encode ARP/NS offload and IPv6 target/NS config limits. WoWLAN structs cover pattern arrays, wakeup filters/flags, config v6/current, RSC/TSC counters, TKIP MIC/P1K, KCK/KEK material v2-v4, GTK/IGTK/BIGTK status versions, MLO GTKs, info notifications v1/v3/v5/current, wake packet notifications, and `struct iwl_d3_end_notif`.

Control flow: No executable flow. Suspend/resume code fills these commands before entering WoWLAN/D3 and parses status/info notifications after wake to restore counters, keys, sequence numbers, wake reason, and wake packet data.

State and persistence: Header owns no state. Firmware maintains protocol offload, pattern, key, sequence, and wake status while host is suspended; driver imports it on resume.

Dependencies and integration points: Includes transport definitions and relies on Ethernet/IP address types, `IWL_MAX_TID_COUNT`, and command IDs in `commands.h`. It integrates with cfg80211/mac80211 WoWLAN, security key management, GTK rekey offload, ARP/NS offload, and MLO key handling.

Risks: Many versioned structs differ in station ID placement, array sizes, key-status fields, and flexible-array tails. Wake packet length can exceed stored buffer size and must be bounded. Key material and replay counters are security-sensitive. IPv6/NS offload limits differ between small and large v3 layouts. MLO key count is variable and must be checked against notification length and `WOWLAN_MAX_MLO_KEYS`.

Test signals: WoWLAN with magic/pattern/beacon/link/GTK/EAPOL/4-way/RFKILL wakes, ARP/NS offload v1-v4, pattern v1/v2 including TCP SYN wildcard types, GTK/IGTK/BIGTK status parsing across versions, MLO GTK variable arrays, wake packet truncation, D0i3 reset-required flag, and key replay-counter restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/d3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/datapath.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/datapath.h

Purpose: Defines datapath-group command IDs and payloads for MU-MIMO groups, timing measurements, channel estimation, datapath monitor notifications, thermal dual-chain requests, RLC/SAD, RX BAID sessions, scheduler queue config, and security key commands.

Important APIs and types: `enum iwl_data_path_subcmd_ids` names datapath commands/notifications. Structures include `iwl_mu_group_mgmt_cmd/notif`, `iwl_time_sync_cfg_cmd`, `iwl_synced_time_cmd/rsp`, `iwl_time_msmt_notify`, `iwl_time_msmt_cfm_notify`, `iwl_channel_estimation_cfg`, `iwl_datapath_monitor_notif`, `iwl_thermal_dual_chain_request`, `iwl_rlc_config_cmd`, `iwl_rx_baid_cfg_cmd/rsp`, `iwl_scd_queue_cfg_cmd`, and `iwl_sec_key_cmd`.

Control flow: No executable flow. Runtime code sends datapath commands to configure receive/transmit behavior and parses notifications for timing, monitor, thermal, BA, and power-management events.

State and persistence: Firmware stores MU group membership, RLC/SAD settings, BAID sessions, scheduler queues, and security keys until modified or reset. Driver mirrors relevant session/key state outside this header.

Dependencies and integration points: Used by MVM/MLD datapath, station security, block-ack setup, queue allocation, timing measurement userspace reporting, channel estimation collection, and command group routing.

Risks: Union fields in BAID, SCD queue, and security key commands must match the selected action/operation. Security key flags combine cipher, TX suppression, key size, MFP, multicast, and SPP A-MSDU semantics in one byte. Timing notifications contain large vendor-specific variable data. BAID limits differ old/current. Scheduler queue DMA addresses must be valid IOVAs.

Test signals: MU group update/notification, TM/FTM and PTM timestamp commands, channel-estimation filters by timer/count/rate/frame type, RLC/SAD configurations, thermal dual-chain SMPS requests, BAID add/modify/remove including old remove layout, scheduler queue add/modify/remove, and security key add/modify/remove for WEP/CCMP/TKIP/GCMP/MFP/multicast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/datapath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dbg-tlv.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dbg-tlv.h

Purpose: Defines firmware INI debug TLV ABI for debug regions, allocations, triggers, host-command injections, register/memory configuration sets, time points, policies, and dump sizing.

Important APIs and types: Common `iwl_fw_ini_header` prefixes TLVs. Region definitions include device address, address ranges, FIFOs, error tables, special memory, internal buffers, and the generic `iwl_fw_ini_region_tlv`. Other TLVs include debug info, allocation, trigger, host command, and config set. Enums define config set types, allocation IDs, buffer locations, region types/subtypes, time points, trigger apply policy, reset policy, dump policy, and dump type.

Control flow: No executable flow. Firmware debug TLV parsing code consumes these layouts to allocate buffers, configure debug registers, arm triggers at time points, and collect selected regions when triggers fire.

State and persistence: Header owns no state. Parsed TLVs drive runtime debug configuration and may allocate DRAM/SMEM/NPK buffers until firmware reset or debug teardown.

Dependencies and integration points: Included by `debug.h`, firmware TLV file parsing, debug dump collection, device-memory/register accessors, and error/assert handling.

Risks: Flexible array members require strict length validation. `regions_mask` supports only up to 64 region IDs. Time-point and policy bits drive reset and dump behavior, so incorrect bits can cause repeated dumps or firmware reloads. Some enum names contain historical typos (`IWL_FW_IWL_DEBUG_*`) that are ABI names and should not be casually renamed.

Test signals: Parse each TLV type, reject overlong region IDs/names/configs, allocate DRAM fragments by allocation ID/location, trigger on firmware assert/hardware error/host time points/D3 events, collect each region type, honor dump size policies, and send dump-complete commands when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dbg-tlv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/debug.h

Purpose: Defines firmware debug command IDs and payloads for memory access, shared-memory configuration, MFUART notifications, trace markers, DBGC suspend/resume and buffer allocation, DRAM fragment info, host event config, dump completion, TAS status, and debug token configuration.

Important APIs and types: `enum iwl_debug_cmds` names debug group commands. `struct iwl_error_resp` reports firmware command errors. Shared-memory layouts v2/current expose TX/RX FIFO and buffer addresses. `iwl_mfuart_load_notif`, `iwl_mfu_assert_dump_notif`, marker command/response structs, `iwl_dbg_mem_access_cmd/rsp`, `iwl_buf_alloc_cmd`, `iwl_dram_info`, `iwl_dbg_host_event_cfg_cmd`, `iwl_dbg_dump_complete_cmd`, `iwl_tas_status_resp`, and `iwl_fw_dbg_config_cmd` are the key payloads.

Control flow: No local execution. Debug/runtime code sends memory access, marker, buffer allocation, host event, dump-complete, TAS, and debug-config commands and parses firmware notifications/responses.

State and persistence: Header owns no state. Firmware and driver maintain debug buffer allocations, shared memory addresses, host event settings, TAS status, and firmware debug token configuration at runtime.

Dependencies and integration points: Includes `dbg-tlv.h`; command IDs are referenced from `commands.h` debug group and legacy IDs. Integrates with debugfs, firmware dump collection, transport memory reads/writes, TAS ACPI/DHC policy, and firmware assert handling.

Risks: Memory access commands can be locked/hidden/length-rejected and must not expose unsafe memory. Shared-memory struct versions depend on firmware capability bits. Buffer allocation has a fixed fragment maximum. MFUART dump notifications are chunked and length-sensitive. TAS status fields are compact and versioned. Debug token command can alter firmware assert behavior.

Test signals: LMAC/UMAC read/write success and failure statuses, shared memory cfg v2/current parsing, MFUART load and assert chunk assembly, marker timestamp response, DBGC suspend/resume, buffer allocation at max fragment count, dump-complete command, TAS status across bands/LMACs, and debug token enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dhc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dhc.h

Purpose: Defines Debug Host Command table selection, command/response formats, TAS status response payload, and integration commands such as TWT operation triggering.

Important APIs and types: `enum iwl_dhc_table_id` selects tools or integration tables. `DHC_TARGET_UMAC` and `DHC_TABLE_MASK_POS` define descriptor bits. `struct iwl_dhc_cmd` wraps variable data with length and index/mask descriptor. `struct iwl_dhc_payload_hdr`, `iwl_dhc_tas_status_per_radio`, `iwl_dhc_tas_status_resp`, `iwl_dhc_cmd_resp_v1`, `iwl_dhc_cmd_resp`, and `iwl_dhc_twt_operation` define response and payload shapes. Enums define UMAC tools/integration entries and TWT operation types.

Control flow: No executable flow. Debug/integration code builds a descriptor identifying table, target, LMAC/UMAC, and entry, sends `DEBUG_HOST_COMMAND`, then parses status plus optional descriptor and payload.

State and persistence: Header owns no state. DHC operations query or alter firmware runtime debug/integration state, such as TAS reporting or TWT negotiation.

Dependencies and integration points: Uses BIOS/TAS types such as `bios_value_u32` and `IWL_WTAS_BLACK_LIST_MAX`, and TAS enums from debug APIs. TWT operation payloads integrate with MAC/TWT management.

Risks: Descriptor bit packing is dense; mixing table ID, target, LMAC selector, and entry index incorrectly sends the wrong DHC operation. v1 and v2/v3 responses differ by descriptor field. Variable `data[]` length is in DWORDs and must match payload sizes. TWT fields are protocol-sensitive and many one-byte booleans are not bitfields.

Test signals: UMAC tools TAS status query, response v1/v2 parsing, invalid descriptor/status handling, integration TLC debug config, all TWT operation enum values, UMAC vs LMAC target bits, and payload length validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/dhc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/filter.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/filter.h

Purpose: Defines the multicast filtering firmware command payload.

Important APIs and types: `MAX_PORT_ID_NUM` and `MAX_MCAST_FILTERING_ADDRESSES` bound firmware multicast address indexing. `struct iwl_mcast_filter_cmd` carries `filter_own`, `port_id`, address count, `pass_all`, current BSSID, padding, and flexible multicast address list.

Control flow: No executable flow. Runtime multicast-filter code builds this variable-length command when multicast lists or pass-all policy changes.

State and persistence: Header owns no state. Firmware stores the multicast filter table per port until replaced or reset.

Dependencies and integration points: Includes `fw/api/mac.h` and is referenced by `MCAST_FILTER_CMD` in `commands.h`. Integrates with mac80211 multicast filter updates, association state, and firmware RX filtering.

Risks: `addr_list[]` must be DWORD-aligned as documented, and `count` must not exceed 256. `port_id` is a firmware index rather than a conventional interface ID. `pass_all` changes receive behavior and can mask address-list bugs.

Test signals: Empty filter, pass-all mode, filter-own enabled, maximum address count, multiple port IDs, BSSID changes on reassociation, and command size/alignment validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/filter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/led.h

Purpose: Defines the firmware LED switching command payload.

Important APIs and types: `struct iwl_led_cmd` contains one little-endian `status` field indicating LED on/off state for `LEDS_CMD`.

Control flow: No executable flow. LED control code sends this command when the driver wants firmware to update LED state.

State and persistence: Header owns no state. Firmware applies LED state until the next command, device reset, or platform LED policy override.

Dependencies and integration points: Used by the legacy `LEDS_CMD` command ID and DVM/MVM LED handling paths.

Risks: The command is intentionally tiny; incorrect endian conversion or command version selection is the main hazard. Platform or rfkill LED policy can make expected visual state differ from firmware command state.

Test signals: LED on/off command submission, endian correctness, firmware command version compatibility, rfkill/suspend interactions, and absence of LED hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/fw/api/led.h -->
