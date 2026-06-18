## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.c

Purpose: provides a shared Dell WMI descriptor probe and exported query helpers used by other Dell WMI drivers to validate the common descriptor GUID and learn interface metadata.

Important APIs, types, and functions: `struct descriptor_priv` stores one descriptor instance on `wmi_list` with `interface_version`, `size`, and `hotfix`. Exported functions `dell_wmi_get_descriptor_valid()`, `dell_wmi_get_interface_version()`, `dell_wmi_get_size()`, and `dell_wmi_get_hotfix()` are the integration surface. Probe reads `DELL_WMI_DESCRIPTOR_GUID` block 0 and validates ACPI object type, exact 128-byte length, and `"DELL WMI"` signature.

Control flow: the module registers a WMI driver for the descriptor GUID. Before descriptor probe completes, `descriptor_valid` is `-EPROBE_DEFER`. On valid probe it becomes `0`, and the metadata object is appended to a mutex-protected global list. Remove deletes the instance from the list. Consumers typically call `dell_wmi_get_descriptor_valid()` during their probe and defer or fail accordingly.

State and persistence: the module maintains process-local descriptor state only. `descriptor_valid` is global and reflects the most recent descriptor validity result; metadata is per WMI device but helpers return the first list entry.

Dependencies and integration: depends on ACPI/WMI, list/mutex infrastructure, and exports GPL symbols to Dell WMI consumers such as `dell-wmi-base`.

Risks: multiple descriptor devices are represented as a list but accessors return only the first entry. The code casts the ACPI buffer to `u32 *` and also checks `obj->string.pointer`, relying on union layout over the buffer pointer. Invalid descriptor state is sticky through `descriptor_valid`. Test signals include absence of GUID, probe defer before descriptor driver binds, invalid type/length/signature paths, unknown interface-version warning, and consumer probe ordering.
