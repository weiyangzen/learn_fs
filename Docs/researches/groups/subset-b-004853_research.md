# Research: subset-b-004853

Grouped research for MediaTek `mt76` Connac MCU helpers and MT76x0 common/PCI support files. Each section preserves the source path in its title and is wrapped for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.c

Purpose: this file implements shared MCU command helpers for MediaTek Connac-family mt76 devices. It is not MT76x0-specific; it serves newer Connac/Connac2/Connac3 chips by building packed command payloads, station/BSS/WTBL TLVs, scan requests, power-save/offload requests, coredump events, firmware/patch download transactions, and the TX descriptor wrapper for MCU messages.

Important APIs: firmware control is exposed through `mt76_connac_mcu_start_firmware`, `mt76_connac_mcu_patch_sem_ctrl`, `mt76_connac_mcu_start_patch`, `mt76_connac_mcu_init_download`, `mt76_connac2_load_patch`, `mt76_connac2_load_ram`, and `mt76_connac2_mcu_fill_message`. Association state is encoded by `__mt76_connac_mcu_alloc_sta_req`, `mt76_connac_mcu_sta_basic_tlv`, `mt76_connac_mcu_sta_tlv`, `mt76_connac_mcu_sta_cmd`, `mt76_connac_mcu_add_key`, `mt76_connac_mcu_sta_ba`, and WTBL helpers such as `mt76_connac_mcu_wtbl_generic_tlv`, `mt76_connac_mcu_wtbl_hdr_trans_tlv`, `mt76_connac_mcu_wtbl_ht_tlv`, and `mt76_connac_mcu_wtbl_ba_tlv`. BSS/vif programming is handled through legacy and unified paths including `mt76_connac_mcu_bss_omac_tlv`, `mt76_connac_mcu_bss_basic_tlv`, `mt76_connac_mcu_uni_add_dev`, `mt76_connac_mcu_uni_add_bss`, and `mt76_connac_mcu_uni_set_chctx`. Scan and WoWLAN entry points include `mt76_connac_mcu_hw_scan`, `mt76_connac_mcu_cancel_hw_scan`, `mt76_connac_mcu_sched_scan_req`, `mt76_connac_mcu_sched_scan_enable`, `mt76_connac_mcu_set_suspend_iter`, and GTK/ARP offload helpers.

Control flow: most functions allocate or extend an skb, append TLVs using `mt76_connac_mcu_add_tlv` or `mt76_connac_mcu_add_nested_tlv`, fill wire-format fields from mac80211 state, then send the message using `mt76_mcu_send_msg` or `mt76_mcu_skb_send_msg`. Firmware download first negotiates an address/length/mode command, streams scatter chunks, then starts firmware or finalizes a patch. Patch loading also acquires/releases a firmware semaphore and interprets region encryption metadata. `mt76_connac2_mcu_fill_message` prepends either a normal or unified MCU TXD, generates a nonzero 4-bit sequence, and marks query/set/CE/WA routing based on encoded command bits.

State and persistence: persistent driver state touched here includes MCU sequence numbers, `MT76_HW_SCANNING` and `MT76_HW_SCHED_SCANNING`, `dev->rnr`, `wiphy->fw_version`, `wcid->amsdu`, coredump queues, wake/suspend settings, and firmware-running state in lower layers. It also consumes regulatory state (`dev->alpha2`, channel flags, SAR/reg power), vif link indices, BSSID/multibssid fields, station capabilities, key material, and WoWLAN patterns.

Dependencies and integration: this code depends on mt76 core MCU transport, mac80211/cfg80211 station/vif/channel/key structures, WED offload when MMIO WED is active, kernel firmware loading, and packed ABI definitions from `mt76_connac_mcu.h`. It is used by chip-specific drivers as a shared serialization layer; callers choose the command ID while this file builds valid payloads.

Risks: the code is ABI-sensitive because packed layouts, little-endian conversions, TLV lengths, and nested TLV counters must match firmware. Firmware parsing trusts trailer/header counts enough to walk regions, so length validation and offset math are important. Scan and WoWLAN paths maintain bits before/after MCU calls; failed sends clear only some state. Key handling stores CCMP material for BIP batching and swaps TKIP MIC halves, so cipher regressions can break encryption. Version-dependent branches for Connac v1, Connac2, MT7925, MT799x, USB/SDIO/MMIO, and WED are major compatibility risk areas.

Test signals: build coverage should include all chip families that include this shared object. Runtime signals include successful patch/RAM firmware load logs, association/disassociation with HT/VHT/HE/EHT stations, BA session setup/teardown, key install/remove for CCMP/TKIP/BIP/GCMP variants, hardware and scheduled scan completion/cancel events, suspend/resume with WoWLAN/GTK/ARP offload, regulatory/SAR rate-power programming on 2/5/6 GHz, and coredump handling after firmware assert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.h

