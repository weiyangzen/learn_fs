# subset-b-004918 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.h

## Purpose
Defines the ACPI-facing data contracts for the Realtek `rtw89` wireless driver. The header describes DSM function IDs, regulatory and 6 GHz policy payloads, antenna gain and SAR result layouts, vendor ACPI method names, SAR table recognition metadata, geo-SAR table formats, and the public ACPI evaluator entry points used by the rest of the driver.

## Important APIs, Types, and Functions
Key types are `struct rtw89_acpi_data`, `struct rtw89_acpi_dsm_result`, `struct rtw89_acpi_rtag_result`, `struct rtw89_acpi_sar_recognition`, `struct rtw89_acpi_geo_sar_handler`, and the packed policy/SAR records such as `rtw89_acpi_policy_6ghz`, `rtw89_acpi_policy_6ghz_sp`, `rtw89_acpi_policy_6ghz_vlp`, `rtw89_acpi_policy_tas`, `rtw89_acpi_policy_reg_rules`, `rtw89_acpi_static_sar_hdr`, and `rtw89_acpi_dynamic_sar_hdr`. Important enums include DSM function selectors for 6 GHz disable/blocking, TAS, U-NII-4, regulatory rules, VLP, and standard-power policy, plus HP/RT SAR customer IDs and legacy versus 6 GHz-aware SAR revisions. Public functions declared here are `rtw89_acpi_sar_get_subband`, `rtw89_acpi_sar_subband_to_band`, `rtw89_acpi_evaluate_dsm`, `rtw89_acpi_evaluate_rtag`, `rtw89_acpi_evaluate_sar`, and `rtw89_acpi_evaluate_dynamic_sar_indicator`.

## Control Flow
This header has no executable flow itself. It defines the payloads consumed by ACPI implementation code: callers evaluate DSM functions into `rtw89_acpi_dsm_result`, evaluate RTAG antenna gain into `rtw89_acpi_rtag_result`, and evaluate WRDS/RWRD/RWSI/RWGS SAR methods into `struct rtw89_sar_cfg_acpi`. Recognition records bind a customer ID, revision, RF-path-to-antenna mapping, normalization callback, optional geo-SAR handler, and load callback so the implementation can parse different vendor table variants through one dispatch path.

## State and Persistence Behavior
All persistent state modeled here comes from firmware/BIOS ACPI tables and is copied into runtime `rtw89` SAR, TAS, regulation, and antenna-gain structures. Flexible arrays use `__counted_by` for ACPI buffers and policy country lists, while `__packed` keeps ACPI wire layout stable. `rtw89_acpi_dsm_result` holds either a scalar byte or allocated policy pointers; its comment makes caller ownership explicit for dynamically returned policy data.

## Dependencies and Integration Points
The header includes `core.h` for central driver types and constants such as SAR subband counts, RF paths, regulation domains, and antenna-gain dimensions. It integrates with the ACPI implementation file, SAR power limit code, TAS logic, regulatory/country handling, chip capability checks, and platform BIOS methods named `WRDS`, `RWRD`, `RWSI`, and `RWGS`.

## Risks
The packed structs are firmware/BIOS ABI. Reordering fields, changing sizes, or changing counted array semantics can break parsing of vendor ACPI payloads. The `u8` size guards in `RTW89_ACPI_SAR_SIZE_OF()` and `RTW89_ACPI_GEO_SAR_SIZE_OF()` imply table sizes must stay within ACPI format limits. Ownership of allocated policy pointers is easy to miss. Country policy logic is compact and bitmask-driven, so adding countries or policy revisions requires matching parser and regulation behavior.

## Test Signals
Useful signals include boot on systems with and without each DSM function, 6 GHz enable/disable and VLP/SP policy changes, TAS enablement by country, U-NII-4 and UK regulatory rule overrides, RTAG antenna gain parsing, WRDS/RWRD static and dynamic SAR parsing for HP and RT table revisions, RWSI dynamic SAR indicator changes, RWGS geo-SAR region selection, malformed/short ACPI buffers, and suspend/resume with dynamic SAR reevaluation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.c

## Purpose
Implements `rtw89` CAM management for address CAM, BSSID CAM, and security CAM entries. It allocates scarce firmware CAM slots, installs and removes hardware encryption keys, attaches security CAM entries to per-link/per-station address CAM records, and packs address/BSSID/security state into H2C command formats consumed by firmware.

