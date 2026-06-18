# Research: subset-b-004727

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi.h

## Purpose
`wmi.h` is the main ath10k firmware control-plane contract for the Qualcomm/Atheros "Unified" WMI interface. It defines the on-wire command and event IDs, packed firmware payload layouts, host-side argument structures, feature/service bit mapping helpers, wake-on-wireless constants, statistics payloads, and event-handler prototypes consumed by the rest of the ath10k driver. The header is intentionally broad: most ath10k MAC, scan, regulatory, power-save, WoW, peer, vdev, pdev, debug, spectral, DFS, TDLS, and stats code depends on this file to build firmware-compatible messages.

## Important APIs, Types, and Constants
- `struct wmi_cmd_hdr`, `WMI_CMD_HDR_*`, `HTC_PROTOCOL_VERSION`, and `WMI_PROTOCOL_VERSION` define the common WMI command envelope placed in sk_buffs sent over HTC/HIF.
- `a_sle32`, `a_cpu_to_sle32()`, and `a_sle32_to_cpu()` provide signed little-endian storage for firmware fields that need negative values, for example transmit-power values.
- `enum wmi_service`, `enum wmi_10x_service`, `enum wmi_main_service`, and `enum wmi_10_4_service` enumerate firmware capability bits across ABI families. `wmi_service_name()` gives debug-readable names.
- `WMI_SERVICE_IS_ENABLED()`, `WMI_EXT_SERVICE_IS_ENABLED()`, and the service mappers `wmi_10x_svc_map()`, `wmi_main_svc_map()`, and `wmi_10_4_svc_map()` translate firmware-specific bit positions into the driver's common `WMI_SERVICE_*` bitmap.
- `struct wmi_cmd_map` is the central firmware-version indirection table. Runtime WMI ops can reference logical command slots instead of hard-coding a single firmware command ID namespace.
- `enum wmi_cmd_group`, `WMI_CMD_GRP()`, `WMI_EVT_GRP_START_ID()`, `enum wmi_cmd_id`, `enum wmi_event_id`, and the 10.x/10.2/10.4 command/event enums define stable numeric protocol IDs. The 10.x families use the documented `0x9000` to `0x9fff` range for many commands/events.
- Channel and regulatory types include `enum wmi_phy_mode`, `ath10k_wmi_phymode_str()`, `struct wmi_channel`, `struct wmi_channel_arg`, channel flags such as `WMI_CHAN_FLAG_DFS`, HT/VHT capability masks, regulatory-domain masks, and `struct hal_reg_capabilities`.
- Service-ready and initialization payloads include `struct wlan_host_mem_req`, `struct wmi_service_ready_event`, `struct wmi_10x_service_ready_event`, `struct wmi_ready_event`, `struct wmi_resource_config`, `struct wmi_resource_config_10x`, `struct wmi_resource_config_10_2`, `struct wmi_resource_config_10_4`, `struct host_memory_chunk`, `struct wmi_host_mem_chunks`, and the per-ABI `wmi_init_cmd*` structures.
- Scan contracts include TLV containers (`wmi_chan_list`, `wmi_bssid_list`, `wmi_ie_data`, `wmi_ssid_list`), `struct wmi_start_scan_common`, `struct wmi_start_scan_cmd`, `struct wmi_10x_start_scan_cmd`, `struct wmi_start_scan_arg`, scan flags, stop-scan types, `struct wmi_scan_event`, and parser argument forms such as `struct wmi_scan_ev_arg`.
- Management and PHY-error receive paths use `struct wmi_mgmt_rx_hdr_v1`, `wmi_mgmt_rx_hdr_v2`, 10.4 variants, `struct wmi_mgmt_rx_ext_info`, `struct wmi_phyerr`, `struct wmi_phyerr_event`, `struct wmi_10_4_phyerr_event`, DFS/radar/FFT TLV definitions, and `struct wmi_phyerr_ev_arg`.
- PDEV, VDEV, peer, key, and association contracts are modeled by `struct wmi_pdev_param_map`, `enum wmi_pdev_param`, ABI-specific pdev param enums, `struct wmi_vdev_param_map`, VDEV param enums, `struct wmi_peer_param_map`, peer flag enums, `struct wmi_vdev_create_cmd`, `struct wmi_vdev_start_request_cmd`, `struct wmi_vdev_install_key_cmd`, `struct wmi_common_peer_assoc_complete_cmd`, and ABI-specific peer association command payloads.
- Statistics and telemetry include pdev/vdev/peer stats events and payloads (`struct wmi_stats_event`, `struct wmi_10_2_stats_event`, `struct wmi_pdev_stats*`, `struct wmi_vdev_stats*`, `struct wmi_peer_stats*`), TPC config/final-table events, channel-info events, temperature, BSS channel survey, debug-log config, and FTM/UTF payload headers.
- WoW/PNO definitions include `enum wmi_wow_wakeup_event`, `wow_wakeup_event()`, `enum wmi_wow_wake_reason`, `wow_reason()`, `struct wmi_wow_ev_arg`, `WOW_MIN_PATTERN_SIZE`, `WOW_MAX_PATTERN_SIZE`, `WOW_MAX_PKT_OFFSET`, `WOW_HDR_LEN`, `WOW_MAX_REDUCE`, `struct wmi_network_type`, and `struct wmi_pno_scan_req`.
- Exported functions at the end provide the implementation hooks from `wmi.c` and related files: attach/detach, service-ready waits, skb allocation, command send, command marshalling helpers, stats pull helpers, event handlers, PHY error parsing, firmware stats formatting, subtype mapping, barriers, and TPC table helpers.

