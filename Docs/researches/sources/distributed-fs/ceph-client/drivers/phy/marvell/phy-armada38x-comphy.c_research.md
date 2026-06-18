# sources/distributed-fs/ceph-client/drivers/phy/marvell/phy-armada38x-comphy.c

## Purpose
Armada 38x COMPHY driver focused on Ethernet SerDes speed switching for lanes configured as GBE. It exposes child lanes as PHYs, validates port/lane muxing, sets SGMII/1000Base-X/2500Base-X speed fields, and waits for TX/RX PLL ready.

## Important APIs, types, and functions
- `struct a38x_comphy` stores shared base, optional `conf` resource, device, and lane array.
- `struct a38x_comphy_lane` stores lane MMIO base, lane number, selected port, and parent.
- `gbe_mux[][]` maps lane/GBE port to expected selector values.
- `a38x_comphy_xlate()` validates port arg, prevents lane reuse, checks hardware selector, and returns the lane PHY.
- `a38x_comphy_set_mode()` supports `PHY_MODE_ETHERNET` with SGMII/1000BASEX/2500BASEX and polls PLL ready.

## Control flow
Probe maps base and optional `conf`, iterates child nodes with `reg`, creates PHYs, and registers custom xlate. Xlate binds a lane to a port only if the current selector matches GBE mux table. `set_mode()` disables optional config, writes speed generation, polls PLL status, and re-enables config on success.

## State and persistence
Per-lane selected `port` is cached in memory; hardware selector/speed/conf registers carry runtime state. No persistent storage.

## Dependencies and integration points
Generic PHY, platform MMIO, OF child nodes, Ethernet PHY interface mode constants. Consumers are Ethernet MAC/PCS drivers using generic PHY set_mode.

## Risks and test signals
Risks include port assignment not being reset after failed xlate, limited support to GBE despite broader COMPHY hardware, optional `conf` behavior changing link enable timing, and polling timeout. Test valid/invalid mux tables, all supported Ethernet submodes, duplicate lane requests, and 2500Base-X link training.
