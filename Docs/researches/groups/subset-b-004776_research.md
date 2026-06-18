# Research: subset-b-004776

Grouped source research for the WCN36xx wireless driver subset. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.h

## Purpose
Defines the WCN36xx DXE DMA engine register map, descriptor control bits, channel defaults, descriptor-ring structures, buffer-pool structures, and public DXE entry points used by the mac80211-facing driver. It is the shared contract between `dxe.c`, TX/RX code, and the platform MMIO resources mapped by `main.c`.

## Important APIs, Types, and Functions
The header declares descriptor control macros for valid/EOP/BD handling, host-to-BMU and BMU-to-host transfer types, queue source/destination selection, interrupt enable, endianness, priority, BMU threshold, and template index fields. Composite descriptor controls include `WCN36XX_DXE_CTRL_TX_L`, `WCN36XX_DXE_CTRL_TX_H`, RX controls, and split BD/SKB TX controls. Channel control defaults `WCN36XX_DXE_CH_DEFAULT_CTL_RX_L`, `RX_H`, `TX_H`, and `TX_L` encode the per-channel mode registers.

Key types are `struct wcn36xx_dxe_desc`, the hardware-visible packed descriptor; `struct wcn36xx_dxe_ctl`, the software ring node that tracks descriptor, SKB, BD CPU/DMA addresses, and ring order; `struct wcn36xx_dxe_ch`, the per-channel descriptor ring and register configuration; and `struct wcn36xx_dxe_mem_pool`, the DMA pool backing BD headers. Public entry points include `wcn36xx_dxe_allocate_mem_pools`, `wcn36xx_dxe_alloc_ctl_blks`, `wcn36xx_dxe_init`, `wcn36xx_dxe_init_channels`, `wcn36xx_dxe_tx_frame`, `wcn36xx_dxe_rx_frame`, `wcn36xx_dxe_tx_flush`, and `wcn36xx_dxe_tx_ack_ind`.

## Control Flow and State
This file has no executable control flow, but it describes the DXE runtime pipeline. TX low/high channels move host descriptors and SKB payloads into BMU work queues, while RX low/high channels move BMU packets back to host buffers. The descriptor-count enum fixes ring depths: 128 TX-low, 10 TX-high, 512 RX-low, and 40 RX-high descriptors. `struct wcn36xx_dxe_ch` stores head/tail control blocks protected by its spinlock, the DMA allocation base, descriptor count, work-queue number, control words for BD and SKB descriptors, and register offsets used by the implementation.

## Dependencies and Integration Points
Depends on `wcn36xx.h` for the main device type and indirectly on Linux DMA, SKB, and spinlock types. `main.c` allocates resources and calls DXE start/stop from mac80211 `.start`, `.stop`, `.tx`, and `.flush` paths. `txrx.c` supplies TX BD format, while `dxe.c` consumes the register constants to program `wcn->dxe_base` and CCU interrupt routing. SMSM bits `WCN36XX_SMSM_WLAN_TX_ENABLE` and `WCN36XX_SMSM_WLAN_TX_RINGS_EMPTY` tie the DMA rings to Qualcomm shared-state signaling.

## Risks and Test Signals
The constants are a hardware ABI: wrong bit positions, ring sizes, queue numbers, or channel offsets can deadlock DMA, corrupt frames, or lose interrupts. The `WCN36XX_DXE_WQ_TX_*` macros contain a TODO and branch on `is_pronto_v3`, so platform variants need explicit traffic testing. The software ring stores both CPU and DMA pointers, making DMA mapping lifetime and head/tail locking critical. Test signals include probe/start DMA initialization, sustained TX/RX on low and high queues, IRQ completion and error paths, TX flush during interface teardown, suspend/resume with IRQ masking, and Pronto versus Riva/Pronto-v3 platform coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/dxe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.c

## Purpose
Implements firmware feature-capability bitmap helpers for WCN36xx. It maps known capability enum values to debug names and provides set/get/clear operations used after firmware capability exchange.

