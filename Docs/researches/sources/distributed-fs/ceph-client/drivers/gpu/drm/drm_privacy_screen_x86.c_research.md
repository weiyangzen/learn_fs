# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_privacy_screen_x86.c

Purpose: provides x86 architecture-specific privacy-screen lookup initialization for known laptop platform providers, currently ThinkPad ACPI and ChromeOS privacy-screen devices when configured.

Important APIs/types/functions: static `arch_lookup` is the runtime lookup copy. `struct arch_init_data` pairs a lookup entry with a detect callback. `detect_thinkpad_privacy_screen()` discovers EC method `HKEY.GSSS`; `detect_chromeos_privacy_screen()` checks ACPI device `GOOG0010`. `drm_privacy_screen_lookup_init()` registers the first detected provider and `drm_privacy_screen_lookup_exit()` removes it.

Control flow: init iterates the compile-time `arch_init_data` array, runs each detect callback, logs the first matching provider, copies its `__initconst` lookup into persistent storage, adds it to the privacy-screen core, and stops. Exit removes the lookup only if one was registered.

State and persistence behavior: only one global x86 lookup is active. The selected lookup persists in `arch_lookup` because the source table is init-only memory.

Dependencies and integration points: depends on ACPI, optional ThinkPad ACPI and ChromeOS privacy-screen configs, and `drm_privacy_screen_lookup_add/remove()` from the core privacy-screen file.

Risks: first-match behavior means only one platform provider is registered even if multiple detectors match. ACPI method names and provider device names must match provider drivers exactly. Build coverage varies with optional configs, so stubs may compile away most code.

Test signals: boot on supported ThinkPad and ChromeOS systems, ACPI-disabled path, configs with each detector enabled/disabled, lookup removal at DRM exit, and consumer deferred-probe behavior until the provider class device appears.
