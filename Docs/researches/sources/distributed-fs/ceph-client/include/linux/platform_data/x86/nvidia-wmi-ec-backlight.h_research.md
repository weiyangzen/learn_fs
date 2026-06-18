# sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h

## Purpose
`nvidia-wmi-ec-backlight.h` is a Linux kernel x86 platform integration data header. It gives board
files, MFD children, ACPI glue, or platform-device setup code a compact contract for passing the
primary type `struct wmi_brightness_args`; enumerations such as `enum wmi_brightness_method`, `enum
wmi_brightness_mode` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `__PLATFORM_DATA_X86_NVIDIA_WMI_EC_BACKLIGHT_H`, `WMI_BRIGHTNESS_GUID`. Types:
`struct wmi_brightness_args`, `enum wmi_brightness_method`, `enum wmi_brightness_mode`, `enum
wmi_brightness_source`. Declared or inline functions: none visible in this header. Important struct
details: struct wmi_brightness_args fields include `u32 mode`, `u32 val`, `u32 ret`, `u32
ignored[3]`. Important enum details: enum wmi_brightness_method values include
`WMI_BRIGHTNESS_METHOD_LEVEL`, `WMI_BRIGHTNESS_METHOD_SOURCE`, `WMI_BRIGHTNESS_METHOD_MAX`; enum
wmi_brightness_mode values include `WMI_BRIGHTNESS_MODE_GET`, `WMI_BRIGHTNESS_MODE_SET`,
`WMI_BRIGHTNESS_MODE_GET_MAX_LEVEL`, `WMI_BRIGHTNESS_MODE_MAX`; enum wmi_brightness_source values
include `WMI_BRIGHTNESS_SOURCE_GPU`, `WMI_BRIGHTNESS_SOURCE_EC`, `WMI_BRIGHTNESS_SOURCE_AUX`,
`WMI_BRIGHTNESS_SOURCE_MAX`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/platform/x86/nvidia-wmi-ec-backlight.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/video_detect.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
Direct source-tree consumers found by include search are `sources/distributed-fs/ceph-
client/drivers/platform/x86/nvidia-wmi-ec-backlight.c`, `sources/distributed-fs/ceph-
client/drivers/acpi/video_detect.c`. It integrates through `struct platform_device` platform data,
board files, MFD child registration, and legacy non-DT setup paths; many modern systems may replace
parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h` completely for this pass (76 lines, 2902 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/x86/nvidia-wmi-ec-backlight.h_research.md`.
