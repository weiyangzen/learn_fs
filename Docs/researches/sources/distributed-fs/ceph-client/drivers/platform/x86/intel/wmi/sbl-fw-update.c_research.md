<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/sbl-fw-update.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/sbl-fw-update.c

Purpose: WMI driver for Intel Slim Bootloader firmware-update signaling. It exposes a `firmware_update_request` sysfs attribute on WMI devices matching GUID `44FADEB1-B204-40F2-8581-394BBDC1B651`, allowing userspace to request an SBL firmware update on next reboot.

Important APIs/functions: `get_fwu_request()` calls `wmidev_query_block()` and decodes a little-endian u32; `set_fwu_request()` calls `wmidev_set_block()` with a little-endian u32. `firmware_update_request_show()` and `_store()` implement the sysfs ABI. The `wmi_driver` uses `dev_groups = firmware_update_groups` and `no_singleton = true`.

Control flow: binding to the WMI GUID logs attachment and automatically creates the sysfs attribute. Reads query WMI block 0 and return the current value. Writes parse an unsigned integer, reject values above 1, and write block 0. Remove only logs detachment.

State/persistence: state lives in firmware/SBL WMI storage, not in the driver. Written value is intended to influence the next reboot firmware update path.

Dependencies/integration: depends on ACPI WMI bus, sysfs device attributes, endian conversion, and SBL firmware implementing the documented GUID/block behavior.

Risks: a write of `1` has firmware-update consequences on reboot; validation restricts values to 0/1 but cannot validate firmware policy. `wmidev_query_block()` allocation is freed with `kfree(result)` after using `buffer.data`.

Test signals: on matching WMI devices, the attribute should read `0` or `1`, reject invalid strings and values >1, and call `wmidev_set_block()` successfully for valid writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/wmi/sbl-fw-update.c -->
