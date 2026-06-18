
# sources/distributed-fs/ceph-client/include/linux/platform_data/hirschmann-hellcreek.h

## Purpose
This header defines platform data for the Hirschmann Hellcreek TSN switch driver.

## Important APIs And Types
`struct hellcreek_platform_data` contains switch name, port count, speed mode flag (`is_100_mbits`), Qbv support for front TSN ports and CPU port, Qbu support, and module id.

## Control Flow, State, And Persistence
The header has no executable flow. The switch driver uses these fields at probe to size ports, label the device, configure speed-specific behavior, and expose TSN features. Runtime state resides in the switch driver and hardware.

## Dependencies And Integration Points
It depends on Linux types and integrates platform devices with the Hellcreek DSA/TSN switch driver, including time-aware shaping and frame preemption capabilities.

## Risks And Test Signals
Risks include wrong port count, feature flags that expose unsupported TSN controls, and speed-mode mismatch. Test signals include switch probe, port creation, link speed verification, Qbv/Qbu control availability, traffic forwarding, and module-id reporting.
