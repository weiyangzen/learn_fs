<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_soc.h -->
# sources/distributed-fs/ceph-client/include/linux/sys_soc.h

## Purpose

`sys_soc.h` declares the SoC bus registration and matching API. It lets platform code register SoC identity attributes as a device and lets drivers match against machine/family/revision/SoC IDs.

## Important APIs, types, and functions

`struct soc_device_attribute` stores machine, family, revision, serial number, SoC ID, opaque data, and an optional custom attribute group. APIs include `soc_device_register()`, `soc_device_unregister()`, `soc_device_to_device()`, `soc_attr_read_machine()`, and `soc_device_match()` when `CONFIG_SOC_BUS` is enabled.

## Control flow

Platform code allocates and fills attributes, registers a SoC device, and exposes attributes through the driver model/sysfs. Consumers call `soc_device_match()` with a table of desired attributes and receive the matching entry or NULL. Unregister tears down the device.

## State and persistence behavior

Registered SoC devices persist in the device model until explicitly unregistered. Attribute strings must remain valid for that lifetime. Match data is static caller-owned data.

## Dependencies and integration points

It depends on the Linux device model and integrates with platform/SoC initialization, sysfs SoC identification, DMI/firmware model reads, and drivers needing SoC-specific quirks.

## Risks and test signals

Risks include attribute lifetime bugs, overly broad matches, missing CONFIG_SOC_BUS stubs returning NULL, and custom attribute group misuse. Tests should register/unregister SoC devices, verify sysfs attributes, match exact and wildcard-like tables, read machine attributes, and build with SOC_BUS disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sys_soc.h -->
