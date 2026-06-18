# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_backlight_quirks.c

## Purpose

`drm_panel_backlight_quirks.c` provides a small platform quirk table for panels whose minimum brightness or brightness encoding cannot be reliably inferred from firmware or EDID alone. It currently covers Framework laptops, Steam Deck variants, and several handheld/OLED systems.

## Important APIs, Types, and Functions

- `struct drm_panel_match` stores one DMI field/value match.
- `struct drm_get_panel_backlight_quirk` combines up to two DMI matches, an optional `drm_edid_ident`, and the returned `drm_panel_backlight_quirk`.
- `drm_panel_min_backlight_quirks[]` is the static quirk database. Entries use `min_brightness = 1` or `brightness_mask = 3`.
- `drm_panel_min_backlight_quirk_matches()` checks required DMI fields and optional EDID identity.
- `drm_get_panel_backlight_quirk()` is the exported lookup function.

## Control Flow

Lookup first returns `-ENODATA` when DMI support is not enabled and `-EINVAL` for a missing EDID pointer. It then scans `drm_panel_min_backlight_quirks[]` in order. Each candidate rejects if the primary DMI match fails, the secondary DMI match fails, or an EDID identity is present and `drm_edid_match()` fails. The first matching entry returns a pointer to the embedded quirk. No match returns `ERR_PTR(-ENODATA)`.

## State and Persistence

The file is read-only after module load. The returned quirk points into static const table storage and must not be modified or freed.

## Dependencies and Integration Points

It depends on DMI matching, DRM EDID helpers, and the public `drm_panel_backlight_quirk` type. Display/backlight code can call the exported function after reading EDID to clamp minimum brightness or mask brightness values for known broken systems.

## Risks and Edge Cases

- Table ordering matters because lookup returns the first match.
- Some entries are DMI-only and ignore EDID, which is intentional for systems where panel identity is not needed but increases false-positive risk.
- `brightness_mask = 3` encodes a hardware-specific workaround; callers must know how to apply it.
- Systems without `CONFIG_DMI` never match even if EDID matches.
- New quirks must use sufficiently specific DMI fields to avoid changing brightness behavior on unrelated hardware.

## Test Signals

Useful tests include DMI/EDID match and mismatch cases, DMI-only Steam Deck entries, Framework EDID-specific entries, `NULL` EDID rejection, `CONFIG_DMI=n` fallback, and caller behavior for both `min_brightness` and `brightness_mask`.
