## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi.c

### Purpose

`vlv_dsi.c` implements the i915 MIPI DSI encoder/connector path for Valleyview, Cherryview, Broxton, and Geminilake. It wires a VBT-described DSI panel into DRM, implements the MIPI host transfer path, computes display state, programs DSI controller timing registers, sequences panel power/reset/backlight VBT commands, handles DSI device-ready/ULPS transitions, and applies known DMI panel quirks.

### Important APIs, types, and functions

Public entry points are `vlv_dsi_init()`, `vlv_dsi_wait_for_fifo_empty()`, and `vlv_dsi_min_cdclk()`. Encoder hooks include `intel_dsi_compute_config()`, `intel_dsi_pre_enable()`, `bxt_dsi_enable()`, `intel_dsi_disable()`, `intel_dsi_post_disable()`, `intel_dsi_get_hw_state()`, and `intel_dsi_get_config()`. The MIPI host API is `intel_dsi_host_ops`, with `intel_dsi_host_transfer()` packing `mipi_dsi_msg` payload/header data into LP or HS generic FIFOs. Important helpers include `set_dsi_timings()`, `intel_dsi_prepare()`, `intel_dsi_unprepare()`, `dpi_send_cmd()`, `vlv_dphy_param_init()`, and platform-specific device-ready helpers for VLV, BXT, and GLK.

### Control flow

Initialization starts in `vlv_dsi_init()`: VBT detection chooses the DSI port, the driver allocates `intel_dsi` and `intel_connector`, registers an encoder, initializes one DSI host per active port, loads VBT panel data, optionally uses GOP fastboot pclk readback, computes D-PHY parameters, initializes GPIO/VBT state, registers the connector, adds fixed mode and panel/backlight properties, and applies DMI quirks.

Modeset compute uses panel and pfit helpers, clears unsupported mode flags, sets pipe bpp from DSI pixel format, selects DSI transcoders on BXT/GLK, and delegates PLL calculation to `bxt_dsi_pll_compute()` or `vlv_dsi_pll_compute()`. Pre-enable powers the panel, enables underrun reporting, reinitializes the PLL, performs platform IO/regulator setup, executes VBT power/reset/init sequences, enters LP-11 device-ready state, sends initial DCS commands, enables command or video mode, and enables backlight. Disable and post-disable reverse the flow: backlight off, video shutdown or tear-off, FIFO drain, port disable, unprepare, display-off sequence, LP-00 transition, regulator/PLL shutdown, reset assertion, panel power-off delay, and timestamp persistence in `panel_power_off_time`.

### State and persistence behavior

State lives in `struct intel_dsi`, `struct intel_connector`, `struct intel_crtc_state`, VBT panel data, DSI controller registers, and sideband/PHY registers. The driver persists computed D-PHY timing fields in `intel_dsi` (`dphy_reg`, `lp_byte_clk`, switch counts, timeout counts), tracks panel power-off timing for required power-cycle delays, and stores per-panel quirk adjustments in VBT-derived panel structures. Hardware state readout reconstructs active pipe and port clock from registers, with platform guards to avoid BXT/GLK register access when the DSI PLL has invalid dividers.

### Dependencies

The file depends on DRM atomic/connector helpers, DRM MIPI DSI packet helpers, i915 display core types, panel/VBT helpers, backlight, pfit/scaler, FIFO underrun reporting, DSI PLL helpers from `vlv_dsi_pll.h`, controller register definitions from `vlv_dsi_regs.h`, and IOSF sideband helpers from `vlv_sideband.h`.

### Integration points

It registers `DRM_MODE_ENCODER_DSI` and `DRM_MODE_CONNECTOR_DSI` objects into the i915 display pipeline. `intel_dsi_host_transfer()` is used by MIPI DSI device/panel code to send DCS/generic messages. VBT sequence execution integrates with board-specific GPIO, I2C, and panel command tables. The encoder hooks integrate with atomic modeset, backlight update, fastboot state readout, and shutdown.

### Risks

The code is highly sequence-sensitive: device-ready, ULPS, PHY latch, regulator, PLL, and panel commands must occur in the required order with hardware delays. BXT/GLK can hang if DSI registers are accessed without a valid PLL divider. Dual-link and burst-mode timing conversions round between pixels and byte clocks, creating readout mismatches that the code partially compensates for. Several comments mark known uncertainty around command reads/writes, MIPI timeout formulas, and D-PHY switch counts. DMI quirks intentionally mutate fixed modes and VBT sequences; broad matches could affect unrelated systems.

### Test signals

Test signals include boot/fastboot on VLV/CHV/BXT/GLK DSI panels, suspend/resume panel recovery, backlight on/off sequencing, DCS command reads/writes in LP and HS mode, dual-link panels, command-mode panels, FIFO-empty waits, underrun absence, PLL lock/readout, DMI-quirked tablets, and mode validation against fixed panels.
