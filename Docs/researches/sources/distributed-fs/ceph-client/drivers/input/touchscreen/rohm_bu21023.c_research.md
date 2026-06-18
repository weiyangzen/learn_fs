<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/rohm_bu21023.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/rohm_bu21023.c

## Purpose
`rohm_bu21023.c` drives ROHM BU21023/BU21024 dual-touch resistive touchscreen controllers over I2C. It performs low-level register setup, loads controller firmware (`bu21023.bin`) on input open, applies manual calibration, exposes axis transform sysfs knobs, and reports up to two multitouch contacts from threaded IRQs.

## Important APIs, Types, And Functions
`struct rohm_ts_data` stores the `i2c_client`, input device, initialization flag, contact debounce counters, current finger count, and `COMMON_SETUP2` transform bits. `rohm_i2c_burst_read()` performs the controller's unusual two-step read under an I2C segment lock. `rohm_ts_device_init()` programs the register table, loads firmware with `rohm_ts_load_firmware()`, seeds calibration registers, enables interrupts, and powers the CPU. `rohm_ts_soft_irq()` reads position/touch registers, debounces 0/1/2 contact transitions using threshold arrays, assigns MT slots, and invokes `rohm_ts_manual_calibration()` on calibration request. Sysfs attributes `swap_xy`, `inv_x`, and `inv_y` update `COMMON_SETUP2` through `rohm_ts_update_setting()`.

## Control Flow
Probe requires an IRQ and adapter `master_xfer`, powers the controller CPU off, allocates state/input, configures two MT slots, requests a threaded IRQ, and registers the input device. The device is not fully initialized until the input node is opened; `rohm_ts_open()` calls `rohm_ts_device_init()` once and marks `initialized`. On close, `rohm_ts_power_off()` turns analog/CPU blocks off and clears `initialized`.

## State And Persistence
Runtime state includes debounce counters and the current axis transform bits. Sysfs writes persist only while the driver instance exists; if initialized, they are immediately written to hardware. Firmware is loaded from the kernel firmware interface into controller program memory; no kernel-side copy persists after load.

## Dependencies And Integration Points
The driver uses I2C SMBus plus low-level `__i2c_transfer()`, firmware loading, threaded IRQs, input MT slot assignment, input mutex guards for sysfs changes, and I2C device IDs. Unlike many modern touchscreen drivers, it does not parse DT touchscreen properties.

## Risks
Initialization is heavy and happens on open, so missing firmware makes the input device present but unusable. The burst read protocol depends on stop conditions and manual bus locking. Contact-count thresholds intentionally delay transitions, which can hide very short touches. Manual calibration modifies several registers and has rollback paths that still depend on successful I2C writes. Axis transform sysfs accepts any nonzero integer as true.

## Test Signals
Probe should reject missing IRQs. Opening the input device should load `bu21023.bin`, power the CPU, and enable coordinates. Test one- and two-finger transitions, calibration request interrupts, sysfs transform writes while opened and closed, close/open reinitialization, and missing/invalid firmware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/rohm_bu21023.c -->
