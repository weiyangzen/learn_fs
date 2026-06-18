# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_bus.h

Purpose: defines the VCHIQ bus abstraction used to register VCHIQ child devices and bind kernel VCHIQ client drivers through the Linux device model.

Important APIs and types: `struct vchiq_device` embeds a `struct device` and points to `vchiq_drv_mgmt`. `struct vchiq_driver` supplies `probe`, `remove`, `resume`, `suspend`, an ID table, and embedded `device_driver`. Helpers `to_vchiq_device()` and `to_vchiq_driver()` perform container conversion. Externs expose `vchiq_bus_type`, `vchiq_device_register()`, `vchiq_device_unregister()`, `vchiq_driver_register()`, and `vchiq_driver_unregister()`. `module_vchiq_driver()` wraps module init/exit registration.

Control flow: the core registers VCHIQ devices under a parent device; client drivers register against `vchiq_bus_type`; probe/remove and PM callbacks are dispatched through the bus.

State and persistence: device-model runtime state is stored in `struct device`, `struct vchiq_device`, and driver bindings. No persistent state is stored.

Dependencies and integration points: depends on Linux device model, module driver helpers, mod_devicetable IDs, PM messages, and VCHIQ management state.

Risks and test signals: risks include device/driver lifetime mismatches, missing ID tables, PM callback ordering around firmware connection state, and parent unbind races. Test driver registration/unregistration, probe/remove failure paths, suspend/resume, module unload, and multiple VCHIQ child devices.
