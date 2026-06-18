# sources/distributed-fs/ceph-client/include/acpi/video.h

Purpose: Defines ACPI video/backlight public interfaces, notification codes, display type constants, brightness state structures, and backlight-selection helpers used by GPU, backlight, and platform drivers.

Important APIs, types, and functions: Exports `struct acpi_video_brightness_flags`, `struct acpi_video_device_brightness`, `ACPI_VIDEO_CLASS`, display type constants, notify values `0x80`-`0x89`, `enum acpi_backlight_type`, and APIs `acpi_video_register()`, `acpi_video_unregister()`, `acpi_video_register_backlight()`, `acpi_video_get_edid()`, `acpi_video_handles_brightness_key_presses()`, `acpi_video_get_levels()`, `__acpi_video_get_backlight_type()`, `acpi_video_get_backlight_type()`, and `acpi_video_backlight_use_native()`. Disabled builds return `-ENODEV`, vendor/native defaults, or false.

Control flow: Enabled GPU/platform drivers query the selected backlight type, optionally signal native GPU backlight availability, retrieve EDID/brightness levels, and register ACPI video support. Disabled builds steer callers to vendor/native fallbacks.

State and persistence: Runtime state includes brightness level arrays, current level, ACPI video registration, and global backlight-detection state. Firmware methods `_BCL`, `_BQC`, `_BCM`, and EDID methods provide persisted/firmware-backed data.

Dependencies and integration points: Depends on ACPI device structures, errno/types, GPU drivers, backlight class devices, input brightness key handling, and platform quirks.

Risks and test signals: Risks include incorrectly caching key-handling state, non-GPU callers invoking `acpi_video_backlight_use_native()`, malformed brightness packages, reversed/indexed brightness handling bugs, and disabled-stub policy changes. Test brightness hotkeys, native/vendor/ACPI selection on laptops, EDID retrieval, `_BCL` variants, module unload, and no-`CONFIG_ACPI_VIDEO` builds.
