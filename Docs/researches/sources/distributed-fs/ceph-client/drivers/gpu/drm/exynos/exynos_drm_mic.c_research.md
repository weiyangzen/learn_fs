# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_mic.c

Purpose: this file implements the Exynos MIC display bridge. MIC appears to be a display path block that transforms/compresses panel timing data between FIMD/DSI-like paths and panel output, with separate RGB and I80 modes.

Important structures and APIs: `struct exynos_mic` stores device, MMIO base, sysreg regmap, two clocks, current I80 mode, current videomode, DRM bridge, and enabled flag. `mic_bridge_funcs` supplies bridge `mode_set`, `pre_enable`, and `post_disable`. Component ops bind the bridge to the encoder associated with the LCD CRTC.

Control flow: probe allocates a DRM bridge object, maps MIC registers, obtains the display syscon regmap and clocks, registers the bridge, enables runtime PM, and adds the component. Bind finds the LCD CRTC, scans encoders for matching `possible_crtcs`, stores driver_private, and attaches the MIC bridge to that encoder. During mode set it converts the DRM mode to `videomode` and copies the CRTC `i80_mode` flag. Pre-enable resumes runtime PM, configures sysreg path selection, software-resets MIC, programs porch timing for RGB mode, image size, output timing, and enables MIC registers. Post-disable clears path selection and runtime-PM puts the device. Runtime PM suspend/resume disables/enables both clocks in order.

State and persistence: state is protected by a global `mic_mutex`, including `enabled`, `i80_mode`, and `vm`. The hardware state is sysreg mux bits and MIC registers. No persistence exists.

Dependencies and integration points: depends on DRM bridge/encoder APIs, Exynos CRTC helpers, OF address/graph, syscon/regmap, clocks, runtime PM, and videomode conversion. It integrates into the LCD encoder chain and observes DSI command-mode state through the CRTC.

Risks: bind assumes an LCD CRTC exists and does not check `IS_ERR()` before using it. It selects an encoder by exact `possible_crtcs` equality, which can fail with clone/multi-CRTC masks. The mutex is global rather than per-device, limiting concurrency but simplifying shared path registers. Error messages in `mic_set_path()` say "read" for a failed write. MIC bypass in FIMD has a TODO, so MIC and FIMD sysreg settings may not be fully coordinated.

Test signals: exynos5433 MIC probe, bridge attach to LCD encoder, RGB and I80 modes, DSI command-mode transitions, runtime PM clock ordering, reset timeout, sysreg read/write failures, pre-enable error unwinding, and bridge disable/unbind while enabled.
