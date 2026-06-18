## sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-wmi-descriptor.h

Purpose: declares the public interface for the Dell WMI descriptor helper. It lets dependent Dell WMI modules determine whether the descriptor GUID exists and whether descriptor probing has accepted or rejected the firmware buffer.

Important APIs/types/functions: `dell_wmi_get_descriptor_valid()` returns `-ENODEV` for missing descriptor GUID, `-EPROBE_DEFER` before descriptor probing, `0` for valid descriptors, and another negative errno for invalid descriptors. `dell_wmi_get_interface_version()`, `dell_wmi_get_size()`, and `dell_wmi_get_hotfix()` return `bool` success and fill a caller-provided `u32`.

Control flow and integration: the header is included by consumers such as `dell-wmi-base`, which uses descriptor validity as a probe gate and interface version to decide WMI event-buffer parsing. The helper signatures hide the internal WMI driver and list state.

State and persistence: the header itself has no state; it documents an external, runtime descriptor state owned by `dell-wmi-descriptor.c`.

Dependencies: includes `<linux/wmi.h>` for WMI-related type availability and is GPL-only in the companion implementation.

Risks and test signals: consumers must handle `false` returns from metadata getters because descriptor probing may not have produced a list entry even when the GUID exists. Probe-order tests should exercise `-EPROBE_DEFER`, missing GUID, valid metadata, and invalid metadata behavior. Because this header is small, regression tests are mostly build coverage for all including drivers and behavioral tests through descriptor consumers.
