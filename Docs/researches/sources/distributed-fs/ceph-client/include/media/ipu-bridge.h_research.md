# sources/distributed-fs/ceph-client/include/media/ipu-bridge.h

## Purpose
Declares the Intel IPU camera sensor bridge data model used to describe ACPI-discovered camera sensors, clocks, GPIOs, software nodes, and V4L2 async integration.

## Important APIs, Types, and Functions
The header defines constants for sensor names/properties, lane/link-frequency limits, clock names, and GPIO naming. Structures model sensor config, per-sensor instance data, software-node properties, clock data, GPIO mapping, and the bridge object. It declares helpers for initializing the IPU bridge, parsing firmware, creating software nodes, and registering async subdevices where supported.

## Control Flow
At probe, IPU drivers use bridge helpers to discover ACPI sensors, synthesize missing firmware graph/software-node properties, register clocks/GPIO lookup tables, and build V4L2 async notifiers for sensor binding.

## State and Persistence Behavior
Bridge state persists for the lifetime of the IPU device and owns synthesized property arrays, software nodes, clock/GPIO lookup state, and async match data. It does not persist across reboot.

## Dependencies and Integration Points
Integrates ACPI, software nodes, GPIO lookup, clock providers, V4L2 async notifiers, and Intel IPU camera pipeline drivers.

## Risks
Firmware synthesis is fragile: wrong lane counts, link frequencies, clock names, or GPIO polarity can prevent sensors from binding or streaming. Lifetime of software-node properties must outlive async registration.

## Test Signals
ACPI camera enumeration on IPU platforms, sensor async binding, generated graph endpoints, clock lookup, GPIO reset/power sequencing, and failure cleanup when only some sensors initialize.