## Control Flow and Data Flow
This header does not implement the runtime WMI state machine, but it defines the structures that constrain it. Boot and firmware negotiation flow from `ath10k_wmi_attach()` and `ath10k_wmi_connect()` through `ath10k_wmi_wait_for_service_ready()` and `ath10k_wmi_wait_for_unified_ready()`. Service-ready events expose capability bitmaps, firmware versions, regulatory limits, host-memory requests, and resource limits. The driver maps those firmware-specific service bits into `ar->wmi.svc_map`, fills resource configuration and host memory chunk payloads, and sends a WMI init command using the correct ABI-specific structure.

Command control flow is command-map driven. Higher-level ath10k modules prepare host argument structures such as `wmi_start_scan_arg`, `wmi_vdev_start_request_arg`, `wmi_vdev_install_key_arg`, `wmi_peer_assoc_complete_arg`, `wmi_sta_keepalive_arg`, or `wmi_per_peer_per_tid_cfg_arg`; WMI ops convert these into packed little-endian firmware payloads and send them via `ath10k_wmi_cmd_send()` or `ath10k_wmi_cmd_send_nowait()`. Incoming HTC messages are demultiplexed by event IDs into handlers such as `ath10k_wmi_event_scan()`, `ath10k_wmi_event_mgmt_rx()`, `ath10k_wmi_event_phyerr()`, `ath10k_wmi_event_update_stats()`, `ath10k_wmi_event_wow_wakeup_host()`, and service-ready/ready handlers.

The header also captures ABI divergence. Mainline, 10.x, 10.2, and 10.4 firmware families have different command numbers, event numbers, service positions, resource layouts, stats layouts, TIM bitmap sizes, and feature fields. The driver keeps a common internal model where possible, then chooses ABI-specific layouts and mapping tables when packing commands or parsing events.

## State and Persistence Behavior
`wmi.h` itself persists no runtime state; it defines firmware-visible state transitions and state snapshots. Persistent driver state affected by these definitions includes service maps, firmware capability state, resource configuration, host memory chunks, scan IDs/requestor IDs, vdev and peer IDs, key material sent to firmware, power-save settings, WoW wake event masks, PNO scan configuration, and statistics snapshots. Most on-wire structures are `__packed` and use explicit little-endian fields, so persistence is effectively the firmware ABI and must remain byte-compatible across compiler and architecture differences.

The WMI protocol assumes host-side validation. The file comments explicitly state that correctness of WMI command parameters belongs to the host driver, and firmware is not required to validate ranges. This makes validation helpers such as `ath10k_wmi_start_scan_verify()`, service-bit checks, size constants, and per-feature gates important for keeping device state coherent.

