<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.h

## Purpose
This header declares shared Lenovo WMI helper types, thermal mode values, and exported helper functions used by Lenovo Legion WMI drivers.

## Important APIs, Types, And Functions
`struct wmi_method_args_32` is the common two-u32 WMI argument payload. `enum lwmi_event_type` defines `LWMI_GZ_GET_THERMAL_MODE`. `enum thermal_mode` maps Lenovo thermal mode values: none, quiet, balanced, performance, extreme, and custom. Function prototypes cover integer WMI evaluation, thermal-mode notifier registration, devm notifier registration, and thermal-mode query calls.

## Control Flow
The header contains no executable control flow. It defines the ABI between `wmi-helpers.c`, `wmi-gamezone.c`, and consumers such as `wmi-other.c`.

## State And Persistence
No state is owned here. State lives in implementation files and firmware/EC mode registers.

## Dependencies And Integration Points
The header forward-declares Linux device/notifier/WMI structures and includes Linux integer types. The thermal-mode enum is shared with `wmi-events.c` validation and `wmi-gamezone.c` platform-profile conversion.

## Risks And Edge Cases
Changing thermal mode numeric values would break firmware ABI. The two-u32 method payload must remain compatible with Lenovo WMI methods that expect packed 32-bit arguments.

## Test Signals
Build coverage should verify all Lenovo WMI modules agree on enum and struct definitions. Runtime signals come from successful GameZone get/set and Other Mode custom-attribute access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-helpers.h -->