## Important APIs, Types, and Functions
`wcn36xx_firmware_caps_names[]` is an indexed string table keyed by `enum wcn36xx_firmware_feat_caps`. `wcn36xx_firmware_get_cap_name()` returns a printable capability name or `"UNKNOWN"` for out-of-table values. `wcn36xx_firmware_set_feat_caps()`, `wcn36xx_firmware_get_feat_caps()`, and `wcn36xx_firmware_clear_feat_caps()` operate on a four-word `u32` bitmap, translating enum values into array and bit indexes.

## Control Flow and State
Each bitmap operation validates that the capability index is in the 0..127 firmware range, logs a warning for invalid indexes, and otherwise mutates or tests one bit in the caller-owned bitmap. The file owns no persistent state except the static name table. Runtime feature state is held in `wcn->fw_feat_caps`, populated by SMD feature exchange and later read by `main.c` to decide whether scan offload is available and to print firmware capabilities.

## Dependencies and Integration Points
Includes `wcn36xx.h` for logging and integer types and `firmware.h` for the enum contract. `main.c` calls `wcn36xx_firmware_get_feat_caps()` for capability decisions and `wcn36xx_feat_caps_info()` iterates through `MAX_FEATURE_SUPPORTED` using `wcn36xx_firmware_get_cap_name()`. SMD feature exchange code fills the bitmap with values defined by `hal.h`'s `WCN36XX_HAL_CAPS_SIZE`.

## Risks and Test Signals
The helper accepts any enum value up to 127 even when the name table has gaps, so callers must not assume a printable name proves support is known to the driver. Bit operations use `1 << bit_idx`, so the bitmap must remain 32-bit words with indexes under 32 per word. Test signals include firmware feature exchange on old and new firmware, scan-offload fallback when the `SCAN_OFFLOAD` bit is absent, debug output for known capability names, and invalid-index warning coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.h

## Purpose
Declares the WCN36xx firmware feature-capability enum and bitmap helper API used by the driver after firmware capability exchange.

## Important APIs, Types, and Functions
`enum wcn36xx_firmware_feat_caps` assigns stable bit positions for capabilities such as MCC, P2P, DOT11AC, SCAN_OFFLOAD, BCN_FILTER, RATECTRL, WOW, FW_IN_TX_PATH, UPDATE_CHANNEL_LIST, WLAN_MCADDR_FLT, FW_STATS, extended scan/statistics features, WIFI_CONFIG, and antenna diversity. `MAX_FEATURE_SUPPORTED` is fixed at 128, matching the four-word firmware capability bitmap. The header declares `wcn36xx_firmware_set_feat_caps()`, `wcn36xx_firmware_get_feat_caps()`, `wcn36xx_firmware_clear_feat_caps()`, and `wcn36xx_firmware_get_cap_name()`.

## Control Flow and State
The header has no runtime control flow. Its state model is declarative: enum numeric values are persistent bit positions in `wcn->fw_feat_caps` and in firmware messages, not ordinary local constants that can be reordered.

## Dependencies and Integration Points
Consumed by `firmware.c`, `main.c`, and SMD feature-capability exchange paths. The enum aligns with `struct wcn36xx_hal_feat_caps_msg` in `hal.h`, whose `feat_caps[WCN36XX_HAL_CAPS_SIZE]` carries the bitset over the control channel. Higher-level mac80211 operations use these bits to choose firmware offloads or fall back to host/mac80211 behavior.

## Risks and Test Signals
Changing enum values would break compatibility with firmware. The enum has intentional gaps, for example no value 50 and no 59, so loops can traverse unsupported bit positions. Test signals are compile coverage for all users, feature exchange with firmware that advertises old and new bitsets, capability-gated behavior such as scan offload, and debug logs that map known bits to the expected names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/hal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/hal.h

## Purpose
Defines the WCN36xx host-to-firmware HAL message ABI: message IDs, version tags, enums, packed request/response structures, configuration IDs, scan formats, station/BSS/key structures, power-management messages, WoWLAN offload messages, packet-filtering formats, feature capability messages, statistics, PNO, thermal mitigation, and indication payloads. It is the dominant data contract used by the SMD control channel.

