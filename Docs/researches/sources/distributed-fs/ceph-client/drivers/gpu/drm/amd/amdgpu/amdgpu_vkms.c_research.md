# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_vkms.c

## Purpose

This file embeds a VKMS-style virtual KMS implementation inside AMDGPU. It gives devices without usable display hardware, SR-IOV virtual functions, emulation, servers, and early bring-up systems an atomic DRM display pipeline without relying on a separate virtual KMS driver or buffer sharing. It exposes virtual CRTCs, connectors, encoders, primary planes, mode lists, and vblank timing through AMDGPU's display and IP block framework.

## Important APIs, types, and functions

The main exported object is `amdgpu_vkms_ip_block`, an `AMDGPU_DCE` IP block using `amdgpu_vkms_ip_funcs`. DRM callbacks are grouped in `amdgpu_vkms_crtc_funcs`, `amdgpu_vkms_crtc_helper_funcs`, `amdgpu_vkms_connector_funcs`, `amdgpu_vkms_conn_helper_funcs`, `amdgpu_vkms_plane_funcs`, and `amdgpu_vkms_primary_helper_funcs`. Important helpers include `amdgpu_vkms_vblank_simulate()`, `amdgpu_vkms_enable_vblank()`, `amdgpu_vkms_get_vblank_timestamp()`, `amdgpu_vkms_prepare_fb()`, `amdgpu_vkms_cleanup_fb()`, `amdgpu_vkms_output_init()`, `amdgpu_vkms_sw_init()`, and `amdgpu_vkms_hw_init()`.

## Control flow, state, and persistence behavior

`amdgpu_vkms_sw_init()` allocates one `struct amdgpu_vkms_output` per CRTC, installs mode config callbacks, creates common display properties, initializes each virtual output, initializes DRM vblank handling, and starts KMS helper polling. Each output creates a primary plane, CRTC, virtual connector, and virtual encoder, then attaches the connector to the encoder. Vblank is simulated with `amdgpu_crtc.vblank_timer`; enabling vblank computes frame duration and starts the hrtimer, while the timer forwards itself and calls `drm_crtc_handle_vblank()`. Atomic flush arms or sends pending vblank events under the DRM event lock. Framebuffer preparation reserves the AMDGPU BO, reserves move fences, pins it in a scanout-capable domain, allocates GART backing, stores the GPU address in `amdgpu_framebuffer.address`, and takes a BO reference; cleanup unpins and drops the reference. `amdgpu_vkms_hw_init()` disables legacy DCE blocks on selected ASICs so the virtual display path owns display exposure. State is runtime-only: DRM mode objects, pinned framebuffer BOs, vblank hrtimers, KMS polling, and hardware DCE-disable bits.

## Dependencies and integration points

The file depends on DRM atomic, connector, framebuffer, simple KMS, EDID, and vblank helpers plus AMDGPU display, object, IRQ, ATOM, and legacy DCE helpers. It integrates with AMDGPU IP block init/fini/suspend/resume, `adev->mode_info`, `amdgpu_display_user_framebuffer_create()`, and TTM/GEM BO pinning. It provides only `DRM_FORMAT_XRGB8888` and uses CVT-generated common modes, with 1024x768 preferred.

## Risks and test signals

Correctness risks are vblank timer races, event delivery while vblank is disabled, framebuffer BO pin/unpin imbalance, leaked mode objects on partial init failure, and assumptions that primary planes are full-screen and unscaled. Hardware risks are accidental interaction between disabled physical DCE and real display hardware on ASICs where VKMS should be virtual-only. Test signals include successful DRM device registration on headless/SR-IOV devices, `modetest` mode enumeration, page flip completion events, stable suspend/resume, no BO refcount leaks after repeated framebuffer changes, and absence of hrtimer warnings during vblank enable/disable churn.
