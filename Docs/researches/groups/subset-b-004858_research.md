# subset-b-004858 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mac.c

Purpose: SDIO MAC/reset support for MT7921, covering interrupt masking, firmware/driver ownership transitions, Wi-Fi subsystem reset, host-card reset, and full MAC recovery for the SDIO variant.

Important APIs/types/functions: `mt7921s_wfsys_reset()` toggles `MCR_WHCR` reset bits and waits for `WF_RST_DONE`; `mt7921s_init_reset()` performs early reset with MCU queues drained; `mt7921s_mac_reset()` is the main SER recovery path. Internal helpers `mt7921s_enable_irq()`, `mt7921s_disable_irq()`, `mt7921s_check_bus()`, `mt7921s_host_reset()`, and work item `mt7921s_card_reset()` integrate SDIO/MMC host operations.

Control flow: reset starts by freeing pending TX SKBs, checking SDIO bus health, and returning early if the bus is marked hung. Otherwise it schedules TX queues, disables TX/SDIO workers, marks MCU reset, wakes waiters, purges MCU responses, waits for SDIO queues to empty, disables interrupts, performs WFSYS reset, reenables workers and IRQs, reloads firmware, reapplies EEPROM, reinitializes MAC, and restarts the device.

State and persistence: persistent state is in hardware registers, SDIO host state, `dev->mt76.bus_hung`, `dev->fw_assert`, `dev->mphy.state` bits, and mt76 worker/queue state. PM wake/sleep ownership is coordinated through `mt7921s_mcu_drv_pmctrl()` and `mt7921s_mcu_fw_pmctrl()`, but the file itself does not store durable configuration.

Dependencies/integration: depends on Linux SDIO/MMC APIs, mt76 SDIO helpers, connac2 MAC definitions, MT7921 firmware/eeprom/MAC startup functions, and mt76 worker/queue infrastructure. The global `msdio` and static `sdio_reset_work` bridge device reset to MMC host remove/add.

Risks: `msdio` is a single global pointer, so simultaneous SDIO devices would share reset context. Card reset removes/re-adds the MMC host and releases the SDIO IRQ, which is high impact. Reset sequencing is timing-sensitive and error handling after `readx_poll_timeout()` in `mt7921s_wfsys_reset()` does not propagate timeout failure.