## Important APIs, Types, and Functions
Important top-level definitions include HAL version constants, `enum wcn36xx_hal_host_msg_type` for control message IDs, `enum wcn36xx_hal_host_msg_version`, mode enums for driver type, stop type, system mode, PHY channel bonding, MIMO power save, station rate mode, BSS/network type, encryption, link state, statistics masks, and configuration IDs `WCN36XX_HAL_CFG_*`. The common header for control messages is `struct wcn36xx_hal_msg_header`, with a 16-bit message type, 16-bit message version, and payload length.

Core lifecycle messages include MAC start/stop, update config, NV image download, feature caps, channel list update, scan init/start/end/finish, and scan-offload start/stop/indication. Connection management is represented by join, switch-channel, config/delete BSS, config/delete STA, add/delete self STA, set link state, EDCA update, beacon/probe-response templates, and delete-station indications. Security and aggregation structures include BSS/STA key messages, WEP/TKIP/CCMP fields, GTK offload, MIC failure indication, BA session add/delete/trigger messages, and TSPEC/QoS messages. Power/offload structures cover IMPS/BMPS/UAPSD, beacon filters, ARP/IPv6 NS host offload, keepalive, WoWLAN pattern/magic/GTK wake reasons, RSSI thresholding, PNO preferred-network scans, packet filters, multicast address lists, and set-power parameters.

## Control Flow and State
There is no executable flow in this header, but each structure defines how `smd.c` serializes operations into firmware and parses synchronous responses or asynchronous indications. State is split between host-owned runtime fields and firmware-owned indexes returned in responses: BSS indexes, STA indexes, DPU descriptor indexes/signatures, BA session IDs, BSS power-state indexes, key replay counters, wake reason data, and scan/offload status. Many structures are marked `__packed` because they are sent byte-for-byte over SMD; versioned variants such as `wcn36xx_hal_config_sta_params_v1` and `wcn36xx_hal_config_bss_params_v1` add VHT fields while preserving old firmware layouts.

## Dependencies and Integration Points
Depends on kernel integer types, Ethernet address sizing, and bitfield/compiler packing conventions through the including driver headers. It is included by `wcn36xx.h`, making it visible to `main.c`, `smd.c`, `txrx.c`, `pmc.c`, and debug/testmode code. Mac80211 state changes are translated into these messages: channel and scan changes, association, AP beaconing, key installation, AMPDU negotiation, multicast filtering, suspend/resume, GTK rekey offload, ARP/IPv6 NS offload, and survey/statistics retrieval.

## Risks and Test Signals
This file is firmware ABI sensitive. Risks include padding drift, enum reordering, endian-sensitive bitfields, variable-length trailing arrays, fixed template-size truncation, version mismatches between v0/v1 STA/BSS layouts, and using config IDs unsupported by a given firmware revision. Security-sensitive paths include key material layout, TKIP MIC ordering, replay counters, GTK offload status, and wake packet data. Test signals include SMD request/response length validation, old firmware 1.2.2.x compatibility, WCN3620/WCN3660/WCN3680 feature differences, association as STA and AP, key install/remove for WEP/TKIP/CCMP, scan offload and software scan fallback, WoWLAN suspend/resume with ARP/NS/GTK offload, AMPDU setup/teardown, beacon/probe template programming, multicast filter updates, and stats/survey retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/main.c

## Purpose
Implements the WCN36xx platform driver and mac80211 operations. It registers the hardware, describes supported channels/rates/capabilities, maps platform resources, opens the Qualcomm WCNSS control channel, starts/stops firmware and DXE DMA, handles interface/station/BSS/key/scan/power-management callbacks, and wires suspend/resume offloads into mac80211.

## Important APIs, Types, and Functions
The `wcn36xx_ops` table is the main mac80211 integration point, providing `.start`, `.stop`, `.config`, `.tx`, `.set_key`, `.hw_scan`, `.cancel_hw_scan`, software scan hooks, `.bss_info_changed`, interface and station add/remove, AMPDU actions, suspend/resume, multicast filtering, flush, survey, and station statistics. `wcn36xx_probe()` and `wcn36xx_remove()` are the platform-driver lifecycle functions. `wcn36xx_init_ieee80211()` sets hardware flags, interface modes, 2.4/5 GHz bands, VHT support for WCN3680, cipher suites, queue count, WoWLAN support, and private data sizes.

