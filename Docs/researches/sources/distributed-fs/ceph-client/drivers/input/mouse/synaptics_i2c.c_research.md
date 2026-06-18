<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_i2c.c

## Purpose
`synaptics_i2c.c` is an older direct I2C Synaptics touchpad driver. It reads RMI-style registers over SMBus page selection, configures a relative-motion reporting mode, and registers a simple Linux input mouse with left button and relative X/Y axes.

## Important APIs, Types, and Functions
`struct synaptics_i2c` owns the I2C client, input device, delayed work, scan-rate state, and cached module parameters. Register helpers `synaptics_i2c_reg_get()`, `synaptics_i2c_reg_set()`, and `synaptics_i2c_word_get()` write `PAGE_SEL_REG` before accessing the low-byte address. Probe/open/close/PM paths are `synaptics_i2c_probe()`, `synaptics_i2c_open()`, `synaptics_i2c_close()`, `synaptics_i2c_suspend()`, and `synaptics_i2c_resume()`. The work path uses `synaptics_i2c_work_handler()` and `synaptics_i2c_get_input()`.

## Control Flow
Probe allocates private state, resets and configures the device, decides between IRQ and polling mode, registers an input device, and stores client data. Opening resets/configures again and schedules polling if needed. In IRQ mode, the interrupt handler schedules immediate delayed work; the worker checks changed module parameters, handles spontaneous error/reset status, reads gesture plus relative X/Y registers, reports `BTN_LEFT`, `REL_X`, and inverted `REL_Y`, then reschedules itself either for periodic health polling or adaptive polling.

## State and Persistence
Driver state is devm-managed except the delayed work lifecycle, which is explicitly canceled on close and suspend. Module parameters (`no_decel`, `reduce_report`, `no_filter`, `polling_req`, `scan_rate`) are global; several are mutable and checked in the worker so configuration can change at runtime. The device is put into deep sleep on close/suspend.

## Dependencies and Integration Points
The driver depends on I2C/SMBus byte and word transfers, Linux workqueues, input core, IRQ registration, OF matching, and simple device PM ops. It advertises `synaptics_i2c` I2C IDs and an OF compatible string `synaptics,synaptics_i2c`.

## Risks and Edge Cases
The file notes that no locking is used because the initial design assumes no I2C bus races; extending the driver with additional asynchronous users would need serialization. `polling_req` is a global module parameter that can be forced true by one IRQ-less or failed-IRQ device, affecting all instances. `SENS_MAX_POS_LSB_REG` references `SENS_MAX_POS_UPPER_REG`, which is not otherwise defined, but the macro is unused here. Error handling resets the device when status bits are unexpected, so noisy hardware may repeatedly reconfigure.

## Test Signals
Test with both IRQ and polling paths, module parameter changes while the device is active, suspend/resume, open/close power transitions, and `evtest` relative movement/button output. I2C fault injection should verify reset-on-error handling and delayed-work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/synaptics_i2c.c -->