## Dependencies and Integration Points
The header depends on Linux kernel core types, endian annotations, IEEE 802.11 definitions, Ethernet address constants, sk_buffs, bit operations, and ath10k private structures declared elsewhere. It is consumed by `wmi.c`, `wmi-ops.h`, `mac.c`, `core.c`, WoW code, scan code, debug/debugfs code, DFS/spectral code, peer/vdev setup, firmware stats reporting, and HIF/HTC transport code.

Integration with mac80211/cfg80211 happens indirectly: mac80211 operations produce channel, scan, association, key, power-save, WoW, and TDLS requests; ath10k translates them into the WMI payloads defined here. Integration with firmware happens directly through numeric command/event IDs and packed structures. Integration with debug and diagnostics comes through debug-log config, firmware stats events, TPC events, UTF/FTM messages, and stringification helpers for PHY mode and WoW reasons.

## Risks and Edge Cases
- Firmware ABI compatibility is the central risk. Reordering fields, changing enum numeric values, changing packing/alignment, or using host-native types in on-wire structures can break hardware behavior.
- The service bitmap helpers use unusual indexing because legacy service maps encode only selected bits in each 32-bit word and extension services start after the legacy length. Off-by-one or length mistakes can silently enable unsupported features or hide supported features.
- `struct wmi_cmd_map` and the parallel command/event enums must stay synchronized with WMI op tables. Unsupported command IDs use `0`, so call sites must correctly gate optional commands.
- Flexible-array payloads require exact length validation in parser implementations. Management RX, PHY error, stats, SWBA, scan TLVs, TDLS peer channels, key data, and FTM/UTF data all carry variable-length buffers.
- WoW/PNO constants are shared with `wow.c`; changing pattern size or header-reduction math can break packet-pattern matching, especially for native Wi-Fi decap mode.
- Some structures intentionally contain packed unions or non-u32 fields despite the top-level WMI extension guideline. Maintainers should distinguish legacy firmware ABI requirements from guidelines for new commands.
- Several debug/test controls can intentionally crash or hang firmware (`WMI_FORCE_FW_HANG_*`, UTF/FTM paths). They should remain gated through debug or test interfaces.

## Test Signals
Useful validation signals include successful firmware boot through service-ready and unified-ready waits, correct service map logging via `wmi_service_name()`, scan start/stop and scan event completion, vdev start/stop responses, association and data path operation across firmware ABI families, management frame RX/TX completion, peer kickout handling, DFS/spectral event parsing, firmware stats output sanity, WoW suspend/resume wake reason reporting, PNO network detection, TDLS configuration, and endianness/size checks from sparse/build warnings. Build coverage should include multiple ath10k firmware targets where possible because much of the file exists to preserve ABI-specific differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.c

## Purpose
`wow.c` implements ath10k wake-on-wireless support for mac80211 suspend/resume. It advertises supported WoWLAN triggers, programs per-vdev wake events and packet patterns through WMI, configures network-list-offload/PNO scans for net-detect wakeups, coordinates target suspend/wakeup completions, and bridges device wakeup capability to the Linux device power-management core.

