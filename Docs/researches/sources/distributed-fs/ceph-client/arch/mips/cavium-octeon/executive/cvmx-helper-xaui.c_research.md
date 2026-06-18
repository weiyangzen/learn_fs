# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-helper-xaui.c

## Purpose
Handles XAUI/HiGig2 high-speed interface probing, PKO virtual-port mapping, enable sequencing, link status, and link recovery.

## Important APIs, Types, And Functions
Entry points are `__cvmx_helper_xaui_enumerate()`, `__cvmx_helper_xaui_probe()`, `__cvmx_helper_xaui_enable()`, `__cvmx_helper_xaui_link_get()`, and `__cvmx_helper_xaui_link_set()`.

## Control Flow
Enumerate returns sixteen virtual ports when HiGig2 TX is enabled, otherwise one. Probe enables GMX early, configures common GMX, and maps sixteen PKO packet ports to one XAUI endpoint. Enable masks interrupts, configures PCS/GMX, waits for reset, alignment, RX readiness, GMX idle, receive link, and no faults, clears stale errors, restores masks, and enables GMX/PCS. Link set re-enables the interface when an up link is requested but hardware is unhealthy.

## State, Persistence, And Dependencies
State lives in PKO maps, GMX, PCSXX, and interrupt CSRs. Model checks suppress reset on affected CN66XX/CN68XX parts.

## Integration Points
Used by `cvmx-helper.c` for XAUI mode and by PKO for virtual port mapping.

## Risks
Multiple timeout points can leave partial configuration. Link get masks interrupts when down. HiGig2 mapping assumes one physical endpoint.

## Test Signals
Check HiGig2 port count, PCS alignment, 10 Gbps link status, link recovery, and interrupt mask preservation.
