# subset-b-004761 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.c

## Purpose

This file implements the ath6kl host-side Wireless Module Interface control plane. It translates cfg80211/mac80211 driver actions into WMI command sk_buffs for firmware, parses WMI events returned by firmware, and maintains the small amount of host state needed to sequence commands, QoS streams, power management, management TX status, scan results, and virtual-interface event routing.

## Important APIs, types, and functions

- `ath6kl_wmi_cmd_send()` is the common command transport wrapper. It validates the interface index, optionally creates sync points, pushes `struct wmi_cmd_hdr`, handles `WMI_OPT_TX_FRAME_CMDID` as data-path traffic on the BE endpoint, and sends through `ath6kl_control_tx()`.
- `ath6kl_wmi_control_rx()` and `ath6kl_wmi_proc_events()` are the central receive path for firmware control packets. They parse `struct wmi_cmd_hdr`, trace/debug the raw event, dispatch global events directly, and route interface-specific events through `ath6kl_wmi_proc_events_vif()`.
- Packet format helpers include `ath6kl_wmi_dix_2_dot3()`, `ath6kl_wmi_dot3_2_dix()`, `ath6kl_wmi_dot11_hdr_remove()`, and `ath6kl_wmi_data_hdr_add()`. They prepend or remove WMI, LLC/SNAP, Ethernet, and 802.11 framing.
- Connection, roaming, scan, and security command builders include `ath6kl_wmi_connect_cmd()`, `ath6kl_wmi_reconnect_cmd()`, `ath6kl_wmi_disconnect_cmd()`, `ath6kl_wmi_beginscan_cmd()`, `ath6kl_wmi_scanparams_cmd()`, `ath6kl_wmi_addkey_cmd()`, `ath6kl_wmi_deletekey_cmd()`, and `ath6kl_wmi_setpmkid_cmd()`.
- QoS and stream management flows through `ath6kl_wmi_implicit_create_pstream()`, `ath6kl_wmi_create_pstream_cmd()`, `ath6kl_wmi_delete_pstream_cmd()`, `ath6kl_wmi_pstream_timeout_event_rx()`, and `ath6kl_wmi_sync_point()`.
- P2P/cfg80211 management operations are handled by remain-on-channel, action/mgmt TX, probe-response, probe-request-report, and P2P-info command/event helpers.
- Lifecycle APIs are `ath6kl_wmi_init()`, `ath6kl_wmi_reset()`, and `ath6kl_wmi_shutdown()`.

## Control flow

Outbound commands allocate a zeroed payload with `ath6kl_wmi_get_new_buf()`, fill packed WMI structures with little-endian conversions, then call `ath6kl_wmi_cmd_send()`. Commands with ordering requirements request a sync before or after the command. Sync builds a control `WMI_SYNCHRONIZE_CMDID` bitmap for active AC endpoints and sends empty `SYNC_MSGTYPE` data packets on each active data endpoint.

Inbound firmware events arrive as sk_buffs on the WMI control endpoint. `ath6kl_wmi_control_rx()` rejects undersized packets, emits a trace event, and hands ownership to `ath6kl_wmi_proc_events()`, which frees the skb after dispatch. Global replies/events such as ready, bitrate, regdomain, pstream timeout, RSSI/SNR threshold, WMIX extension events, testmode, and PMKID list are handled immediately. Unknown global IDs are attempted as vif-specific events by looking up `fw_vif_idx`; vif events then call cfg80211/mac80211-facing ath6kl callbacks such as connect, disconnect, scan-complete, BSS inform, MIC failure, CAC, PS-Poll, DTIM expiry, ADDBA/DELBA, ROC, TX status, RX probe request/action, and TX-error notification.

## State and persistence behavior

The state is in-memory only inside `struct wmi`. `fat_pipe_exist` and `stream_exist_for_ac[]` track active QoS pstreams and are protected by `wmi->lock`. `pwr_mode`, `saved_pwr_mode`, `is_wmm_enabled`, `traffic_class`, and `is_probe_ssid` reflect current host/firmware operating state. `last_mgmt_tx_frame` holds a copied management frame until a matching TX status event reports it to cfg80211, then it is freed. Reset clears pstream state; shutdown frees the pending management frame and the `wmi` object. No durable on-disk state exists.

