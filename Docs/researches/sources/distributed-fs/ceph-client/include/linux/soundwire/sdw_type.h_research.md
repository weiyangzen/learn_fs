<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_type.h -->
# sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_type.h

Purpose: This header declares SoundWire bus/device types and driver registration helpers used by SoundWire slave drivers.

Important APIs/types/functions: Exports `sdw_bus_type`, `sdw_slave_type`, and `sdw_master_type`; `is_sdw_slave()` tests a device type; `drv_to_sdw_driver()` converts from `device_driver`; `sdw_register_driver()`, `__sdw_register_driver()`, `sdw_unregister_driver()`, `sdw_slave_uevent()`, and `module_sdw_driver()` provide driver model integration.

Control flow: Modules define an `sdw_driver`, register it through the helper macro or direct call, then the driver core probes matching SoundWire slaves. `module_sdw_driver()` wires init/exit automatically.

State and persistence: Driver registration state is owned by the driver core; this header has no local state.

Dependencies/integration: Depends on SoundWire driver definitions from `sdw.h`, kernel module helpers, and the driver model. Uevent support exports device identity to userspace.

Risks and test signals: Risks include registering malformed drivers, wrong device type checks, and uevent modalias mismatches. Test with module load/unload, driver binding, uevents, and `is_sdw_slave()` behavior for master/slave devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/soundwire/sdw_type.h -->
