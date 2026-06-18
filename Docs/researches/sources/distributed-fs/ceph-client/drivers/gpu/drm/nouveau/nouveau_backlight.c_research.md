# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_backlight.c

## Purpose

This file registers and manages Nouveau's native backlight devices for internal LVDS/eDP panels. It supports NV40 register brightness, NV50+ output brightness hooks, eDP AUX/DPCD brightness, Apple GMUX avoidance, ACPI-video fallback, and unique `nv_backlight` naming.

## Important APIs, Types, and Functions

Important functions are `nouveau_backlight_init`, `nouveau_backlight_fini`, `nouveau_backlight_ctor`, `nouveau_backlight_dtor`, `nouveau_get_backlight_name`, `nv40_get_intensity`, `nv40_set_intensity`, `nv40_backlight_init`, `nv50_edp_get_brightness`, `nv50_edp_set_brightness`, `nv50_get_intensity`, `nv50_set_intensity`, and `nv50_backlight_init`. Backlight ops are `nv40_bl_ops`, `nv50_edp_bl_ops`, and `nv50_bl_ops`.

## Control Flow

Initialization skips Apple GMUX, finds an LVDS or eDP encoder, allocates `struct nouveau_backlight`, selects the NV40 or NV50+ backend by GPU family, optionally probes eDP DPCD backlight support, checks ACPI native-backlight preference, reserves a unique IDA-backed name, registers a raw backlight device, stores it on the connector, initializes brightness if needed, and updates status. eDP brightness callbacks take modeset locks and only touch AUX backlight state while the CRTC is active. Teardown unregisters the backlight, frees the ID, clears connector state, and frees memory.

## State and Persistence Behavior

Static `bl_ida` tracks unique backlight names. Per-connector `nouveau_backlight` state stores the registered device, ID, DPCD info, and whether DPCD brightness is used. Hardware brightness persists in NV40 PMC registers, NVIF output state, or panel DPCD registers depending on backend.

## Dependencies and Integration Points

It depends on Linux backlight/IDA APIs, DRM connector/probe/modeset locking, DP AUX/eDP backlight helpers, Nouveau encoder/connector/outp NVIF helpers, ACPI video policy, and Apple GMUX detection.

## Risks

Modeset locking must handle `-EDEADLK` correctly. Registration must not create duplicate native and ACPI backlights. eDP DPCD support probing happens after connector registration and may miss early panel state. Backlight ID cleanup must match successful ID allocation. Ampere support is marked unconfirmed.

## Test Signals

Test NV40 register brightness, NV50 LVDS/eDP brightness, DPCD backlight panels, ACPI fallback, Apple GMUX systems, suspend/resume brightness restoration, connector disconnect/teardown, and deadlock-backoff paths.
