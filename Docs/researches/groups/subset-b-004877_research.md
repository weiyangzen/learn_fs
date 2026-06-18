# Research: subset-b-004877

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/regs.h

## Purpose
`regs.h` is the register map and bit-field vocabulary for the `rtl8xxxu` USB Realtek driver. It names the hardware address space used by chip initialization, firmware download, EFUSE access, DMA setup, MAC/WMAC programming, security CAM access, beacon timing, RF/BB calibration, USB SIE configuration, and 8710B indirect/SYSON access. The file has no executable code; its value is the stable contract between chip-specific driver routines and Realtek RTL8xxxU-family hardware.

## Important APIs, Types, And Functions
The file exposes preprocessor constants only. Major regions are system configuration registers `REG_SYS_ISO_CTRL` through `REG_SYS_CFG2`, MAC-top registers such as `REG_CR`, `REG_MSR`, `REG_TRXDMA_CTRL`, `REG_RQPN`, `REG_RXDMA_AGG_PG_TH`, protocol/EDCA registers such as `REG_RESPONSE_RATE_SET`, `REG_ARFR*`, `REG_EDCA_*`, beacon/TSF registers, WMAC receive/filter/security registers `REG_RCR`, `REG_RXFLTMAP*`, `REG_CAM_CMD`, `REG_SECURITY_CFG`, baseband/RF registers under `REG_FPGA*`, `REG_CCK*`, `REG_OFDM*`, TX power/IQK registers, USB endpoint/register constants under `0xfe00`, and RF6052 register identifiers.

Important bit masks encode power isolation and clocks (`SYS_ISO_*`, `SYS_FUNC_*`, `APS_FSMCO_*`, `SYS_CLK_*`), firmware load state (`MCU_FW_DL_*`), chip/vendor/package discovery (`SYS_CFG_*`, `GPIO_OUTSTS_*`), interrupt status/masks (`IMR0_*`, `IMR1_*`, `USB_HIMR_*`), TX/RX DMA queues and page loading (`TRXDMA_*`, `RQPN_*`, `RXDMA_*`), response rates (`RSR_*`), receive acceptance policy (`RCR_*`), beacon control (`BEACON_*`, `DUAL_TSF_*`), security CAM commands (`CAM_CMD_*`, `CAM_WRITE_VALID`, `SEC_CFG_*`), and 8710B normal/EFUSE indirect offsets.

## Control Flow
There is no local control flow. Runtime control flow emerges when `rtl8xxxu` implementation files call `rtl8xxxu_read8/16/32()`, `rtl8xxxu_write8/16/32()`, masked writes, RF register helpers, firmware loaders, and chip-specific init functions with these constants. Typical sequences are power-on and clock enabling via the system registers, firmware download through `REG_MCU_FW_DL` and mailbox registers, LLT/TX page programming through DMA registers, RCR/filter setup for receive paths, CAM programming for keys, and RF/BB calibration through the baseband/RF register names.

## State And Persistence
The header itself persists no state. The constants address hardware state that persists in device registers while powered and is lost across USB disconnect, firmware reset, full power-down, or suspend paths that reset the MAC/BB/RF blocks. Some registers describe one-time or semi-persistent data sources, especially EFUSE and USB SIE fields, while most are live operational state. Backup/restore users in `rtl8xxxu.h` rely on these addresses to save ADDA, MAC, and BB calibration state around IQK and channel operations.

## Dependencies And Integration Points
The definitions depend on Linux `BIT()` and `GENMASK()` style bit helpers via including translation units. They integrate with all chip-specific `rtl8xxxu` code, firmware H2C/C2H mailbox flows, USB endpoint configuration, EFUSE parsing, mac80211 channel/rate/filter state, LED classdev code, security CAM programming, and Bluetooth coexistence hooks on combo chips. Several aliases and comments document generation-specific differences for 8188E/F, 8192C/E/F, 8723A/B/U, 8812/8821, and 8710B.

## Risks
The main risk is silent hardware misprogramming: many addresses are reused with generation-specific meanings, and several masks intentionally alias bits differently on different chips. A wrong constant can disable clocks, corrupt EFUSE access, misroute USB endpoints, break beacon timing, or install keys in the wrong CAM slot. The 8710B offset/indirect access rules are especially easy to violate because low register addresses need remapping or SYSON helper access. Bit-field comments are sparse in places and inherited from vendor drivers, so changes need hardware validation rather than compile-only confidence.

