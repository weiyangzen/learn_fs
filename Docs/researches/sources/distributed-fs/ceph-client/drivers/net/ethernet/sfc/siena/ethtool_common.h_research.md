# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ethtool_common.h

## Purpose
Declares shared Siena ethtool functions used by the concrete ops table.

## Important APIs
Declares driver info, message level, self-test, pause, string set count, strings, stats, link ksettings, FEC params, RX NFC, RX ring count, RSS indirection/key get/set, RSS hash fields, ethtool reset, and module EEPROM/info functions.

## Control flow and integration
`ethtool.c` binds these declarations into `efx_siena_ethtool_ops`. Implementations call self-test, MCDI PHY, filter, RSS, stats, and reset subsystems.

## State and persistence behavior
The header stores no state. Implementations read or mutate NIC runtime state, firmware state, filters, RSS, and stats.

## Dependencies
Depends on Linux netdev and ethtool types. Callers must pass a Siena netdev whose private data is `struct efx_nic`.

## Risks
Prototype drift from kernel ethtool API changes causes build failures. Locking expectations are implementation-specific and must be preserved by callers.

## Test signals
Compile against target kernel ethtool APIs and invoke each bound ethtool operation at runtime.
