# sources/distributed-fs/ceph-client/drivers/net/ethernet/oki-semi/pch_gbe/pch_gbe_ethtool.c

## Purpose
Supplies ethtool operations for PCH GBE identity, register dumps, WOL, autonegotiation, ring sizing, pause flow control, link settings, and driver stats.

## Important APIs, Types, And Functions
`pch_gbe_ethtool_ops` wires drvinfo, regs, WOL, nway reset, link, ringparam, pauseparam, strings/stats, and link ksettings. `pch_gbe_gstrings_stats[]` maps `struct pch_gbe_hw_stats` fields. `pch_gbe_set_ethtool_ops()` installs the table.

## Control Flow
Link changes reset PHY/MII state and restart or reset hardware. Ring changes may down the device, allocate replacement rings, set up resources, free old rings, and bring it up. Pause changes mutate cached flow-control mode and either restart autoneg or program MAC flow control. Stats reads update and copy counters by offset.

## State And Persistence
Mutates in-memory adapter state, MAC/PHY registers, WOL event bits, ring sizes, and feature-related settings. No persistence across unload/reboot.

## Dependencies And Integration Points
Uses generic MII ethtool helpers, PCI identity, MMIO register map, PHY MIIM helpers, and main driver up/down/resource APIs.

## Risks And Edge Cases
TX pending clamp uses RX min/max constants, currently equivalent but fragile. Live ring replacement rollback is complex. Register dumps read all MAC and 32 PHY registers. WOL is cached until suspend/shutdown programs hardware.

## Test Signals
Exercise `ethtool -i`, `-d`, `-S`, `-g/-G`, `-a/-A`, link setting changes, and WOL on stopped and running devices.
