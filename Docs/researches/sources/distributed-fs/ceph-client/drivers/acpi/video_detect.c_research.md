# sources/distributed-fs/ceph-client/drivers/acpi/video_detect.c

### Purpose
`video_detect.c` centralizes ACPI backlight-provider selection. It decides whether the system should expose ACPI video backlight control, native GPU backlight control, vendor/platform control, NVIDIA WMI EC control, Apple gmux, Dell UART, or no backlight device.

### Important APIs, Types, And Functions
The exported API is `__acpi_video_get_backlight_type(bool native, bool *auto_detect)`. Internal helpers parse `acpi_video_backlight_string`, walk ACPI namespace devices via `find_video()`, probe NVIDIA WMI EC support with `nvidia_wmi_ec_supported()`, detect Google EC, Apple gmux, and Dell UART backlight devices, and apply DMI callbacks such as `video_detect_force_vendor()`, `video_detect_force_video()`, `video_detect_force_native()`, and `video_detect_portege_r100()`. The large `video_detect_dmi_table` is the main policy database.

### Control Flow
The first call takes `init_mutex`, parses command-line policy, applies DMI quirks, walks ACPI devices for `ACPI_VIDEO_HID` devices backed by PCI graphics devices, and caches special-controller presence. Later calls only update `native_available` when GPU drivers report native backlight availability. Decision precedence is command line, DMI quirk, special controllers, ACPI video unless native is preferred on Win8+/Chromebook systems, native, `none` for Win8+ systems with no provider yet, then vendor for old hardware.

### State, Persistence, And Dependencies
State is process-wide static cache: command-line choice, DMI result, feature-detection booleans, `native_available`, `video_caps`, and `init_done`. It depends on ACPI namespace walking, DMI, PCI lookup, WMI, `apple_gmux_detect()`, Dell ACPI HIDs, OSI Win8 detection, and GPU drivers calling the native query path.

### Integration Points
Backlight drivers use this to avoid registering competing `/sys/class/backlight` devices. It integrates with `video.ko`, GPU DRM drivers, vendor laptop drivers, `nvidia-wmi-ec-backlight`, `apple-gmux`, Dell UART backlight, Chromebook EC handling, and boot parameter parsing.

### Risks
The risk is mostly policy misclassification: a wrong DMI entry can suppress the only working backlight path, create duplicate controls, or select a provider whose key events/userspace expectations differ. The `native_available` cache makes call order observable, so GPU probe timing affects fallback behavior. The namespace walk intentionally only treats ACPI video devices with PCI graphics backing as usable, which can miss unusual firmware.

### Test Signals
Useful signals are exact backlight provider selected under command-line overrides, DMI quirk coverage on listed systems, absence of duplicate backlight devices, brightness key behavior before and after GPU driver load, Win8+/Chromebook defaulting to native, and NVIDIA EC/Apple gmux/Dell UART detection on matching hardware.
