<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.h

## Purpose
`i2c.h` declares the OMAP I2C hwmod reset helper for board/platform integration code.

## Important APIs, Types, and Functions
It forward-declares `struct omap_hwmod` and declares `int omap_i2c_reset(struct omap_hwmod *oh)`.

## Control Flow
There is no runtime control flow. Including code can assign or call the reset helper defined in `i2c.c`.

## State and Persistence Behavior
No state is stored.

## Dependencies and Integration Points
It integrates `i2c.c` with OMAP hwmod data and any board/hwmod setup code that needs the reset callback.

## Risks
Prototype drift would break reset callback assignment or hide build failures. The header itself is otherwise low risk.

## Test Signals
Compile OMAP I2C/hwmod users and verify `omap_i2c_reset()` remains available for configured SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.h -->
