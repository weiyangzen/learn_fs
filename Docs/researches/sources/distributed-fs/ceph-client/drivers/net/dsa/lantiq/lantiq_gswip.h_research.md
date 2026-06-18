# sources/distributed-fs/ceph-client/drivers/net/dsa/lantiq/lantiq_gswip.h

Purpose: shared GSWIP register, bitfield, descriptor, and private-state definitions for SoC GSWIP and standalone MaxLinear GSW1xx drivers.

Important APIs/types/functions: defines `struct gswip_pce_microcode`, `struct gswip_hw_info`, `struct gswip_gphy_fw`, `struct gswip_vlan`, `struct gswip_priv`, and declares `gswip_probe_common()`. Register groups cover MDIO, MII/PCDU, reset/version, buffer management/RMON, PCE tables, VLAN/bridge tables, MAC controls, FDMA/SDMA, and version comparisons.

Control flow: no executable flow. Descriptor fields drive runtime behavior: max ports, allowed CPU ports, per-port register availability, 2.5G support, microcode, tag protocol, phylink caps, PCS selection, and optional port setup.

State and persistence: `struct gswip_priv` carries regmaps, hardware info, DSA switch, device, RCU mapping, 64-entry VLAN shadow table, GPHY descriptors, PCE mutex, and normalized version.

Dependencies and integration: bitfield helpers, clocks, resets, phylink, platform devices, regmap, mutexes, DSA, PCE microcode headers, and both front-ends.

Risks and test signals: register-definition drift, version byte-order mistakes, wrong `mii_cfg` sentinel values, and packet length workaround assumptions. Test builds and runtime register programming across GSWIP 2.0/2.1/2.2 and GSW1xx descriptors.
