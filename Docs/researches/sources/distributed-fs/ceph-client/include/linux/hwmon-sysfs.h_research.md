# sources/distributed-fs/ceph-client/include/linux/hwmon-sysfs.h

## Purpose
Provides legacy sysfs attribute helper structs and macros for hardware monitoring sensor drivers.

## APIs, Control Flow, and State
`struct sensor_device_attribute` embeds `device_attribute` plus one integer index; `struct sensor_device_attribute_2` adds `nr` and `index` bytes for two-dimensional sensor attributes. `to_sensor_dev_attr()` and `_2()` recover containers from attributes. `SENSOR_ATTR*` and `SENSOR_DEVICE_ATTR*` macros generate read-only, write-only, and read-write attribute initializers or definitions using conventional `_show` and `_store` function names. State is per static/global attribute object and per sysfs file created elsewhere.

## Dependencies, Integration, Risks, and Tests
Depends on driver core device attributes and kstrtox helpers commonly used by store callbacks. Integrates with hwmon drivers that expose raw sysfs groups instead of the newer `hwmon_chip_info` API. Risks include duplicate static symbol names, wrong permissions, index/nr truncation in `_2`, and callbacks misinterpreting the encoded indices. Test signals are sysfs file presence, permissions, read/write callback coverage, and sensor index mapping tests.
