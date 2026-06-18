# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_mac.h

## Purpose
`fbnic_mac.h` defines the MAC-facing contract for the FBNIC driver: link/FEC/AUI enums, pause storm constants, sensor IDs, jumbo frame bounds, and the `struct fbnic_mac` operations table consumed by other driver modules.

## Important APIs, Types, And Functions
The key type is `struct fbnic_mac`, a vtable with hooks for register initialization, link events, link status, PHY/MAC preparation, statistics collection, link transitions, and sensor reads. Public prototypes are `fbnic_mac_init()`, `fbnic_mac_get_fw_settings()`, `fbnic_mac_ps_protect_to_config()`, `fbnic_mac_ps_protect_handler()`, and `fbnic_mac_check_tx_pause()`. Constants include pause storm unit conversion helpers, default/max pause storm timeouts, `FBNIC_MAX_JUMBO_FRAME_SIZE`, PMD states, link event enums, FEC mode bits, AUI modes, and sensor IDs.

## Control Flow
The header does not execute code, but it shapes the runtime flow. PCI probe initializes `fbd->mac`, phylink calls the prepare/link hooks, service work calls pause storm and link training helpers, and ethtool/hwmon paths call stats/sensor hooks through this table.

## State And Persistence
The header defines state values stored elsewhere: PMD state in `fbnic_dev`, FEC/AUI in `fbnic_net`, and pause storm timeout in `fbnic_dev`. `struct fbnic_mac` itself is normally static const implementation data, while hardware state lives in registers configured through the hooks.

## Dependencies And Integration Points
It forward declares `struct fbnic_dev` and references statistics structs declared in the broader driver headers. It is included by MAC implementation, phylink, PCI service logic, and netdev-facing code that needs jumbo MTU limits or link mode names.

## Risks
Enum bit meanings are consumed by register programming and phylink reporting. Changing AUI or FEC values breaks lane-mask logic, firmware setting translation, and ethtool FEC exposure. Pause storm constants depend on ASIC RXB clock granularity and register field width.

## Test Signals
Build coverage across `fbnic_mac.c`, `fbnic_phylink.c`, and netdev MTU paths is the primary signal. Runtime signals are correct MTU maximum, stable AUI/FEC translation, pause storm timeout bounds, and expected PMD state transitions.