## Important APIs, Types, and Functions
- `ath10k_wowlan_support` is the base `struct wiphy_wowlan_support`. It advertises disconnect and magic-packet wakeups, pattern limits from `wmi.h`, and a maximum packet offset. `ath10k_wow_init()` later augments it for net-detect and adjusts limits for native Wi-Fi decap.
- `ath10k_wow_vif_cleanup()` disables every `WOW_EVENT_MAX` wake event for a vdev and deletes all configured firmware patterns from `0` to `ar->wow.max_num_patterns - 1`.
- `ath10k_wow_cleanup()` applies that per-vdev cleanup across `ar->arvifs` while `ar->conf_mutex` is held.
- `ath10k_wow_convert_8023_to_80211()` rewrites cfg80211 Ethernet-style packet patterns into 802.11 + RFC1042 positions for firmware running in native Wi-Fi RX decapsulation mode.
- `ath10k_wmi_pno_check()` validates and converts `struct cfg80211_sched_scan_request` into `struct wmi_pno_scan_req`, including SSIDs, channels, RSSI thresholds, scan plans, passive/active behavior, hidden-network marking, random MAC parameters, delay, and dwell times.
- `ath10k_vif_wow_set_wakeups()` chooses wake events based on vdev type and requested `struct cfg80211_wowlan`, programs PNO if requested, converts and installs packet patterns, and enables the final event mask through WMI.
- `ath10k_wow_set_wakeups()` loops over all ath10k vifs and applies the requested wakeups.
- `ath10k_vif_wow_clean_nlo()` and `ath10k_wow_nlo_cleanup()` disable firmware PNO after resume when NLO had been enabled.
- `ath10k_wow_enable()` sends `ath10k_wmi_wow_enable()` and waits up to `3 * HZ` for `ar->target_suspend`.
- `ath10k_wow_wakeup()` sends `ath10k_wmi_wow_host_wakeup_ind()` and waits up to `3 * HZ` for `ar->wow.wakeup_completed`.
- `ath10k_wow_op_suspend()`, `ath10k_wow_op_resume()`, and `ath10k_wow_op_set_wakeup()` are the mac80211 PM operation entry points declared in `wow.h`.
- `ath10k_wow_init()` validates firmware/service support, publishes `ar->hw->wiphy->wowlan`, and marks the device wakeup-capable.

## Control Flow
Suspend starts in `ath10k_wow_op_suspend()`. The function locks `ar->conf_mutex`, verifies `ATH10K_FW_FEATURE_WOWLAN_SUPPORT`, clears stale wake events/patterns, programs new wakeups from the mac80211 `wowlan` request, waits for TX completion, enables firmware WoW, and finally suspends HIF. Failure after wakeup programming runs cleanup; failure after firmware WoW enable also sends a wakeup indication before cleanup. The mac80211 suspend callback returns `0` on success and `1` for most failures, matching this driver's PM callback convention.

Wakeup programming is vdev-aware. AP vdevs wake on deauth/disassoc/probe/auth/assoc/HTT/RA-match events; IBSS additionally wakes on beacon events; STA vdevs wake on disconnect-related events when requested, magic packets when requested, PNO detection when net-detect is requested, and packet-pattern matches when patterns are supplied. Once the bitmap is built, each selected WMI wake event is enabled individually.

Pattern handling first converts cfg80211's packed bitmask into a byte mask. If firmware is in `ATH10K_HW_TXRX_NATIVE_WIFI` decap mode, Ethernet patterns below the Ethernet header length are transformed into 802.11 header/SNAP positions; patterns after the Ethernet header are shifted by `WOW_HDR_LEN - ETH_HLEN`. Converted patterns are bounded by `WOW_MAX_PATTERN_SIZE` and installed with incremental pattern IDs.

Resume starts in `ath10k_wow_op_resume()`. It resumes HIF, sends the firmware host-wakeup indication, disables NLO if it had been enabled, and if an error remains, either moves an ON device to `ATH10K_STATE_RESTARTING` or reports an unrecoverable state error.

## State and Persistence Behavior
The file mutates `ar->wow.wowlan_support`, `ar->hw->wiphy->wowlan`, `ar->nlo_enabled`, device wakeup capability/enabled state, firmware wake-event state, firmware pattern tables, firmware PNO configuration, and suspend/wakeup completions. Firmware-side state is intentionally cleaned before suspend programming and cleaned/disabled again on errors or resume. There is no disk persistence; the state is runtime PM and firmware state.

`ar->conf_mutex` is asserted or held across all multi-step hardware state transitions. `ar->target_suspend` and `ar->wow.wakeup_completed` completions are reinitialized before waiting, avoiding stale completions from prior suspend/resume cycles.

## Dependencies and Integration Points
`wow.c` integrates with mac80211/cfg80211 through `struct ieee80211_hw`, `struct cfg80211_wowlan`, `struct cfg80211_pkt_pattern`, and scheduled-scan requests. It integrates with firmware through WMI helpers from `wmi-ops.h` and WMI constants/types from `wmi.h`, including WoW wake events, PNO limits, and pattern-size limits. It integrates with HIF for bus suspend/resume, with ath10k MAC code for TX drain, and with Linux PM through `device_set_wakeup_capable()` and `device_set_wakeup_enable()`.

