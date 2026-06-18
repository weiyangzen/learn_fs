# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/simatic-ipc.c

Purpose: This is the central Siemens SIMATIC IPC platform identification driver. It reads Siemens DMI station IDs and creates model-specific child platform devices for LEDs, watchdogs, and CMOS battery monitoring, plus requests companion sensor/watchdog modules.

Important APIs, types, and functions: `device_modes[]` maps station IDs to LED, watchdog, battery devmodes, and up to two extra module names. `register_platform_devices()` creates child devices with `struct simatic_ipc_platform` platform data and names selected by devmode. `request_additional_modules()` requests extra modules. `simatic_ipc_init_module()` gates on Siemens DMI and uses `simatic_ipc_find_dmi_entry_helper()`.

Control flow: Init checks the DMI vendor whitelist, walks DMI for the OEM station ID, requests model-specific extra modules, and registers battery, LED, then watchdog platform devices if their modes are not `NONE`. Exit unregisters all three child pointers. Unsupported station IDs warn and return an error after attempting no child devices.

State and persistence: Static global platform-device pointers track created child devices. `platform_data` is a static structure reused and modified before each `platform_device_register_data()` call; registration copies it into each device.

Dependencies and integration points: It depends on Siemens platform data headers, DMI station-id parsing helpers, platform-device autoloading by module aliases, and downstream LED/watchdog/battery drivers. It also interacts with module autoloading through `request_module()`.

Risks and edge cases: Error handling does not unwind previously registered child devices if a later child registration fails, potentially leaking a battery or LED child on partial failure. The static `platform_data` reuse is safe only because platform core copies data. Device-mode-to-platform-name mapping must remain synchronized with backend module names and aliases. Init returns 0 when Siemens vendor matches but station ID is missing, so absence can be quiet except for a warning.

Test signals: Test all station IDs in `device_modes`, platform-device names and platform data contents, requested extra modules, unsupported station ID behavior, partial registration failure cleanup, and module exit after partial or full initialization.
