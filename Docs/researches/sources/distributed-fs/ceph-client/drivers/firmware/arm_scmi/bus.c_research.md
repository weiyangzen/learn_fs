# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/bus.c

## Purpose
Implements the SCMI protocol bus. It manages SCMI client driver registration, requested protocol/name device tables, SCMI device creation/destruction per SCMI instance, modalias/sysfs attributes, PM forwarding, and bus lifecycle.

## APIs, Types, And Functions
Exports `scmi_bus_type`, `scmi_requested_devices_nh`, `scmi_driver_register()`, `scmi_driver_unregister()`, `scmi_device_create()`, and `scmi_device_destroy()`. State helpers use `DEFINE_IDA(scmi_bus_id)`, `DEFINE_IDR(scmi_requested_devices)`, `scmi_requested_devices_mtx`, and `atomic_t scmi_syspower_registered`.

## Control Flow
When an SCMI driver registers, its ID table is recorded as requested devices and advertised on the blocking notifier chain. SCMI core instances later call `scmi_device_create()` to instantiate one named device or all requested devices for a protocol. Matching requires protocol ID and name equality, excluding internal transport devices. Probe defers until `scmi_dev->handle` exists. Device destruction clears the unique SystemPower registration flag when applicable, frees the bus ID, and unregisters the device.

## State, Persistence, And Dependencies
Runtime state includes requested-device IDR lists, bus devices, allocated names, IDA IDs, notifier chain entries, and a global SystemPower uniqueness flag. There is no persistent storage. Dependencies include device core, OF node association, notifier chains, IDA/IDR, mutexes, atomics, and SCMI public driver IDs.

## Integration Points
The main SCMI driver creates devices as firmware protocols are discovered; SCMI client drivers register ID tables and bind through this bus. Sysfs exposes `protocol_id`, `name`, and `modalias`, while PM callbacks forward suspend/resume to bound client drivers.

## Risks And Test Signals
Risks include races between late driver registration and SCMI instance probe, duplicate requested names, raw-mode rejection changing client availability, global SystemPower uniqueness across instances, and cleanup ordering on module unload. Signals are SCMI client module autoload, bind/unbind tests, multiple SCMI instance probing, raw-mode configs, and sysfs/modalias inspection.
