# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_crtc.c

Purpose: this file adapts Exynos display-controller implementations to the DRM CRTC core. It owns `struct exynos_drm_crtc` allocation, helper callbacks, vblank event handling, possible-CRTC assignment for encoders, and the Tearing Effect callback dispatch used by command-mode panels.

Important APIs and functions: `exynos_drm_crtc_create()` allocates the Exynos wrapper, stores the output type, callback table, and implementation context, then calls `drm_crtc_init_with_planes()` and attaches `exynos_crtc_helper_funcs`. `exynos_drm_crtc_get_by_type()` scans `drm_for_each_crtc()` and returns the CRTC whose `type` matches an `enum exynos_drm_output_type`. `exynos_drm_set_possible_crtcs()` converts that result to an encoder `possible_crtcs` bitmask. `exynos_crtc_handle_event()` arms pending page-flip events on the next vblank. `exynos_drm_crtc_te_handler()` forwards panel TE signals to the hardware-specific callback.

Control flow: DRM atomic helpers enter this file through helper callbacks. Atomic enable calls the hardware `ops->atomic_enable()` first, then enables vblank accounting with `drm_crtc_vblank_on()`. Atomic disable reverses this order: vblank accounting is turned off, hardware is disabled, and a pending event is sent immediately if the state is no longer active. Atomic check, begin, flush, mode validation, mode fixup, vblank enable, and vblank disable are all thin dispatchers into the `exynos_drm_crtc_ops` supplied by FIMD, DECON, mixer, or another CRTC provider.

State and persistence: there is no persistent storage. State lives in the heap-allocated `exynos_drm_crtc`, its `ops`, `ctx`, output `type`, optional `pipe_clk`, and CRTC atomic state. Event state is coordinated under `crtc->dev->event_lock`.

Dependencies and integration points: this file depends on DRM atomic helper, encoder, probe helper, and vblank APIs plus Exynos plane and driver structures. It is consumed by display controllers such as FIMD and by bridge/encoder glue such as DPI, DSI, and MIC when selecting LCD CRTCs or relaying TE signals.

Risks: the code assumes `ops` is valid and that hardware callbacks tolerate the CRTC state being in the DRM helper phase in which they are called. `exynos_crtc_handle_event()` warns if `drm_crtc_vblank_get()` fails, so incorrect vblank enablement can surface as event loss. `exynos_drm_crtc_get_by_type()` casts all CRTCs to Exynos CRTCs, so mixed CRTC types in the device would be unsafe.

Test signals: useful tests are atomic modesets, page flips with and without vblank, command-mode TE page flips, encoder binding for each output type, and suspend/disable cases that must deliver outstanding events exactly once.