## Test Signals
Useful signals include successful probe across supported USB IDs, correct chip/vendor detection from `REG_SYS_CFG`, clean firmware download and `MCU_*_READY` transitions, working RX/TX DMA without queue stalls, correct beaconing and TSF behavior in AP mode, CAM key install/remove with encrypted traffic, RF calibration and channel changes without hangs, USB interrupt/bulk endpoint behavior, and suspend/resume or reset cycles. Register-read/write debug output and hardware traces are the primary diagnostics because this file has no unit-testable logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/rtl8xxxu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/rtl8xxxu.h

## Purpose
`rtl8xxxu.h` is the central private interface for the Realtek `rtl8xxxu` USB driver. It defines debug classes, USB control constants, TX page geometry, EFUSE layouts, RX/TX descriptor layouts, firmware/H2C/C2H message formats, rate and Bluetooth coexistence metadata, per-device private state, per-station/vif state, the chip operation table, and the cross-file helper prototypes used by the driver implementation.

## Important APIs, Types, And Functions
Key hardware data structures include `struct rtl8xxxu_rxdesc16`, `struct rtl8xxxu_rxdesc24`, `struct rtl8xxxu_txdesc32`, and `struct rtl8xxxu_txdesc40`, which model descriptor formats with endian-dependent bit fields. Rate constants `DESC_RATE_*`, `TXDESC_*`, and `enum ratr_table_mode_new` connect mac80211 rate decisions to firmware/HW descriptor fields. PHY-stat structures include `struct rtl8723au_phy_stats` and the Jaguar2 type 0/1/2 stat layouts.

Persistent identity/calibration data is represented by `struct rtl8xxxu_firmware_header`, `struct rtl8xxxu_power_base`, and chip-specific EFUSE structs for 8723AU/BU, 8192CU/EU/FU, 8188EU/FU, and 8710BU. H2C/C2H integration is described by `enum h2c_cmd_8723a`, `enum h2c_cmd_8723b`, `struct h2c_cmd`, `enum c2h_evt_8723b`, BT MP opcodes, and `struct rtl8723bu_c2h`.

The main runtime container is `struct rtl8xxxu_priv`, which stores USB device handles, URB anchors/lists, endpoint mappings, firmware and EFUSE data, calibration backups, chip capabilities, locks, queues, delayed work, Bluetooth coexistence state, rate-adaptation state, CFO tracking, LEDs, MAC-ID and CAM bitmaps, and mac80211 vif pointers. `struct rtl8xxxu_fileops` is the chip-specific dispatch table for identify, EFUSE parse, firmware load, power on/off, LLT, BB/RF init, calibration, channel setup, RX descriptor parsing, aggregation, statistics, RF control, USB quirks, TX power, rate masks, connect/RSSI reporting, TX descriptor fill, crystal cap, RSSI conversion, and chip capability constants.

Public prototypes cover register and RF access, masked writes, register backup/restore, PHY/RF init, firmware load/reset, endpoint config, EFUSE read, LLT setup, power-state transitions, calibration, channel setup, rate-mask reporting, aggregation, RX descriptor/stat parsing, TX descriptor fill, BT coexistence helper commands, crystal calibration, RA reports, and chip `fileops` objects.

## Control Flow
The header does not implement control flow, but it defines the objects that make probe and runtime dispatch possible. Probe allocates `rtl8xxxu_priv`, identifies a chip, selects one `rtl8xxxu_fileops`, reads/parses EFUSE into the union, loads firmware, configures endpoints, initializes BB/RF/MAC state, and registers mac80211. TX paths build a `rtl8xxxu_txdesc32` or 40-byte variant using the selected `fill_txdesc` callback and queue mapping constants. RX paths parse 16- or 24-byte descriptors, optionally parse PHY stats, then deliver frames to mac80211. Firmware command paths serialize `struct h2c_cmd` through mailbox helpers and parse C2H reports into BT, TX report, and rate-adaptation state.

## State And Persistence
`struct rtl8xxxu_priv` is the persistent driver state for a USB device lifetime. Hardware state is mirrored in capability flags, endpoint arrays, `regrcr`, RF path counts, power-index arrays, backup register arrays, firmware pointers, queue anchors, work items, and bitmaps for MAC IDs and security CAM slots. `rtl8xxxu_sta_info` persists per-station MAC-ID/RSSI state in mac80211 private storage, while `rtl8xxxu_vif` stores the port number and hardware key index. EFUSE data is retained in memory after parsing, but hardware registers and firmware state must be rebuilt after reset, disconnect, or full power cycling.

