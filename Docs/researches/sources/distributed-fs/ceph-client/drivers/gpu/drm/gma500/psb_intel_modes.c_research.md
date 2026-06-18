# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/psb_intel_modes.c

## Purpose
This file contains the shared DDC mode probing helper for GMA500 connectors. It reads EDID from an I2C adapter, updates the connector EDID property, and adds EDID modes to the connector.

## Important APIs, Types, and Functions
The single exported function is `psb_intel_ddc_get_modes(struct drm_connector *connector, struct i2c_adapter *adapter)`. It calls `drm_get_edid()`, `drm_connector_update_edid_property()`, `drm_add_edid_modes()`, and frees the returned EDID block.

## Control Flow
The helper initializes `ret` to zero, attempts to read EDID over the provided adapter, and if successful updates connector metadata, adds modes, frees EDID, and returns the number of modes added. If EDID read fails, it returns zero.

## State and Persistence Behavior
No persistent local state is kept. The function mutates DRM connector state by updating its EDID property and probed modes list.

## Dependencies and Integration Points
It is used by LVDS and other display probing paths that have a DDC adapter. It depends on Linux I2C and DRM EDID helpers.

## Risks
The function assumes the adapter pointer is valid; callers must guard missing DDC buses. A zero return conflates absent EDID, invalid EDID, and zero modes, so callers need fallback paths such as VBT or pre-programmed modes.

## Test Signals
Signals include successful EDID reads adding expected modes, connector EDID property updates, proper fallback when `drm_get_edid()` returns NULL, and no EDID memory leaks.
