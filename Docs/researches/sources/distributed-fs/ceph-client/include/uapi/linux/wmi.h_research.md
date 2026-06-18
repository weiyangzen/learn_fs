<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wmi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wmi.h

Purpose: defines ACPI-WMI userspace ioctl payloads for vendor WMI requests, especially Dell SMBIOS-over-WMI commands.

Important APIs and types: `struct wmi_ioctl_buffer` is a generic length-prefixed variable payload. `struct calling_interface_buffer` carries Dell command class/select plus volatile input/output registers modified through SMM. `struct dell_wmi_extensions` and `dell_wmi_smbios_buffer` wrap extended data. Whitelisted class/select constants and token constants constrain supported SMBIOS operations. `DELL_WMI_SMBIOS_CMD` is the ioctl.

Control flow, state, and persistence: userspace sends a whitelisted SMBIOS command through the WMI char device; firmware may mutate the calling buffer in SMM and returns output words/data. Hardware/firmware settings may persist depending on the command.

Dependencies and integration points: integrates with ACPI WMI bus, Dell SMBIOS WMI driver, firmware SMM interfaces, and ioctl userspace tools.

Risks and test signals: risks include SMM side effects, whitelist bypass, packed/volatile layout, variable length validation, and firmware-specific persistence. Test allowed and rejected commands, token read/write, firmware error returns, and buffer length bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wmi.h -->
