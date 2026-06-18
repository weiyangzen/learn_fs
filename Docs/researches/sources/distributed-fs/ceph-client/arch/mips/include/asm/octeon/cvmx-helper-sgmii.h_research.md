# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-sgmii.h

## Purpose
`cvmx-helper-sgmii.h` declares the mode-specific helper operations for SGMII interfaces. SGMII requires PCS/QLM configuration plus MAC setup, so the common helper layer delegates probe, enumeration, enablement, and link synchronization to this backend.

## Important APIs, Types, And Functions
The exports are `__cvmx_helper_sgmii_probe(int interface)`, `__cvmx_helper_sgmii_enumerate(int interface)`, `__cvmx_helper_sgmii_enable(int interface)`, `__cvmx_helper_sgmii_link_get(int ipd_port)`, and `__cvmx_helper_sgmii_link_set(int ipd_port, union cvmx_helper_link_info link_info)`.

## Control Flow
Probe determines how many SGMII ports are connected while leaving the interface down. Enable runs after IPD is enabled and before full packet I/O. Link get reads negotiated PCS/PHY state, and link set programs Octeon MAC/PCS state to match that result.

## State And Persistence
Persistent state is PCS/GMX/QLM and PHY hardware configuration. The header stores no variables. Link-set changes affect future packet transmission until the link is reconfigured.

## Dependencies And Integration Points
The API integrates with QLM/JTAG/errata helpers, board PHY hooks, GMX definitions, and the common `cvmx_helper_link_get/set` dispatcher. It is selected for `CVMX_HELPER_INTERFACE_MODE_SGMII`.

## Risks
SGMII depends on PCS autonegotiation and high-speed lane configuration. Calling link set with stale link info can misconfigure speed or duplex. Probe and enumerate are separate declarations, so implementations may have different side effects that common code must respect.

## Test Signals
Exercise probe counts, PCS link-up, PHY link changes, speed/duplex propagation into GMX, QLM errata paths on affected silicon, and packet traffic with error counters checked after negotiation changes.
