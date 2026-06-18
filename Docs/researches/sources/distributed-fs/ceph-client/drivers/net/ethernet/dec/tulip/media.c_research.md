<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/media.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/media.c

Purpose: Implements shared Tulip MII/MDIO access, transceiver selection, duplex negotiation, and PHY discovery for the DEC 21x4x Tulip core and compatible chips.

Important APIs and functions: `tulip_mdio_read()` and `tulip_mdio_write()` bit-bang IEEE 802.3 MDIO over CSR9, with special paths for COMET internal registers and LC82C168 register 0xA0. `tulip_select_media()` interprets parsed EEPROM media-table leaves and programs CSR12 through CSR15 plus `tp->csr6`. `tulip_check_duplex()` reads `MII_BMSR` and `MII_LPA`, derives negotiated duplex with `mii_duplex()`, updates `FullDuplex` and `TxThreshold`, and restarts RX/TX when CSR6 changes. `tulip_find_mii()` probes PHY addresses, builds `tp->phys[]`, initializes advertising, and adjusts BMCR for autonegotiation or forced media.

Control flow: Open/probe paths call `tulip_select_media()` after EEPROM parsing and may call `tulip_find_mii()` during PCI probe. Media timers and link-change handlers later call `tulip_check_duplex()` to keep CSR6 synchronized with link partner capabilities. MDIO operations serialize through `tp->mii_lock`; CSR6 state changes rely on the core helper `tulip_restart_rxtx()`.

State and persistence: Persistent device state is in `struct tulip_private`: `phys[]`, `mii_cnt`, `advertising[]`, `mii_advertise`, `full_duplex`, `full_duplex_lock`, `cur_index`, `mtable`, `csr6`, and `dev->if_port`. The source does not write persistent storage; EEPROM media tables are consumed from memory built by `eeprom.c`.

Dependencies and integration: Depends on Linux MII constants, PCI MMIO helpers, `tulip.h` media capability arrays, `t21142_csr14[]`, and `medianame[]`. It integrates with `tulip_core.c` for startup, `timer.c` for media monitoring, and PNIC/PNIC2 link code for duplex checks.

Risks: MDIO bit-banging is timing-sensitive and chip-specific. Media leaf parsing uses byte layouts from EEPROM and casts unaligned data, so malformed tables can select incorrect CSRs. Link status is sticky and double-read behavior is needed. Restarting RX/TX under the wrong lock could race with interrupts.

Test signals: Exercise PHY probing with MII and no-MII boards, forced media options, COMET and LC82C168 special MDIO paths, link partner duplex changes, missing PHY return `0xffff`, and EEPROM media leaves of types 0 through 6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/dec/tulip/media.c -->
