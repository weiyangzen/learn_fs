<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.h

## Purpose

`radeon_legacy_encoders.h` is the private declaration header for legacy Radeon encoder setup. It exposes the two functions other mode/discovery code needs: LVDS backlight registration and legacy encoder creation/merging.

## Important APIs, Types, and Functions

- `radeon_legacy_backlight_init(struct radeon_encoder *, struct drm_connector *)`: registers and initializes a legacy LVDS backlight device for the connector/encoder pair.
- `radeon_add_legacy_encoder(struct drm_device *, uint32_t encoder_enum, uint32_t supported_device)`: creates or updates a DRM/Radeon legacy encoder based on BIOS object information and supported device mask.
- Include guard `__RADEON_LEGACY_ENCODERS_H__` provides normal private-header protection.

## Control Flow

The header itself has no runtime flow. Legacy connector/BIOs discovery includes it to call `radeon_add_legacy_encoder()` as encoders are found. LVDS connector setup includes it to register backlight control after the encoder private data is available.

## State and Persistence Behavior

No state is stored here. The declared functions allocate/update DRM encoder objects, Radeon encoder private data, and backlight devices in `radeon_legacy_encoders.c`.

## Dependencies and Integration Points

The declarations rely on `struct radeon_encoder`, `struct drm_connector`, and `struct drm_device` being visible through including contexts. It is part of the private display subsystem contract alongside `radeon_mode.h`.

## Risks and Edge Cases

Because this header is narrow, its main risk is signature drift from the implementation or callers. Adding broad legacy display declarations here would increase coupling and make the legacy modeset boundary harder to maintain.

## Test Signals

Build coverage for legacy connector discovery and LVDS backlight setup is the main signal. Runtime coverage comes from successful encoder creation and backlight registration on legacy Radeon systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_encoders.h -->
