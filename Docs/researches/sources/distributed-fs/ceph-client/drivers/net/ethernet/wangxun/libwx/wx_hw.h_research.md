# sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_hw.h

## Purpose
`wx_hw.h` declares the common hardware-control API for libwx PF and VF-capable drivers. It is the public boundary for register programming, reset, filtering, VLAN, RSS, flow control, and statistics helpers implemented in `wx_hw.c`.

## Important APIs, types, and functions
The header declares MDIO clause 22 and 45 accessors, interrupt enable/disable, flash-load and management checks, firmware host-interface commands, PPS firmware setup, EEPROM reads, MAC address setup, MAC filter add/delete/flush, multicast hash vector calculation, netdev MAC/MTU/Rx-mode operations, Rx queue control, RSS table/key storage, full Rx/device configuration, reset/stop/start helpers, MSI-X count discovery, software initialization, VLAN filter operations, flow-control enablement, and stats update/clear functions.

## Control flow and behavior
There is no executable logic in the header. The declarations outline the expected lifecycle: initialize software state, inspect flash/NVM, reset/start hardware, configure queues/RSS/Rx mode, service netdev changes, update stats, and stop/reset on teardown.

## State and persistence
The header owns no data. Its APIs act on `struct wx`, `struct net_device`, `struct wx_ring`, `struct mii_bus`, and hardware registers through implementation-defined helpers.

## Dependencies and integration points
It includes `<linux/phy.h>` for MII/MDIO bus types and relies on prior visibility of `struct wx`, `struct wx_ring`, and netdevice types from libwx headers. It is included by ethtool, datapath, PTP, and device-specific code that need common hardware operations.

## Risks and edge cases
This header exposes a broad low-level surface; call ordering is critical but not encoded in types. For example, `wx_configure_rx()` assumes rings/resources exist, VLAN operations assume initialized shadow tables, and stats update assumes a running netdev outside reset. Kernel API drift around VLAN prototypes, netdev features, or MDIO signatures would surface here.

## Test signals
Compilation across PF and VF drivers is the baseline. Integration tests should validate each netdev op wired from this header is only called after required initialization and is not called after resources are freed.
