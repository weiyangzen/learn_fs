<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.c

Purpose: shared core driver for Bosch BMC150/BMC156/BMM150 magnetometers. Bus wrappers provide regmap transport; this core implements device initialization, compensation, IIO ABI, optional data-ready trigger, triggered buffer, regulators, mount matrix, and runtime/system PM.

Important APIs/types/functions: exported symbols are `bmc150_magn_regmap_config`, `bmc150_magn_probe()`, `bmc150_magn_remove()`, and `bmc150_magn_pm_ops`. `struct bmc150_magn_data` stores device, mutex, regmap, regulators, orientation, scan buffer, optional trigger, max ODR, and IRQ. Key internal functions include power-mode helpers, ODR/oversampling helpers, `bmc150_magn_compensate_x/y/z()`, `bmc150_magn_read_xyz()`, raw read/write handlers, trigger state/reenable handlers, `bmc150_magn_init()`, and buffer PM hooks.

Control flow: common probe allocates an IIO device, obtains `vdd`/`vddio`, reads mount matrix, initializes and validates chip id, programs the regular preset ODR/repetition counts, sets normal mode, configures IIO channels and optional IRQ-backed data-ready trigger, sets up the triggered buffer, enables runtime autosuspend, and registers. Direct reads resume runtime PM, read raw axes/RHALL and trim registers, apply Bosch integer compensation, return one axis, then autosuspend. Buffered reads keep power active between preenable/postdisable and push compensated XYZ data on trigger.

State/persistence: ODR, repetition counts, and power mode live in device registers; `max_odr` caches the valid ceiling derived from repetition settings. Runtime PM changes normal/sleep modes, while remove puts the device into suspend and disables regulators. Regmap uses RBTREE caching with volatile data/status registers.

Dependencies/integration: integrates with IIO core, sysfs, events include headers, triggered buffers, triggers, regmap, regulators, runtime PM, and bus-specific modules through exported namespace `IIO_BMC150_MAGN`. The mount matrix is exposed through IIO ext_info.

Risks: compensation formulas are dense fixed-point code from Bosch API and sensitive to trim read correctness and overflow sentinels. `bmc150_magn_show_samp_freq_avail()` assumes at least one frequency before replacing the final space. IRQ setup uses non-devm `request_irq()`/manual cleanup. Error paths after initialization should preserve regulator/power balance. Direct reads reject when the buffer is enabled.

Test signals: test I2C and SPI wrappers against this core, chip-id rejection, regulator failures, direct raw/scale/ODR/oversampling sysfs operations, max-ODR validation, data-ready IRQ trigger enable/disable/reenable, buffered scans, runtime suspend/resume, and mount-matrix output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.c -->
