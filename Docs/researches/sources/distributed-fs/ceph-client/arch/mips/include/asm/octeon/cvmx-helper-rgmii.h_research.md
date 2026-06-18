# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-rgmii.h

## Purpose
`cvmx-helper-rgmii.h` declares helper hooks for RGMII, GMII, and MII Ethernet interfaces. It provides the mode-specific operations used by the common helper layer to probe ports, enable ASX/GMX/PKO programming, query PHY link state, set MAC link parameters, and force internal loopback.

## Important APIs, Types, And Functions
The file exports `__cvmx_helper_rgmii_probe(int interface)`, aliases `__cvmx_helper_rgmii_enumerate` to that probe, declares `cvmx_helper_rgmii_internal_loopback(int port)`, and provides `__cvmx_helper_rgmii_enable`, `__cvmx_helper_rgmii_link_get`, and `__cvmx_helper_rgmii_link_set`.

## Control Flow
Generic helper code probes an interface, optionally lets board code override physical port count, enables the interface after IPD setup, then uses link get/set around PHY autonegotiation changes. Loopback can be requested per IPD port to echo internal and external packets through the RGMII path.

## State And Persistence
The implementation changes ASX, GMX, PKO, and possibly PHY hardware state. Link-set updates MAC speed, duplex, and flow-control-related settings to match PHY state. The header stores no software state.

## Dependencies And Integration Points
It depends on `union cvmx_helper_link_info` from `cvmx-helper.h` and integrates with board PHY hooks, GMX CSR definitions, ASX registers, IPD, and PKO. It is the mode backend for `CVMX_HELPER_INTERFACE_MODE_RGMII` and related GMII/MII operation.

## Risks
RGMII timing and PHY wiring are board-specific. Probe/enumerate aliasing requires a side-effect-safe probe. Link-set must match PHY autonegotiation exactly or traffic can fail despite link-up reporting. Loopback can mask external wiring faults if tests do not distinguish internal from external paths.

## Test Signals
Test all configured ports for PHY address discovery, link up/down transitions, 10/100/1000 speed and duplex combinations, packet traffic in both directions, internal loopback behavior, and absence of GMX RX/TX errors after link changes.
