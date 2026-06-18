# sources/distributed-fs/ceph-client/drivers/thermal/broadcom/sr-thermal.c

## Purpose
Broadcom Stingray thermal driver. It registers one thermal zone per enabled TMON bit in the `brcm,tmon-mask` device property and reports memory-mapped temperature register values directly.

## Important APIs, Types, and Functions
- `struct sr_thermal` stores the remapped register window and fixed array of up to six TMON descriptors.
- `struct sr_tmon` binds a TMON id to its parent private state.
- `sr_get_temp()` reads `regs + id * 4` and returns the value as millicelsius.
- `sr_thermal_probe()` memremaps the resource, reads `brcm,tmon-mask`, flushes each enabled temperature register to zero, and registers OF zones by hardware id.

## Control Flow
Probe allocates the parent structure, gets the memory resource, maps it with `devm_memremap(..., MEMREMAP_WB)`, reads the enabled-sensor mask, then iterates ids 0 through 5. For each set bit it clears the register, initializes the `sr_tmon`, and registers a thermal OF zone using the same id.

## State and Persistence
Runtime state is devm-managed memory and the fixed sensor array. Hardware temperature registers are cleared once during probe.

## Dependencies and Integration Points
Depends on platform resources, generic device properties, OF thermal zones, and the Stingray hardware temperature register layout.

## Risks and Edge Cases
- `devm_memremap()` with write-back semantics is unusual for device registers; ordering/cacheability assumptions should match the hardware block.
- The driver ignores mask bits above `SR_TMON_MAX_LIST`.
- No validity or unit conversion is performed; firmware/hardware must expose values in thermal-framework units.
- `crit_temp` and `max_crit_temp` fields are unused.

## Test Signals
Probe tests should check missing resource, missing mask property, multiple mask bits, per-id zone registration, register flush writes, and readback from each enabled offset.