Purpose: this header is the shared Connac MCU ABI contract. It defines command encoding macros, firmware/patch metadata layouts, MCU TX/RX descriptors, BSS/STA/WTBL TLV structures, scan/offload/WoWLAN payloads, capability bits, event IDs, cipher mappings, and prototypes for the helpers implemented in `mt76_connac_mcu.c`.

Important types and APIs: key structures include `mt76_connac2_mcu_txd`, `mt76_connac2_mcu_uni_txd`, `mt76_connac2_mcu_rxd`, `mt76_connac2_patch_hdr`, `mt76_connac2_patch_sec`, `mt76_connac2_fw_trailer`, `mt76_connac2_fw_region`, generic `struct tlv`, `sta_req_hdr`, `wtbl_req_hdr`, many `sta_rec_*` and `wtbl_*` TLVs, `mt76_connac_bss_basic_tlv`, scan request/done structures, GTK/ARP/suspend/WoWLAN TLVs, and `mt76_sta_cmd_info`. Inline helpers include `mt76_connac_mcu_get_cipher`, `mt76_connac_mcu_gen_dl_mode`, `mt76_connac_mcu_get_wlan_idx`, and `mt76_connac_mcu_add_tlv`.

Control flow role: this file does not execute control flow directly beyond small inline encoders. It shapes control flow by defining how command IDs are constructed with `MCU_CMD`, `MCU_EXT_CMD`, `MCU_UNI_CMD`, `MCU_CE_CMD`, and query/WA/WM variants. The helpers in the C file then inspect these bit fields to choose descriptor format, query/set flags, and destination indexes.

State and persistence behavior: all structures are transient command/event payloads, but they encode persistent firmware state such as station connection state, BSS activation, WTBL entries, BA windows, security keys, channel context, WoWLAN triggers, rate-power SKU tables, and firmware download state. The inline WLAN index split is state-compatible behavior: non-v1 devices use low/high portions while v1 devices use the legacy low byte only.

Dependencies and integration: the header depends on `mt76_connac.h`, kernel bitfield/endian helpers, mac80211/cfg80211 constants, and mt76 core types. It is included by Connac chip drivers and the shared implementation, so any layout change affects firmware interoperability across multiple chips.

Risks: packed structure size and alignment are critical. The `static_assert` around `mt76_connac2_mcu_rxd` guards a flexible-array layout hazard. Command/event numeric IDs must remain synchronized with firmware. Several comments document subtle firmware semantics, such as unified command option bits, WoWLAN trigger bits, and rekey modes. Incorrect cipher mapping or download-mode generation can silently break security or firmware boot.

Test signals: compile-time `static_assert` and `BUILD_BUG_ON` checks catch some layout issues. Runtime validation comes from firmware command acknowledgements, event parsing, successful STA/BSS/WTBL programming, scan/WoWLAN behavior, and security interop with every advertised cipher. ABI changes should be tested against all Connac generations represented by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac_mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Kconfig

Purpose: this Kconfig file declares the MT76x0 driver build options. `MT76x0_COMMON` is an internal tristate selected by bus-specific variants and selects `MT76x02_LIB`. `MT76x0U` exposes USB dongle support and selects `MT76x02_USB`; `MT76x0E` exposes PCIe support for MT7610/MT7630 devices.

Important symbols: `MT76x0U` depends on `MAC80211` and `USB`, while `MT76x0E` depends on `MAC80211` and `PCI`. Both select `MT76x0_COMMON`; neither directly selects firmware or platform-specific regulatory features. Help text documents 802.11ac 1x1 433 Mbps devices and module build behavior.

Control flow and integration: Kconfig selection determines which objects the Makefile links. Selecting USB or PCIe pulls in the shared init/main/eeprom/phy code through `MT76x0_COMMON` plus bus-specific transport and firmware loaders.

State and persistence behavior: no runtime state is stored here. The persistent effect is build-time configuration in kernel `.config`, which controls module availability and dependency closure.

Dependencies: the file integrates with the parent mt76 Kconfig tree and relies on mac80211 plus either USB or PCI kernel subsystems. The common code depends on the mt76x02 library selected here.

Risks: missing dependency or select statements can produce link failures or drivers without required bus helpers. Because common code is selected only through USB/PCI variants, new bus support would need an additional symbol and Makefile object mapping.

Test signals: `make oldconfig`, `make menuconfig`, and kernel builds with `CONFIG_MT76x0U=m`, `CONFIG_MT76x0E=m`, both enabled, and each disabled should verify dependency and object selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Makefile

