
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/trx.c

Purpose: Implements the RTL8192CE PCIe transmit and receive descriptor path. It translates mac80211 skb metadata into 92C hardware descriptors, maps hardware queues to firmware queue selectors, decodes RX descriptors into `rtl_stats` and `ieee80211_rx_status`, performs RSSI/EVM signal translation, exposes generic descriptor get/set helpers to the PCI core, and kicks hardware TX polling registers.

Important APIs/functions: `_rtl92ce_map_hwqueue_to_fwqueue()` selects `QSLT_BEACON`, `QSLT_MGNT`, or skb priority. `rtl92ce_rx_query_desc()` parses descriptor fields, handles robust-management decryption flag correction, maps rates with `rtlwifi_rate_mapping()`, and invokes `_rtl92ce_translate_rx_signal_stuff()` when PHY status is present. `rtl92ce_tx_fill_desc()` DMA maps the skb, fills rate, security, AMPDU, RTS/CTS, bandwidth, segment, buffer-address, MAC ID, and multicast bits. `rtl92ce_tx_fill_cmddesc()` builds a firmware command/beacon queue descriptor. `rtl92ce_set_desc()`, `rtl92ce_get_desc()`, `rtl92ce_is_tx_desc_closed()`, and `rtl92ce_tx_polling()` are the PCI ring integration hooks.

Control flow: TX starts with skb/frame classification, DMA mapping, optional station lookup under RCU, `rtl_get_tcb_desc()`, descriptor zeroing, first-segment-only rate/protection programming, segment ownership fields, buffer address programming, and optional hardware sequence enable for firmware-controlled power save. RX starts with descriptor bit extraction, status population, optional PHY status parsing, signal scaling, and return to the caller for mac80211 receive handling.

State and persistence: The file writes transient descriptor memory and persistent hardware DMA ownership bits. It reads `rtlpriv->dm.useramask`, `rtl_mac` operating mode/bandwidth/BSSID, power-save state, and station private rate indexes. DMA mappings persist until ring cleanup elsewhere; incorrect ownership or buffer address state can wedge TX/RX rings.

Dependencies/integration: Depends on `../pci.h`, `../base.h`, `../stats.h`, 8192CE register/PHY definitions, mac80211 frame helpers, DMA APIs, CAM/security state, and rtlwifi common rate/signal helpers. It is wired into the 8192CE PCI HAL ops by the surrounding driver.

Risks: DMA mapping failure exits after logging but leaves higher layers dependent on cleanup behavior. Descriptor bit layout must match `trx.h`; any field drift corrupts DMA. RX robust-management handling is security-sensitive. `rtl92ce_is_tx_desc_closed()` ignores the requested `index` and checks `ring->idx`, which is worth regression testing if ring indexing changes. The beacon descriptor ownership exception is hardware-specific.

Test signals: Exercise PCIe TX with data, management, nullfunc, fragmented, multicast, encrypted, and AMPDU frames; verify DMA mappings are unmapped by ring completion code. RX tests should validate CRC/ICV flags, HT/40 MHz rate mapping, robust management frame decryption handling, RSSI/EVM reporting, and beacon/probe/data receive paths. Hardware tests should confirm `REG_PCIE_CTRL_REG` polling per queue and no stuck OWN bits under suspend/resume.
