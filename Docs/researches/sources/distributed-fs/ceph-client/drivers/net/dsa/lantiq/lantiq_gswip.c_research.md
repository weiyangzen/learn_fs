# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.c

Purpose: SoC MMIO front-end for Lantiq/Intel GSWIP switches in VRX200, xRX300, and xRX330 SoCs. It maps register windows, validates version/compatible pairing, loads internal GPHY firmware, and delegates DSA behavior to common GSWIP code.

Important APIs/types/functions: `struct xway_gphy_match_data`; `gswip_gphy_fw_load()`, `_probe()`, `_remove()`, `_list()`; `gswip_probe()`/remove/shutdown; `gswip_xrx200` and `gswip_xrx300` `gswip_hw_info` descriptors.

Control flow: platform probe allocates private state, maps switch/MDIO/MII resources, initializes regmaps, gets match data, reads `GSWIP_VERSION`, validates it against the OF compatible, optionally loads `lantiq,gphy-fw`, calls `gswip_probe_common()`, and stores drvdata. Error/remove paths unload firmware.

State and persistence: stores regmaps, `hw_info`, RCU regmap, firmware descriptors, and common DSA state. GPHY firmware is copied into 16 KiB-aligned coherent memory and its DMA address is written to RCU registers until removal clears it.

Dependencies and integration: platform resources, regmap MMIO, syscon RCU, clocks, resets, firmware loader, OF children, Lantiq GPHY bindings, and common GSWIP code. Declares required firmware through `MODULE_FIRMWARE()`.

Risks and test signals: firmware/version mismatches, missing reset/clock resources, DMA alignment, required PHY settle delays, and strict compatible checks. Test firmware load, RCU programming, MDIO visibility, phylink caps by SoC/port, and CPU-port 6 validation.