## Important APIs, Types, and Functions
Public entry points include `rtw89_cam_init`, `rtw89_cam_deinit`, `rtw89_cam_init_addr_cam`, `rtw89_cam_deinit_addr_cam`, `rtw89_cam_init_bssid_cam`, `rtw89_cam_deinit_bssid_cam`, `rtw89_cam_bssid_changed`, `rtw89_cam_sec_key_add`, `rtw89_cam_sec_key_del`, `rtw89_cam_reset_keys`, `rtw89_cam_attach_link_sec_cam`, `rtw89_cam_fill_addr_cam_info`, `rtw89_cam_fill_bssid_cam_info`, and `rtw89_cam_fill_dctl_sec_cam_info_v1/v2/v3`. Internal helpers allocate security CAM slots, choose address CAM security entry positions, send H2C security key commands, and hash address bytes for firmware matching. The key state is held in `rtwdev->cam_info`, `struct rtw89_sec_cam_entry`, `struct rtw89_addr_cam_entry`, and `struct rtw89_bssid_cam_entry`.

## Control Flow
Security key addition starts in the mac80211 `set_key` path and enters `rtw89_cam_sec_key_add()`, which maps WLAN cipher suites to Realtek hardware key types, sets mac80211 offload flags such as software management TX or generated IV where needed, and calls `rtw89_cam_sec_key_install()`. Installation reserves one security CAM slot or two adjacent slots for 256-bit keys, allocates `struct rtw89_sec_cam_entry`, copies key bytes, sends one or two H2C security key updates, then attaches the security CAM index into the relevant address CAM. MLD pairwise keys with negative `key->link_id` are attached to every station link and tracked in `rtwsta->pairwise_sec_cam_map` so later link association can reapply the key. Deletion detaches from all relevant links, optionally informs firmware by updating DCTL and role CAM, clears CAM bitmaps, and frees the key entry.

Address/BSSID initialization is separate: `rtw89_cam_init()` allocates a BSSID CAM slot for the current BSSID, allocates an address CAM slot, sets default matching/security fields, and associates address CAM with BSSID CAM. Firmware packing functions later write little-endian bitfields for source/target MAC addresses, BSSID, AID, WoW flags, BSS color, masks, port/TSF sync, target indication, security key IDs, and security CAM indexes. DCTL security command variants v1, v2, and v3 differ in field widths, MLD fields, and security entry encoding.

## State and Persistence Behavior
CAM allocation persists in `rtwdev->cam_info` bitmaps: `addr_cam_map`, `bssid_cam_map`, and `sec_cam_map`; the `sec_entries[]` array owns allocated security key records. Per-link and per-station address/BSSID CAM structs persist indexes, lengths, validity, masks, BSSID mapping, security entry mode, key IDs, and security CAM indexes. Key deletion clears the valid reference from address CAM before freeing the security entry; firmware does not receive a separate security CAM invalidation because clearing the address CAM valid bits disables use. WoW PTK IV and key index state from `rtwdev->wow` is optionally inserted into DCTL security updates.

## Dependencies and Integration Points
The file depends on `cam.h`, `debug.h`, `fw.h`, `mac.h`, and `ps.h`, plus mac80211 key/vif/sta structures and RCU link dereference helpers. It integrates with `mac80211.c` key callbacks, `fw.c` H2C CAM builders, `mac.c` role lifecycle, SER recovery, WoW reset, MLO link association, chip-specific H2C DCTL implementations, and firmware commands in `rtw89_fw_h2c_cam()` and `rtw89_chip_h2c_dctl_sec_cam()`.

## Risks
CAM slots are scarce and shared across links, stations, and key types; leaks or missed bitmap clears can exhaust hardware resources. 256-bit ciphers require adjacent security CAM entries, so allocation must remain contiguous. Address CAM security entry mode dictates where unicast, group, and BIP keys may land; wrong placement breaks RX/TX decryption. MLD key handling splits per-link group keys from cross-link pairwise keys and can fail if links are missing. The H2C layouts are versioned and bitfield-sensitive; changing masks, field widths, or endian encoding can silently misprogram firmware. Error paths after sending a key but before attaching it leave firmware with a key that is no longer referenced locally, which is acceptable only because address CAM validity gates use.

