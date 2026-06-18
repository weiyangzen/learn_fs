# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.h

## Purpose
`fimc-is-i2c.h` declares module-internal registration helpers for the FIMC-IS ISP I2C platform driver.

## Important APIs, Types, and Functions
It declares `fimc_is_register_i2c_driver()` and `fimc_is_unregister_i2c_driver()`.

## Control Flow
There is no executable flow. The FIMC-IS module init/exit functions call these helpers.

## State and Persistence
The header stores no state.

## Dependencies and Integration Points
It is included by `fimc-is.c` so the main FIMC-IS module can register the ISP I2C adapter driver before registering the FIMC-IS platform driver.

## Risks and Edge Cases
The header intentionally exposes only registration hooks. Init ordering is important: failure to register the main platform driver should unregister this I2C driver to avoid leaving a partial module setup.

## Test Signals
Compile-time checks and module init failure-injection should verify that registration/unregistration symbols match the implementation and unwind order remains correct.
