# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool_common.h

## Purpose
`ethtool_common.h` is the public internal interface for the shared Solarflare `sfc` ethtool implementation. It declares reusable `efx_ethtool_*` handlers so NIC-specific driver files can build `struct ethtool_ops` tables without duplicating common logic.

## Important APIs, Types, and Functions
The header exports handlers for driver info, message level, self-test execution and self-test metadata, pause settings, stats string/data counts, link settings, FEC, RX NFC classification, RX ring count, RSS indirection/key/context operations, reset, and module EEPROM/module info access. It references kernel ethtool structures such as `struct ethtool_link_ksettings`, `struct ethtool_fecparam`, `struct ethtool_rxnfc`, `struct ethtool_rxfh_param`, and `struct ethtool_rxfh_context`, plus driver-owned `struct efx_nic` and `struct efx_self_tests`.

## Control Flow
The header has no executable control flow. Its design implies that consumers wire these declarations into ethtool operation tables and call `efx_ethtool_fill_self_tests()` consistently for test count, strings, and results.

## State and Persistence
No state is stored here. The declared functions mutate runtime NIC state in `struct efx_nic`, filter tables, RSS context tables, and PHY/MAC configuration through their implementations.

## Dependencies and Integration Points
The header depends on prior declarations for `struct net_device`, ethtool types, `struct efx_nic`, and `struct efx_self_tests` from surrounding driver headers and kernel headers. It is the coupling point between NIC-specific ethtool ops definitions and the common implementation in `ethtool_common.c`.

## Risks
Prototype drift between this file and `ethtool_common.c` or kernel ethtool API signatures will break compilation. The RSS context functions use newer ethtool context APIs, so kernel-version backports must keep signatures aligned. Because this header deliberately does not include all dependency headers itself, include order matters in consumers.

## Test Signals
Build coverage is the main signal: all consumers should compile with these prototypes, and sparse/clang warnings should catch mismatched pointer types. Runtime signals are the full ethtool command suite exercised through whichever `struct ethtool_ops` table imports these functions.
