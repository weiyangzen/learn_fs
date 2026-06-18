<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.c

## Purpose

This file initializes GMA500 DRM mode configuration and user framebuffer validation. It creates CRTCs, invokes chip-specific output initialization, assigns encoder CRTC/clone masks, and performs chip errata after output setup.

## Important APIs, Types, And Functions

Important functions are `psb_user_framebuffer_create()`, `psb_setup_outputs()`, `psb_modeset_init()`, and `psb_modeset_cleanup()`. `psb_mode_funcs` supplies the framebuffer creation callback.

## Control Flow

User framebuffer creation rejects unknown depth, YUV or unsupported formats, formats with more than four bytes per pixel, and pitches not aligned to 64 bytes, then delegates to `drm_gem_fb_create()`. Modeset init calls `drmm_mode_config_init()`, sets min bounds and callbacks, creates one CRTC per `dev_priv->num_pipe`, sets max bounds to 4096x4096, runs `psb_setup_outputs()`, applies chip errata, and marks `modeset` true. Output setup creates a scaling property, optionally creates a backlight property, invokes `dev_priv->ops->output_init()`, then iterates connectors to set encoder `possible_crtcs` and clone masks based on GMA output type.

## State And Persistence

Mode config state, CRTC objects, connector/encoder lists, properties, and `dev_priv->modeset` persist after initialization. User framebuffer objects persist through GEM/framebuffer references. Cleanup only finalizes KMS polling when modeset was initialized.

## Dependencies And Integration Points

It integrates DRM mode config, GEM framebuffer helper, connector iteration, chip ops output init/errata masks, CRTC init from other GMA500 files, and `gma_connector_clones()`.

## Risks And Test Signals

Risks include legacy helper mode config without full atomic funcs, pitch alignment rejection compatibility, possible null `backlight_property` attachment if property creation fails, and clone-mask assumptions by output type. Test signals are framebuffer creation with supported/unsupported formats and pitch alignments, CRTC count variants, connector masks for CRT/LVDS/HDMI/DP/eDP, errata invocation, and modeset cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/framebuffer.c -->
