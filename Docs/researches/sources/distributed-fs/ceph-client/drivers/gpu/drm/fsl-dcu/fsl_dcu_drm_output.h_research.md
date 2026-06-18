<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_output.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_output.h

## Purpose

This header defines the FSL DCU connector wrapper and output creation entry points. It is the interface between core driver storage and the RGB/panel/bridge output implementation.

## Important APIs, Types, And Functions

`struct fsl_dcu_drm_connector` embeds `struct drm_connector` and stores its `drm_encoder` and attached `drm_panel`. `to_fsl_dcu_connector()` converts a DRM connector pointer to the wrapper. The file declares `fsl_dcu_drm_encoder_create()` and `fsl_dcu_create_outputs()`.

## Control Flow

There is no runtime logic beyond the inline container conversion. The declared functions are called during KMS initialization: encoder creation precedes output discovery, and output discovery may create a panel-backed connector or attach a bridge.

## State And Persistence

The connector wrapper persists as part of `struct fsl_dcu_drm_device`; it is not dynamically allocated per connector in this header. The `panel` pointer is set by output discovery and used for mode enumeration.

## Dependencies And Integration Points

It depends on DRM connector/encoder/panel types through including translation units. It integrates `fsl_dcu_drm_drv.h`, the RGB output file, KMS initialization, panel helpers, and bridge attachment.

## Risks And Test Signals

Risks are lifetime mismatches around the embedded connector and panel pointer, and null conversion use if a connector is absent. Test signals are build coverage, panel-backed device trees via legacy `fsl,panel`, modern graph panel/bridge endpoints, connector cleanup, and mode enumeration through `drm_panel_get_modes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_output.h -->