## Dependencies and integration points

This file depends on ath6kl core callbacks, HTC endpoint routing, cfg80211 notification APIs, kernel sk_buff helpers, regulatory-domain tables from `../regd*.h`, aggregation callbacks, debug/testmode/recovery hooks, and firmware capability bits. It is the boundary between Linux network configuration and ath6kl firmware WMI ABI, so field layout, endianness, flexible-array sizing, and command IDs must match `wmi.h` and target firmware.

## Risks

Risk centers on malformed firmware lengths, flexible array bounds, interface-index routing, skb headroom, and lifetime of asynchronous management TX state. Many handlers check minimum struct sizes, but variable-length structures require exact `struct_size()` and pointer-bound checks. QoS pstream state has comments noting questionable lock granularity and a stale workaround around `traffic_class == 100`. `ath6kl_get_vif_by_index()` has a FIXME about locking, making vif lifetime assumptions important. Firmware command errors are logged as programming errors but not recovered locally.

## Test signals

Useful validation signals include WMI trace/debug dumps, connect/disconnect/scan success through cfg80211, BSS table updates from beacon/probe events, remain-on-channel readiness and expiry callbacks, management TX status completion, TXE CQM notification, scheduled-scan timer behavior, pstream activity indications per AC, suspend/WOW transitions, and negative tests for invalid channel lists, key lengths, multicast filters, PMKID payload lengths, unsupported wait-on-mgmt-TX, invalid vif indices, and truncated event payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.h

## Purpose

This header defines the ath6kl WMI ABI shared by the host driver and firmware-facing code. It contains protocol versions, command and event IDs, packed command/event payload structures, bitfield helpers for WMI data and command headers, rate/security/scan/power/QoS/P2P/AP-mode enums, and function prototypes implemented by `wmi.c`.

## Important APIs, types, and constants

- `struct wmi` is the host control-plane state object. It stores the parent device, control endpoint, power mode, WMM/pstream bitmaps, signal-quality thresholds, probe/WMM flags, and pending management TX frame copy.
- `struct wmi_data_hdr` and helpers such as `wmi_data_hdr_get_up()`, `wmi_data_hdr_get_dot11()`, `wmi_data_hdr_get_seqno()`, `wmi_data_hdr_get_meta()`, and `wmi_data_hdr_get_if_idx()` describe the data-path header that carries message type, user priority, metadata version, A-MSDU, and vif index.
- `struct wmi_cmd_hdr` plus `wmi_cmd_hdr_get_if_idx()` define the control message prefix used by `ath6kl_wmi_cmd_send()` and `ath6kl_wmi_control_rx()`.
- `enum wmi_cmd_id` and `enum wmi_event_id` enumerate a large firmware ABI, including base connection/scan/security commands, developer commands, AP/P2P/WOW/DFS/coexistence extensions, scheduled scan, and TXE notify.
- Packed payloads cover connect/reconnect, key install/delete, PMKID, scan, BSS filter, power parameters, pstreams, RSSI/SNR thresholds, target stats, roam tables, CAC, AP mode, remain-on-channel, management TX, P2P info, WMIX extension commands, and WOW filters.
- Exported prototypes expose the command builders, receive dispatcher, packet conversion helpers, rate lookup, WMI lifecycle, and vif lookup.

## Control flow encoded by the ABI

The header separates host-to-firmware commands from firmware-to-host events. Host commands are packed into `struct wmi_cmd_hdr` plus one command-specific payload and sent by `wmi.c`. Firmware events return the same header form with an event ID and a payload from the event section. Data packets use `struct wmi_data_hdr`, while out-of-band WMIX messages are nested under `WMI_EXTENSION_CMDID` or `WMI_EXTENSION_EVENTID` with `struct wmix_cmd_hdr`.

## State and persistence behavior

No persistent storage is defined. All structures are transient kernel/firmware ABI records. Because most payloads are `__packed` and include explicit endian types, the persistent contract is binary layout compatibility with firmware rather than local disk state. `struct wmi` fields are runtime state initialized in `ath6kl_wmi_init()` and reset by `ath6kl_wmi_reset()`.