Important helpers include `wcn36xx_start()` and `wcn36xx_stop()` for SMD/DXE lifecycle; `wcn36xx_config()` for channel, power-save, and idle changes; `wcn36xx_change_opchannel()` and `wcn36xx_change_ps()` for per-VIF firmware updates; `wcn36xx_set_key()` for WEP/TKIP/CCMP key programming; `wcn36xx_bss_info_changed()` for join, association, AP beaconing, SSID, beacon/probe templates, and link-state transitions; `wcn36xx_ampdu_action()` for BA session control; and `wcn36xx_platform_get_resources()` for IRQ, SMEM state, CCU/DXE MMIO, Pronto variant, and RF module discovery.

## Control Flow and State
Probe allocates `ieee80211_hw`, initializes mutexes, allocates the HAL buffer and survey table, sets a 32-bit DMA mask, reads the NV firmware name and optional local MAC address, opens the `WLAN_CTRL` rpmsg channel, maps resources, initializes the wiphy, and registers mac80211 hardware. Start opens SMD, allocates DXE memory pools and control blocks, loads NV data, starts firmware, optionally exchanges feature capabilities, initializes DXE, initializes debugfs, and initializes runtime lists/locks. Stop aborts any active scan, tears down debugfs, stops firmware, deinitializes DXE, closes SMD, and frees DXE resources.

Most firmware-facing state changes run under `wcn->conf_mutex`: channel changes, PS/idle transitions, multicast filtering, key programming, BSS association/AP transitions, interface and station lists, AMPDU setup, suspend/resume offload programming, RTS threshold, and station statistics requests. `scan_lock` protects `wcn->scan_req` and `scan_aborted`; `survey_lock` protects current band/channel and per-channel RSSI/SNR survey data; per-station `ampdu_lock` protects AMPDU state by TID. Runtime state includes `wcn->vif_list`, per-VIF `bss_index`, association and encryption state, per-STA hardware indexes and supported rates, firmware feature caps, current channel/survey data, scan ownership, IRQ numbers, MMIO mappings, and rpmsg endpoint.

## Dependencies and Integration Points
Depends on mac80211/cfg80211, platform and OF APIs, Qualcomm WCNSS rpmsg control, SMEM state handles, firmware loading, Linux DMA mask setup, IPv6 address notifications, and the local SMD/DXE/PMC/TXRX/debug/testmode modules. It translates mac80211 events into `smd.c` HAL messages described by `hal.h` and into DXE queue operations described by `dxe.h`. Device-tree integration requires `qcom,wcnss-wlan`, parent `qcom,mmio`, named `tx`/`rx` IRQs, `tx-enable` and `tx-rings-empty` SMEM states, `ccu`/`dxe` register ranges, optional `firmware-name`, optional `local-mac-address`, and optional `iris` child compatibility to distinguish WCN3620/WCN3660/WCN3680.

## Risks and Test Signals
Probe and start have staged resources and must unwind without leaking rpmsg endpoints, MMIO mappings, DXE memory, or firmware references. Firmware feature exchange is skipped for a specific old firmware version, so capability-gated paths need old/new firmware coverage. `wcn36xx_set_key()` rewrites TKIP key order for firmware expectations and assumes pairwise keys have a station private object. BSS and station hardware indexes are returned asynchronously through SMD responses and must remain valid across association, disassociation, AP mode, and STA removal. Scanning has two paths: firmware offload only when supported and under 49 channels, otherwise mac80211 software scan with explicit firmware scan-session management. Suspend disables IRQs after offload setup and resume reenables them after host-resume cleanup, making error ordering important. Test signals include platform probe/remove with all resource-failure unwind points, mac80211 start/stop, STA association/disassociation, AP beacon enable/disable, WEP/TKIP/CCMP keys, scan offload and software scan, channel changes during scan, BMPS/IMPS power save, WoWLAN suspend/resume with GTK rekey data and IPv6 NS offload, AMPDU RX/TX start/stop, multicast filter updates, TX flush, survey/noise reporting, and WCN3620 versus WCN3680 band/VHT capability selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.c

