<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_kms.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_kms.c

## Purpose

This file initializes the DRM mode-setting topology for the FSL DCU driver. It sets mode configuration bounds and callbacks, creates the CRTC, encoder, and output connector/bridge/panel objects, resets mode state, and starts KMS polling.

## Important APIs, Types, And Functions

The exported entry point is `fsl_dcu_drm_modeset_init()`. It uses `drm_mode_config_init()`, `drm_mode_config_reset()`, `drm_kms_helper_poll_init()`, `drm_mode_config_cleanup()`, `fsl_dcu_drm_crtc_create()`, `fsl_dcu_drm_encoder_create()`, and `fsl_dcu_create_outputs()`. The local `fsl_dcu_drm_mode_config_funcs` supplies atomic helper check/commit and GEM framebuffer creation.

## Control Flow

Initialization sets the mode bounds to minimum zero and maximum 2031x2047, assigns `fsl_dcu_drm_mode_config_funcs`, creates the CRTC first, then the encoder, then external outputs. On success it resets mode state and enables helper polling. Any failure jumps to cleanup and returns the failing error code.

## State And Persistence

The file mutates `drm->mode_config` and causes CRTC/encoder/connector objects to be registered inside DRM mode lists. No independent state is stored in this file. Polling state persists until `drm_kms_helper_poll_fini()` in the driver unload/remove path.

## Dependencies And Integration Points

It integrates DRM atomic helpers, GEM framebuffer helper, probe/poll helpers, the local CRTC creation API, and output creation API. It is called by `fsl_dcu_load()` and is therefore on the critical DRM registration path.

## Risks And Test Signals

Risks include cleanup after partially-created objects, too-low max width/height for future DCU variants, and missing polling teardown on later load failure paths. Test signals are probe success/failure injection in CRTC/encoder/output creation, `modetest` connector enumeration, fb creation, atomic commits, and hotplug/panel detection polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_kms.c -->