## Test Signals
Exercise WEP40/WEP104, TKIP, CCMP128/256, GCMP128/256, and AES-CMAC keys; pairwise and group keys; BIP keys; MLD pairwise keys applied before and after link association; MLO group key rejection when `hw_mlo_bmc_crypto` is absent; key deletion with TX queue flushing; WoW PTK IV DCTL updates; address/BSSID CAM exhaustion; SER recovery and `rtw89_cam_reset_keys()`; firmware H2C failures; BSSID changes; nontransmitted BSSID mask selection; and v1/v2/v3 DCTL command generation on chips with different CAM versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.h

## Purpose
Defines the firmware command layouts, bit masks, constants, and exported function prototypes for `rtw89` CAM programming. It is the contract between CAM implementation code, firmware H2C builders, chip-specific DCTL paths, and mac80211-facing key/address management.

## Important APIs, Types, and Functions
The header defines `RTW89_SEC_CAM_LEN`, BSSID match masks, packed address CAM H2C structs `rtw89_h2c_addr_cam_v0` and `rtw89_h2c_addr_cam`, and packed DCTL update structs `rtw89_h2c_dctlinfo_ud_v1`, `rtw89_h2c_dctlinfo_ud_v2`, and `rtw89_h2c_dctlinfo_ud_v3`. Most of the file is field-mask definitions for address CAM words, BSSID CAM words, and DCTL words, including MAC ID, port, TSF sync, target indication, AID, WoW, WAPI, security entry mode, key IDs, security entry validity, MLD address/BSSID fields, VLAN fields, NAT25, and version-specific security entry widths. It declares all public CAM lifecycle, key, and H2C packing functions implemented in `cam.c`.

## Control Flow
The header has no runtime control flow, but its layouts drive firmware command construction. `fw.c` and chip hooks allocate command buffers and call `rtw89_cam_fill_addr_cam_info()`, `rtw89_cam_fill_bssid_cam_info()`, or the DCTL v1/v2/v3 fillers to populate these bitfields. `mac80211.c`, `mac.c`, SER, and WoW code call the lifecycle and key APIs declared here to keep firmware CAM state aligned with vif/link/station/key state.

## State and Persistence Behavior
The structs in this header are packed command payloads rather than long-lived state. Persistent CAM state lives in `core.h` structures referenced by the APIs, especially `rtwdev->cam_info`, per-link address/BSSID CAM entries, and security CAM entries. The masks encode the persistent state into firmware-visible little-endian words and must match firmware interpretation for each CAM/DCTL version.

## Dependencies and Integration Points
Includes `core.h` for driver-private types and constants. Integrates directly with `cam.c`, `fw.c`, chip-specific firmware command code, mac80211 key callbacks, MLO address handling, WoW PTK replay/IV restoration, and firmware role updates. The v2/v3 DCTL structs add MLD fields, so this header is also part of the driver's Wi-Fi 7/MLO firmware ABI.

## Risks
This is an ABI-sensitive header. Field masks, word numbering, packed layout, and version-specific widths must remain synchronized with firmware. Several masks differ subtly between v1, v2, and v3, especially MAC ID size, security entry indexing, and MLD address placement. A wrong mask may compile cleanly but corrupt unrelated firmware fields. Adding a cipher or changing `RTW89_SEC_CAM_LEN` requires coordinated changes in key installation and firmware command builders.

## Test Signals
Compile all chip variants using address CAM and DCTL v1/v2/v3. Validate H2C command dumps for station, AP, P2P, WoW, MLD, non-MLD, group and pairwise keys, BIP, and 256-bit ciphers. Runtime signals include successful association, encrypted data and management frames, MLD link setup, WoW resume, BSSID color/mask handling, and absence of firmware CAM update errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/cam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.c

## Purpose
Implements channel construction, channel-context bookkeeping, multi-role entity mode selection, remain-on-channel coordination, MLO DBCC selection, MCC/MRC scheduling, and mac80211 channel-context operation handlers for the `rtw89` driver. It is the central runtime coordinator for switching between ordinary single-channel operation, single-role multi-link operation, and two-role multi-channel concurrency.

