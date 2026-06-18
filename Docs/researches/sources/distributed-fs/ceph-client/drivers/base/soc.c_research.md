# sources/distributed-fs/ceph-client/drivers/base/soc.c

Purpose: this file implements the generic SoC bus and SoC device registration helpers used to expose SoC identity information through sysfs and to let drivers match against machine/family/revision/SoC ID tuples.

Important APIs, types, and functions: `struct soc_device` wraps a `struct device`, `struct soc_device_attribute *`, and IDA-allocated numeric ID. Exported functions are `soc_device_to_device`, `soc_attr_read_machine`, `soc_device_register`, `soc_device_unregister`, and `soc_device_match`. It defines a `soc` bus type and sysfs attributes `machine`, `family`, `serial_number`, `soc_id`, and `revision`.

Control flow: registration first fills the machine string from DT model when absent. If the SoC bus is not registered yet, one early attribute pointer can be stored and later registered by the `core_initcall`. Normal registration allocates the device and attribute group array, assigns a unique ID via `ida_alloc`, configures bus/groups/release callback, names the device `socN`, and calls `device_register`. Attribute visibility is conditional: only attributes with non-NULL source strings are exposed. Matching iterates candidate match entries and bus devices, comparing requested fields with `glob_match`.

State and persistence: global state includes `soc_ida`, `soc_bus_registered`, and `early_soc_dev_attr`. Per-device state persists as a registered device until `soc_device_unregister`, at which point `soc_release` frees the ID, groups, and wrapper.

Dependencies and integration points: it integrates with the device core, sysfs, IDA, Open Firmware model reading, and `linux/sys_soc.h`. Consumers use `soc_device_match()` as a fallback when device-tree compatible strings are not enough to identify variants.

Risks: early registration supports only one pending SoC attribute, so competing early users get `-EBUSY`. The attribute strings are owned by the caller and the comment requires freeing `soc_dev->attr` only after unregister. Matching with glob patterns is flexible but can hide overly broad match rules.

Test signals: boot-time sysfs entries under the `soc` bus and callers of `soc_device_match()` are the main runtime signals. Tests should check early registration before `soc_bus_register`, missing optional attributes, glob matching, unregister cleanup, and ID reuse.
