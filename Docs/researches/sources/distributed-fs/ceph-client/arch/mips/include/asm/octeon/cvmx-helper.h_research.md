# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper.h

## Purpose
`cvmx-helper.h` is the central public include for Octeon packet helper functionality. It defines interface modes, link-state representation, includes the mode-specific helper headers, and declares the common packet I/O initialization, interface probing, port count, and link get/set APIs.

## Important APIs, Types, And Functions
The key type `cvmx_helper_interface_mode_t` enumerates disabled, RGMII, GMII, SPI, PCIe, XAUI, SGMII, PICMG, NPI, and LOOP modes. `union cvmx_helper_link_info` packs `link_up`, `full_duplex`, and 18-bit Mbps `speed` into a 64-bit value. Public APIs include `cvmx_helper_ipd_and_packet_input_enable`, `cvmx_helper_initialize_packet_io_global`, `cvmx_helper_ports_on_interface`, `cvmx_helper_get_number_of_interfaces`, `cvmx_helper_interface_get_mode`, `cvmx_helper_link_get`, `cvmx_helper_link_set`, `cvmx_helper_interface_probe`, and `cvmx_helper_interface_enumerate`.

## Control Flow
Users normally initialize global packet I/O, probe/enumerate interfaces to populate port counts, make any extra IPD configuration, then call `cvmx_helper_ipd_and_packet_input_enable()`. Link management flows through `cvmx_helper_link_get()` to observe PHY/PCS state and `cvmx_helper_link_set()` to program Octeon MAC state.

## State And Persistence
The header itself stores no state, but implementations maintain probed interface port counts and write persistent IPD/PIP/PKO/GMX/PCS/PHY hardware state. Link info is a value object passed between helper layers.

## Dependencies And Integration Points
It includes configuration, FPA, WQE, errata, loop, NPI, RGMII, SGMII, SPI, util, and XAUI headers. It is a high-level integration point for packet I/O consumers, board code, and Ethernet mode backends.

## Risks
Initialization order matters: packet interfaces must be enabled after IPD, and link set must match link get. Some interfaces lack normal PHY link semantics. The central include creates dependency coupling across helper backends, so type or enum changes have broad impact.

## Test Signals
System tests should cover global packet I/O init, every interface mode present on a board, port-count reporting before and after probe, link get/set under cable changes, packet ingress/egress on all ports, and clean behavior when unsupported interfaces return disabled or negative errors.
