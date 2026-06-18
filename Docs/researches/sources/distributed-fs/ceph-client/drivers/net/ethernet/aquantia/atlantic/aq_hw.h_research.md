## sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_hw.h

Purpose: central hardware abstraction contract for Atlantic chips and firmware.

Important APIs/types: defines hardware capabilities (`struct aq_hw_caps_s`), link status, statistics, hardware flags, media types, queue/filter limits, loopback private flags, chip feature bits, live hardware object (`struct aq_hw_s`), `struct aq_hw_ops` for chip-specific operations, and `struct aq_fw_ops` for firmware-mediated operations.

Control flow: no implementations, but this file defines the dispatch tables used throughout the driver. `aq_hw_ops` covers ring TX/RX, MAC address, reset/start/stop, IRQ, filters, multicast, interrupt moderation, RSS, traffic class rate limits, stats/registers, offloads, PTP, flow control, loopback, temperature, and module EEPROM. `aq_fw_ops` covers firmware init/reset, MAC retrieval, link speed/state/status, stats, temperatures, flow control, LED, power, PTP, EEE, PHY tunables, MACsec requests, and module EEPROM.

State and persistence: `struct aq_hw_s` contains atomic flags, MMIO base, firmware ops, link status, mailbox/RPC state, stats snapshots, interrupt moderation, chip feature bits, PTP offset, PHY id, and private chip data. This is live runtime state only.

Dependencies/integration: consumed by nearly every Atlantic source file. Hardware generation files fill `aq_hw_ops`; firmware utility files fill `aq_fw_ops`; `aq_main`, `aq_ethtool`, `aq_filters`, `aq_hw_utils`, and `aq_macsec` call through these tables.

Risks: this is a broad ABI inside the driver; signature changes have wide impact. Optional callbacks require defensive NULL checks. Flag constants mix hardware and NIC-level readiness semantics via macros referencing NIC flags, so include ordering and meaning must be consistent. Filter location constants define user-visible ethtool rule ranges.

Test signals: full Atlantic build, probe across supported chip revisions, ring TX/RX, firmware operations, PTP/MACsec optional paths, filter programming, loopback modes, and error flag propagation.