## Dependencies And Integration Points
The header depends on Linux USB, mac80211, LED, bitmap, average/EWMA, sk_buff, endian, and kernel locking/workqueue APIs. It integrates with `regs.h`, chip implementation files, firmware blobs, mac80211 callbacks, cfg80211 bands/rates, USB URB submission, security CAM management, Bluetooth coexistence, LED classdev registration, and rate control. `rtl8xxxu_fileops` is the key integration seam between common USB/mac80211 logic and per-chip hardware procedures.

## Risks
Descriptor bit fields and EFUSE packed structs are ABI-sensitive; endian mistakes, padding changes, or field width changes can corrupt RX status, TX control, power tables, or MAC addresses. `rtl8xxxu_fileops` mixes required callbacks and capability data, so a new chip definition with a missing or mismatched callback can fail late in probe or runtime. The large `rtl8xxxu_priv` state has several concurrency domains: URB locks, H2C mutex, station mutex, indirect-register mutex, workqueues, anchors, and bitmaps must stay coordinated. H2C/C2H formats differ between generations, making command length and command-id mistakes high-risk.

## Test Signals
Signals include descriptor parsing for both old and new chips, successful EFUSE parse with valid MAC/power/channel data, firmware load and H2C mailbox operation, TX/RX under aggregation, rate adaptation reports, security CAM allocation exhaustion behavior, LED and rfkill behavior, Bluetooth coexistence notifications, suspend/disconnect cleanup of URB anchors, and chip-specific probe coverage for each exported `rtl8xxxu_fileops`. Sparse/smatch and compiler warnings around packed bit fields are useful early warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl8xxxu/rtl8xxxu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Kconfig

## Purpose
This Kconfig file defines the build-time configuration surface for the legacy `rtlwifi` Realtek mac80211 driver family. It presents the parent `RTL_CARDS` menu, per-device PCI/USB driver symbols, common transport symbols, shared chip-family symbols, debug support, and Bluetooth coexistence support.

## Important APIs, Types, And Functions
The user-visible parent is `menuconfig RTL_CARDS`, a tristate that depends on `MAC80211` and either `PCI` or `USB`. Per-device symbols include `RTL8192CE`, `RTL8192SE`, `RTL8192DE`, `RTL8723AE`, `RTL8723BE`, `RTL8188EE`, `RTL8192EE`, `RTL8821AE`, `RTL8192CU`, and `RTL8192DU`. Internal/common symbols include `RTLWIFI`, `RTLWIFI_PCI`, `RTLWIFI_USB`, `RTLWIFI_DEBUG`, `RTL8192C_COMMON`, `RTL8192D_COMMON`, `RTL8723_COMMON`, and `RTLBTCOEXIST`.

Each device option selects the shared core and the needed transport. 8192C devices select `RTL8192C_COMMON`; 8192D devices select `RTL8192D_COMMON`; 8723A/B devices select `RTL8723_COMMON` and `RTLBTCOEXIST`; 8192EE, 8821AE, and 8723AE/BE select coexistence. `RTLWIFI` selects `FW_LOADER`, which is required by the family at runtime.

## Control Flow
There is no runtime control flow. Build control flow starts with the user selecting a device symbol or enabling the parent menu. Kconfig dependency resolution then selects the shared core, PCI or USB transport object, optional common chip directories, and optional coexistence library. The resulting `CONFIG_*` symbols drive the Makefile object graph.

## State And Persistence
The file persists kernel configuration decisions in `.config`, either built-in or module. Those decisions determine which object files are compiled and which modules are produced. Runtime driver state is not represented here, but missing symbols prevent device support from existing in the built kernel.

## Dependencies And Integration Points
This file integrates with mac80211, PCI/USB buses, firmware loading, the `rtlwifi/Makefile`, per-chip subdirectory Kconfigs/Makefiles through selected symbols, and kernel module naming. It also controls whether `RTLWIFI_DEBUG` compiles debug output support and whether `RTLBTCOEXIST` builds the shared coexistence code used by combo Wi-Fi/Bluetooth devices.

## Risks
Incorrect `select` or `depends on` relationships can produce broken builds, unresolved symbols, missing firmware loader support, or device drivers without required common code. The parent menu defaults to `y`, which can increase build surface in broad kernel configs. `RTLWIFI_DEBUG` also defaults to `y`, trading diagnostics for memory/code size. Bluetooth coexistence selection must stay aligned with chips that include combo behavior.

