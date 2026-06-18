# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-loop.h

## Purpose
`cvmx-helper-loop.h` declares the helper implementation for Octeon's internal LOOP packet interface. LOOP is used for internal packet path testing or loopback-style traffic without external PHY link negotiation.

## Important APIs, Types, And Functions
The exported functions are `__cvmx_helper_loop_probe(int interface)` and `__cvmx_helper_loop_enable(int interface)`. It also defines `__cvmx_helper_loop_enumerate(int interface)` as an inline function that always returns 4 ports.

## Control Flow
Generic `cvmx_helper_interface_probe()` dispatches to the LOOP probe for interfaces reported in loop mode. Enumeration is fixed at four logical ports. After IPD is enabled and before normal packet I/O, common helper code calls the LOOP enable hook to configure the loop interface.

## State And Persistence
The header has no storage. The implementation programs packet-interface hardware state for LOOP operation, and that hardware configuration persists until changed or reset.

## Dependencies And Integration Points
It is included by `cvmx-helper.h` and participates in the common interface mode dispatcher. It interacts with IPD/PIP/PKO setup through the same helper framework as external Ethernet modes, but has no link-get or link-set API because there is no external PHY.

## Risks
The fixed four-port enumerate result can be wrong if used on unsupported silicon or without matching implementation checks. Code that assumes all helper interfaces have link APIs must special-case LOOP. Misconfiguring LOOP can hide real external-interface failures by passing only internal traffic tests.

## Test Signals
Test signals are successful probe counts, ability to send and receive internal packets on all four loop ports, no external PHY dependencies, and clean enable/disable behavior when packet I/O is reinitialized.