## Risks and Edge Cases
- PNO programming sets `ar->nlo_enabled = true` before validating and successfully configuring the PNO request. If validation fails, no NLO wake event is added, but resume cleanup may still attempt to disable NLO.
- `ath10k_vif_wow_set_wakeups()` does not propagate an error from `ath10k_wmi_wow_config_pno()` because the return value is not assigned around that call. A PNO configuration failure could leave net-detect silently disabled.
- Pattern conversion assumes the old pattern buffer is valid for `ETH_HLEN - old->pkt_offset` when `pkt_offset < ETH_HLEN`; cfg80211 limits and earlier checks are important for avoiding malformed offsets.
- Patterns larger than `WOW_MAX_PATTERN_SIZE` are skipped rather than failing the suspend request, which can surprise users if they expected all patterns to be armed.
- Every vdev receives the same `wowlan` request, so multi-vdev configurations rely on vdev-type filtering rather than per-interface wake policy.
- Suspend and resume depend on firmware completion events arriving within three seconds. Missing completions force PM failure or device restart.

## Test Signals
Relevant test signals include `iw phy` WoWLAN capability reporting, successful suspend/resume with magic-packet wake, disconnect wake, pattern wake, and net-detect wake; logs for `failed to issue wow`, `failed to add pattern`, timeout messages, and NLO cleanup failures; confirmation that HIF suspend/resume pairs are balanced; and suspend/resume behavior in native Wi-Fi decap mode where pattern offsets are reduced by `WOW_MAX_REDUCE`. Firmware/service combinations without `ATH10K_FW_FEATURE_WOWLAN_SUPPORT`, `WMI_SERVICE_WOW`, or `WMI_SERVICE_NLO` should be tested for graceful feature suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.h

## Purpose
`wow.h` declares the small ath10k per-device Wake-on-Wireless state container and the PM entry points implemented by `wow.c`. It also provides a no-op initializer when power management is not compiled in.

## Important APIs and Types
- `struct ath10k_wow` stores `max_num_patterns`, the `wakeup_completed` completion used by resume wakeup handshaking, and the `wiphy_wowlan_support` instance exported to cfg80211.
- Under `CONFIG_PM`, the header declares `ath10k_wow_init()`, `ath10k_wow_op_suspend()`, `ath10k_wow_op_resume()`, and `ath10k_wow_op_set_wakeup()`.
- Without `CONFIG_PM`, `ath10k_wow_init()` is a static inline stub returning `0`. The suspend/resume/set_wakeup operation declarations are not exposed in that build mode.

## Control Flow
The header participates in driver initialization by allowing common ath10k setup code to call `ath10k_wow_init()` unconditionally. In PM-enabled builds the real implementation initializes cfg80211 wake capabilities and device wakeup support; in non-PM builds the inline stub makes initialization a no-op. mac80211 operation tables can use the declared suspend/resume/set_wakeup functions only when PM code is built.

## State and Persistence Behavior
The only state defined here is in-memory per-device WoW state embedded in the larger `struct ath10k`. `max_num_patterns` comes from firmware/driver capability setup, `wakeup_completed` synchronizes firmware resume acknowledgement, and `wowlan_support` is copied or adjusted before being assigned to the wiphy. No state is persisted beyond the runtime device lifetime.

## Dependencies and Integration Points
The declarations depend on ath10k core type declarations, mac80211's `struct ieee80211_hw`, cfg80211's `struct cfg80211_wowlan`, kernel completions, and `struct wiphy_wowlan_support`. `wow.c`, `core.c`, and MAC operation setup are the primary consumers.

## Risks and Edge Cases
- Build guards must stay aligned with operation-table setup. Referencing suspend/resume symbols when `CONFIG_PM` is disabled would fail because only `ath10k_wow_init()` has a stub.
- `struct ath10k_wow` exposes mutable `wowlan_support`; callers should treat it as per-device data, not a global constant, because `wow.c` adjusts limits for native Wi-Fi decap and NLO support.
- Any change to `wakeup_completed` usage must preserve completion initialization and event signaling in the WMI event path.