## Test Signals
Important signals are `allmodconfig`, `allyesconfig`, and minimal PCI-only/USB-only builds; module names matching help text; successful builds with and without `RTLWIFI_DEBUG`; and boot/probe coverage for each selected device symbol. Kconfig linting should confirm no impossible dependency paths or unselected common objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Makefile

## Purpose
This Makefile maps the `rtlwifi` Kconfig symbols to built objects and subdirectories. It builds the shared `rtlwifi.o` core, PCI and USB transport modules, chip-family common directories, per-device directories, and the optional Bluetooth coexistence library.

## Important APIs, Types, And Functions
The main object aggregate is `rtlwifi-objs`, made from `base.o`, `cam.o`, `core.o`, `debug.o`, `efuse.o`, `ps.o`, `rc.o`, `regd.o`, and `stats.o`. Transport aggregates are `rtl_pci-objs := pci.o` and `rtl_usb-objs := usb.o`. The Makefile then attaches subdirectories to symbols such as `RTL8192C_COMMON`, `RTL8192CE`, `RTL8192CU`, `RTL8192SE`, `RTL8192D_COMMON`, `RTL8192DE`, `RTL8192DU`, `RTL8723AE`, `RTL8723BE`, `RTL8188EE`, `RTLBTCOEXIST`, `RTL8723_COMMON`, `RTL8821AE`, and `RTL8192EE`.

## Control Flow
Build flow is declarative. When `CONFIG_RTLWIFI` is enabled, kbuild links the shared core object. Transport symbols pull in transport modules. Device and common-family symbols recurse into their subdirectories. Bluetooth coexistence is included only when `CONFIG_RTLBTCOEXIST` is enabled.

## State And Persistence
The Makefile persists no runtime state. It determines the module/object graph emitted by kbuild and therefore the boundaries of loadable modules and built-in code. The core module exports many helpers from `base.c` and adjacent files for transport and per-chip modules.

## Dependencies And Integration Points
It depends on the Kconfig file for `CONFIG_*` symbol validity and on each listed source file/subdirectory existing with matching object names. It integrates the shared core with transport and chip modules, including `btcoexist/Makefile` for coexistence code.

## Risks
Incorrect object membership can create unresolved symbols or duplicated definitions. Missing subdirectory wiring can silently omit a device driver even when Kconfig exposes it. The empty `rtl8192c_common-objs +=` line is harmless but notable because actual 8192C common code is built through the subdirectory entry, not this aggregate.

## Test Signals
Signals are successful kbuild for modular and built-in combinations, expected `.ko` names (`rtlwifi`, `rtl_pci`, `rtl_usb`, per-chip modules, and `btcoexist`), `modpost` without unresolved symbols, and probe tests proving per-chip modules can use shared core exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.c

## Purpose
`base.c` is the shared mac80211, rate, aggregation, watchdog, C2H, scan, and interoperability core for the legacy `rtlwifi` driver family. It initializes advertised bands/capabilities, sets common driver state and workqueues, derives transmit-control block descriptors from mac80211 TX metadata, manages special packet handling for power save/coexistence, tracks TX report acknowledgements, maintains aggregation state, detects AP loss and scan-list state, dispatches firmware events, builds SMPS/DELBA management frames, and identifies peer AP vendors for interoperability workarounds.

## Important APIs, Types, And Functions
Initialization APIs include `rtl_init_core()`, `_rtl_init_mac80211()`, `_rtl_init_hw_ht_capab()`, `_rtl_init_hw_vht_capab()`, `_rtl_init_deferred_work()`, `rtl_deinit_core()`, `rtl_deinit_deferred_work()`, `rtl_init_rfkill()`, `rtl_deinit_rfkill()`, and `rtl_init_rx_config()`. TX/rate APIs include `rtl_tid_to_ac()`, `rtl_mrate_idx_to_arfr_id()`, `rtlwifi_rate_mapping()`, `rtl_get_tcb_desc()`, `rtl_tx_mgmt_proc()`, `rtl_action_proc()`, `rtl_is_special_data()`, `rtl_get_hal_edca_param()`, and TX report helpers `rtl_tx_ackqueue()`, `rtl_set_tx_report()`, `rtl_tx_report_handler()`, `rtl_check_tx_report_acked()`, and `rtl_wait_tx_report_acked()`.

