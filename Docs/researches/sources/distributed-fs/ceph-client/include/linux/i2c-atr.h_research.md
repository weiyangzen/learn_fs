# sources/distributed-fs/ceph-client/include/linux/i2c-atr.h

## Purpose
Defines the I2C Address Translator helper API for devices that expose downstream buses using address aliases.

## APIs, Control Flow, and State
`enum i2c_atr_flags` distinguishes static mapping and passthrough behavior. `struct i2c_atr_ops` lets hardware drivers attach or detach an alias for a downstream address on a channel. `struct i2c_atr_adap_desc` describes each child adapter, including channel ID, parent device, firmware node, and optional private alias pool. `i2c_atr_new()` creates an ATR helper tied to a parent adapter and device; `i2c_atr_add_adapter()` creates child buses; `i2c_atr_del_adapter()` removes them; `i2c_atr_delete()` requires all child adapters be removed first; set/get driver-data helpers attach private state.

## Dependencies, Integration, Risks, and Tests
Depends on I2C core, device/fwnode APIs, and bit flags. Integrates with camera/serializer/deserializer and similar topologies where identical downstream devices need address translation. Risks include alias pool exhaustion, deleting ATR before child adapters, static mapping assumptions with dynamic devices, incorrect firmware-node channel matching, and passthrough address conflicts. Test signals include adding/removing downstream devices, alias attach/detach callback order, private alias pool selection, duplicate address handling, and hot-unplug cleanup.
