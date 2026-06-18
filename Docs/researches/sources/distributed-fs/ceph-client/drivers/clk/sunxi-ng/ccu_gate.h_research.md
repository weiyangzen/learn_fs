# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_gate.h

## Purpose
This header declares the sunxi-ng gate clock class and constructor macros for string, hardware, firmware, parent-data, and predivided-parent variants.

## Important APIs, Types, And Functions
Important items are `struct ccu_gate`, `SUNXI_CCU_GATE*` macros, `hw_to_ccu_gate()`, helper prototypes, and `ccu_gate_ops`.

## Control Flow
No runtime flow is present. Macros expand to static descriptors consumed by `ccu_gate.c`.

## State And Persistence
Descriptor state includes enable mask, register offset, optional common predivider, feature flags, and embedded `clk_hw` init data.

## Dependencies And Integration Points
It depends on CCF and `ccu_common`. Integration is broad across SoC descriptor tables and compound gate users.

## Risks
Choosing the wrong parent initializer flavor can break firmware-parent resolution. Predivider flags change reported rates for all consumers of that gate.

## Test Signals
Compile coverage and simple gate enable/readback tests validate the header.