## Dependencies and integration points

The header depends on Linux IEEE 802.11 definitions, HTC endpoint IDs, cfg80211/nl80211 enums visible through included headers, ath6kl crypto and HT capability types from core headers, and firmware WMI version compatibility. It is included by WMI implementation and other ath6kl modules that need command prototypes or protocol constants.

## Risks

The primary risk is ABI drift: command IDs, event IDs, enum numeric values, field ordering, packing, flexible arrays, and endian annotations must match firmware. Several comments warn that changing AP-mode constants requires rebuilding firmware and driver. Duplicate-looking prototypes and long enum ranges raise maintenance risk. `P2P_FLAG_HMODEL_REQ` shares the same value as `P2P_FLAG_MACADDR_REQ`, which may be intentional firmware behavior or a bug-prone overlap. Flexible-array payloads require callers to allocate with the exact payload length.

## Test signals

Compile-time signals include sparse/endian warnings, packed-structure layout assumptions, and all callers building against prototypes. Runtime signals include successful WMI ready/version negotiation, correct command/event dispatch IDs in debug logs, successful scan/connect/security/AP/P2P/WOW operations, and negative handling of invalid payload lengths for flexible event structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Kconfig

## Purpose

This Kconfig file defines build-time configuration for the ath9k family: core PCI/AHB mac80211 devices, USB HTC devices, shared hardware/common libraries, debugfs, bluetooth coexistence, DFS certification hooks, dynamic ACK, WOW, rfkill, channel contexts, PC-OEM support, EEPROM-less PCI loader, hardware RNG, and spectral scan support.

## Important options

- `ATH9K_HW` and `ATH9K_COMMON` are hidden tristate helper modules selected by `ATH9K` and `ATH9K_HTC`.
- `ATH9K` is the main mac80211 Atheros 802.11n driver and depends on `MAC80211` and `HAS_DMA`; it selects LEDs where available and selects the shared helper modules.
- `ATH9K_PCI` and `ATH9K_AHB` enable bus frontends for PCI/PCIe and OF-backed SoC AHB devices.
- `ATH9K_HTC` enables USB HTC devices such as AR9271 and selects shared ath9k hardware/common code.
- `ATH9K_DEBUGFS`, `ATH9K_HTC_DEBUGFS`, `ATH9K_STATION_STATISTICS`, `ATH9K_DFS_DEBUGFS`, and `ATH9K_COMMON_SPECTRAL` expose debug and spectral functionality.
- Certification/risk-sensitive options include `ATH9K_TX99` and `ATH9K_DFS_CERTIFIED`, both guarded by `CFG80211_CERTIFICATION_ONUS`.

## Control flow and integration

The file controls which objects in `Makefile` are built. User-visible options choose bus support and optional functionality; hidden helper symbols allow the Makefile to build shared modules only when a frontend needs them. Several options depend on kernel subsystems such as PCI, USB, OF, PM, RFKILL, DEBUG_FS, MAC80211_DEBUGFS, RELAY, and HW_RANDOM.

## State and persistence behavior

There is no runtime state here. Kernel `.config` selections persist across builds and determine available code paths, modules, and exported features. Defaults are conservative for testing/certification features and permissive for common hardware support such as PCI and rfkill.

## Dependencies and risks

Incorrect dependencies can produce link failures or expose code without required kernel subsystems. Regulatory-sensitive options are intentionally not default because enabling TX99 or DFS initiation on uncertified platforms can violate certification assumptions. Debugfs and station statistics increase visibility but also code size and runtime surface. `ATH9K_PCI_NO_EEPROM` is separated because it supports special EEPROM-less platforms and should not be enabled accidentally.

## Test signals

