# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-helper-npi.h

## Purpose
`cvmx-helper-npi.h` declares helper hooks for the NPI packet interface, a non-PHY packet path used by some Octeon systems to exchange packets with host or internal bus-side logic.

## Important APIs, Types, And Functions
The exported declarations are `__cvmx_helper_npi_probe(int interface)` and `__cvmx_helper_npi_enable(int interface)`. `__cvmx_helper_npi_enumerate` is a macro alias for the probe function, so enumeration and probing share one implementation.

## Control Flow
When generic helper code identifies an interface as NPI, it calls the probe/enumerate hook to determine available ports and later calls enable after IPD is ready. There are no per-port link APIs because NPI does not use ordinary Ethernet PHY autonegotiation.

## State And Persistence
State is entirely in hardware registers programmed by the implementation. The header stores no data. Enabled NPI state affects how IPD/PKO traffic is routed through the NPI block.

## Dependencies And Integration Points
The file is included by `cvmx-helper.h` and integrates with common packet I/O initialization, IPD enablement, and PKO port routing. It is related to IOB/NPI hardware definitions outside this header set.

## Risks
Aliasing enumeration to probe means probe side effects must be safe to repeat. Code that expects link status for every interface must avoid calling Ethernet PHY paths for NPI. Incorrect port counts can misroute PKO queues.

## Test Signals
Validate probe counts on boards that expose NPI, packet ingress and egress through the host/NPI path, repeated probe/enumerate idempotence, and correct interaction with IPD and PKO global initialization.
