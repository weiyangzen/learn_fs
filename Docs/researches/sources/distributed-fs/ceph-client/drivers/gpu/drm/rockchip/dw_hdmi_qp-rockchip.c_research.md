# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi_qp-rockchip.c

## Purpose
Provides Rockchip glue for DW HDMI QP controllers on RK3576 and RK3588, including HDMI 2.1-style PHY configuration, HPD interrupt handling, GRF/VO-GRF IO setup, and bridge connector integration.

## Important APIs, Types, And Functions
Key types are `rockchip_hdmi_qp`, `rockchip_hdmi_qp_ctrl_ops`, and `rockchip_hdmi_qp_cfg`. Important callbacks cover encoder enable/atomic-check, PHY power, HPD read/setup, hard IRQ/threaded IRQ, delayed HPD work, SoC IO init, encoder color-depth init, component bind/unbind, and PM suspend/resume.

## Control Flow
Bind identifies the HDMI port by MMIO base, obtains GRF and VO-GRF regmaps, enables all clocks, reads ref clock rate, gets optional FRL GPIO and required PHY, runs SoC IO init, registers threaded HPD IRQ, creates encoder, binds DW HDMI QP, initializes bridge connector, and attaches it. Atomic check configures the HDMI PHY when TMDS character rate or bpc changes and updates Rockchip CRTC output state. Enable forces TMDS by clearing FRL GPIO and writes color-depth state. HPD IRQ masks, clears, debounces, and notifies DRM.

## State And Persistence
Stores selected port, cached TMDS character rate, encoder, PHY, HPD delayed work, GRF handles, and FRL GPIO. GRF/VO-GRF writes persist HPD, pin, grant, mode, and color-depth settings.

## Dependencies And Integration Points
Depends on DW HDMI QP bridge, DRM HDMI state helper data, bridge connector, generic HDMI PHY options, GPIO, clocks, IRQs, system workqueues, and Rockchip CRTC state.

## Risks
FRL is explicitly disabled even though QP hardware may support it. HPD status registers differ by SoC and port, so port base matching is critical. The cached `tmds_char_rate` avoids repeated PHY config but must stay coherent with bpc.

## Test Signals
RK3576/RK3588 port-ID matching, HPD IRQ debounce, PHY configure failures, 8/10 bpc modes, suspend/resume IO reinit and HPD event, FRL GPIO behavior, and dual-port RK3588 operation.