Purpose: this Makefile maps MT76x0 Kconfig symbols to kernel module objects. It is the build glue between `MT76x0_COMMON`, USB, and PCIe support.

Important targets: `mt76x0-common-y` contains `init.o`, `main.o`, `eeprom.o`, and `phy.o`. `mt76x0u-y` contains `usb.o` and `usb_mcu.o` outside this subset. `mt76x0e-y` contains `pci.o` and `pci_mcu.o`. The top-level `obj-$(CONFIG_...)` lines produce `mt76x0-common.o`, `mt76x0u.o`, and `mt76x0e.o` as selected.

Control flow and integration: the file ensures both bus modules link against the shared common module. `pci.c` and `pci_mcu.c` are built only for the PCIe variant; USB transport files are separate and not researched here.

State and persistence behavior: no runtime state. The persistent effect is object composition and module names in the kernel build output.

Dependencies: symbol names must match `Kconfig`, and object names must match source files. The commented `ccflags-y := -DDEBUG` is a local debug knob, left disabled.

Risks: adding common APIs without updating object membership causes unresolved symbols. Moving code between common and bus modules can change module dependencies and autoload behavior.

Test signals: kernel/module build with USB-only, PCI-only, and both variants should emit the expected objects and no unresolved exports from common code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.c

Purpose: this file loads, validates, and interprets MT76x0 EEPROM/efuse calibration data. It initializes MAC address, hardware capabilities, frequency/temp offsets, RX gain, per-rate TX power, and channel target power used by the PHY code.

Important functions: `mt76x0_eeprom_init` is the entry point called during common hardware init. `mt76x0_load_eeprom` tries `mt76_eeprom_init`, validates chip IDs with `mt76x0_check_eeprom`, falls back to efuse after `mt76x0_efuse_physical_size_check`, and reads `MT76X0_EEPROM_SIZE` bytes. `mt76x0_set_chip_cap`, `mt76x0_set_freq_offset`, and `mt76x0_set_temp_offset` populate device calibration/capability fields. Exported helpers `mt76x0_read_rx_gain`, `mt76x0_get_tx_power_per_rate`, and `mt76x0_get_power_info` feed channel switching and txpower programming.

Control flow: initialization loads EEPROM data, warns on unsupported version, copies the factory MAC, applies override data, programs the MAC address, then derives chip caps and offsets. TX power computation decodes CCK/OFDM/HT/VHT per-rate fields from EEPROM, applies BW deltas unless TSSI is enabled, then channel-specific power is selected from a channel map or target-power field.

State and persistence behavior: EEPROM contents are persistent hardware calibration data copied into `dev->mt76.eeprom.data`. Derived runtime state includes `dev->mphy.macaddr`, band capability flags, `dev->cal.rx.freq_offset`, `dev->cal.rx.temp_offset`, `dev->cal.rx.lna_gain`, RSSI offsets, and rate power tables. The code does not write EEPROM.

Dependencies and integration: it uses mt76 core EEPROM helpers, mt76x02 EEPROM offsets and parser helpers, Linux MTD/OF includes for platform EEPROM sources, and mac80211 channel data. PHY code calls these helpers on channel changes and txpower recalculation.

Risks: bad or unsupported EEPROM data can misconfigure bands, power, gain, or MAC address. Efuse size checking rejects default/empty efuse with fewer than five used blocks, which protects against bogus defaults but can block unusual hardware. Signed 6-bit and 8-bit decoding is error-prone. TSSI and non-TSSI code paths produce different target-power behavior.

Test signals: probe logs should show EEPROM version/FAE and valid ASIC IDs. Test with EEPROM file override and efuse fallback, MT7610/MT7630/MT7650 IDs, 2 GHz/5 GHz channels, TSSI enabled/disabled, and invalid EEPROM data. Regulatory/SAR-visible max power should align with decoded channel values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.h

Purpose: this header exposes MT76x0 EEPROM constants and helpers to common init and PHY code.

Important APIs: it defines `MT76X0U_EE_MAX_VER` as `0x0c`, `MT76X0_EEPROM_SIZE` as 512 bytes, and prototypes for `mt76x0_eeprom_init`, `mt76x0_read_rx_gain`, `mt76x0_get_tx_power_per_rate`, and `mt76x0_get_power_info`. Inline `s6_to_s8` converts signed 6-bit EEPROM rate values to `s8`; inline `mt76x0_tssi_enabled` reads `MT_EE_NIC_CONF_1_TX_ALC_EN`.

Control flow and state: callers use this header to gate PHY behavior. `mt76x0_tssi_enabled` controls whether txpower uses closed-loop TSSI calibration or static EEPROM deltas. `s6_to_s8` is used while populating `mt76x02_rate_power`.

