# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_display.h

## Purpose

`amdgpu_display.h` declares the shared AMDGPU display helper API and defines convenience wrappers around `adev->mode_info.funcs`. It is the contract between display IP implementations, AMDGPU core display setup, and common KMS helper code in `amdgpu_display.c`.

## Important APIs, types, and functions

- Function-hook macros dispatch to ASIC/display-manager-specific callbacks for vblank counters, backlight level, HPD sense/polarity/GPIO, bandwidth update, page flip, scanout position, encoder creation, and connector creation.
- `amdgpu_display_hotplug_work_func()` is the deferred HPD worker entry point.
- `amdgpu_display_update_priority()` applies the module display-priority setting into `adev->mode_info`.
- `amdgpu_display_supported_domains()` returns VRAM and optionally GTT scanout domains for a BO.
- `amdgpu_display_user_framebuffer_create()` and `amdgpu_lookup_format_info()` support DRM framebuffer creation and modifier-aware format lookup.
- `amdgpu_display_suspend_helper()` and `amdgpu_display_resume_helper()` provide shared suspend/resume display handling.
- `amdgpu_display_get_scanout_buffer()` supports DRM panic rendering.
- `ABM_*` constants define adaptive backlight modulation values including sysfs-controlled, off, min, bias, and max levels.

## Control flow

Display IP-specific code installs `adev->mode_info.funcs`; callers use the macros to invoke the active implementation without hard-coding DC or legacy display paths. The declared functions are called from DRM mode-config hooks, PM paths, HPD work scheduling, panic handling, and display initialization.

## State and persistence behavior

The header itself owns no storage beyond constants, but it exposes operations that mutate `adev->mode_info`, CRTC state, framebuffer state, connector properties, BO pinning, and panic scanout buffers. The macros assume `adev->mode_info.funcs` is valid before use.

## Dependencies and integration points

The header includes `<drm/drm_panic.h>` for `struct drm_scanout_buffer` and relies on forward-visible AMDGPU/DRM types supplied by including translation units. It integrates with the mode-info function table populated by ASIC display backends and with common DRM framebuffer and suspend/resume paths.

## Risks and edge cases

The macro wrappers perform no NULL checks. A missing or partially initialized `mode_info.funcs` table will fail at call sites. Because the macros evaluate arguments in function-call form, they should be used with side-effect-safe arguments. ABM constants must stay aligned with property creation and DC/sysfs expectations.

## Test signals

Compile coverage for all display backends is the key header-level signal. Runtime signals include successful page flips, HPD, backlight, scanout position queries, framebuffer creation, suspend/resume, and panic scanout on both DC and non-DC configurations.
