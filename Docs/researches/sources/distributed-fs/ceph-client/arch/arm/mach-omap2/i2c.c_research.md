<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.c

## Purpose
`i2c.c` provides the OMAP I2C module custom reset sequence used by hwmod integration. Older OMAP2/3 I2C modules require disable, soft reset, re-enable, and reset-done polling.

## Important APIs, Types, and Functions
The public function is `omap_i2c_reset(struct omap_hwmod *oh)`. Important constants are `I2C_EN`, `OMAP2_I2C_CON_OFFSET`, `OMAP4_I2C_CON_OFFSET`, and `MAX_OMAP_I2C_HWMOD_NAME_LEN` (unused in this file).

## Control Flow
The reset helper selects the I2C CON register offset based on SoC generation, clears `I2C_EN`, calls `omap_hwmod_softreset()`, sets `I2C_EN`, and polls the hwmod reset-done bit up to `MAX_MODULE_SOFTRESET_WAIT`. It logs success or timeout and returns zero.

## State and Persistence Behavior
State is the I2C controller enable bit and soft-reset state. It does not persist data and does not own transfer state; the I2C driver owns runtime bus state after reset.

## Dependencies and Integration Points
It depends on SoC detection, OMAP hwmod accessors, PRM/common reset constants, and `i2c.h`. It integrates through hwmod class reset hooks used before I2C controller probe or during module reset.

## Risks
Wrong CON offset can hit unrelated registers on newer SoCs. Returning zero despite reset timeout can mask broken hardware state. Resetting while transfers are active would disrupt the bus, so callers must use it at safe lifecycle points.

## Test Signals
Boot with OMAP I2C controllers, confirm no reset timeout warnings, scan/probe I2C devices, and run suspend/resume plus repeated controller runtime reset where supported. Validate both OMAP2/3 and OMAP4-style offsets in compile/runtime coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/i2c.c -->