Dependencies and integration: it includes `../mt76x02_eeprom.h` for EEPROM offsets and shared helpers and forward-declares `struct mt76x02_dev`. It is included by `mt76x0.h`, `eeprom.c`, `init.c`, and `phy.c`.

Risks: signed conversion and TSSI flag interpretation affect transmit-power limits and calibration. Changing the max version or EEPROM size can break compatibility with firmware/hardware data layout.

Test signals: compile users with no duplicate definitions, validate txpower decoding on known EEPROM dumps, and test TSSI-enabled and non-TSSI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/init.c

Purpose: this file implements shared MT76x0 hardware bring-up, MAC/BBP initialization, WLAN power control, MAC stop, txpower initialization, and mac80211 registration support for both USB and PCIe variants.

Important functions: `mt76x0_chip_onoff` toggles WLAN function state and optional reset; `mt76x0_mac_stop` drains TX/RX queues and disables MAC engines; `mt76x0_init_hardware` performs common post-firmware hardware setup; `mt76x0_register_device` initializes mt76/mac80211 registration and debugfs. Internal helpers include `mt76x0_set_wlan_state`, `mt76x0_reset_csr_bbp`, `mt76x0_init_bbp`, `mt76x0_init_mac_registers`, and `mt76x0_init_txpower`.

Control flow: common init waits for WPDMA/MAC readiness, resets CSR/BBP, enables MCU queue selection, writes common MAC tables, waits for TX/RX idle, initializes BBP and DCOC values, snapshots the RX filter, clears shared keys and WCIDs, loads EEPROM, and initializes PHY. Registration then initializes mt76x02 device data, configures MAC address lists, registers with mac80211, adjusts VHT LDPC on 5 GHz, computes per-channel original/max power, and adds debugfs.

State and persistence behavior: it programs hardware registers, clears security/WCID tables, stores `dev->mt76.rxfilter`, initializes supported-band channel power fields, and schedules no work itself except through PHY init. It does not persist configuration to EEPROM.

Dependencies and integration: it relies on mt76 core MMIO/MCU accessors, `mt76x02` MAC/PHY helpers, `eeprom.c`, static tables from `initvals.h`/`initvals_init.h`, and PHY initialization from `phy.c`. Bus-specific probe paths call this after their firmware and DMA setup.

Risks: register sequencing is timing-sensitive. `mt76x0_set_wlan_state` deliberately does not disable WLAN clock because probe can otherwise fail. MAC stop loops can time out and only warn, leaving possible DMA/MAC residue. The init path assumes firmware is already running and hardware is responsive.

Test signals: probe/resume should pass WPDMA/MAC wait checks, no PLL/XTAL error should log, MAC stop should not warn about TX/RX failure, EEPROM/PHY init should complete, and registered bands should expose sane channel power values. Regression tests should cover USB and PCIe because register access mechanisms differ downstream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals.h

Purpose: this header contains the `mt76x0_bbp_switch_tab` table used to program BBP/AGC/RXFE settings according to RF band and bandwidth.

Important data: `mt76x0_bbp_switch_tab` is an array of `struct mt76x0_bbp_switch_item` values. Each row combines band/bandwidth masks such as `RF_G_BAND`, `RF_A_BAND`, `RF_BW_20`, `RF_BW_40`, and `RF_BW_80` with a BBP register/value pair. The table covers AGC registers 4, 6, 8, 12, 13, 14, 26, 27, 28, 31, 32, 33, 35, 39, 43, 51, 53, 55, 58, RXO 28, and RXFE 0.

Control flow and integration: `init.c` applies the subset matching G-band 20 MHz during initial BBP setup. `phy.c` applies the matching rows on every channel/bandwidth change through `mt76x0_phy_set_chan_bbp_params`, with special adjustment for `MT_BBP(AGC, 8)` based on EEPROM-derived LNA gain.

State and persistence behavior: this file has no executable state; it supplies constant calibration values written into BBP hardware registers at runtime. No values are persisted back to hardware storage.

Dependencies: it includes `phy.h` for the switch item type and RF mask constants. Register macros come indirectly from the mt76x02 headers included by users.

Risks: values are hardware-calibration constants. Incorrect masks can apply 2 GHz gain tables to 5 GHz channels or wrong bandwidth behavior. Since AGC 8 is dynamically adjusted, table shape must remain compatible with that special case.

Test signals: channel changes across 2 GHz/5 GHz and 20/40/80 MHz should maintain receive sensitivity, false CCA rates, and stable AGC. DFS/radar channels are particularly useful for observing gain behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_init.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_init.h

