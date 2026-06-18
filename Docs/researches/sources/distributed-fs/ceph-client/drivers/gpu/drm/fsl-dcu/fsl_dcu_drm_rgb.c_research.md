<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_rgb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_rgb.c

## Purpose

This file implements the simple RGB/LVDS output side of the FSL DCU DRM driver. It creates a simple LVDS encoder, optionally enables TCON bypass, discovers a panel or bridge from device tree, and creates/registers a panel-backed connector when needed.

## Important APIs, Types, And Functions

Main entry points are `fsl_dcu_drm_encoder_create()` and `fsl_dcu_create_outputs()`. Internal helpers include `fsl_dcu_drm_connector_destroy()`, `fsl_dcu_drm_connector_get_modes()`, `fsl_dcu_drm_connector_mode_valid()`, and `fsl_dcu_attach_panel()`. Connector callbacks use atomic state helpers, single-connector probing, panel mode enumeration, and LVDS connector type.

## Control Flow

Encoder creation sets `possible_crtcs = 1`, enables TCON bypass if available, and initializes a simple LVDS encoder. Output creation first checks the legacy `fsl,panel` phandle and attaches that panel through a locally initialized connector. If absent, it calls `drm_of_find_panel_or_bridge()` for graph-based discovery. A panel is attached through the same connector path; otherwise the bridge is attached directly to the encoder. Mode validation rejects horizontal display values not divisible by 16, matching the DCU display-size register encoding.

## State And Persistence

Output state is stored in the embedded encoder and connector inside `fsl_dcu_drm_device`. The connector stores the panel pointer and encoder pointer. TCON bypass is a hardware bit in the optional TCON block. Connector registration creates sysfs/user-visible state until cleanup.

## Dependencies And Integration Points

The file integrates OF graph helpers, DRM panel/bridge APIs, simple encoder helpers, atomic connector helpers, `drm_panel_get_modes()`, `drm_bridge_attach()`, and `fsl_tcon_bypass_enable()`. It is called by KMS initialization after CRTC creation.

## Risks And Test Signals

Risks include legacy and graph bindings disagreeing, unhandled deferred probe from panel/bridge lookup, connector registration cleanup on attach failure, no EDID/HPD path for bridges in this file, and the strict 16-pixel width rule surprising userspace. Test signals are legacy panel DT, graph panel DT, graph bridge DT, deferred-probe behavior, connector sysfs cleanup, and `modetest` mode validation for widths with and without low four bits set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_rgb.c -->
