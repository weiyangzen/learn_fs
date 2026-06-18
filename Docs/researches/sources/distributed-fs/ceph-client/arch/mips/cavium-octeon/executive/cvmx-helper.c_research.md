# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper.c

## Purpose
Coordinates Octeon packet I/O discovery and bring-up: interface modes, port counts, IPD/PIP/PKO setup, hardware enable, errata, and link dispatch.

## Important APIs, Types, And Functions
Public APIs include `cvmx_helper_get_number_of_interfaces()`, `cvmx_helper_ports_on_interface()`, `cvmx_helper_interface_get_mode()`, `cvmx_helper_interface_enumerate()`, `cvmx_helper_interface_probe()`, `cvmx_helper_initialize_packet_io_global()`, `cvmx_helper_ipd_and_packet_input_enable()`, `cvmx_helper_link_get()`, and `cvmx_helper_link_set()`. Static state is `interface_port_count[9]`.

## Control Flow
Model-specific mode detection handles CN68XX, Octeon II, CN7XXX, and older chips. Enumeration dispatches to mode helpers and board overrides. Global initialization applies errata, adjusts L2 arbitration, initializes PKO, probes interfaces, configures PIP/IPD tagging and PKO queues, applies global setup/backpressure, and optionally enables packet I/O. Packet enable turns on IPD, enables each hardware interface, then enables PKO.

## State, Persistence, And Dependencies
`interface_port_count` is synchronized with `CVMX_SYNCWS`. Hardware state spans L2C, IPD, PIP, PKO, POW, GMX, ASX, PCS, and SPI.

## Integration Points
This file ties together all helper mode modules, board helpers, PKO, IPD/PIP, FPA, SPI, L2C, POW, and errata code.

## Risks
Initialization ordering is critical. Mode tables are hardware-specific. The IPD pointer-alignment workaround temporarily rewrites live port registers and sends crafted loopback packets.

## Test Signals
Verify interface mode/counts per model, queue and tag setup, IPD-before-PKO enable ordering, link dispatch per mode, and errata gating.