Purpose: this header provides static register tables for common MAC initialization, MT76x0-specific MAC initialization, BBP initialization, and DCOC calibration setup.

Important data: `common_mac_reg_table` programs beacon offsets, legacy/HT rates, RX filter, backoff, TX link/timeout/max length, LED, PBF, retry, protection, WPDMA, and timing registers. `mt76x0_mac_reg_table` programs IO/PBF/FCE, AMPDU length, TX software and power registers, LDO, HT control, PN padding, VHT fallback, and related MAC/PHY glue. `mt76x0_bbp_init_tab` initializes core, IBI, AGC, TXC/RXC, TXBE, RXFE, and RXO BBP blocks. `mt76x0_dcoc_tab` sets CAL registers 47-55.

Control flow and integration: `mt76x0_init_mac_registers` writes the common and MT76x0 MAC tables during common hardware init. `mt76x0_init_bbp` writes the BBP init table, selected switch-table rows, and DCOC table after BBP readiness is confirmed.

State and persistence behavior: all arrays are read-only constants. Runtime writes configure volatile hardware registers and are re-applied on probe/resume/reinit.

Dependencies: it includes `phy.h` for RF-related type context and is consumed by `init.c`. It relies on register macros from mt76/mt76x02 headers in the includer.

Risks: this file is register-programming data with little self-description. Wrong values can break DMA, aggregation, protection, power, or receive behavior. Some raw registers use numeric addresses, which are harder to audit than named macros.

Test signals: successful probe, DMA start, beaconing, TX/RX traffic, HT/VHT aggregation, key/WCID setup, and resume are practical tests. Hardware register dumps before/after init help diagnose regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_phy.h

Purpose: this header contains RF programming tables and frequency plans used by MT76x0 PHY channel setup and RF initialization.

Important data: tables include `mt76x0_rf_central_tab`, `mt76x0_rf_2g_channel_0_tab`, `mt76x0_rf_5g_channel_0_tab`, `mt76x0_rf_vga_channel_0_tab`, `mt76x0_rf_bw_switch_tab`, `mt76x0_rf_band_switch_tab`, `mt76x0_frequency_plan`, `mt76x0_sdm_frequency_plan`, `mt76x0_sdm_channel`, and `mt76x0_rf_ext_pa_tab`. The frequency plans map channels to PLL register fields and band classes including 2 GHz, 5 GHz low/mid/high, and 4.9 GHz/11J-style entries. Switch tables map RF bank/register writes to band and bandwidth combinations.

Control flow and integration: `phy.c` uses these arrays in `mt76x0_phy_rf_init`, `mt76x0_phy_set_band`, and `mt76x0_phy_set_chan_rf_params`. Initial RF setup writes central/2G/5G/VGA defaults with patching for chip/bus variants. Channel changes select a frequency-plan row, program PLL and SDM fields, apply bandwidth and band switch rows, and optionally apply external-PA rows.

State and persistence behavior: constants are not mutated. They configure volatile RF registers every init/channel-change. EEPROM-derived frequency offset and external PA capability combine with these table values at runtime.

Dependencies: it depends on RF macros and struct definitions from `phy.h`; consumers provide register access helpers for either direct RF CSR writes or MCU register-pair writes.

Risks: RF tables are extremely hardware-specific and high impact. Array index coupling between `mt76x0_frequency_plan` and `mt76x0_sdm_frequency_plan` means channel coverage/order changes must be synchronized. Incorrect band classification or external-PA values can cause poor sensitivity, failed channel lock, or regulatory power issues.

Test signals: tune every supported channel family, including channel 14, 4.9 GHz entries if enabled, low/mid/high 5 GHz, 20/40/80 MHz, and devices with external PA. Watch for VCO calibration failures, TX power anomalies, receive sensitivity drops, and firmware/BBP calibration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/initvals_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/main.c

Purpose: this file provides shared mac80211 configuration callbacks for MT76x0 devices: channel switching, SAR power updates, and general config changes.

Important functions: `mt76x0_set_channel` is the driver-op set-channel path used by bus drivers. `mt76x0_set_sar_specs` updates SAR constraints and reapplies txpower when running. `mt76x0_config` handles mac80211 `IEEE80211_CONF_CHANGE_CHANNEL`, `IEEE80211_CONF_CHANGE_POWER`, and `IEEE80211_CONF_CHANGE_MONITOR`.

Control flow: channel switching disables pre-TBTT, disables the DFS tasklet on MMIO devices, calls `mt76x0_phy_set_channel`, resets channel counters/EDCCA, reinitializes DFS params for MMIO, reenables the tasklet and pre-TBTT, and returns success. Power config updates channel data before locking, then applies SAR and calls `mt76x0_phy_set_txpower` only when the PHY is running. Monitor mode toggles the promiscuous bit in `dev->mt76.rxfilter` and writes `MT_RX_FILTR_CFG`.

