# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_ctrl.h

Purpose: Declares the public MSM DP controller interface used by DP display, bridge, IRQ, panel, and link code.

Important APIs/types: `struct msm_dp_ctrl` currently exposes `wide_bus_en`. Public functions cover link/stream power on/off, idle push, IRQ handling, sink request handling, allocation, reset, PHY init/exit, PSR config/set, core clock enable/disable, and IRQ mask enable/disable. The header also declares `msm_dp_ctrl_irq_phy_exit()`.

Control flow/state: Display code obtains a controller with `msm_dp_ctrl_get()`, initializes PHY/clocks around connector state, calls `on_link()` before stream, `on_stream()` to send video, and matching off calls during disable/disconnect. IRQ code calls `msm_dp_ctrl_isr()`.

Dependencies/integration: Includes DP AUX, panel, and link headers and forward-declares PHY. The single public field `wide_bus_en` is consumed by timing setup and pixel-clock decisions.

Risks and test signals: `msm_dp_ctrl_irq_phy_exit()` lacks a visible implementation in the researched source, so link errors or external users may hit a missing symbol depending on build scope. Test full DP display enable/disable and compile/link coverage for all declarations.
