<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.h

## Purpose

This header declares Cedarview-specific display callbacks and clock helpers shared across the GMA500 Cedarview files.

## Important APIs, Types, And Functions

It declares `cdv_intel_helper_funcs`, `cdv_clock_funcs`, `cdv_intel_crt_init()`, `cdv_intel_lvds_init()`, `cdv_hdmi_init()`, `cdv_intel_crtc_mode_get()`, `cdv_update_wm()`, and `cdv_disable_sr()`. Forward declarations cover DRM CRTC/device and `psb_intel_mode_device`.

## Control Flow

There is no executable flow. The chip ops table consumes the helper/clock structs, output init calls the connector init functions, LVDS/eDP fallback mode discovery calls `cdv_intel_crtc_mode_get()`, and generic CRTC DPMS calls watermark/self-refresh helpers through `psb_ops`.

## State And Persistence

No state is stored here. The declared functions operate on persistent DRM objects, Cedarview hardware registers, and `drm_psb_private` state.

## Dependencies And Integration Points

It links `cdv_device.c` with `cdv_intel_display.c`, `cdv_intel_crt.c`, `cdv_intel_lvds.c`, `cdv_intel_hdmi.c`, and the DP file through declarations.

## Risks And Test Signals

Risks are API drift between declarations and definitions, especially around legacy DRM helper signatures. Test signals are compile/link coverage and Cedarview mode-set, connector init, watermark, and mode-query paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_device.h -->