State and persistence behavior: it mutates `mphy->chandef` through `mt76_update_channel`, `dev->txpower_conf`, current PHY txpower through PHY helpers, DFS/pre-TBTT tasklet state, EDCCA/channel counters, and the RX filter cache. No persistent storage is changed.

Dependencies and integration: it depends on mac80211 configuration callbacks, mt76 core channel/SAR helpers, mt76x02 DFS/EDCCA/MAC helpers, and `phy.c` for channel/txpower programming. `pci.c` wires these functions into `ieee80211_ops`/driver ops; USB code likely does the same.

Risks: channel changes interact with DFS tasklets and calibration work, so ordering matters. The monitor-mode condition is counterintuitive: non-monitor sets `PROMISC`, monitor clears it, so changes require careful validation against hardware semantics. SAR updates require a valid chandef and mutex protection.

Test signals: change channel width/band under traffic, scan/DFS on PCIe, update regulatory/SAR/power level, and toggle monitor mode while checking RX filter behavior and packet capture expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mcu.h

Purpose: this header defines MT76x0 MCU memory-map constants, calibration command IDs, bus-specific MCU init prototypes, and a simple firmware-running probe.

Important definitions: `MT_MCU_IVB_SIZE` is 0x40, `MT_MCU_DLM_OFFSET` is 0x80000, and `MT_MCU_MEMMAP_RF` is 0x80000000. `enum mcu_calibrate` assigns firmware calibration commands such as `MCU_CAL_R`, `MCU_CAL_RXDCOC`, `MCU_CAL_LC`, `MCU_CAL_TXIQ`, `MCU_CAL_VCO`, and `MCU_CAL_FULL`. Prototypes are `mt76x0e_mcu_init` and `mt76x0u_mcu_init`. Inline `mt76x0_firmware_running` reads `MT_MCU_COM_REG0`.

Control flow and integration: `pci_mcu.c` implements `mt76x0e_mcu_init`; USB code implements `mt76x0u_mcu_init`. `phy.c` uses the calibration enum for `mt76x02_mcu_calibrate` calls and uses `MT_MCU_MEMMAP_RF` for USB RF register access through MCU register-pair commands.

State and persistence behavior: constants address MCU memory and RF register maps; calibration commands alter firmware/hardware state at runtime but are not persisted by this header.

Dependencies: it includes `../mt76x02_mcu.h` for shared MCU command helpers and forward-declares `struct mt76x02_dev`.

Risks: memory-map constants must match firmware loaders and register-pair access. Calibration numeric IDs are firmware ABI values; changing them breaks PHY calibration.

Test signals: firmware boot should set `MT_MCU_COM_REG0` to 1, RF register-pair accesses should work on USB, and calibration commands should complete without errors during init/channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mt76x0.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mt76x0.h

Purpose: this is the central private MT76x0 header tying common code, bus drivers, firmware names, and shared function prototypes together.

Important APIs and constants: firmware names are `MT7610E_FIRMWARE`, `MT7650E_FIRMWARE`, and `MT7610U_FIRMWARE`. USB aggregation constants are `MT_USB_AGGR_SIZE_LIMIT` and `MT_USB_AGGR_TIMEOUT`. Inline helpers `is_mt7610e` and `is_mt7630` identify chip variants. The header declares init, registration, chip power, MAC stop, config, SAR, channel, PHY init/wait/channel/txpower/calibration functions.

Control flow and integration: bus-specific code includes this header to call common init and PHY functions. Common files include it to share prototypes and access mt76x02 definitions. Firmware loader code uses the firmware name macros for module firmware declarations and request_firmware paths.

State and persistence behavior: no direct state. The inline chip helpers read `mt76_chip` and bus type, influencing runtime branches for PA/current quirks, 5 GHz masking, and RF table patching.

Dependencies: includes Linux kernel, USB, mac80211, debugfs, and `../mt76x02.h`, plus `eeprom.h`. It is intentionally broad because it is the local umbrella header for the MT76x0 module.

Risks: the include guard name says `MT76X0U_H` even though it is used for both USB and PCIe; harmless but potentially confusing. Incorrect chip helper logic affects many hardware-specific branches. Firmware path changes must stay aligned with module firmware declarations and installed firmware blobs.

Test signals: compile all MT76x0 objects, probe MT7610E/MT7630/MT7650E and USB variants, verify correct firmware request strings, and check variant-specific branches such as MT7630 5 GHz masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/mt76x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci.c