## Important APIs, Types, and Functions
Public functions include `rtw89_chan_create`, `rtw89_assign_entity_chan`, `rtw89_iterate_entity_chan`, `rtw89_config_entity_chandef`, `rtw89_config_roc_chandef`, `rtw89_entity_init`, `rtw89_entity_recalc`, `rtw89_entity_check_hw`, `rtw89_entity_force_hw`, `__rtw89_mgnt_chan_get`, `rtw89_chanctx_work`, `rtw89_queue_chanctx_change`, `rtw89_queue_chanctx_work`, `rtw89_query_mr_chanctx_info`, `rtw89_chanctx_track`, `rtw89_chanctx_pause`, `rtw89_chanctx_proceed`, `rtw89_mcc_get_links`, `rtw89_mcc_prepare_done_work`, `rtw89_mcc_gc_detect_beacon_work`, `rtw89_mcc_detect_go_bcn`, and the `rtw89_chanctx_ops_*` mac80211 wrappers. Important internal areas are channel parameter derivation, entity management table normalization, MCC role filling, beacon offset and TSF calculations, strict/anchor/loose MCC pattern calculation, Bluetooth duration handling, firmware MCC/MRC start/update/stop commands, NoA updates, beacon-loss detection, and chanctx swapping.

## Control Flow
Channel creation converts center/primary channel, band, and bandwidth into frequency, subband, TX compensation band, primary channel index, and primary subband index. mac80211 channel-context callbacks add/remove/change chanctx records, assign/unassign links, and reassign links during context switches. Assignment updates per-link `chanctx_idx`, increments refcounts, aborts scans, tracks active roles, optionally swaps the first active chanctx down to `RTW89_CHANCTX_0`, calls `rtw89_set_channel()`, and resets TAS.

`rtw89_entity_recalc()` computes active chanctx and active role weights. Zero or one active chanctx, or one active role with multiple links, becomes `RTW89_ENTITY_MODE_SCC_OR_SMLD`; two active roles become `RTW89_ENTITY_MODE_MCC_PREPARE` unless already in MCC; unsupported counts return `UNHANDLED`. Recalc also derives `struct rtw89_chan` from each chandef, updates management role tables, normalizes the designated link to chanctx 0 for legacy behavior, and selects MLO DBCC mode on BE chips.

MCC starts through delayed `rtw89_chanctx_work()`: MCC prepare switches entity mode to MCC, calls `rtw89_set_channel()`, fills two MCC roles from active roles, selects GO/STA or GC/STA mode, computes beacon offset from firmware TSF reports, chooses durations and Bluetooth treatment, calculates an MCC pattern, computes start TSF, sends MCC or BE-generation MRC firmware commands, updates beacon filtering and P2P NoA, suspends DIG, and stops queues until the prepare delay completes. MCC updates recalculate pattern/duration/sync on beacon offset, P2P PS, BT slot, remote station, or TSF32 changes. MCC stop deletes firmware schedules, clears NoA, resumes DIG, wakes queues, and is used for unassign, scan/ROC pauses, and beacon-loss detection.

## State and Persistence Behavior
Persistent runtime state lives in `rtwdev->hal`: `entity_map`, `changes`, `entity_active[]`, `entity_mode`, `entity_pause`, `entity_force_hw`, `roc_chanctx_idx`, `roc_chandef`, `chanctx[]`, and `entity_mgnt` active-role tables. Per-mac80211 chanctx private state is `struct rtw89_chanctx_cfg` with index and refcount. MCC state persists in `rtwdev->mcc`: group number, mode, reference and auxiliary roles, BT role, computed pattern, sync settings, start TSFs, interval, and beacon offset. Per-link state tracks `chanctx_assigned`, `chanctx_idx`, sync beacon TSF, last sync beacon TSF, and beacon detection counters. Delayed work items persist queued channel/MCC changes and prepare completion.

## Dependencies and Integration Points
This file depends on `chan.h`, `coex.h`, `debug.h`, `fw.h`, `mac.h`, `phy.h`, `ps.h`, `sar.h`, and `util.h`. It integrates with mac80211 channel-context callbacks in `mac80211.c`, core channel setting and tracking, hardware scan abort, power-save exit, firmware MCC/MRC H2C commands, BT coexistence duration queries, P2P NoA helpers, beacon filter updates, DIG suspend/resume, SAR/TAS handling, chip-specific channel listeners, RF calibration paths using management channel lookup, and connection-loss reporting.

## Risks
The mode machine is timing-sensitive. Wrong active-role counts, refcounts, chanctx swaps, or pause/proceed ordering can leave firmware and mac80211 disagreeing about the active channel. MCC/MRC pattern math mixes TU and microseconds, signed offsets, beacon intervals, NoA limits, and BT slots; mistakes can miss beacons, starve a role, or break P2P power-save behavior. BE chips use MRC firmware paths while older chips use MCC paths, so command parity matters. Workqueue delays, scan aborts, ROC pause, GC beacon-loss recovery, and unassign paths all stop or restart MCC and can race if not under the wiphy lock. The management channel getter falls back to chanctx 0 when no table entry exists, which preserves legacy behavior but can hide missing role table updates.