## Purpose
Implements the small WCN36xx power-management controller layer for BMPS station power save and keepalive null-packet programming. It translates driver policy decisions from `main.c` into SMD power-management requests and updates per-VIF power state.

## Important APIs, Types, and Functions
`wcn36xx_pmc_enter_bmps_state()` asks firmware to enter BMPS for a VIF, updates `vif_priv->pw_state`, resets the BMPS failure counter, and enables mac80211 beacon filtering on success. `wcn36xx_pmc_exit_bmps_state()` exits BMPS only when the VIF is currently marked `WCN36XX_BMPS`, restores `WCN36XX_FULL_POWER`, and clears the beacon-filter driver flag. `wcn36xx_enable_keep_alive_null_packet()` sends a firmware keepalive request using `WCN36XX_HAL_KEEP_ALIVE_NULL_PKT`. `WCN36XX_BMPS_FAIL_THREHOLD` defines the failure count that triggers connection-loss reporting.

## Control Flow and State
Entering BMPS calls `wcn36xx_smd_enter_bmps()`. On success it stores BMPS state in `struct wcn36xx_vif` and sets `IEEE80211_VIF_BEACON_FILTER`; on failure it increments `bmps_fail_ct` and calls `ieee80211_connection_loss()` once the threshold is reached. Exiting BMPS is guarded against unbalanced calls: if the VIF is not in BMPS it returns `-EALREADY` without sending firmware exit. Keepalive programming is stateless in this file and delegates to SMD.

## Dependencies and Integration Points
Includes `wcn36xx.h`, which provides `struct wcn36xx_vif`, logging, HAL constants, and SMD declarations. `main.c` calls BMPS enter/exit from `wcn36xx_change_ps()` when mac80211 toggles `IEEE80211_CONF_PS` and calls keepalive setup after STA association. Firmware message layouts are defined in `hal.h` by BMPS and keepalive request/response structures.

## Risks and Test Signals
The TODO about ensuring a clean TX chain before BMPS means entering power save while frames are pending can be risky. Failure handling intentionally converts repeated BMPS failures into connection loss, so transient firmware timing after association can disrupt connectivity if the threshold is too aggressive. Exiting when the software state is stale skips firmware exit. Test signals include PS enable/disable around association, BMPS enter before first beacon, repeated BMPS failure causing connection loss, beacon-filter flag transitions, keepalive request success after association, and suspend/resume interactions with BMPS state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.h

## Purpose
Declares the WCN36xx power-management controller interface and the per-VIF power-state enum used by the driver.

## Important APIs, Types, and Functions
`enum wcn36xx_power_state` has `WCN36XX_FULL_POWER` and `WCN36XX_BMPS`, stored in `struct wcn36xx_vif`. The header declares `wcn36xx_pmc_enter_bmps_state()`, `wcn36xx_pmc_exit_bmps_state()`, and `wcn36xx_enable_keep_alive_null_packet()`.

## Control Flow and State
The header owns no runtime flow. Its enum values define the software power state that gates whether `pmc.c` sends BMPS exit requests and whether mac80211 beacon filtering is considered active for a VIF.

## Dependencies and Integration Points
Forward-declares `struct wcn36xx` and relies on including contexts for `struct ieee80211_vif`. Included through `wcn36xx.h`, making the PMC API available to `main.c` and other driver modules. The implementation delegates to SMD messages whose ABI is declared in `hal.h`.

## Risks and Test Signals
Prototype drift would break the power-save integration in `main.c`. Because only two software power states are modeled, additional firmware states such as IMPS, UAPSD, and WoWLAN are tracked elsewhere and must not be inferred from this enum. Test signals are compile coverage with mac80211 power-save code, BMPS enter/exit state transitions, and keepalive programming after association.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.h -->
