# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7996/Kconfig

## Purpose
This Kconfig file declares build-time options for the MT7996 PCIe driver and optional NPU acceleration support.

## Important APIs, Types, And Functions
`CONFIG_MT7996E` is a tristate driver option selecting `MT76_CONNAC_LIB`, `WANT_DEV_COREDUMP`, and `RELAY`, and depending on `MAC80211` plus `PCI`. `CONFIG_MT7996_NPU` is a bool option depending on MT7996E and compatible `NET_AIROHA_NPU`, selecting `MT76_NPU`.

## Control Flow
There is no runtime flow. Kconfig resolution controls whether mt7996 objects are built and whether NPU-specific code is included.

## State And Persistence
Configuration persists in the kernel build `.config`. Selecting devcoredump and relay enables runtime support used by `coredump.c` and `debugfs.c`.

## Dependencies And Integration Points
It integrates with the kernel wireless menu, mac80211, PCI, mt76 connac library, devcoredump, relayfs, and optional Airoha NPU support.

## Risks
Incorrect dependency expressions can expose unbuildable combinations. The NPU dependency is specialized and must match symbol tristate semantics. Selecting RELAY is required for firmware binary logging support.

## Test Signals
`allyesconfig`, modular `MT7996E=m`, NPU enabled/disabled builds, and absence of missing-symbol errors validate the configuration.
