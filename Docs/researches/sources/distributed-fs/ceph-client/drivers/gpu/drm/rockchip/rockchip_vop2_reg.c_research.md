## sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rockchip_vop2_reg.c

### Purpose

`rockchip_vop2_reg.c` is the SoC capability and register-operation table for Rockchip VOP2 display controllers. It describes supported DRM pixel formats/modifiers, per-window register fields, video-port limits, debug register dump ranges, interface muxing, clock divider setup, alpha blending, overlay layer assignment, and platform-driver matching for RK3566, RK3568, RK3576, and RK3588.

### Important APIs, Types, and Functions

The file is mostly static data consumed by `rockchip_drm_vop2.c` through `struct vop2_data`, `struct vop2_win_data`, `struct vop2_video_port_data`, `struct reg_field`, `struct vop2_regs_dump`, and `struct vop2_ops`. Format arrays distinguish cluster, esmart, smart, RK3576-specific cluster/esmart, AFBC, RK3576 32x8 AFBC half mode, and linear-only planes.

Executable helpers include `rk3568_set_intf_mux()`, `rk3576_set_intf_mux()`, `rk3588_calc_dclk()`, `rk3588_calc_cru_cfg()`, `rk3588_set_intf_mux()`, `vop2_parse_alpha()`, `vop2_setup_cluster_alpha()`, `vop2_setup_alpha()`, `rk3568_vop2_setup_layer_mixer()`, `rk3576_vop2_setup_layer_mixer()`, SoC-specific overlay setup functions, and background-delay setup functions. `vop2_dt_match`, `vop2_probe()`, `vop2_remove()`, and `vop2_platform_driver` connect the table to platform devices and the component framework.

### Control Flow

Platform probing is intentionally thin: `vop2_probe()` registers the component with `vop2_component_ops`, while compatible strings provide the correct `struct vop2_data`. During atomic modeset/commit, the shared VOP2 implementation calls the SoC operations selected from `rk3568_vop_ops`, `rk3576_vop_ops`, or `rk3588_vop_ops`.

Interface setup reads display mode state and output endpoint ID, computes mux selections and polarity fields, writes VOP system interface registers, and, on RK3588/RK3568, also writes GRF/regmap bits for HDMI/eDP/MIPI/RGB routing. RK3588 adds clock-tree calculations for HDMI, eDP, DP, MIPI, and DPI, returning the desired input dclk rate for the common clock code.

Overlay setup walks the DRM CRTC plane list, builds a video-port window mask, configures cluster alpha if a cluster window is present, assigns layers to ports, programs alpha mixers, and writes window delay/background pre-scan timing. RK3568/RK3588 share global overlay layer/port registers guarded by `vop2->ovl_lock` plus polling for cfg-done effects; RK3576 uses per-VP overlay registers and immediate per-window VP selection/delay fields.

### State and Persistence Behavior

Most state is immutable platform data. Runtime writes persist in memory-mapped VOP registers and GRF/PMU regmaps until the next atomic commit, reset, or power cycle. `vop2->old_layer_sel` and `vop2->old_port_sel` cache shared overlay programming so subsequent commits can migrate layers without selecting one window on multiple layers. Per-window `delay`, per-VP `win_mask`, and CRTC state-derived alpha/mode data are transient commit state.

The alpha helpers translate DRM blend state into hardware mixer fields. Cluster windows get an internal cluster mixer pass, while the VP mixer handles zpos > 0 layers and special propagation of bottom-layer global alpha into the HDR mixer path for VP0.

### Dependencies and Integration Points

The file depends on DRM atomic plane/CRTC state, DRM fourcc modifiers, blend constants, Rockchip output endpoint IDs, VOP2 register macros and accessors from `rockchip_drm_vop2.h`, Linux `regmap`, `FIELD_PREP`, `readx_poll_timeout_atomic`, and the component/platform bus. It integrates with device-tree compatible matching, Rockchip encoder/connector output routing, CRTC state (`rockchip_crtc_state`), and debug dump code that consumes `regs_dump`.

### Risks and Edge Cases

Clock and mux programming is highly SoC-specific; a wrong endpoint ID, polarity mapping, or divider can black-screen only one output type. RK3588 eDP1 programming clears HDMI1/eDP1 masks but appears to use HDMI0 divider field macros in the assignment path, which should be reviewed against the register definition. Shared RK3568/RK3588 overlay registers require strict ordering; skipping the port/layer cfg-done waits can cause layer migration artifacts. Alpha code assumes active planes have framebuffers when computing `fb->format->has_alpha`; callers must not pass malformed atomic state. Many array fields use `0xf` as "not attachable"; new VP/window additions must keep layer IDs, possible VP masks, AXI IDs, and win count consistent. AFBC modifier lists must match the hardware format restrictions or userspace can submit unsupported buffers.

### Test Signals

Useful signals include KMS atomic plane tests across all VPs and zpos orderings, alpha/global-alpha/premultiplied blend tests, AFBC and linear buffer scanout tests, YUV420 high-clock mode tests, output mux smoke tests for HDMI/eDP/DP/MIPI/RGB/LVDS, suspend/resume display restoration, register dump availability, and lockdep/poll-timeout logs during layer migration. SoC bring-up should specifically validate RK3568, RK3576, and RK3588 multi-output combinations because they use different overlay and clock-control paths.