## Test Signals
Useful validation includes single STA/AP operation, MLD single-role multi-link operation, two-role MCC with GO+STA and GC+STA, BE MRC scheduling, 2 GHz plus BT coexistence, both roles on 2 GHz, different-band roles, P2P NoA generation and removal, beacon filter toggles, beacon offset drift updates, remote station bitmap updates for GO, GC beacon-loss detection and connection loss, hardware scan and ROC pause/proceed, chanctx add/remove/change/switch callbacks, width and puncturing changes, SER recovery, suspend/resume around MCC, queue stop/wake behavior, DIG suspend/resume, and debug traces for firmware H2C failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.h

## Purpose
Declares the channel-context, multi-role, pause/proceed, and MCC public interface for `rtw89`. It also centralizes MCC timing constants, role classification enums, and small entity-mode accessors used across core, firmware, PHY, SAR, coexistence, RFK, and mac80211 integration code.

## Important APIs, Types, and Functions
The header defines MCC timing constants such as prepare delay, MCC work delay, trigger times, early beacon margins, minimum role durations, switch-channel time, probe limits, group rotation, null-data lead time, and courtesy slot defaults. Multi-role classification types are `enum rtw89_mr_wtype`, `enum rtw89_mr_wmode`, and `enum rtw89_mr_ctxtype`, returned in `struct rtw89_mr_chanctx_info`. Pause and callback parameters are `struct rtw89_chanctx_pause_parm` and `struct rtw89_chanctx_cb_parm`; `struct rtw89_entity_weight` summarizes recalculation inputs; `struct rtw89_mcc_links_info` exposes MCC role links. Inline helpers read and write `hal->entity_active[]` and `hal->entity_mode` with `READ_ONCE`/`WRITE_ONCE`. Function declarations cover channel creation, entity assignment/iteration, chandef and ROC configuration, entity recalc, channel work queueing, management channel lookup, MCC helpers, and mac80211 chanctx operation wrappers.

## Control Flow
The header defines the callable stages implemented in `chan.c`: initialize entity state, add/configure chanctx definitions, assign links, recalculate entity mode, queue delayed channel-context work, pause MCC for scans/ROC/beacon recovery, proceed and optionally invoke a callback after `rtw89_set_channel()`, query multi-role topology, track MCC drift, and add/remove/change/reassign mac80211 chanctxs. The `RTW89_MCC_REQ_COURTESY()` macro is used during MCC pattern assignment to decide when firmware courtesy slots are required because a role has too little time before or after beacon reception.

## State and Persistence Behavior
No state is stored in the header, but it exposes accessors and interfaces for persistent `rtwdev->hal` and `rtwdev->mcc` state. The constants here shape persisted scheduling decisions such as role duration floors, beacon detection retries, group rotation, queue dwell times, and courtesy behavior. Inline state accessors deliberately use one-copy atomic reads/writes because entity mode and active flags are consulted from multiple paths.

## Dependencies and Integration Points
Includes `core.h` for all central driver types. Consumers include mac80211 callback wrappers, core channel setup, firmware C2H/H2C paths, PHY/RFK channel users, coexistence, SAR channel-context listeners, power-save code, hardware scan/ROC paths, and chip-specific channel listener tables. The exported `rtw89_mgnt_chan_get()` macro records the caller function name for debug fallback diagnostics.

## Risks
Timing constants are policy, not just documentation. Changing minimum durations, trigger times, or work delays can destabilize MCC beacon reception, queue wake timing, P2P NoA alignment, and BT coexistence. Role classification enums must stay aligned with diagnostic and firmware consumers. The pause/proceed callback contract is subtle: callbacks run after channel programming and before restarting entity scheduling when paused. Management channel fallback can hide invalid link indexes unless callers use the `_or_null` variant.

## Test Signals
Compile coverage across all rtw89 chips, channel-context add/remove/assign/reassign paths, MCC start/update/stop timing, hardware scan and ROC pause/proceed, multi-role classification queries for non-MLD and MLD topologies, BE MRC versus legacy MCC operation, BT coexistence slot changes, GC beacon-loss retries, and SAR/RFK listeners that consume channel-context state are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/chan.h -->
