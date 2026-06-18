# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-eth-devlink.c

## Purpose
This file implements DPAA2 Ethernet devlink support: driver info, physical devlink port registration, and parser-error drop traps.

## Important APIs, Types, and Functions
`dpaa2_eth_devlink_ops` provides `info_get`, `trap_init`, independent trap action rejection, and trap group action setting. `dpaa2_eth_dl_alloc/free/register/unregister()` manage the devlink instance. `dpaa2_eth_dl_port_add/del()` manage the physical devlink port. `dpaa2_eth_dl_traps_register/unregister()` install generic parser-error traps. `dpaa2_eth_dl_get_trap()` maps frame annotation parser error bits to registered trap items.

## Control Flow
Probe allocates a devlink, registers trap groups and traps, adds a physical port, and later registers devlink. Trap initialization stores trap contexts in `priv->trap_data`. Error frame processing in the main driver can call `dpaa2_eth_dl_get_trap()` to identify the devlink trap item from FAF bits. Trap group action changes configure DPNI error behavior: drop means discard parser-error frames, trap means send them to the error queue with annotations.

## State and Persistence
Runtime state includes `priv->devlink`, `priv->devlink_port`, `priv->trap_data`, dynamically allocated trap item arrays, and DPNI error behavior programmed in the Management Complex. There is no persistence.

## Dependencies and Integration Points
The file depends on devlink, DPNI MC commands, DPAA2 parser annotation structures, generic devlink trap IDs, and main-driver fields such as DPNI version and MC token.

## Risks
Trap mapping relies on hard-coded FAF bit positions and endian conversions; wrong positions misclassify drops. Only group action changes are supported, not independent trap actions. Failure unwinding must unregister groups/traps and free allocations in exact reverse order. The label `trap_groups_unregiser` is misspelled but harmless.

## Test Signals
Use `devlink dev info`, `devlink trap show`, `devlink trap set group parser_error_drops action trap/drop`, inject parser errors for each supported protocol bit, and run allocation/failure-injection tests through trap registration.
