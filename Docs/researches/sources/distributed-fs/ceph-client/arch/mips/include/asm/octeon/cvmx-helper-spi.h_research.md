# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-spi.h

## Purpose
`cvmx-helper-spi.h` declares helper operations for SPI packet interfaces. It gives the common packet I/O helper layer a mode backend for probing connected SPI ports, enabling the interface, and translating link state into Octeon hardware settings.

## Important APIs, Types, And Functions
The declarations are `__cvmx_helper_spi_probe(int interface)`, `__cvmx_helper_spi_enumerate(int interface)`, `__cvmx_helper_spi_enable(int interface)`, `__cvmx_helper_spi_link_get(int ipd_port)`, and `__cvmx_helper_spi_link_set(int ipd_port, union cvmx_helper_link_info link_info)`.

## Control Flow
Probe leaves the interface down while determining port count. Enable is called with IPD enabled and PKO disabled so SPI/GMX state can be initialized before traffic begins. Link get and link set are used by the generic helper API to synchronize MAC state with negotiated or externally supplied link state.

## State And Persistence
The implementation writes SPI, GMX, PKO, and possibly PHY state; the header stores none. Configured link state persists in hardware until reset or a later link-set call.

## Dependencies And Integration Points
It is included by `cvmx-helper.h` and selected for `CVMX_HELPER_INTERFACE_MODE_SPI`. It depends on `union cvmx_helper_link_info` and integrates with board link discovery, GMX SPI CSR fields, IPD, and PKO queue setup.

## Risks
SPI packet interfaces have stricter bring-up ordering and timing than simple GMII modes. Calling enable before IPD readiness or after PKO is active can produce dropped or malformed traffic. Stale link info and board-specific port-count mistakes are common failure points.

## Test Signals
Validate SPI training/enable status, expected port count, link-state propagation, traffic under each configured port, GMX/SPI interrupt counters, and clean behavior across disable/reinitialize cycles.