## Test Signals
Build ath10k with and without `CONFIG_PM`. PM builds should expose WoWLAN capability when firmware supports it and should link suspend/resume callbacks. Non-PM builds should compile with the no-op init path and no unresolved WoW PM symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/wow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Kconfig

## Purpose
This Kconfig file defines build-time configuration switches for the ath11k Qualcomm 802.11ax driver family. It controls the core ath11k module, AHB and PCI bus frontends, debug/debugfs/tracing features, spectral scan support, and channel frequency response dump support.

## Important Symbols
- `ATH11K` is the core tristate for Qualcomm Technologies 802.11ax chipset support. It depends on `MAC80211` and `HAS_DMA`, selects `ATH_COMMON` and `QCOM_QMI_HELPERS`, and builds a module named `ath11k` when modular.
- `ATH11K_AHB` is a tristate bus support option depending on `ATH11K` and `REMOTEPROC`; it enables AHB platform support.
- `ATH11K_PCI` is a tristate bus support option depending on `ATH11K` and `PCI`; it selects `MHI_BUS`, `QRTR`, `QRTR_MHI`, and conditionally `PCI_PWRCTRL_PWRSEQ` when `HAVE_PWRCTRL` is available.
- `ATH11K_DEBUG` is a boolean debug support switch depending on `ATH11K`.
- `ATH11K_DEBUGFS` is a boolean debugfs support switch depending on `ATH11K`, `DEBUG_FS`, and `MAC80211_DEBUGFS`.
- `ATH11K_TRACING` is a boolean tracing support switch depending on `ATH11K` and `EVENT_TRACING`.
- `ATH11K_SPECTRAL` is a boolean spectral scan switch depending on `ATH11K_DEBUGFS` and `RELAY`.
- `ATH11K_CFR` is a boolean channel frequency response dump switch depending on `ATH11K_DEBUGFS` and `RELAY`.

## Control Flow
Kconfig resolution determines which object lists in the ath11k Makefile are active. Enabling `ATH11K` provides the common module foundation. Enabling a bus option adds either the AHB or PCI module objects. Optional booleans then add debugfs, trace, spectral, CFR, thermal, PM, testmode, and coredump compilation paths via Makefile conditionals and broader kernel configuration symbols.

## State and Persistence Behavior
The file has no runtime state. It persists only build configuration choices in the kernel `.config`. Those choices determine which source files compile into built-in objects or modules and which runtime interfaces can exist.

## Dependencies and Integration Points
The file integrates ath11k into Linux wireless configuration. Its direct dependencies are mac80211, DMA support, remoteproc for AHB, PCI/MHI/QRTR for PCI devices, debugfs and mac80211 debugfs for debug interfaces, event tracing for tracepoints, and relay for spectral/CFR data export. The selected symbols ensure common ath support and QMI helpers are available to the driver.

## Risks and Edge Cases
- Incorrect dependency/select relationships can produce link failures or unusable runtime features. PCI support relies on MHI and QRTR selections; AHB relies on remoteproc.
- Debug-oriented options increase built code and expose debugfs or tracing surfaces. They are useful for diagnostics but should remain explicitly gated.
- `ATH11K_SPECTRAL` and `ATH11K_CFR` both depend on debugfs and relay; enabling either without the supporting kernel infrastructure would otherwise leave incomplete data paths.
- The help text recommends enabling debug options for easier problem diagnosis; distribution configs may choose differently to reduce attack surface or footprint.

## Test Signals
Configuration tests should cover `ATH11K=m` with `ATH11K_PCI=m`, `ATH11K_AHB=m`, and combinations of debugfs/tracing/spectral/CFR. Build output should show the matching module names from the Makefile. Kconfig tools should reject impossible combinations, such as PCI support without PCI or spectral support without debugfs/relay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Makefile