Aggregation APIs are `rtl_tx_agg_start()`, `rtl_tx_agg_stop()`, `rtl_tx_agg_oper()`, `rtl_rx_agg_start()`, `rtl_rx_agg_stop()`, and `rtl_rx_ampdu_apply()`. Workqueue and event APIs include `rtl_watch_dog_timer_callback()`, watchdog worker logic, `rtl_c2hcmd_enqueue()`, `rtl_c2hcmd_launcher()`, and firmware-event dispatch. Frame/interop helpers include `rtl_find_ie()`, `rtl_send_smps_action()`, `rtl_phy_scan_operation_backup()`, `rtl_make_del_ba()`, and `rtl_recognize_peer()`.

## Control Flow
At probe, `rtl_init_core()` calls `_rtl_init_mac80211()` to populate 2.4/5 GHz bands, HT/VHT capabilities, hardware feature flags, interface modes, WoWLAN data, queue counts, headroom, and permanent MAC address. It then initializes regulatory handling, locks, lists, queues, link state, and deferred work. Shutdown calls `rtl_deinit_deferred_work()` and `rtl_deinit_core()` to stop timers/work, drain C2H and TX report queues, free scan entries, and destroy the workqueue.

TX setup flows through `rtl_get_tcb_desc()`: it maps mac80211 rates into hardware descriptor rates, chooses driver-rate versus firmware fallback behavior, identifies multicast/broadcast/nullfunc/special frames, selects rate table IDs by wireless mode and RF type, applies bandwidth, short preamble, short GI, RTS/CTS/CTS-to-self, and TX report sequence metadata. Management auth frames mark the MAC as linking and request IQK. Action frames inspect BA categories; when an ADDBA request arrives while RX aggregation is already started, the file fabricates a DELBA frame back into mac80211 to release resources.

The watchdog timer queues `rtl_watchdog_wq_callback()` periodically. The worker computes rolling TX/RX and per-TID traffic averages, enters/leaves low power save unless Bluetooth coexistence controls LPS, updates throughput counters, runs chip dynamic-management watchdog hooks, detects AP silence and triggers `ieee80211_connection_loss()` after repeated missed beacon periods, invokes coexistence periodical work, expires scan-list entries, and fails stale TX report SKBs. Firmware C2H packets are either parsed immediately for fast BT MP commands or queued to the C2H workqueue and dispatched by command ID to TX report, rate report, and Bluetooth coexistence handlers.

## State And Persistence
Persistent state is kept in `struct rtl_priv` and nested `rtl_mac`, `rtl_phy`, `rtl_hal`, `rtl_ps_ctl`, `rtl_link_info`, `rtl_stats`, `rtl_tx_report`, `rtl_works`, scan-list, C2H queue, and per-station `rtl_sta_info` TID aggregation fields. Timers/workqueues persist periodic behavior after initialization. Scan-list entries and TX report SKBs are dynamic allocations freed on expiry/deinit. The file updates link state, beacon counters, traffic windows, power-save timestamps, Bluetooth 4-way-handshake flags, AP vendor classification, and aggregation state, but hardware/firmware state is programmed indirectly via callbacks in `rtlpriv->cfg->ops` and `rtlpriv->intf_ops`.

## Dependencies And Integration Points
The file integrates tightly with mac80211/cfg80211, Realtek shared headers (`wifi.h`, `rc.h`, `base.h`, `efuse.h`, `cam.h`, `ps.h`, `regd.h`, `pci.h`), the rtlwifi rate-control module, regulatory code, firmware C2H/H2C handlers, Bluetooth coexistence callbacks, chip `rtl_hal_ops`, transport TX hooks, Linux workqueues/timers/sk_buffs, and kernel IP/UDP parsing for DHCP/ARP/EAPOL special handling.

## Risks
Risk clusters are concurrency, packet parsing, and firmware/hardware ordering. Workqueue cancellation must be paired with timer deletion and queue draining to avoid use-after-free during device removal. `rtl_skb_ether_type_ptr()` trusts frame layout and encryption header assumptions, so malformed or short SKBs could be sensitive if callers do not guarantee length. TX report matching relies on a small sequence space and timeout fallback; stale or duplicated reports can misreport ACK status. Watchdog AP-loss logic depends on beacon and RX counters being updated correctly. Aggregation state is split between mac80211 and driver TID fields, with a fake DELBA workaround that must not regress normal BA negotiation. Peer OUI detection is heuristic and can misclassify APs.

