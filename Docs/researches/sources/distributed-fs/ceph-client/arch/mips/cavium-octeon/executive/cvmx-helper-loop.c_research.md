# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-loop.c

## Purpose
Handles Octeon LOOP interfaces, internal packet loopback ports separate from external Ethernet loopback modes.

## Important APIs, Types, And Functions
The two entry points are `__cvmx_helper_loop_probe()` and `__cvmx_helper_loop_enable()`. Probe writes `CVMX_PIP_PRT_CFGX` and `CVMX_IPD_SUB_PORT_FCS`.

## Control Flow
Probe assumes four ports, disables PIP min/max length errors for each, disables FCS stripping for loopback subports, and returns four. Enable is a no-op.

## State, Persistence, And Dependencies
Only PIP/IPD CSR state changes. It depends on generic IPD port mapping.

## Integration Points
`cvmx-helper.c` calls it for LOOP probe and enable and excludes LOOP from normal link handling.

## Risks
Length-check relaxation is specific to internal loop traffic. The fixed four-port assumption must match mode detection.

## Test Signals
Verify four ports in LOOP mode, acceptance of short/jumbo internal packets, and no external link-status dependency.
