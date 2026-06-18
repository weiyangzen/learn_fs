# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-i2c.c

## Purpose
`fimc-is-i2c.c` registers a Linux I2C adapter that represents the ISP-owned sensor control bus. The host CPU does not perform transfers; the adapter exists so sensor client devices can bind and so runtime PM can propagate through the device hierarchy.

## Important APIs, Types, and Functions
`struct fimc_is_i2c` stores an `i2c_adapter` and the `i2c_isp` clock. `is_i2c_func()` advertises `I2C_FUNC_I2C` through an otherwise empty `i2c_algorithm`. Probe/remove are `fimc_is_i2c_probe()` and `fimc_is_i2c_remove()`. Runtime/system PM callbacks enable or disable the bus clock. Module-level registration is exposed through `fimc_is_register_i2c_driver()` and `fimc_is_unregister_i2c_driver()`.

## Control Flow
The FIMC-IS module init registers this platform driver before the main FIMC-IS platform driver. Probe allocates state, gets the `i2c_isp` clock, initializes and registers the I2C adapter, enables runtime PM, and clears `ignore_children` after adapter registration. Runtime resume prepares/enables the clock, and runtime suspend disables it. Remove disables runtime PM and unregisters the adapter.

## State and Persistence
State is per platform device and contains only the adapter and clock handle. Runtime PM state is managed by the PM core. There is no persistent storage and no actual host-side transfer state.

## Dependencies and Integration Points
The file depends on the I2C core, common clock framework, runtime PM, platform bus, OF matching for `samsung,exynos4212-i2c-isp`, and FIMC-IS module init/exit.

## Risks and Edge Cases
Because the algorithm has no transfer callback, any client attempting normal I2C transactions would fail despite advertised I2C functionality; the design assumes firmware controls the bus. Clearing `ignore_children` is important for sensor client PM propagation. Probe-time client PM calls are assumed absent, as noted in the comments.

## Test Signals
Validate adapter registration under the ISP I2C DT node, sensor child device binding without host transfers, runtime PM clock enable/disable from child activity, system suspend/resume when runtime active or suspended, and clean unregister during module removal.