## Test Signals
Signals include successful mac80211 registration with correct bands/capabilities, association in station/AP/IBSS/mesh/P2P modes, HT/VHT rate negotiation for 1T1R/2T2R devices, TX ACK status for EAPOL/nullfunc frames, DHCP/ARP/EAPOL power-save exits, BA start/stop and RX AMPDU behavior with BT coexistence enabled, watchdog-triggered roam on AP loss, scan-list growth/expiry, C2H TX-report/RA/BT event dispatch, SMPS action transmission, rfkill polling, workqueue cleanup under remove/suspend, and lockdep/KASAN coverage around timers and queued SKBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.h

## Purpose
`base.h` declares the shared `rtlwifi` base-layer API implemented primarily by `base.c` and consumed by core, transport, and chip-specific modules. It also defines common rate limits, TX descriptor sizing, 802.11 header offsets, helper macros for frame/header/descriptor fields, and AP peer-vendor identifiers.

## Important APIs, Types, And Functions
`enum ap_peer` classifies recognized AP vendors (`PEER_RTL`, Broadcom, Ralink, Atheros, Cisco, Marvell, and others). Constants include TX descriptor/header sizing, maximum HT/VHT bitrate values for capability advertisement, frame offset constants, listen interval and retry limits. Header mutation macros fill PS-Poll and 802.11 address fields, while `SET_TX_DESC_SPE_RPT()` and `SET_TX_DESC_SW_DEFINE()` set TX report descriptor bits through little-endian bit replacement.

Declared lifecycle and configuration APIs include `rtl_init_core()`, `rtl_deinit_core()`, `rtl_init_rx_config()`, rfkill init/deinit, watchdog/deferred-work cleanup, and scan-operation backup. TX/rate/report APIs include `rtl_get_tcb_desc()`, `rtlwifi_rate_mapping()`, `rtl_tx_mgmt_proc()`, `rtl_is_special_data()`, `rtl_tx_ackqueue()`, `rtl_is_tx_report_skb()`, `rtl_set_tx_report()`, `rtl_tx_report_handler()`, `rtl_check_tx_report_acked()`, `rtl_wait_tx_report_acked()`, `rtl_get_hal_edca_param()`, `rtl_mrate_idx_to_arfr_id()`, and `rtl_tid_to_ac()`. Aggregation and frame APIs include TX/RX AMPDU start/stop/operational helpers, `rtl_rx_ampdu_apply()`, `rtl_action_proc()`, `rtl_find_ie()`, `rtl_send_smps_action()`, `rtl_collect_scan_list()`, `rtl_scan_list_expire()`, and `rtl_recognize_peer()`.

## Control Flow
There is no executable control flow in the header. It establishes the call graph used by `core.c`, transport files, and per-chip drivers: initialization enters through `rtl_init_core()`, transmit paths request TCB descriptors and special-packet decisions, RX paths update beacon/scan/peer state, mac80211 aggregation callbacks delegate to declared AMPDU helpers, and firmware-event paths invoke C2H queue/launcher functions.

## State And Persistence
The header does not store state directly. Its macros mutate caller-provided frame or descriptor buffers, and its function prototypes operate on persistent `struct ieee80211_hw`, `struct rtl_priv`, `struct rtl_tcb_desc`, station, vif, SKB, and driver-private state declared elsewhere. Constants in this file shape persistent advertised capability state, TX descriptor layout, retry behavior, and AP vendor classification values.

## Dependencies And Integration Points
`base.h` depends on mac80211 types, rtlwifi private types from surrounding headers, endian bit helpers, and Ethernet address helpers. It is a shared integration point between `base.c`, `core.c`, `pci.c`, `usb.c`, chip modules, power-save code, Bluetooth coexistence, rate control, security/CAM code, and regulatory/channel handling.

## Risks
Macros cast raw pointers to unaligned integer pointers or descriptor offsets, so callers must provide correctly sized and aligned buffers. Descriptor bit positions must remain synchronized with per-chip descriptor formats. Any prototype drift breaks exported-symbol users across modules. Constants used in capability advertisement must stay consistent with actual chip support to avoid mac80211 enabling unsupported modes.

## Test Signals
Signals include clean builds of all rtlwifi modules, no modpost unresolved symbols, TX descriptor report bits appearing in firmware TX reports, correct PS-Poll/header construction, successful aggregation callbacks, correct EDCA register values, and runtime coverage of peer recognition and special-packet paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/Makefile

