# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb_ethtool.c

## Purpose
`igb_ethtool.c` implements the driver's ethtool surface. It exposes link settings, pause parameters, message level, register dumps, EEPROM reads/writes, driver info, ring sizing, offline/online self tests, wake-on-LAN, LED identify, interrupt coalescing, statistics strings/values, timestamp capabilities, RX flow classification, RSS hash fields and indirection, EEE settings, SFP module EEPROM reads, channel counts, private flags, and installs the `struct ethtool_ops`.

## Important APIs, Types, and Functions
The file defines stat descriptor tables (`struct igb_stats`, `igb_gstrings_stats`, `igb_gstrings_net_stats`), diagnostic labels, private flags, register-test tables per MAC generation (`reg_test_i210`, `reg_test_i350`, `reg_test_82580`, `reg_test_82576`, `reg_test_82575`), and the exported `igb_write_rss_indir_tbl`, `igb_add_filter`, `igb_erase_filter`, and `igb_set_ethtool_ops`. Important ethtool callbacks include `igb_get_link_ksettings`, `igb_set_link_ksettings`, `igb_get_regs`, `igb_get_eeprom`, `igb_set_eeprom`, `igb_set_ringparam`, `igb_diag_test`, `igb_get_ethtool_stats`, `igb_get_ts_info`, RX NFC get/set helpers, EEE get/set, module info/eeprom helpers, RSS get/set, channel get/set, and private flag get/set.

## Control Flow
Configuration mutators generally serialize against resets using `__IGB_RESETTING` or by calling `igb_reinit_locked`. Link setting changes validate management reset blocks, MDI/MDIX restrictions, autoneg vs forced speed, then restart the running interface or reset a stopped device. Pause changes either re-negotiate via reset or directly force MAC flow control and refresh RX SRRCTL. Ring parameter changes allocate temporary ring structures while the interface is down, then swap resources to preserve MSI-X ISR ring pointers.

The self-test path sets `__IGB_TESTING`. Offline tests save link settings, power up link, run link, register, EEPROM, interrupt, and loopback tests across resets, restore settings, and reopen the interface if needed. Online tests only perform the link test and mark invasive tests as passed. RX NFC insertion parses limited `ETHER_FLOW` masks, programs scarce hardware filters, adds the software rule under `nfc_lock`, and rolls back hardware on list update failure.

## State and Persistence
The file reads and mutates many `struct igb_adapter` fields: ring counts, queue counts, stats, `msg_enable`, `wol`, `rx_itr_setting`, `tx_itr_setting`, flags, RSS indirection table, NFC filter list/count, EEE advertisement, link settings, test rings, and LED state. It can also write persistent EEPROM contents via `igb_set_eeprom`, updating checksum and firmware version afterward. Hardware filter, RSS, EEE, interrupt, register-test, and loopback changes write MMIO registers and PHY registers.

## Dependencies and Integration Points
It integrates Linux ethtool APIs with igb internals from `igb.h`, low-level NVM ops, PHY helpers, MAC setup functions, PTP support, PCI/runtime PM, I2C SFP access, netdev queue APIs, DMA mapping, and XDP-aware rings. It is the user-facing control plane for many capabilities implemented elsewhere.

## Risks
The highest risks are invasive diagnostics and live reconfiguration. Register tests intentionally overwrite hardware registers and must be run offline. Loopback allocates test rings, forces MAC/PHY loopback, disables some PHY receiver behavior, and must clean up reliably. EEPROM writes can corrupt device configuration if magic, alignment, checksum, or flash presence checks are wrong. RX NFC uses both software list state and hardware table state; partial failure requires careful rollback. Enabling UDP RSS warns about fragmented packet reordering. Channel/ring changes can race with traffic if reset serialization is broken.

## Test Signals
Signals include correct `ethtool -k/-i/-S/-g/-c/-l/-x/-n` output, successful link setting changes with expected link renegotiation, register dump length/version stability, EEPROM read/write and checksum validation, online/offline self-test results, WOL persistence through suspend, LED identify operation, RSS distribution matching indirection table, filter add/delete steering traffic to requested queues, EEE negotiation reporting, SFP EEPROM reads, and no leaks or crashes when ring/channel changes fail allocation.
