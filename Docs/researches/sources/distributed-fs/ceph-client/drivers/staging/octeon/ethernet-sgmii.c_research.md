# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-sgmii.c

## Purpose
Minimal SGMII mode integration for Octeon Ethernet ports.

## Important APIs, Types, And Functions
Exports `cvm_oct_sgmii_init()` and `cvm_oct_sgmii_open()`.

## Control Flow
Initialization delegates to `cvm_oct_common_init()` and leaves a FIXME for autonegotiation logic. Open delegates to `cvm_oct_common_open()` with generic CVMX link polling.

## State And Persistence
Uses common per-netdev `struct octeon_ethernet` state only. No file-local state.

## Dependencies And Integration Points
Integrates SGMII netdev ops in `ethernet.c` with common init/open/link code and phylib/MDIO support.

## Risks
Autonegotiation is explicitly incomplete. SGMII behavior relies on common link polling or PHY setup rather than mode-specific configuration.

## Test Signals
SGMII port registration, common init side effects, PHY link negotiation, carrier polling, and regression around the FIXME on autoneg-capable hardware.
