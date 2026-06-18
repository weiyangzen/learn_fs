# sources/distributed-fs/ceph-client/drivers/mfd/rk8xx-i2c.c

## Purpose
`rk8xx-i2c.c` is the I2C bus wrapper for Rockchip RK8xx PMICs. It selects the correct regmap configuration and variant ID from OF match data, creates an I2C regmap, and delegates common setup to `rk8xx_probe()`.

## Important APIs, Types, And Functions
`struct rk8xx_i2c_platform_data` pairs a `regmap_config` with a variant constant. Variant-specific volatile-register callbacks define cache policy for RK801, RK806, RK808/RK805/RK818, RK816, and RK817/RK809. `rk8xx_i2c_probe()` initializes regmap and calls the core. `rk8xx_i2c_shutdown()` delegates to `rk8xx_shutdown()`, and PM ops delegate to `rk8xx_suspend()`/`rk8xx_resume()`.

## Control Flow
Probe reads match data, initializes the variant regmap with `devm_regmap_init_i2c()`, and passes `client->irq` and the variant ID to `rk8xx_probe()`. Shutdown and suspend/resume are thin pass-throughs to the shared core.

## State And Persistence
State is mostly regmap cache configuration. Volatile register policies determine which PMIC values are cached versus read live. Persistent hardware state is written by the shared core and child drivers, not by this wrapper beyond regmap access.

## Dependencies And Integration Points
It depends on I2C, OF compatibles `rockchip,rk801`, `rk805`, `rk806`, `rk808`, `rk809`, `rk816`, `rk817`, and `rk818`, regmap cache backends, and exported core functions from `rk8xx-core.c`.

## Risks
RK809 intentionally reuses the RK817 regmap config. RK817 uses `REGCACHE_NONE`, while other variants use cached regmaps; changing volatile lists can cause stale status or excessive I2C traffic. Passing a zero IRQ causes the core to fail, so firmware must provide the PMIC IRQ.

## Test Signals
Verify each compatible maps to the expected variant and max register, volatile registers bypass cache, IRQ propagation to the core, shutdown and PM callbacks, and error handling for regmap init failure or missing match data.
