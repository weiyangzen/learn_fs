# sources/distributed-fs/ceph-client/drivers/acpi/acpi_video.c

Purpose: implements the Linux ACPI video bus driver. It discovers ACPI video output devices, evaluates `_DOD`, `_DOS`, `_BCL`, `_BCM`, `_BQC`/`_BCQ`, and `_DDC`, exposes firmware backlight devices, emits input events for video and brightness hotkeys, registers LCD thermal cooling devices, and exports helper APIs for GPU/vendor drivers.

Important APIs/types/functions: core state is `struct acpi_video_bus` plus `struct acpi_video_device`; exported APIs are `acpi_video_register`, `acpi_video_unregister`, `acpi_video_register_backlight`, `acpi_video_get_levels`, `acpi_video_get_edid`, and `acpi_video_handles_brightness_key_presses`. Key internals include `acpi_video_bus_probe`, `acpi_video_device_enumerate`, `acpi_video_bus_get_one_device`, `acpi_video_init_brightness`, `acpi_video_bqc_quirk`, `acpi_video_bus_notify`, and `acpi_video_device_notify`.

Control flow: module init either registers immediately or defers behind Intel OpRegion initialization. Probe rejects duplicate buses unless allowed, detects capabilities, verifies a PCI VGA parent, enumerates `_DOD`, walks child ACPI devices, binds children by `_ADR`, installs input and ACPI notify handlers, and optionally registers backlights. Brightness setup reads and normalizes `_BCL`, validates `_BQC`, initializes brightness through `_BCM`, and hotkey notifications schedule delayed brightness changes when firmware is not expected to handle them.

State and persistence: persistent kernel state includes module parameters, `register_count`, `may_report_brightness_keys`, `video_bus_head`, per-bus child lists, per-device brightness tables, input devices, backlight devices, cooling devices, and PM notifier state. Firmware-visible state is changed through `_DOS` and `_BCM`; resume restores cached brightness.

Dependencies and integration: depends on ACPI evaluation/notification, auxiliary bus, PCI lookup, DMI quirks, input, backlight, thermal cooling, sysfs links, workqueues, and `<acpi/video.h>`. GPU drivers use the exported registration/backlight calls; vendor drivers use the brightness-key ownership helper; EDID consumers use `acpi_video_get_edid`; userspace sees backlight/input/thermal devices.

Risks: firmware variance drives most risk: malformed `_BCL`, broken or indexed `_BQC`, missing or duplicate `_DOD`, wrong device ID scheme bits, duplicate video buses, and systems that change brightness themselves. Backlight ownership must not conflict with native GPU drivers, and notify removal must cancel delayed brightness work before device free.

Test signals: boot ACPI-video and native-backlight systems; cover DMI quirks, reversed/unordered brightness tables, missing AC/battery `_BCL` entries, `_BQC` value-versus-index behavior, hotkey reporting/veto, suspend/resume restore, duplicate detection, EDID length fallbacks, and module unload with lockdep/workqueue checks.