## Purpose
This Makefile maps ath11k Kconfig symbols to kernel objects. It builds the common ath11k module from core WLAN, firmware, control, datapath, hardware, QMI, and PCI-common components, then conditionally adds optional diagnostics, PM, thermal, coredump, spectral, testmode, and CFR objects. It also builds separate AHB and PCI bus modules.

## Important Build Rules
- `obj-$(CONFIG_ATH11K) += ath11k.o` creates the main ath11k module/built-in object.
- `ath11k-y` lists the mandatory common objects: `core.o`, `hal.o`, `hal_tx.o`, `hal_rx.o`, `wmi.o`, `mac.o`, `reg.o`, `htc.o`, `qmi.o`, datapath files, `debug.o`, copy-engine support, peer management, data-buffer-ring support, hardware tables, PCI-common code, firmware support, and P2P support.
- `ath11k-$(CONFIG_ATH11K_DEBUGFS)` adds `debugfs.o`, `debugfs_htt_stats.o`, and `debugfs_sta.o`.
- `ath11k-$(CONFIG_NL80211_TESTMODE)` adds `testmode.o`.
- `ath11k-$(CONFIG_ATH11K_TRACING)` adds `trace.o`.
- `ath11k-$(CONFIG_THERMAL)` adds `thermal.o`.
- `ath11k-$(CONFIG_ATH11K_SPECTRAL)` adds `spectral.o`.
- `ath11k-$(CONFIG_PM)` adds `wow.o`, tying WoW support to the kernel PM option.
- `ath11k-$(CONFIG_DEV_COREDUMP)` adds `coredump.o`.
- `ath11k-$(CONFIG_ATH11K_CFR)` adds `cfr.o`.
- `obj-$(CONFIG_ATH11K_AHB) += ath11k_ahb.o` with `ath11k_ahb-y += ahb.o` builds the AHB bus module.
- `obj-$(CONFIG_ATH11K_PCI) += ath11k_pci.o` with `ath11k_pci-y += mhi.o pci.o` builds the PCI bus module.
- `CFLAGS_trace.o := -I$(src)` ensures the tracing framework can find local `trace.h`.

## Control Flow
Kernel kbuild expands `obj-*` and `ath11k-*` variables based on resolved Kconfig symbols. The common module always receives the mandatory `ath11k-y` object list when `CONFIG_ATH11K` is enabled. Optional objects are linked into the same common module when their symbols are enabled. Bus-specific objects are built as separate modules or built-ins according to `ATH11K_AHB` and `ATH11K_PCI`, allowing one common driver core to be paired with different host interfaces.

## State and Persistence Behavior
The file has no runtime state. It persistently defines build composition. Runtime availability of features such as WoW, debugfs, spectral scan, tracing, thermal support, coredump, CFR, AHB, and PCI is determined by whether their object files are linked.

## Dependencies and Integration Points
The Makefile integrates with the Kconfig symbols in the sibling `Kconfig`, Linux kbuild module aggregation rules, and local source files in the ath11k directory. It also uses the broader kernel symbols `CONFIG_NL80211_TESTMODE`, `CONFIG_THERMAL`, `CONFIG_PM`, and `CONFIG_DEV_COREDUMP`. The local include flag for `trace.o` is an integration point with Linux trace event generation.

## Risks and Edge Cases
- Missing an object in `ath11k-y` can produce link failures or runtime feature holes even when Kconfig dependencies are correct.
- Optional source files must remain guarded by matching Kconfig symbols. For example, `wow.o` is linked solely under `CONFIG_PM`; code that references WoW symbols outside PM guards would fail.
- Bus modules depend on common-module symbols and initialization ordering. AHB/PCI object split must keep bus-specific code out of the common object list unless shared intentionally.
- Trace builds often require local header include paths; removing `CFLAGS_trace.o` can break generated trace compilation.

## Test Signals
Build tests should cover common-only, PCI, AHB, PM-enabled, debugfs-enabled, tracing-enabled, spectral/CFR-enabled, and coredump-enabled configurations. Expected artifacts are `ath11k.o`, optional objects folded into it, plus `ath11k_ahb.o` and/or `ath11k_pci.o` when bus support is enabled. A tracing build should compile `trace.o` without missing `trace.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Makefile -->
