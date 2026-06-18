# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-sgmii.c

## Purpose
Implements SGMII/PICMG port setup, PCS autonegotiation handling, link status, and GMX speed programming.

## Important APIs, Types, And Functions
Main functions are `__cvmx_helper_sgmii_enumerate()`, `__cvmx_helper_sgmii_probe()`, `__cvmx_helper_sgmii_enable()`, `__cvmx_helper_sgmii_link_get()`, and `__cvmx_helper_sgmii_link_set()`, plus internal one-time, link, and speed initialization helpers.

## Control Flow
Probe enables GMX early for GMX-700 errata and returns four ports. Enable runs common GMX setup, programs PCS timers/advertisements, enables GMX ports, and turns on PCS/GMX interrupts. Link get handles simulator/loopback, restarts PCS negotiation if needed, decodes autoneg results in PHY mode, or asks board code in MAC mode. Link set resets/restarts PCS and programs GMX/PCS speed fields.

## State, Persistence, And Dependencies
Persistent state resides in PCS, GMX, and interrupt CSRs. Timing depends on `cpu_clock_hz`.

## Integration Points
`cvmx-helper.c` delegates SGMII/PICMG modes here. Board helpers provide MAC-mode link status.

## Risks
1000BASE-X link get is marked FIXME. Reset/autoneg/idle timeouts can leave links down. Simulator bypasses real negotiation.

## Test Signals
Check PCS reset/autoneg completion, decoded speeds, GMX idle before speed writes, packet flow, and PCS/GMX fault interrupts.
