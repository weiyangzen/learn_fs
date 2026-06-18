<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio.c

Purpose: provides generic exported helper routines for MDIO-compatible transceivers, especially Clause 45 probing, link status, auto-negotiation reporting, and ioctl mediation for drivers using `struct mdio_if_info`.

Important APIs/types/functions: exported symbols are `mdio45_probe`, `mdio_set_flag`, `mdio45_links_ok`, `mdio45_nway_restart`, `mdio45_ethtool_ksettings_get_npage`, and `mdio_mii_ioctl`. The helper uses `mdio_if_info` callbacks `mdio_read`/`mdio_write`, `prtad`, `mmds`, and `mode_support`.

Control flow: `mdio45_probe` scans MMDs 1-5, checks `STAT2`, reads device bitmaps, and records address/MMD presence. `mdio45_links_ok` clears latched bits then validates `STAT1` and fault state across MMDs. Ethtool reporting derives port type, supported/advertised modes, AN state, partner modes, speed, duplex, and 10GBASE-T MDI-X. `mdio_mii_ioctl` validates Clause 22/45 addressing or emulates common MII registers over Clause 45.

State and persistence: no owned persistent state; helpers update caller-owned `mdio_if_info` fields and ioctl/ethtool output structures. Hardware register changes occur only through callback writes such as flag setting and AN restart.

Dependencies/integration: depends on `linux/mdio.h`, ethtool legacy-link-mode conversion, MII ioctl data, and driver-supplied MDIO callbacks. It is a library module for Ethernet drivers rather than an MDIO bus controller.

Risks and test signals: risks include incomplete decoding for nonstandard next pages, negative MDIO reads being treated as bitfields in some paths, C22 emulation limits, and incorrect speed/duplex if hardware reports uncommon modes. Tests should mock read/write callbacks for C45 probe, link-fault latching, ioctl validation, and ethtool mode conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio.c -->