Purpose: this file implements the PCIe MT76x0 driver: PCI probe/remove, mac80211 operations, start/stop, hardware init, suspend/resume, and module registration for MT7610/MT7630/MT7650 devices.

Important functions: `mt76x0e_probe` enables PCI, maps BAR0, sets DMA mask, allocates an `mt76x02_dev`, initializes MMIO, requests IRQ, and registers the device. `mt76x0e_init_hardware` powers WLAN on, loads MCU firmware through `mt76x0e_mcu_init`, initializes DMA when not resuming, runs common hardware init, configures beacon behavior, and applies PCI/chip quirks. `mt76x0e_start` starts MAC/calibration work; `mt76x0e_stop` and `mt76x0e_stop_hw` stop running state and drain DMA/MAC. `mt76x0e_cleanup`, `mt76x0e_remove`, `mt76x0e_suspend`, and `mt76x0e_resume` handle teardown and PM.

Control flow: probe follows standard PCI driver ordering: enable, map, master, DMA mask, disable ASPM, allocate mt76 device, init MMIO/revision, mask interrupts, request IRQ, then register. Registration calls hardware init and common mac80211 registration, then sets initialized state. Runtime start schedules MAC and calibration delayed work. Stop/suspend cancel work, disable workers/NAPI/DMA, clean queues, stop MAC, and power down. Resume restores PCI state, re-enables worker/NAPI, schedules NAPI, then reinitializes hardware with resume flag.

State and persistence behavior: persistent runtime state includes `MT76_STATE_RUNNING`, `MT76_STATE_INITIALIZED`, queue/NAPI state, DMA enable bits, delayed works, PCI power state, and WLAN function power. It reads EEPROM for quirks but does not persist hardware storage.

Dependencies and integration: integrates with Linux PCI, mac80211 `ieee80211_ops`, mt76 MMIO/DMA/IRQ helpers, common MT76x0 init/PHY/main APIs, PCI MCU loader, and mt76x02 shared callbacks for TX/RX, stations, keys, AMPDU, survey, and debug.

Risks: resume skips DMA init but still reinitializes hardware, so queue/NAPI ordering must be correct. Stop warnings mention TX DMA twice, including the RX wait path. Empty `flush` may be acceptable through mt76 queues but gives no explicit drain semantics. Hardware quirks for MT7610 PA current and raw registers need device coverage.

Test signals: PCI probe/remove, firmware load, IRQ RX/TX traffic, suspend/resume, module unload under traffic, DFS/channel switching, calibration work scheduling, and devices for all PCI IDs. Check no DMA busy warnings or queue leaks appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci_mcu.c

Purpose: this file implements PCIe firmware loading and MCU operation setup for MT76x0E devices.

Important functions: `mt76x0e_load_firmware` selects `mediatek/mt7610e.bin` for MT7610 or `mediatek/mt7650e.bin` for combo chips, validates `struct mt76x02_fw_header` size fields, uploads ILM/IVB/DLM regions, triggers firmware, polls `MT_MCU_COM_REG0`, and exports the ethtool firmware version. `mt76x0e_mcu_init` installs mt76x02 MCU ops and marks `MT76_STATE_MCU_RUNNING`.

Control flow: firmware is requested, header and total size are checked, version is logged, combo chips acquire a hardware semaphore, ILM is written through `MT_MCU_ILM_ADDR`, combo IVB is copied to `MT_MCU_IVB_ADDR`, DLM is written after remapping `MT_MCU_PCIE_REMAP_BASE4`, firmware is triggered by `MT_MCU_INT_LEVEL` for combo chips or `MT_MCU_RESET_CTL` for MT7610, and the running bit is polled. The semaphore is released and firmware object freed on all exits.

State and persistence behavior: it writes firmware into MCU RAM and control registers, sets `dev->mt76.mcu_ops`, updates firmware-version reporting, and sets the MCU-running state bit. Firmware contents are transient and reloaded on init/resume.

Dependencies and integration: depends on Linux firmware loader, mt76x02 firmware header format, mt76 MMIO copy helpers, common firmware name macros, and `mcu.h` memory constants. It is called from `pci.c` before common hardware init.

Risks: header length validation protects against malformed blobs, but any mismatch in ILM/DLM offsets or IVB handling prevents boot. Combo semaphore acquisition can time out. Firmware trigger register differs by chip class. The function releases the semaphore even on failure if combo, which is correct but must remain paired.

Test signals: firmware files present, correct version logs, `Firmware running!` debug after poll, ethtool firmware version, successful resume reload, and failure-path tests for missing/truncated firmware. Combo and non-combo chips should both be covered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/pci_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.c