## Purpose
This Makefile builds the shared `btcoexist.o` module used by rtlwifi chips that need Realtek Wi-Fi/Bluetooth coexistence algorithms. It groups chip-specific coexistence implementations and the shared output-source/adapter layer.

## Important APIs, Types, And Functions
The aggregate `btcoexist-objs` includes `halbtc8192e2ant.o`, `halbtc8723b1ant.o`, `halbtc8723b2ant.o`, `halbtc8821a1ant.o`, `halbtc8821a2ant.o`, `halbtcoutsrc.o`, and `rtl_btc.o`. The module is attached to `obj-$(CONFIG_RTLBTCOEXIST)`.

## Control Flow
Build flow is controlled by `CONFIG_RTLBTCOEXIST`, selected by Kconfig for combo-capable rtlwifi devices. When enabled, kbuild compiles all listed coexistence algorithms into one object/module, regardless of which specific supported chip selected the symbol.

## State And Persistence
The Makefile has no runtime state. It determines whether coexistence object code is available for runtime callbacks through `rtlpriv->btcoexist` and BTC operation tables.

## Dependencies And Integration Points
It integrates with `rtlwifi/Kconfig`, the top-level `rtlwifi/Makefile`, and headers under `btcoexist/` including the precompile header. Runtime integration is through `rtl_btc.o` and the chip-specific HAL BTC implementations consumed by the rtlwifi core and device drivers.

## Risks
Because all listed coexistence objects build together, one broken chip-specific file can break coexistence support for all chips. Missing an object from this list can produce unresolved callbacks or silently remove an algorithm. The module must stay aligned with `RTLBTCOEXIST` users in Kconfig.

## Test Signals
Signals include builds with `CONFIG_RTLBTCOEXIST=m/y`, successful `modpost`, probe of RTL8723/RTL8821/RTL8192E combo devices, and runtime BT coexistence notifications for scan, connect, special packets, AMPDU policy, and periodic watchdog callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbt_precomp.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbt_precomp.h

## Purpose
`halbt_precomp.h` is the common include aggregator for the rtlwifi Bluetooth coexistence implementation. It pulls in core rtlwifi headers, the coexistence output-source interface, chip-specific coexistence algorithm headers, bus-type constants, and local `BIT0` through `BIT31` definitions expected by imported Realtek coexistence code.

## Important APIs, Types, And Functions
The file defines include guards, includes `wifi.h`, `efuse.h`, `base.h`, `regd.h`, `cam.h`, `ps.h`, `pci.h`, `halbtcoutsrc.h`, and chip-specific headers for 8192E 2-antenna, 8723B 1/2-antenna, and 8821A 1/2-antenna coexistence. It defines `RT_PCI_INTERFACE`, `RT_USB_INTERFACE`, `RT_SDIO_INTERFACE`, and hard-codes `DEV_BUS_TYPE` to `RT_PCI_INTERFACE`. It also defines numeric bit masks `BIT0` through `BIT31`.

## Control Flow
There is no runtime control flow. Compile-time flow uses this header to make the imported coexistence source files see one consolidated environment of rtlwifi types, register/helper declarations, interface constants, and bit macros.

## State And Persistence
The header stores no runtime state. The selected bus constant and bit macros influence compiled coexistence logic. Runtime coexistence state lives in rtlwifi private structures and BTC-specific data structures declared in the included headers.

## Dependencies And Integration Points
It integrates the coexistence source tree with the broader rtlwifi core, including EFUSE data, base-layer helpers, regulatory/CAM/power-save state, PCI transport declarations, and chip-specific BTC algorithms. The local `BITn` macros reflect vendor-code expectations rather than the kernel `BIT()` macro style.

## Risks
The hard-coded `DEV_BUS_TYPE` as PCI is risky if shared coexistence code is reused by USB/SDIO rtlwifi variants or if logic branches on bus type. Local `BIT0`-`BIT31` definitions can collide with other headers or diverge from kernel idioms, though they are ordinary constants. As an include aggregator, adding heavy or order-sensitive headers can create circular include or compile-time coupling problems.

## Test Signals
Signals include clean builds of all `btcoexist-objs`, coexistence behavior on the chip families whose headers are included, no macro redefinition warnings, and runtime validation that bus-type-dependent coexistence decisions are correct for the actual transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbt_precomp.h -->
