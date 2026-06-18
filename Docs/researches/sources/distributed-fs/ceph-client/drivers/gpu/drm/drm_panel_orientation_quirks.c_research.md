# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_panel_orientation_quirks.c

## Purpose

`drm_panel_orientation_quirks.c` is a DMI-based quirk database for x86 devices whose built-in portrait panels need a default framebuffer rotation but cannot expose reliable orientation metadata. The file is intentionally independent of broader DRM internals because fbdev/efifb also uses it.

## Important APIs, Types, and Functions

- `struct drm_dmi_panel_orientation_data` stores expected panel width, height, optional BIOS date allow-list, and a `DRM_MODE_PANEL_ORIENTATION_*` value.
- Static data objects define common resolution/orientation pairs and special GPD/OneGX entries with BIOS date filters.
- `orientation_data[]` is the DMI system table covering Acer, Anbernic, ASUS, AYANEO, GPD, Lenovo, Valve, ZOTAC, and other handheld/tablet devices.
- `drm_get_panel_orientation_quirk(width, height)` is the exported lookup API. With `CONFIG_DMI=n`, it always returns `DRM_MODE_PANEL_ORIENTATION_UNKNOWN`.

## Control Flow

When DMI is enabled, lookup iterates every matching DMI entry by repeatedly calling `dmi_first_match()`. For each matched system, it reads the attached orientation data, verifies the caller-provided width and height exactly match the expected panel resolution, and then either returns the orientation directly or checks the current BIOS date against the entry's allow-list. If resolution or BIOS date does not match, lookup continues to later DMI matches. If nothing qualifies, it returns `UNKNOWN`.

## State and Persistence

All state is static const data. There are no allocations, no locks, and no runtime mutation. The result is computed from current system DMI strings and caller-provided panel dimensions.

## Dependencies and Integration Points

The file depends on Linux DMI helpers, `drm_connector.h` orientation enum definitions, and `drm_utils.h` for matching helpers. It is consumed by DRM and framebuffer boot paths that need a safe default orientation before full userspace display configuration.

## Risks and Edge Cases

- False positives are a major concern; many entries add exact DMI strings, resolution checks, and sometimes BIOS dates to avoid matching generic tablet platforms.
- Two devices can share DMI identity but use different panel resolutions; the width/height filter is mandatory to select the right orientation.
- Entries with `DMI_MATCH` are broader than `DMI_EXACT_MATCH` and need careful review.
- `CONFIG_DMI=n` means no quirks are available on non-DMI platforms.
- Adding a new DMI quirk can affect early framebuffer console orientation before userspace starts.

## Test Signals

Tests should cover exact DMI plus resolution matches, generic DMI plus BIOS date filters, resolution mismatch returning `UNKNOWN`, multiple matching DMI rows selecting the row whose resolution matches, `CONFIG_DMI=n` behavior, and representative devices for each orientation value.
