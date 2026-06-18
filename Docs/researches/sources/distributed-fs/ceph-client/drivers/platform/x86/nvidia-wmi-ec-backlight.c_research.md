<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/nvidia-wmi-ec-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/nvidia-wmi-ec-backlight.c

## Purpose
This NVIDIA WMI EC backlight driver registers a firmware backlight device for systems where panel brightness is controlled through NVIDIA's WMI-wrapped EC methods.

## Important APIs, Types, And Functions
It uses platform data definitions from `linux/platform_data/x86/nvidia-wmi-ec-backlight.h`, especially `WMI_BRIGHTNESS_GUID`, method IDs, modes, and `struct wmi_brightness_args`. `wmi_brightness_notify()` validates method/mode, calls `wmidev_evaluate_method()`, and reads/writes the in-place argument struct. Backlight operations are `nvidia_wmi_ec_backlight_update_status()` and `nvidia_wmi_ec_backlight_get_brightness()`. Probe queries max and current brightness and registers `nvidia_wmi_ec_backlight`.

## Control Flow
Probe refuses to bind unless ACPI video detection selected `acpi_backlight_nvidia_wmi_ec`, unless `force=1`. It marks the device as `BACKLIGHT_FIRMWARE`, reads maximum brightness with `GET_MAX_LEVEL`, reads current brightness with `GET`, then registers a devm backlight device. Updates call WMI `SET` with the requested brightness.

## State And Persistence
The backlight core stores current requested brightness; firmware/EC stores actual brightness. The driver has no separate persistent state.

## Dependencies And Integration Points
Dependencies include WMI, ACPI video backlight detection, backlight core, and NVIDIA WMI EC platform data. It is intended to be prioritized over raw GPU backlights by using firmware backlight type.

## Risks And Edge Cases
The module parameter description has a missing closing parenthesis but no behavior impact. The WMI helper reuses the same buffer for input and output and assumes firmware updates `args.ret`. Invalid method or mode returns `-EINVAL`; ACPI failures become `-EIO`. `force` can create duplicate or wrong backlight devices.

## Test Signals
Tests should cover ACPI video backlight type gating, force override, max/current brightness queries, set/get round trips, invalid method/mode rejection, ACPI failure handling, and userspace backlight priority against GPU raw backlights.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/nvidia-wmi-ec-backlight.c -->
