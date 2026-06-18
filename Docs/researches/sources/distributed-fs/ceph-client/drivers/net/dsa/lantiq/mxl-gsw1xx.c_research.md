# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/mxl-gsw1xx.c

Purpose: MDIO/SMDIO front-end for standalone Intel/MaxLinear GSW1xx Ethernet switches. It supplies paged SMDIO regmap access, chip identification, SGMII/1000BASE-X/2500BASE-X PCS support, per-chip descriptors, and common GSWIP DSA integration.

Important APIs/types/functions: `struct gsw1xx_priv`; `gsw1xx_config_smdio_badr()`, `gsw1xx_regmap_read/write()`, custom `regmap_bus`, PCS ops (`pcs_enable`, `pcs_disable`, `pcs_get_state`, `pcs_config`, `pcs_an_restart`, `pcs_link_up`), SGMII reset/PHY writes, phylink caps, `gsw1xx_probe()`/remove/shutdown, and `gswip_hw_info` descriptors for GSW12x, GSW140, GSW141, and GSW150.

Control flow: MDIO probe allocates state, initializes SMDIO-backed regmaps for switch/MDIO/MII/SGMII/GPIO/clock/shell windows, validates manufacturer and part IDs, initializes PCS if present, configures GPIO MMDIO pinmux, reads `GSWIP_VERSION`, initializes delayed work, calls `gswip_probe_common()`, logs part information, and stores drvdata. Remove/shutdown unregister or shut down DSA and cancel delayed work.

State and persistence: caches `smdio_badr` for the current 16-register SMDIO window. PCS state includes `tbi_interface`, hardware TBI/SGMII registers, and delayed work to clear RANEG after 10 ms. Common switch state lives in embedded `struct gswip_priv`.

Dependencies and integration: MDIO, custom regmap bus callbacks, phylink PCS, DSA, PHY polarity common props, OF match data, delayed work, common GSWIP code, `DSA_TAG_PROTO_MXL_GSW1XX`, and MaxLinear PCE microcode.

Risks and test signals: SMDIO page-window mistakes, nested MDIO locking, PCS resets disrupting links, polarity interpretation, RANEG erratum, per-chip CPU-port/2.5G differences, and ambiguous GSW150 slew scope. Test chip ID validation, register reads across windows, DSA registration per compatible, SGMII/1000BASE-X/2500BASE-X with/without in-band AN, delayed RANEG clearing, slew DT properties, and common bridge/VLAN/FDB behavior.