Purpose: this file implements MT76x0 PHY/RF initialization, channel programming, transmit-power programming, calibration, temperature/TSSI compensation, and periodic gain adjustment.

Important functions: RF access is abstracted by `mt76x0_rf_wr`, `mt76x0_rf_rr`, `mt76x0_rf_rmw`, `mt76x0_rf_set`, and `mt76x0_rf_clear`, using direct RF CSR on MMIO and MCU register-pair access on USB. Public/common APIs are `mt76x0_phy_wait_bbp_ready`, `mt76x0_phy_init`, `mt76x0_phy_set_channel`, `mt76x0_phy_set_txpower`, and `mt76x0_phy_calibrate`. Internal helpers program band/frequency tables, antenna selection, BBP bandwidth, TSSI DC/ADC calibration, target/delta power, temperature sensor, gain, and RF init patching.

Control flow: PHY init initializes delayed calibration work, selects antenna/coexistence wiring from EEPROM, writes RF defaults, and sets RX/TX paths. Channel setup computes RF band/bandwidth and center-channel group, programs BBP bandwidth, mt76x02 bandwidth/band, EXT_CCA mapping, RF band tables, PLL/frequency plan fields, channel 14 filter, RX gain, BBP params, and VCO enable. If not scanning, it initializes AGC, calibrates, applies txpower, and queues calibration work. Calibration runs full/VCO/LC/RXDCOC sequences through MCU commands and handles TSSI-specific DC calibration on power-on.

State and persistence behavior: it mutates RF/BBP/MAC registers, `dev->cal` fields such as TSSI DC/target/temp/gain, `dev->rate_power`, `dev->target_power`, `dev->mphy.txpower_cur`, delayed `cal_work`, and gain/RSSI tracking fields. It relies on EEPROM-derived offsets and does not write EEPROM.

Dependencies and integration: it depends on `mcu.h`, `eeprom.h`, `phy.h`, `initvals.h`, `initvals_phy.h`, and mt76x02 PHY helpers. It is invoked from init, channel config, start calibration, and periodic delayed work. USB behavior depends on `MT76_STATE_MCU_RUNNING` because RF writes are routed through the MCU.

Risks: this is timing- and hardware-sensitive code. RF CSR access is mutex-protected, but register programming and delayed calibration interact with channel changes and device removal. Unsupported widths 5/80+80/160 are silently returned from BBP bandwidth helper. Frequency-plan arrays and SDM channels must stay aligned. TSSI math uses fixed-point saturation and signed EEPROM fields; mistakes affect regulatory power and link quality. `is_mt7630` skips calibration entirely.

Test signals: BBP ready logs, channel changes across 2/5 GHz and 20/40/80 MHz, scanning path without recalibration, periodic calibration under traffic, TSSI enabled/disabled devices, MT7630 special behavior, USB and PCI RF writes, external PA devices, temperature-triggered VCO/full recalibration, and txpower/current-power reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.h

Purpose: this header defines MT76x0 RF/PHY constants and table element types used by `phy.c` and static init tables.

Important definitions: RF band masks include `RF_G_BAND`, `RF_A_BAND`, low/mid/high/11J 5 GHz masks, and bandwidth masks `RF_BW_20`, `RF_BW_40`, `RF_BW_10`, `RF_BW_80`. `MT_RF`, `MT_RF_BANK`, and `MT_RF_REG` encode/decode RF bank/register offsets. PLL, VCO, SDM, and clock bit masks define fields used while programming frequency plans.

Important types: `mt76x0_bbp_switch_item` maps a band/bandwidth mask to a BBP register pair. `mt76x0_rf_switch_item` maps RF bank/register plus band/bandwidth mask to an RF byte value. `mt76x0_freq_item` describes per-channel PLL/SDM fields. `mt76x0_rate_pwr_item` and `mt76x0_rate_pwr_tab` model rate power and PA mode for CCK/OFDM/HT/VHT/STBC/MCS32 classes.

Control flow and integration: the header is consumed by `initvals.h`, `initvals_init.h`, `initvals_phy.h`, and `phy.c`. Its masks drive table matching during init and channel changes; its structures determine table layout.

State and persistence behavior: no runtime state. It defines how immutable tables are interpreted and how RF register addresses are encoded for runtime writes.

Dependencies: expects mt76 register-pair definitions and Linux bit macros from includers. It intentionally contains no function prototypes beyond types/constants.

Risks: wrong RF address encoding or masks would corrupt unrelated RF registers. `mt76x0_freq_item` field meanings must match the PLL programming sequence in `phy.c`; adding/removing fields requires synchronized table updates.

Test signals: compile all table users, verify RF register bank/reg bounds in `phy.c` do not warn, and validate channel tuning across every table category.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/phy.h -->
