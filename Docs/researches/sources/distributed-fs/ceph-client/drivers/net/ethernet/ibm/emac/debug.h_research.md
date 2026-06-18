
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/debug.h

## Purpose
`debug.h` centralizes debug-print macros for the IBM EMAC family. It gives EMAC, MAL, ZMII, and RGMII code consistent `KERN_DEBUG` formatting with the OF node included when `CONFIG_IBM_EMAC_DEBUG` is enabled.

## Important APIs, Types, and Functions
`EMAC_DBG(d, name, fmt, arg...)` emits a printk prefixed by the subsystem name and `d->ofdev->dev.of_node`. `DBG`, `MAL_DBG`, `ZMII_DBG`, and `RGMII_DBG` are level-1 debug macros; `DBG2`, `MAL_DBG2`, `ZMII_DBG2`, and `RGMII_DBG2` are level-2 macros. `DBG_LEVEL` is set to `1` when `CONFIG_IBM_EMAC_DEBUG` is enabled and `0` otherwise.

## Control Flow
There is no runtime flow beyond macro expansion. With debug disabled the macros compile to no-ops, so call sites incur no printk behavior. With debug enabled, frequently executed paths such as TX/RX polling and register changes can produce debug logs.

## State and Persistence
The file keeps no state. It relies on the caller’s object exposing `ofdev`, which is true for the EMAC helper instance structs in this driver family.

## Dependencies and Integration Points
It includes `core.h`, which in turn includes many local headers. That creates a broad include dependency for a small macro file and assumes consumers can tolerate the full private EMAC type graph.

## Risks
The no-op macro signatures are inconsistent for `DBG` versus `MAL_DBG` style macros, but existing call sites compile because they match the expected forms. Enabling debug on busy datapath code may flood logs and alter timing. Because the macro dereferences `d->ofdev`, misuse with partially initialized objects can crash.

## Test Signals
Kconfig build coverage with `CONFIG_IBM_EMAC_DEBUG=y` and unset is the main signal. Runtime debug logs should include OF node paths and not appear when debug is disabled.
