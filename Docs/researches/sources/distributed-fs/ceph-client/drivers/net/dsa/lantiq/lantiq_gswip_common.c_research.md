# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip_common.c

Purpose: shared DSA implementation for Lantiq/Intel/MaxLinear GSWIP-family switches, translating DSA port, bridge, VLAN, FDB, STP, phylink, MDIO, RMON, EEE, and MTU callbacks into PCE/VLAN/MAC/FDMA/SDMA register operations.

Important APIs/types/functions: private `struct gswip_pce_table_entry`; `gswip_pce_table_entry_read/write()`, `gswip_add_single_port_br()`, `gswip_vlan_active_create/remove()`, `gswip_vlan_add/remove()`, `gswip_pce_load_microcode()`, `gswip_mdio()`, phylink setters, `gswip_switch_ops`, and exported `gswip_probe_common()`.

Control flow: common probe initializes the PCE mutex, allocates/fills `dsa_switch`, normalizes version, registers DSA, then validates exactly one supported CPU port. DSA setup resets the switch, disables ports, initializes VLAN defaults, enables MDIO, loads PCE microcode, routes unknown traffic to CPU, disables MDIO autopolling, registers MDIO child bus, configures CPU special tagging, enables VLAN-aware switching, flushes MAC table, and marks ingress MTU enforcement.

State and persistence: maintains `priv->vlans[64]` mapping bridge/VID to active-VLAN entries and FIDs. PCE table accesses are locked. Hardware table, MAC, DMA, RMON, and port state persists until reset and must stay synchronized with the software VLAN cache.

Dependencies and integration: DSA, switchdev, phylink, OF MDIO, regmap polling, MII/PHY helpers, `lantiq_gswip.h` descriptors, HSR simple helpers, bridge device lookup, and DSA port maps.

Risks and test signals: high-risk areas are DSA-to-hardware VLAN/FID translation, 64-entry VLAN capacity, version-specific learning, 2048-entry MAC scans, CPU-port validation after registration, and GSWIP 2.2 VID indexing behavior. Test standalone isolation, VLAN-aware/unaware bridges, PVIDs, VLAN capacity errors, FDB add/delete/dump, fast age, STP, MDIO bus, RMON, EEE, and MTU enforcement near 2400 bytes.
