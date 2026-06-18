# sources/distributed-fs/ceph-client/include/dt-bindings/clock/rk3399-ddr.h

## Purpose
`rk3399-ddr.h` defines RK3399 DDR3 speed-bin constants for device-tree or firmware-facing memory timing descriptions. The comments tie each constant to JEDEC-style DDR3 data rates and CAS timing groups.

## Important APIs, types, and functions
The ABI consists of `DDR3_800D` through `DDR3_2133N` plus `DDR3_DEFAULT`. There are no functions or structs. The IDs are compact enum-like values from `0` through `21` and represent timing bins such as DDR3-800, DDR3-1066, DDR3-1333, DDR3-1600, DDR3-1866, and DDR3-2133 with different latency suffixes.

## Control flow
Consumers include the header and place one of the constants in data consumed by RK3399 DDR initialization logic. Runtime selection happens in the memory controller or firmware code that interprets the selected bin and chooses matching timing parameters.

## State and persistence
The header is stateless, but the constants are ABI: a device tree compiled with `DDR3_1600K` must continue to mean the same bin. The selected bin affects hardware memory-controller state programmed during initialization and may persist until reset.

## Dependencies and integration points
It integrates with RK3399 board device trees, DDR timing data, boot firmware, and kernel-side Rockchip DDR support that reads memory timing properties. It is separate from the CRU clock IDs but influences memory clock/timing compatibility.

## Risks and test signals
Risks include mapping a board to the wrong speed bin, assuming `DDR3_DEFAULT` is universally safe, or changing numeric IDs. Test signals are stable memory training, no early boot memory faults, stress tests under high memory bandwidth, and board DTS review against the actual DDR3 part datasheet.
