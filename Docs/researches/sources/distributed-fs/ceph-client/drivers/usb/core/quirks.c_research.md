# sources/distributed-fs/ceph-client/drivers/usb/core/quirks.c

## Purpose
Maintains USB device, interface, endpoint-ignore, and platform-specific quirk detection. It combines static device ID tables with a runtime module parameter so usbcore can adjust enumeration, power management, descriptors, endpoint parsing, reset behavior, and LPM decisions for known-broken devices.

## Important APIs, Types, And Functions
The dynamic parameter is `quirks=` implemented by `quirks_param_set()` with `device_param_cb()`. Static tables include `usb_quirk_list`, `usb_interface_quirk_list`, `usb_amd_resume_quirk_list`, and `usb_endpoint_ignore`. Exported/internal detection APIs are `usb_endpoint_is_ignored()`, `usb_detect_quirks()`, `usb_detect_interface_quirks()`, and `usb_release_quirk_list()`. Helper functions include `usb_match_any_interface()`, `usb_amd_resume_quirk()`, `usb_detect_static_quirks()`, and `usb_detect_dynamic_quirks()`. The private `struct quirk_entry` stores VID/PID/flags for the runtime list.

## Control Flow
Writing `quirks=` parses comma-separated `VID:PID:flags` entries, reallocates `quirk_list` under `quirk_mutex`, and maps flag characters to `USB_QUIRK_*` bits. Static quirk detection walks ordered USB ID tables, matching device fields and optionally any interface's first altsetting. AMD resume quirks apply only for level-1 devices on HCDs marked with the AMD resume bug. Dynamic quirks are XORed with static quirks, allowing runtime toggling of bits. Endpoint-ignore matching checks device, interface, and endpoint address when a device has `USB_QUIRK_ENDPOINT_IGNORE`.

## State And Persistence
Static quirk tables are compile-time data. Dynamic state is the in-memory `quirk_list`, `quirk_count`, and copied `quirks_param` string, protected by `quirk_mutex`. Detected result bits persist for the lifetime of each `usb_device` in `udev->quirks`; `usb_detect_quirks()` may also initialize `persist_enabled`.

## Dependencies And Integration Points
Depends on USB matching helpers, module parameter infrastructure, HCD flags, descriptor parsing, and USB persist configuration. Quirk bits are consumed by enumeration (`message.c` string/config/interface handling), hub reset/LPM code, descriptor parsing, endpoint ignore logic, and sysfs visibility of quirk state.

## Risks And Test Signals
Risks include dynamic XOR semantics surprising users, malformed parameter parsing truncating the parsed list, stale static entries, incorrect interface matching before all altsettings are considered, endpoint-ignore overreach, and persist policy side effects. Test signals include parameter parsing for every flag letter, clearing the list with an empty string, static plus dynamic quirk combination, AMD root-port mouse cases, endpoint-ignore descriptor parsing, and enumeration behavior for devices using string, LPM, reset, BOS, or SetInterface quirks.