Run Kconfig dependency tests through `oldconfig`/`allmodconfig`, verify object inclusion through `make M=...`, test matrix builds for PCI-only, AHB-only, HTC-only, debugfs, WOW, HWRNG, BT coexistence, and spectral combinations, and confirm certification-gated options remain disabled unless explicitly selected with `CFG80211_CERTIFICATION_ONUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Makefile

## Purpose

This Makefile maps ath9k Kconfig symbols to kernel objects. It builds the main `ath9k` softmac module, the shared `ath9k_hw` hardware library, `ath9k_common`, the USB `ath9k_htc` module, and the optional PCI EEPROM-less loader.

## Important build targets

- `ath9k-y` contains core runtime objects such as beacon, GPIO, init, main, receive, transmit, link, antenna, and channel support.
- Conditional `ath9k-*` entries add MCI bluetooth coexistence, PCI, AHB, DFS debug/certified files, TX99, WOW, HWRNG, debugfs, and station statistics.
- `ath9k_hw-y` builds hardware support: AR9002/AR9003 hardware, PHY/MAC, calibration, EEPROM formats, ANI, PAPRD, and optional WOW/BT coexistence/PCOEM/dynamic ACK components.
- `ath9k_common-y` builds shared helper code for common init/beacon/debug/spectral functionality.
- `ath9k_htc-y` builds the USB HTC stack with host transport, HIF USB, WMI, TX/RX, main/beacon/init/GPIO, and optional debug.

## Control flow and integration

The file consumes symbols from `Kconfig` and decides object composition at build time. The generated modules are linked by Kbuild according to `obj-$(CONFIG_...)` lines. Runtime entry points in `init.c`, bus-specific files, and HTC files depend on these object lists being consistent with selected capabilities.

## State and persistence behavior

No runtime state exists. The Makefile persists build topology: changing it alters which code is present in modules and which symbols can resolve. Conditional object inclusion is the build-time equivalent of feature state.

## Dependencies and risks

The main risk is mismatch between Kconfig dependencies and object references. For example, enabling AHB requires `ahb.o` plus OF support, and BT coexistence pulls both high-level and hardware MCI/AIC pieces. Missing optional objects can produce unresolved symbols; extra objects can expose unsupported features or increase module size.

## Test signals

Build-test representative configs: `ATH9K=m` with PCI, with AHB, with both, `ATH9K_HTC=m`, debugfs/spectral combinations, WOW, BT coexistence, DYNACK, HWRNG, TX99, DFS, and `ATH9K_PCI_NO_EEPROM`. Inspect linked module contents or `modinfo` to verify expected objects are included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ahb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ahb.c

## Purpose

This file is the platform/AHB bus frontend for ath9k on OF-described Qualcomm/Atheros SoCs with integrated Wi-Fi MACs. It maps MMIO resources, obtains IRQs, allocates the mac80211 hardware object, registers the interrupt handler, and calls shared ath9k initialization with AHB-specific bus operations.

## Important APIs and functions

- `ath9k_of_match_table[]` maps compatible strings such as `qca,ar9130-wifi`, `qca,ar9330-wifi`, `qca,ar9340-wifi`, and qca9530/9550/9560 variants to ath9k device IDs.
- `ath_ahb_read_cachesize()` reports L1 cache line size in 4-byte words for bus tuning.
- `ath_ahb_eeprom_read()` always fails and logs that EEPROM data must be supplied externally.
- `ath_ahb_bus_ops` supplies `ATH_AHB`, cache-size read, and EEPROM read callbacks to shared hardware code.
- `ath_ahb_probe()` is the platform probe path; `ath_ahb_remove()` is cleanup; `ath_ahb_init()` and `ath_ahb_exit()` register and unregister the `platform_driver`.

## Control flow

Probe maps the first platform resource with `devm_platform_ioremap_resource()`, obtains IRQ 0, fills channel-context ops, allocates `struct ieee80211_hw` with private `struct ath_softc`, binds the platform device to the hw object, initializes softc fields, requests a shared IRQ using `ath_isr`, retrieves the device ID from OF match data, and calls `ath9k_init_device()`. On success it logs the hardware name, MMIO pointer, and IRQ. Error paths free the IRQ and ieee80211 hardware object in reverse order. Remove deinitializes the device, frees IRQ, and frees the hw object.

## State and persistence behavior

Runtime state is stored in `struct ath_softc` under the allocated `ieee80211_hw`. `sc->mem`, `sc->irq`, `sc->dev`, and `sc->hw` bind platform resources to shared ath9k code. There is no persistent state; calibration/EEPROM state must come from external platform data or other firmware mechanisms because direct EEPROM read is intentionally unsupported here.

## Dependencies and integration points

The file depends on Linux platform driver, OF match data, MMIO resource management, IRQ registration, mac80211 allocation, and shared ath9k APIs from `ath9k.h`. It integrates with Kconfig through `CONFIG_ATH9K_AHB` and with the main module via `ath_ahb_init()`/`ath_ahb_exit()`.

## Risks

AHB devices require correct device-tree compatible strings, resource layout, IRQ, and external calibration data. A missing or wrong match data device ID leads to incorrect hardware initialization. Since IRQ is requested before `ath9k_init_device()`, failures must reliably free the IRQ; the code does. External EEPROM provisioning is a platform integration risk, not handled locally.

## Test signals

Boot an OF platform with each compatible, verify probe logs the expected hardware name, test missing MMIO/IRQ failures, confirm interrupt handling and remove cleanup, validate external calibration provisioning, and run mac80211 association/traffic tests on AHB SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ahb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.c

## Purpose

This file implements ath9k Adaptive Noise Immunity for hardware. ANI observes PHY error counters and listen time, then raises or lowers OFDM and CCK noise-immunity levels by programming hardware controls such as spur immunity, FIR first step, OFDM weak signal detection, and MRC CCK.

## Important APIs, tables, and functions

- `ofdm_level_table[]` maps OFDM immunity levels to spur immunity, FIR step, and weak-signal-detection state.
- `cck_level_table[]` maps CCK immunity levels to FIR step and MRC CCK state.
- `ath9k_hw_ani_init()` initializes thresholds, default levels, poll period, counters, and MIB counter collection.
- `ath9k_ani_reset()` restores default or historical levels on reset/channel change and restarts counters.
- `ath9k_hw_ani_monitor()` is exported and performs periodic counter analysis, raising or lowering immunity.
- `ath9k_enable_mib_counters()` and `ath9k_hw_disable_mib_counters()` configure and freeze/clear MIB counters.

## Control flow

Initialization chooses old or new trigger thresholds based on chip revision, sets default ANI state, restarts counters, and enables MIB counters. Reset chooses either default levels for scanning/AP-style operation or historical levels for station/adhoc operation, applies OFDM and CCK levels, and restarts PHY error counters.

Monitoring first updates cycle/listen counters. If listen time is non-positive, ANI restarts and records the anomaly. Otherwise it accumulates listen time, updates MIB stats, reads PHY error counters, derives OFDM and CCK error rates per second, and compares them with high/low thresholds once `listenTime > aniperiod`. Low OFDM and CCK error rates lower one immunity side per turn. High OFDM error rates raise OFDM immunity and mark the next lowering turn for CCK; high CCK error rates raise CCK immunity and mark the next lowering turn for OFDM. Any adjustment restarts counters.

## State and persistence behavior

All state is in `ah->ani`, `ah->stats`, `ah->ah_mibStats`, and `ah->config`. The driver remembers current immunity levels, OFDM/CCK turn selection, listen time, previous counter values, and stats. Nothing persists across driver unload. ANI level choices can be restored across channel changes while the same `ath_hw` instance lives.

## Dependencies and integration points

The file depends on register definitions and helper macros from `hw.h` and `hw-ops.h`, chip revision predicates, `ath9k_hw_ani_control()`, cycle counter helpers, MIB/PHY error registers, and cfg80211 opmode constants. It is built into `ath9k_hw.o` and called by reset, channel, and periodic maintenance paths elsewhere in ath9k.

## Risks

Incorrect threshold tuning can reduce sensitivity or allow high false-detect rates. Register writes depend on chip family behavior; there are explicit exceptions for AR9100, pre-AR9300, AR9485, AR9565, and AR9561. Counter wrap or listen-time anomalies can distort rates. The level tables must keep default entries aligned with INI programming, as noted by the sanity-check comment.

## Test signals

Observe ANI debug logs under clean and noisy RF conditions, verify `ast_ani_*` stats change as expected, compare packet loss/throughput while forcing OFDM or CCK interference, test scan/AP/station resets, validate chip-family exceptions, and confirm no regressions in MIB counter accounting across suspend/reset/channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.h

## Purpose

This header declares ath9k Adaptive Noise Immunity constants, state structures, statistics structures, command bits, and public hardware ANI functions. It is the shared contract between ANI implementation and the rest of the ath9k hardware layer.

## Important APIs and types

- Threshold macros such as `ATH9K_ANI_OFDM_TRIG_HIGH`, `ATH9K_ANI_CCK_TRIG_LOW`, and old/below-INI variants define error-rate decision points in errors per second.
- Default setting macros define initial spur immunity, FIR first step, RSSI thresholds, ANI period, poll interval, and legal register-control ranges.
- `enum ath9k_ani_cmd` defines control bits passed to `ath9k_hw_ani_control()`: OFDM weak signal detection, firstep level, spur immunity level, MRC CCK, and all.
- `struct ath9k_mib_stats` stores accumulated ACK/RTS/FCS/beacon counters.
- `struct ath9k_ani_default` stores INI register defaults used by hardware-specific ANI controls.
- `struct ar5416AniState` holds current ANI levels, flags, listen time, PHY error counts, and INI defaults.
- `struct ar5416Stats` holds ANI transition counters, error counters, average beacon RSSI, and MIB stats.
- Public functions are `ath9k_enable_mib_counters()`, `ath9k_hw_disable_mib_counters()`, and `ath9k_hw_ani_init()`.

## Control flow and integration

`ani.c` consumes these definitions to initialize defaults, compare PHY error rates, and apply hardware controls. Other hardware code embeds `struct ar5416AniState` and `struct ar5416Stats` inside `struct ath_hw`, uses `ah_mibStats` as shorthand, and calls the public functions during reset, start/stop, and monitoring.

## State and persistence behavior

The header defines in-memory state only. ANI state persists only for the lifetime of `struct ath_hw`, allowing per-channel/historical immunity decisions while the device is active. Counter and level fields are reset or reinitialized by ANI reset/init paths.

## Dependencies and risks

This header assumes `struct ath_hw` and related register-control functions are visible to includers through ath9k hardware headers. Risk lies in threshold constants and structure layout coupling with `ani.c`; changing defaults can affect RF behavior on all supported chips. Range macros must stay aligned with hardware register fields.

## Test signals

Compile coverage should include all hardware families that include ANI. Runtime signals include expected ANI stats, MIB counter behavior, periodic monitor calls at `ATH9K_ANI_POLLINTERVAL`, and stable throughput/receive sensitivity when default thresholds are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ani.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/antenna.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/antenna.c

## Purpose

This file implements ath9k antenna diversity and LNA combining decisions for chips with ant-div support, especially AR9285 and AR9485/AR9565/AR9331-style EEPROM layouts. It observes received packet RSSI and antenna-selection metadata, decides when alternate antenna/LNA configurations are better, and writes updated hardware ant-div configuration.

## Important APIs and functions

- `ath_ant_comb_scan()` is the public entry point called with `struct ath_softc` and `struct ath_rx_status` for RX samples.
- `ath_is_alt_ant_ratio_better()` evaluates whether alternate antenna usage and RSSI justify preference changes.
- `ath_ant_div_comb_alt_check()` applies group-specific decision rules for switching main and alternate LNA settings.
- `ath_lnaconf_alt_good_scan()`, `ath_select_ant_div_from_quick_scan()`, and `ath_ant_set_alt_ratio()` manage multi-step quick scans when the alternate path looks promising.
- `ath_ant_div_conf_fast_divbias()` maps main/alt LNA combinations and diversity groups to hardware `fast_div_bias` values.
- `ath_ant_try_scan()`, `ath_ant_try_switch()`, and `ath_ant_short_scan_check()` implement scan-state progression and early termination.

## Control flow

Each RX sample extracts current and main antenna configuration from `rs_rssi_ctl[2]` and reads main/alt RSSI from control chains 0 and 1. Positive RSSI samples increment packet counts, RSSI totals, main/alt receive counters, and debug stats. The function waits until enough packets are sampled, an aggregate ends, or a short-scan condition fires. It then computes alternate receive ratio and average RSSI, reads current hardware ant-div config, and updates the ant-comb state machine.

Every `ATH_ANT_DIV_COMB_MAX_COUNT` windows, a high alternate ratio starts an alternate-good quick scan; otherwise the scan starts with simpler alternate LNA swapping. During scans the code cycles through LNA1, LNA2, LNA1+LNA2, and LNA1-LNA2 combinations, records RSSI for each, selects the best main and alternate config, adjusts fast-div bias, writes the config with `ath9k_hw_antdiv_comb_conf_set()`, records debug stats, and resets sample counters.

## State and persistence behavior

State lives in `sc->ant_comb`: scan flags, quick-scan count, RSSI totals for LNA variants, alternate ratios, threshold choices, packet counters, scan start time, and optional fast-div bias override. Hardware state is persisted in ant-div registers until changed again or reset. No disk state exists.

## Dependencies and integration points

The file depends on `ath9k.h`, `struct ath_rx_status`, `struct ath_hw_antcomb_conf`, ant-div constants/macros, jiffies timing, hardware get/set helpers, and debug statistic helpers. It integrates with RX processing and the hardware layer that reads EEPROM-derived ant-div capabilities.

## Risks

The algorithm is sensitive to RSSI sample quality, packet count thresholds, aggregate handling, and group-specific magic constants. Bad thresholds can cause oscillation, poor diversity choice, or reduced sensitivity. RSSI values of zero or negative are ignored for totals, so unusual hardware reporting can starve decisions. Fast-div bias tables are dense hardware knowledge and easy to regress. Timing and counter reset behavior matters for short scans.

## Test signals

Useful tests include RX diversity debug stats, controlled RF tests with known stronger LNA paths, mobility tests that force main/alt changes, low-RSSI and high-RSSI threshold cases, short-scan timeout and packet-count cases, aggregate traffic behavior, and per-chip EEPROM ant-div configuration validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/antenna.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar5008_initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar5008_initvals.h

## Purpose

This header contains static initialization tables for AR5008/AR5416-class ath9k hardware. The arrays provide register address/value sequences for base modes, common registers, RF gain, Bank6 transmit-power-control programming, and ADDAC settings.

## Important data

- `ar5416Modes[][5]` stores mode-specific register values with columns for 5 GHz HT20, 5 GHz HT40, 2 GHz HT40, and 2 GHz HT20.
- `ar5416Common[][2]` stores register writes shared by all modes, including MAC/baseband defaults, timing, filter, queue, PHY, and chain-related registers.
- `ar5416BB_RfGain[][3]` stores 5 GHz and 2 GHz RF gain table programming values.
- `ar5416Bank6TPC[][3]` stores Bank6 transmit power control sequences for 5 GHz and 2 GHz.
- `ar5416Addac[][2]` stores common ADDAC programming values.

## Control flow and integration

There are no functions in this file. Hardware initialization code includes these tables and walks them during device reset/attach or channel/mode setup, selecting the correct column for the target band and HT width. The table shapes encode how generic init helpers interpret address and value columns.

## State and persistence behavior

The arrays are compile-time read-only data. They do not hold runtime state, but applying them programs persistent hardware register state until reset or subsequent register writes. They represent vendor-provided INI defaults that other runtime systems, including ANI, assume as baselines.

## Dependencies and risks

The header depends on includers having `u32` defined and knowing the exact array names and dimensions. Risk is high for accidental numeric edits: register addresses, repeated writes to the same address, mode columns, and band-specific values are hardware calibration data. Misaligned columns can break one band or channel width while leaving others apparently functional. Default ANI levels and calibration paths may assume these values.

## Test signals

Validation requires hardware bring-up on AR5008/AR5416-class devices across 2 GHz and 5 GHz, HT20 and HT40, plus regression checks for attach/reset success, calibration, transmit power, receive sensitivity, ANI stability, throughput, and spectral/regulatory behavior. Code review should treat diffs as table-data changes rather than algorithm changes and compare against known vendor INI sources where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/ar5008_initvals.h -->