Test signals: exercise SDIO firmware assert/SER, bus-hung detection, suspend/resume ownership handoff, TX queue drain during reset, and successful reload through `mt7921_run_firmware()`, `mt7921_mcu_set_eeprom()`, `mt7921_mac_init()`, and `__mt7921_start()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mcu.c

Purpose: SDIO-specific MCU transport and power ownership support for MT7921. It adapts common connac2 MCU messages to SDIO packet framing and implements driver-own/firmware-own transitions.

Important APIs/types/functions: `mt7921s_mcu_init()` installs `mt76_mcu_ops`, powers the chip to driver-own, runs firmware, and marks `MT76_STATE_MCU_RUNNING`. `mt7921s_mcu_send_message()` fills connac2 MCU TXD, chooses command versus firmware-download SDIO packet type, appends USB/SDIO header and padding, queues to `MT_MCUQ_WM`, and kicks the queue. `mt7921s_mcu_drv_pmctrl()` and `mt7921s_mcu_fw_pmctrl()` manipulate WHLPCR/mailbox ownership.

Control flow: command send refuses work during firmware assertion, fills the message, sets a three-second timeout, tags firmware scatter downloads as `MT7921_SDIO_FWDL`, aligns to four bytes, submits the raw MCU queue, and kicks. PM wake clears firmware-own request and polls PCR/mailbox until driver-own; PM sleep clears driver-own mailbox ack, requests firmware-own, and polls until ownership drops.

State and persistence: updates `mdev->mcu.timeout`, `dev->mt76.mcu_ops`, `MT76_STATE_MCU_RUNNING`, `MT76_STATE_PM`, and PM awake/doze accounting in `pm->stats`. Hardware-visible state is SDIO WHLPCR/PCR and D2HRM3R mailbox state.

Dependencies/integration: uses `mt76_connac2_mcu_fill_message()`, `mt7921_mcu_parse_response`, mt76 SDIO queue operations, SDIO register helpers, and MT7921 firmware loader. The PM functions are consumed by SDIO reset and runtime PM paths.

Risks: ownership polling timeouts return `-EIO` and can block reset/recovery. `dev->fw_assert` deliberately returns `-EBUSY` to avoid common workqueue blockage, so callers must tolerate transient MCU send failures. Queue submission errors leave ownership and timeout state unchanged.

Test signals: verify firmware download over SDIO, normal MCU command/response sequences, ownership transitions around runtime PM, firmware assert behavior, and reset paths that call driver-own before touching registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/testmode.c

Purpose: cfg80211/mac80211 vendor testmode bridge for MT7921 RF test commands and queries. It exposes driver-private set/query netlink attributes and translates them into firmware test-control commands.

Important APIs/types/functions: `mt7921_testmode_cmd()` handles set operations; `mt7921_testmode_dump()` handles one-shot query dumps; `mt7921_tm_set()` switches normal/test/ICAP-like RF modes and sends `MCU_CE_CMD(TEST_CTRL)`; `mt7921_tm_query()` sends a query and copies `param0`/`param1` from `mt7921_rftest_evt`.

Control flow: entry points require the phy to be running, monitor mode enabled, and for dumps, mt76 testmode already enabled. Netlink data is parsed with mt76 testmode policy, then nested MT7921 driver data policy. Testmode switch disables PM and forces driver-own before enabling `MT76_TM_STATE_ON`; switching back to normal sends the command then clears test state and reenables PM.

State and persistence: modifies `phy->test.state`, `pm->enable`, and delayed/workqueue PM tasks. Firmware receives requested RF-test state, but no local durable configuration is stored.

Dependencies/integration: depends on cfg80211 testmode netlink, mt76 common testmode attributes, `mt76_mcu_send_msg()`, `mt76_mcu_send_and_get_msg()`, MT7921 RF-test command structures from `mcu.h`, and runtime PM helpers.

Risks: testmode is only reachable in monitor mode and returns `-ENOTCONN` otherwise. `mt7921_tm_query()` calls `dev_kfree_skb(skb)` on the `out` path even if send failed before assigning `skb`, which depends on compiler/control-flow assumptions and is worth auditing. Testmode disables power save, so failed normal-mode transitions can leave PM behavior altered.

Test signals: netlink policy validation, successful switch to RF test and back, query response formatting through `MT7921_TM_ATTR_RSP`, rejection outside monitor/running state, and PM restoration after normal mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/usb.c

Purpose: USB bus driver for MT7921U devices. It declares supported USB IDs, adapts MCU send and reset flows to USB endpoints, probes/registers the mt76 device, and implements USB suspend/resume.

Important APIs/types/functions: `mt7921u_probe()` allocates and registers the device; `mt7921u_mcu_send_message()` sends MCU/FWDL messages over bulk endpoints; `mt7921u_mcu_init()` installs MCU ops and runs firmware; `mt7921u_mac_reset()` recovers the chip; PM hooks `mt7921u_suspend()` and `mt7921u_resume()` coordinate HIF suspend and USB queue restart.

Control flow: probe selects mac80211 ops/features from firmware name, allocates mt76 device with USB/SDIO TX handlers, resets the USB device, initializes mt76 USB bus ops, reads ASIC revision, resets already-running firmware if needed, powers MCU, allocates queues, initializes DMA, configures TX fragmentation based on scatter-gather support, and calls `mt7921_register_device()`. Reset stops workers/RX/TX, resets WFSYS, resumes RX, powers MCU, initializes DMA, reruns firmware/eeprom/MAC, and restarts.

State and persistence: uses USB interface driver data, device revision, `dev->fw_features`, `dev->hif_ops`, `MT76_RESET`/`MT76_MCU_RESET` bits, UDMA firmware download select, PM suspended flag, and USB queue/DMA state. Firmware files are declared with `MODULE_FIRMWARE`.

Dependencies/integration: integrates Linux USB core, mt76 USB helpers, common MT792x USB helpers, MT7921 core registration, connac2 MCU framing, and mac80211 device ops. Device table includes MediaTek, Comfast, Netgear, and TP-Link IDs.

Risks: probe calls `usb_reset_device()` before mt76 initialization, which can disturb composite/host state if assumptions change. Resume heuristics depend on firmware suspend event bits and may require DMA reinit. Error cleanup must keep USB references, interface data, queues, and mt76 allocation balanced.

Test signals: enumerate every USB ID, firmware download over correct endpoints, reset after firmware assert, suspend/resume with and without DMA reinit, scatter-gather AMSDU behavior, and clean disconnect/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Kconfig

Purpose: Kconfig declarations for the MT7925 Wi-Fi 7 driver family. It separates common code from PCIe and USB front ends.

Important APIs/types/functions: `MT7925_COMMON` is a hidden tristate selecting `MT792x_LIB` and `WANT_DEV_COREDUMP`. `MT7925E` enables PCIe support and depends on `MAC80211` and `PCI`. `MT7925U` enables USB support, selects `MT792x_USB`, and depends on `MAC80211` and `USB`.

Control flow: build selection is user-facing for PCIe/USB modules. Selecting either bus driver selects the common MT7925 core; USB additionally pulls the MT792x USB support library.

State and persistence: no runtime state. Persistent effect is kernel build configuration and module availability.

Dependencies/integration: integrates with the mt76 Kconfig hierarchy, mac80211, PCI, USB, common MT792x library, and devcoredump support.

Risks: SDIO is not exposed for MT7925 in this file; adding one would require new config and Makefile objects. Common code always selects devcoredump, increasing dependency surface. Bus symbols must stay aligned with objects in `Makefile`.

Test signals: `allyesconfig`, modular PCIe-only, USB-only, and disabled builds should select the expected objects and avoid unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Makefile

Purpose: Object composition for MT7925 kernel modules.

Important APIs/types/functions: `mt7925-common.o` is built for `CONFIG_MT7925_COMMON`; `mt7925e.o` for PCIe; `mt7925u.o` for USB. Common objects are `mac.o`, `mcu.o`, `regd.o`, `main.o`, `init.o`, and `debugfs.o`; `testmode.o` is conditional on `CONFIG_NL80211_TESTMODE`; PCIe objects are `pci.o`, `pci_mac.o`, `pci_mcu.o`; USB object is `usb.o`.

Control flow: Kbuild combines common and bus-specific objects according to Kconfig symbols. The bus modules link against exported common symbols such as MAC/MCU helpers and mac80211 ops.

State and persistence: no runtime state. It controls built module contents.

Dependencies/integration: must match Kconfig symbols and exported functions across MT7925 common, PCIe, and USB source files.

Risks: missing a common object creates link failures; adding new exported bus helpers requires object list updates. Testmode code is excluded unless nl80211 testmode is enabled, so references must stay macro-guarded.

Test signals: compile with `CONFIG_MT7925E=m`, `CONFIG_MT7925U=m`, both enabled, and `CONFIG_NL80211_TESTMODE` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/debugfs.c

Purpose: debugfs controls and diagnostics for MT7925, including register access, firmware logging, runtime PM/deep sleep toggles, TX power tables, queue views, TX stats, PM stats, and chip reset/assert injection.

Important APIs/types/functions: `mt7925_init_debugfs()` registers all entries. `mt7925_reg_get/set()` uses MCU register access; `mt7925_fw_debug_set/get()` toggles firmware log forwarding; `mt7925_txpwr()` queries and prints per-rate power; `mt7925_pm_set/get()` controls runtime PM; `mt7925_deep_sleep_set/get()` controls deep sleep; `mt7925_chip_reset()` triggers reset or firmware assert.

Control flow: debugfs operations acquire mt792x mutex before MCU register/config operations. TX power allocates a `mt7925_txpwr` buffer, queries firmware for the active band, and prints CCK/OFDM/HT/VHT/HE/EHT tables with `127` as not-available. PM writes wake the chip, update user and effective PM flags, reschedule power save, and reject USB. Chip reset value `1` directly resets WFSYS; other values send an `"assert"` chip-config command to collect coredump before reset.

State and persistence: manipulates `dev->fw_debug`, `pm->enable_user`, `pm->enable`, `pm->ds_enable_user`, `pm->ds_enable`, PM statistics, and firmware log/deep-sleep state. Register writes go through firmware and affect hardware state.

Dependencies/integration: depends on debugfs, mt76 debugfs registration, mt7925 MCU helpers (`mt7925_mcu_regval`, `mt7925_mcu_fw_log_2_host`, `mt7925_get_txpwr_info`, `mt7925_mcu_set_deep_sleep`, `mt7925_mcu_chip_config`), and shared mt792x queue/PM debug functions.

Risks: debugfs register writes and chip reset/assert are privileged but can disrupt live traffic. Runtime PM and deep sleep are unsupported on USB and must be kept consistent with monitor mode. TX power output assumes firmware layout matches `struct mt7925_txpwr`.

Test signals: read/write each debugfs attribute, validate PM toggles on PCIe and `-EOPNOTSUPP` on USB, query TX power on all bands, trigger assert/reset in controlled setups, and verify debugfs creation failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/init.c

Purpose: MT7925 common hardware/device initialization. It initializes firmware/eeprom/MAC, mac80211 capabilities, work items, PM defaults, debugfs, hwmon thermal reporting, thermal protection, and deferred device registration.

Important APIs/types/functions: `mt7925_mac_init()` programs MDP RX length, enables de-aggregation, clears WTBL admission counters, initializes bands and basic rate table, and clears regulatory alpha2. `mt7925_register_device()` wires mt76/mac80211 state and queues `init_work`. `mt7925_init_work()` runs hardware init, capability setup, MLO setup, `mt76_register_device()`, debugfs, hwmon, thermal protection, and deep sleep. `mt7925_thermal_temp_show()` exposes MCU temperature in millidegrees C.

Control flow: registration initializes `dev->phy`, mt76 private pointers, worker functions, delayed work, waitqueues, locks, scan/coredump queues, reset/ROC/timers, PM defaults, ACPI SAR, WCIDs, wiphy settings, band capabilities, antennas, regulatory notifier, then queues deferred initialization. Hardware init retries MCU/eeprom/MAC setup up to `MT792x_MCU_INIT_RETRY_COUNT`, resetting between attempts.

State and persistence: initializes workqueues, timers, skb queues, PM flags, `MT76_STATE_INITIALIZED`, `hw_init_done`, coredump queues, scan queues, runtime/deep-sleep defaults, wiphy bands/capabilities, thermal hwmon device, and firmware-backed thermal/deep-sleep settings.

Dependencies/integration: uses firmware loading through `mt792x_mcu_init()` and MT7925 MCU helpers, mt76 EEPROM override, mt76 registration/wiphy/WCID helpers, mac80211 capabilities, hwmon, thermal, ACPI SAR, debugfs, regd notifier, coredump, and IPv6 neighbor-solicitation offload work when enabled.

Risks: deferred `init_work` means probe can return before registration completes; failure paths log and stop but do not always unwind already initialized work items. Hardware init retry depends on bus-specific reset working. Thermal and debugfs registration failures prevent later setup but not earlier resource creation.

Test signals: cold probe, firmware init retry after injected failure, debugfs/hwmon availability, thermal readout, PM defaults on USB versus non-USB, MLO capability registration, and successful `mt76_register_device()` with correct HE/EHT/antenna capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.c

Purpose: MT7925 MAC datapath and recovery logic. It parses RX descriptors, builds TX descriptors, handles TX status/free events, tracks airtime and ACK signal, routes MCU/RX packets, performs SER/coredump reset work, and provides USB/SDIO TX helpers.

Important APIs/types/functions: `mt7925_mac_write_txwi()` builds TXWI for 802.3/802.11 frames; `mt7925_queue_rx_skb()` dispatches RX packets; `mt7925_rx_check()` prefilters DMA RX; `mt7925_mac_fill_rx()` decodes RX metadata/rate/security/AMSDU; `mt7925_mac_add_txs()` and `mt7925_mac_tx_free()` process TX status/free reports; `mt7925_mac_reset_work()` and `mt7925_coredump_work()` implement recovery; `mt7925_usb_sdio_tx_prepare_skb()` and completion/status helpers support non-MMIO buses.

Control flow: RX begins by classifying packet type from RXD. TX-free and TXS packets update token/status state and are consumed; MCU events go to `mt7925_mcu_rx_event()`; normal frames are validated, descriptor groups are walked, status/rate/security fields are filled, optional header translation reversal is done, radiotap HE/EHT metadata is decoded, and frames enter `mt76_rx()`. TXWI construction chooses queue and packet format from beacon/inband discovery/PSD/data path, fills WCID/OMAC/band/WMM, handles fixed-rate cases, keys, no-ack, BIP, injected sequence numbers, and basic/beacon/multicast rate tables.

State and persistence: updates WCID statistics, packet IDs, tx status queues, airtime counters, `wcid->rate`, RSSI/ACK EWMA, A-MPDU state bits, reset flags, coredump message queue, scan state on reset, PM suspended state, and IPv6 NS offload queue. Hardware state is touched through WTBL reads/writes and reset calls.

Dependencies/integration: integrates mt76 DMA/token queues, connac3 radiotap decoding, mac80211 TX/RX status, WTBL register layout, MT7925 MCU event and reset helpers, devcoredump, USB/SDIO shared framing, IPv6 offload, and regulatory fallback after reset.

Risks: descriptor parsing is length-sensitive and must reject malformed RXD groups. Header translation reversal for fragmented mesh frames is complex and can corrupt skb layout if offsets are wrong. Reset work retries device reset ten times and then reconnects interfaces; partial failures can leave firmware/mac80211 state mismatched. TX-free parsing relies on firmware event format version.

Test signals: RX for legacy/HT/VHT/HE/EHT rates, checksum offload, security error flags, AMSDU, header translation, TX status reporting, BA session start, token cleanup, USB/SDIO TX pad handling, firmware coredump collection, SER reset with active AP/STA interfaces, and IPv6 NS offload send failure purge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.h

Purpose: MT7925 MAC header constants and WTBL address helper.

Important APIs/types/functions: defines WTBL rate/airtime offsets (`MT_WTBL_TXRX_CAP_RATE_OFFSET`, `MT_WTBL_TXRX_RATE_G2_HE`, `MT_WTBL_TXRX_RATE_G2`, `MT_WTBL_AC0_CTT_OFFSET`) and inline `mt7925_mac_wtbl_lmac_addr()`.

Control flow: `mt7925_mac_wtbl_lmac_addr()` writes `MT_WTBLON_TOP_WDUCR` with the WCID group selected from `wcid >> 7`, then returns the LMAC WTBL offset for the requested doubleword. MAC code uses it before reading/writing per-WCID WTBL counters/rate fields.

State and persistence: changes the WTBL-on top group selector register as a side effect before returning an address. No local state is stored.

Dependencies/integration: includes `mt76_connac3_mac.h` and depends on MT7925 register macros from the broader driver. It is used by `mac.c` station polling and WTBL update paths.

Risks: the helper has an implicit register side effect, so callers must serialize access through the same locking discipline used for other WTBL operations. Incorrect WCID or doubleword values can address unrelated WTBL state.

Test signals: station polling across WCID group boundaries, concurrent WTBL reads under mutex/driver serialization, and TX/RX rate/airtime updates for WCIDs above 127.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/main.c

Purpose: mac80211 operations for MT7925. It exposes HE/EHT/MLO capabilities and implements interface, station, key, scan, ROC, AP, PM, channel context, SAR, antenna, CSA, rfkill, and link-management operations.

Important APIs/types/functions: exported `mt7925_ops` is the central mac80211 ops table. Key helpers include `mt7925_init_he_caps()`, `mt7925_init_eht_caps()`, `mt7925_init_mlo_caps()`, `__mt7925_start()`, `mt7925_add_interface()`, `mt7925_mac_sta_add/remove/event()`, `mt7925_set_key()`, scan and sched-scan wrappers, `mt7925_change_vif_links()`, `mt7925_change_sta_links()`, channel-context ops, and CSA work.

Control flow: start programs regulatory channel domain and RTS threshold, resets counters, marks running, starts watchdog, and maybe rfkill polling. Interface add allocates BSS/WCID indexes and firmware device info. Station add allocates WCIDs per link, publishes RCU pointers, wakes PM, updates BSS before station records, and handles MLO primary/secondary ordering. Association updates BSS/STA records and MLO link selection. Removal tears down ROC, pending TX, firmware STA/BSS records, poll lists, WCIDs, and MLO state.

State and persistence: manages `vif_mask`, `omac_mask`, `valid_links`, `deflink_id`, per-link `mt792x_bss_conf`, per-link WCIDs, `mlo_pm_state`, queue parameters, PM flags, scan/ROC bits, channel context pointers, SAR power limits, CQM settings, CSA timers/work, IPv6 NS offload queue, and wiphy capabilities/flags. Firmware mirrors most BSS/STA/key/channel/PM state through MCU commands.

Dependencies/integration: integrates mac80211/cfg80211 callbacks, mt76 common helpers, MT7925 MCU and MAC helpers, regulatory code, EHT/HE capability encoding, MLO link APIs, IPv6 neighbor discovery, PM/WoW, SAR, rfkill, and channel switch mechanisms.

Risks: MLO link add/remove has complex partial failure handling; host-only unwind intentionally avoids firmware cleanup after MCU timeouts, relying on reset recovery. Several operations assume valid per-link context and can warn/fail if mac80211 ordering changes. Monitor mode disables PM/deep sleep and changes sniffer firmware state. Channel switch is unsupported for MLD and limited to associated STA contexts.

Test signals: add/remove AP, STA, P2P and monitor interfaces; associate/disassociate legacy and MLD stations; add/remove links; key install/remove across ciphers and MLO links; hardware/scheduled scans; ROC/join flows; AP start/stop and beacon offload; runtime PM and monitor transitions; SAR updates; channel context assignment/change/CSA; rfkill polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.c

Purpose: MT7925 firmware command/event implementation. It builds MCU TX headers, parses responses, handles unsolicited events, loads firmware/regulatory CLC data, configures BSS/STA/key/scan/ROC/power/filter/thermal/sniffer state, and exposes firmware helpers used by MAC/main/debugfs/bus code.

Important APIs/types/functions: exported functions include `mt7925_mcu_parse_response()`, `mt7925_mcu_regval()`, `mt7925_mcu_update_arp_filter()`, `mt7925_mcu_rx_event()`, BA setup, firmware run/eeprom/deep-sleep/thermal helpers, key and STA/BSS update functions, ROC/scan functions, channel-domain/CLC setup, `mt7925_mcu_fill_message()`, RTS/radio/rxfilter/RSSI monitor, and rate TX power programming. Numerous static helpers construct STA_REC, BSS_INFO, scan, WOW, CLC, and TX power TLVs.

Control flow: command responses validate sequence IDs and pull MCU headers before returning status. Firmware run loads firmware, queries NIC caps, loads CLC regulatory chunks, marks MCU running, and enables FW log-to-host. Unsolicited events are dispatched by event ID to HIF, debug log, ROC grant, scan done, TX done, beacon loss, RSSI monitor, or coredump handlers. STA/BSS updates allocate TLV skbs, append ordered firmware TLVs, and send UNI commands. Scans build header, request, SSID/BSSID/channel/misc/IE TLVs and set scan state until completion or cancel. TX power iterates static channel lists in batches and sends SKU power tables per band.

State and persistence: updates firmware-visible configuration for EEPROM mode, CLC regulatory rules, deep sleep, thermal thresholds, BSS/STA/key records, BA sessions, beacon offload/filtering, scan/sched-scan state, ROC grants/timers, ARP/NS offload, WoW patterns, channel domains, SAR/rate limits, RX filters, and RSSI monitor thresholds. Host state includes capability bits, MAC address, antenna/chain masks, EML cap, CLC buffers, scan queues, wait flags, coredump state, `fw_assert`, and PM/WoW side effects.

Dependencies/integration: depends on mt76 MCU allocation/send APIs, connac MCU TLV helpers, firmware loader, cfg80211/mac80211 scan/STA/BSS/key structures, regulatory CLC parser types, PM/WoW, devcoredump path via MAC event handling, and MT7925 register/MAC helpers.

Risks: many TLV layouts are packed firmware ABI and size/order sensitive. Several event parsers trust TLV lengths after basic checks; malformed firmware events can drop packets or misnotify mac80211. CLC parsing depends on firmware trailer region layout and EEPROM hardware type. MLO STA/BSS TLVs are complex and can desynchronize host/firmware on partial failures. `mt7925_mcu_sched_scan_enable()` sets `req->active = !enable`, which is counterintuitive and should be verified against firmware semantics.

Test signals: firmware boot and NIC capability parsing, CLC/regulatory country changes, register access, thermal query/protection, STA/BSS/key install for legacy and MLO, AP beacon offload, HW and scheduled scan including 6 GHz RNR, ROC grant/timeout/abort, WoW suspend patterns, coredump event handling, TX done events, SAR/rate power across 2/5/6 GHz, rxfilter/CQM RSSI monitor, and testmode command header behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.h

Purpose: MT7925 firmware ABI header. It defines MCU event IDs, packed command/event/TLV structures, firmware constants, cipher mapping, testmode payloads, scan/BSS/STA/power/offload structures, and exported MCU function prototypes.

Important APIs/types/functions: key structs include `mt7925_mcu_rxd`, `mt7925_mcu_uni_event`, `mt7925_txpwr_req/event`, scan TLVs, `bss_req_hdr`, `bss_rate_tlv`, `bss_mld_tlv`, `bss_eht_tlv`, `sta_rec_ba_uni`, `sta_rec_eht`, `sta_rec_sec_uni`, `sta_rec_hdr_trans`, `sta_rec_mld`, `sta_rec_eht_mld`, power-limit TLVs, ARP/NS/WoW TLVs, ROC TLV, and testmode command payloads. `mt7925_mcu_get_cipher()` maps Linux WLAN cipher suites to connac3 firmware cipher IDs.

Control flow: the header does not execute logic beyond the inline cipher mapping, but its structure definitions drive how `mcu.c` serializes commands and interprets events. Size macros `MT7925_STA_UPDATE_MAX_SIZE` and `MT7925_BSS_UPDATE_MAX_SIZE` determine skb allocation capacity for composite firmware messages.

State and persistence: no runtime state is stored in the header. It defines the serialized state exchanged with firmware for EEPROM, rate power, scan, BSS, STA, security keys, MLO, PM/offload, ROC, and testmode.

Dependencies/integration: includes `mt76_connac_mcu.h` and relies on Linux wireless cipher constants and mt76/connac shared TLV definitions. Prototypes are consumed by `main.c`, `mac.c`, `init.c`, `debugfs.c`, and bus-specific MT7925 drivers.

Risks: packed ABI structs must match firmware exactly; changing field sizes/order or allocation-size macros can break command parsing. Inline cipher mapping returning `CONNAC3_CIPHER_NONE` controls software fallback paths. Max scan/BSS/STA sizes must stay large enough as TLVs evolve.

Test signals: compile ABI users with sparse/packed warnings, install every supported cipher, exercise EHT/MLO STA and BSS records, scan with max SSID/BSSID/channel data, WoW patterns, ROC requests, and firmware response parsing against real firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mcu.h -->
