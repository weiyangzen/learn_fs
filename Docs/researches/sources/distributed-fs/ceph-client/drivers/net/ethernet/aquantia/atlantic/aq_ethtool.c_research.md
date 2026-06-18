## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_ethtool.c

Purpose: ethtool control and reporting surface for Atlantic netdevices.

Important APIs/types: exports `const struct ethtool_ops aq_ethtool_ops`. Implements register dumps, link settings, driver info, statistics strings/data, LED identify, RSS get/set, RX NFC rule get/set, interrupt coalescing, WOL, timestamp info, EEE, pause parameters, ring sizing, message level, private loopback flags, PHY tunables, and module EEPROM access.

Control flow: ethtool callbacks translate userspace requests into `aq_nic_*`, `aq_hw_ops`, `aq_fw_ops`, PTP, MACsec, and filter helpers. Stats count and string generation are dynamic: base hardware stats plus per-queue/per-TC stats, optional PTP rings, and optional MACsec SC/SA stats. Ring parameter changes close/reopen the device when running. RSS updates write config then call hardware RSS programming. Coalescing accepts timing-based moderation and rejects unsupported frame-count combinations. Firmware-request operations such as LED, EEE, renegotiation, and flow control use `fwreq_mutex`.

State and persistence: modifies live `aq_nic_cfg_s` fields such as RSS key/table, interrupt moderation, WOL, EEE speeds, flow control, descriptor counts, msg level, private flags, and loopback settings. No disk persistence; settings last for device lifetime unless reapplied by upper layers.

Dependencies/integration: integrates with `aq_nic`, `aq_vec`, `aq_ptp`, `aq_filters`, `aq_macsec`, hardware and firmware ops, PCI, ethtool core, linkmode, and module EEPROM definitions.

Risks: dynamic stats counts must exactly match strings/data writers or userspace reads misalign. Some callbacks restart the interface and must preserve configuration. PTP TX/RX stats and MACsec stats are conditional on build/runtime state. Firmware/hardware EEPROM fallback must handle unsupported firmware cleanly. Private loopback allows only one loopback mode at a time and may restart for DMA network loopback.

Test signals: `ethtool -i/-S/-k/-K/-c/-C/-g/-G/-l/-n/-N/-x/-X/--show-eee/--set-eee`, WOL get/set, LED identify, PTP timestamp info, module EEPROM reads on fibre PHY, MACsec stats with active SAs, and running-interface ring/feature restart tests.
