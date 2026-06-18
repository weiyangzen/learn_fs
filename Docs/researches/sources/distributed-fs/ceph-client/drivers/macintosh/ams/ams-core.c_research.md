<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-core.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-core.c

Purpose: This is the Apple Motion Sensor core. It discovers the sensor backend, normalizes axis orientation, exposes current x/y/z values through sysfs, handles freefall/shock interrupts, and coordinates joystick-style input registration.

Important APIs and state: Global `struct ams ams_info` is the singleton device state. `ams_sensors()` calls the backend `get_xyz()` and applies orientation swap/invert bits. `ams_sensor_attach()` reads OF orientation, registers PMF interrupt clients, creates an OF platform device named `ams`, creates the `current` sysfs file, determines vendor flag, and initializes optional input. `ams_sensor_detach()` removes input/sysfs/device/interrupt clients. `ams_worker()` handles pending interrupt bits and calls backend `clear_irq()`.

Control flow: Module init initializes locks and work, then looks for an I2C node named `accelerometer` compatible with `AAPL,accelerometer_1` if I2C is enabled, otherwise/then a PMU node named `sms` compatible with `sms` if PMU is enabled. The chosen backend fills function pointers and calls `ams_sensor_attach()`. Interrupt handlers only set bits under `irq_lock` and schedule work; the worker takes the main mutex before clearing hardware interrupts.

State and persistence: Singleton runtime state includes OF nodes/devices, orientation values, backend callbacks, vendor flag, pending IRQ bits, input device pointer, and calibration offsets in `ams_info`. No configuration persists beyond module parameters and firmware properties.

Dependencies and integration: It depends on Open Firmware platform creation, PMF interrupt clients, backend modules, input helper code, and PowerMac platform function infrastructure.

Risks and test signals: `ams_sensor_detach()` flushes work after sysfs/input removal but before unregistering PMF clients; comments note interrupts can arrive before backend disable. Orientation property length is assumed to include two u32s. Test backend discovery precedence, missing/short orientation property, freefall/shock IRQ coalescing, sysfs current output, and detach with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ams/ams-core.c -->
